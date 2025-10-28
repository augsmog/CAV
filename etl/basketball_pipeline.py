"""
Basketball Data ETL Pipeline
Collects and transforms basketball data from the API
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models_basketball import (
    BasketballTeam, BasketballPlayer, BasketballPerformanceStat, BasketballTransfer
)
from scrapers.cbb_api_client import CollegeBasketballDataAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasketballDataPipeline:
    """ETL pipeline for basketball data"""
    
    def __init__(self, api_client: CollegeBasketballDataAPI):
        self.api = api_client
        self.session = get_session()
    
    def transform_player_data(self, player_data: Dict, team_id: int, year: int) -> Dict:
        """Transform raw API player data to database format"""
        return {
            'team_id': team_id,
            'name': player_data.get('name', ''),
            'jersey': player_data.get('jersey', player_data.get('number')),
            'position': player_data.get('position', ''),
            'height': player_data.get('height'),
            'weight': player_data.get('weight'),
            'year_str': player_data.get('year', player_data.get('class')),
            'hometown': player_data.get('hometown'),
            'state': player_data.get('state'),
            'high_school': player_data.get('high_school'),
            'season': year
        }
    
    def transform_stat_data(self, stat_data: Dict, player_id: int, year: int) -> Dict:
        """Transform raw API stat data to database format"""
        return {
            'player_id': player_id,
            'season': year,
            'games_played': stat_data.get('games', stat_data.get('gp', 0)),
            'games_started': stat_data.get('games_started', stat_data.get('gs', 0)),
            'minutes_per_game': stat_data.get('minutes', stat_data.get('mpg', 0.0)),
            'points': stat_data.get('points', stat_data.get('pts', 0.0)),
            'rebounds': stat_data.get('rebounds', stat_data.get('reb', 0.0)),
            'assists': stat_data.get('assists', stat_data.get('ast', 0.0)),
            'steals': stat_data.get('steals', stat_data.get('stl', 0.0)),
            'blocks': stat_data.get('blocks', stat_data.get('blk', 0.0)),
            'turnovers': stat_data.get('turnovers', stat_data.get('tov', 0.0)),
            'personal_fouls': stat_data.get('fouls', stat_data.get('pf', 0.0)),
            'fg_made': stat_data.get('fgm', 0.0),
            'fg_attempts': stat_data.get('fga', 0.0),
            'fg_pct': stat_data.get('fg_pct', 0.0),
            'three_pt_made': stat_data.get('three_pm', stat_data.get('3pm', 0.0)),
            'three_pt_attempts': stat_data.get('three_pa', stat_data.get('3pa', 0.0)),
            'three_pt_pct': stat_data.get('three_pct', stat_data.get('3p_pct', 0.0)),
            'ft_made': stat_data.get('ftm', 0.0),
            'ft_attempts': stat_data.get('fta', 0.0),
            'ft_pct': stat_data.get('ft_pct', 0.0),
            # Advanced stats (if available)
            'per': stat_data.get('per'),
            'usage_rate': stat_data.get('usage_rate', stat_data.get('usg', 0.0)),
            'offensive_rating': stat_data.get('offensive_rating', stat_data.get('ortg')),
            'defensive_rating': stat_data.get('defensive_rating', stat_data.get('drtg')),
            'ws': stat_data.get('ws'),
            'bpm': stat_data.get('bpm')
        }
    
    def collect_rosters(self, year: int, limit: int = None) -> tuple:
        """Collect rosters for all teams"""
        logger.info(f"Collecting basketball rosters for {year} season...")
        
        teams = self.session.query(BasketballTeam).all()
        if limit:
            teams = teams[:limit]
        
        total_teams = len(teams)
        players_added = 0
        players_updated = 0
        teams_processed = 0
        teams_failed = 0
        
        for i, team in enumerate(teams, 1):
            try:
                logger.info(f"  [{i}/{total_teams}] {team.school}...")
                
                # Get roster from API
                roster_data = self.api.get_team_roster(team.school, year=year)
                
                if not roster_data:
                    logger.warning(f"    No roster data for {team.school}")
                    teams_failed += 1
                    continue
                
                team_players = 0
                for player_data in roster_data:
                    try:
                        # Check if player exists
                        player_name = player_data.get('name', '')
                        if not player_name:
                            continue
                        
                        existing = self.session.query(BasketballPlayer).filter_by(
                            team_id=team.id,
                            name=player_name,
                            season=year
                        ).first()
                        
                        if existing:
                            # Update existing player
                            for key, value in self.transform_player_data(player_data, team.id, year).items():
                                if value is not None:
                                    setattr(existing, key, value)
                            players_updated += 1
                        else:
                            # Create new player
                            player = BasketballPlayer(**self.transform_player_data(player_data, team.id, year))
                            self.session.add(player)
                            players_added += 1
                        
                        team_players += 1
                    
                    except Exception as e:
                        logger.warning(f"    Failed to process player: {e}")
                        continue
                
                self.session.commit()
                logger.info(f"    Added/updated {team_players} players")
                teams_processed += 1
                
            except Exception as e:
                logger.error(f"    Failed to process {team.school}: {e}")
                self.session.rollback()
                teams_failed += 1
                continue
        
        logger.info(f"\nRoster collection complete:")
        logger.info(f"  Teams processed: {teams_processed}/{total_teams}")
        logger.info(f"  Teams failed: {teams_failed}")
        logger.info(f"  Players added: {players_added}")
        logger.info(f"  Players updated: {players_updated}")
        
        return (teams_processed, players_added, players_updated)
    
    def collect_player_stats(self, year: int) -> tuple:
        """Collect player statistics"""
        logger.info(f"Collecting basketball player stats for {year} season...")
        
        # Get all stats from API
        stats_data = self.api.get_player_season_stats(year=year)
        
        if not stats_data:
            logger.warning("No stats data returned from API")
            return (0, 0)
        
        logger.info(f"  Retrieved {len(stats_data)} stat records from API")
        
        stats_added = 0
        stats_updated = 0
        stats_failed = 0
        
        # Process each stat record
        for stat_record in stats_data:
            try:
                player_name = stat_record.get('player', stat_record.get('name'))
                team_name = stat_record.get('team')
                
                if not player_name or not team_name:
                    stats_failed += 1
                    continue
                
                # Find the player in our database
                player = self.session.query(BasketballPlayer).join(BasketballTeam).filter(
                    BasketballPlayer.name == player_name,
                    BasketballTeam.school == team_name,
                    BasketballPlayer.season == year
                ).first()
                
                if not player:
                    # Player not in database yet
                    stats_failed += 1
                    continue
                
                # Check if stats exist
                existing = self.session.query(BasketballPerformanceStat).filter_by(
                    player_id=player.id,
                    season=year
                ).first()
                
                if existing:
                    # Update
                    for key, value in self.transform_stat_data(stat_record, player.id, year).items():
                        if value is not None:
                            setattr(existing, key, value)
                    stats_updated += 1
                else:
                    # Create new
                    stat = BasketballPerformanceStat(**self.transform_stat_data(stat_record, player.id, year))
                    self.session.add(stat)
                    stats_added += 1
                
                # Commit every 100 records
                if (stats_added + stats_updated) % 100 == 0:
                    self.session.commit()
                    logger.info(f"    Progress: {stats_added} added, {stats_updated} updated...")
            
            except Exception as e:
                logger.warning(f"    Failed to process stat: {e}")
                stats_failed += 1
                self.session.rollback()
                continue
        
        # Final commit
        self.session.commit()
        
        logger.info(f"\nStats collection complete:")
        logger.info(f"  Stats added: {stats_added}")
        logger.info(f"  Stats updated: {stats_updated}")
        logger.info(f"  Stats failed: {stats_failed}")
        
        return (stats_added, stats_updated)
    
    def close(self):
        """Close the database session"""
        self.session.close()


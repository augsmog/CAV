"""
Main data pipeline orchestrator
Coordinates data collection, transformation, and loading
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database import get_session, init_database
from database.models import (
    Player, Team, PerformanceStat, Transfer,
    SocialMedia, SchemeInfo, DataRefreshLog
)
from scrapers.cfb_api_client import CollegeFootballDataAPI
from scrapers.social_media_scraper import SocialMediaScraper
from etl.transformers import (
    transform_roster_data, transform_stats_data, transform_transfer_data,
    transform_team_data, transform_advanced_stats, transform_ppa_stats,
    merge_stat_dicts, validate_player_data, validate_stats_data
)
from etl.stats_aggregator import aggregate_all_categories
from config import get_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Main data pipeline for collecting and storing player/team data
    """
    
    def __init__(self):
        self.config = get_config()
        self.cfb_api = CollegeFootballDataAPI()
        self.social_scraper = SocialMediaScraper()
        self.session = get_session()
    
    def _log_refresh(self, data_type: str, season: int, status: str,
                    records_added: int = 0, records_updated: int = 0,
                    records_failed: int = 0, error_message: str = None):
        """Log data refresh operation"""
        log_entry = DataRefreshLog(
            data_type=data_type,
            season=season,
            status=status,
            records_added=records_added,
            records_updated=records_updated,
            records_failed=records_failed,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            error_message=error_message
        )
        self.session.add(log_entry)
        self.session.commit()
    
    def collect_teams(self) -> int:
        """
        Collect all FBS team data
        
        Returns:
            Number of teams added/updated
        """
        logger.info("=== Collecting Team Data ===")
        
        try:
            teams_data = self.cfb_api.get_teams()
            count_added = 0
            count_updated = 0
            
            for team_data in teams_data:
                transformed = transform_team_data(team_data)
                
                # Check if team exists
                existing_team = self.session.query(Team).filter_by(
                    cfb_id=transformed['cfb_id']
                ).first()
                
                if existing_team:
                    # Update existing
                    for key, value in transformed.items():
                        if value is not None:
                            setattr(existing_team, key, value)
                    count_updated += 1
                else:
                    # Add new
                    new_team = Team(**transformed)
                    self.session.add(new_team)
                    count_added += 1
            
            self.session.commit()
            logger.info(f"✓ Teams: {count_added} added, {count_updated} updated")
            
            self._log_refresh('teams', None, 'success', count_added, count_updated)
            return count_added + count_updated
        
        except Exception as e:
            logger.error(f"Failed to collect teams: {e}")
            self._log_refresh('teams', None, 'failed', error_message=str(e))
            self.session.rollback()
            return 0
    
    def collect_roster(self, team_name: str, year: int) -> int:
        """
        Collect roster data for a specific team and year
        
        Args:
            team_name: Team name
            year: Season year
        
        Returns:
            Number of players added/updated
        """
        logger.info(f"=== Collecting Roster: {team_name} ({year}) ===")
        
        try:
            roster_data = self.cfb_api.get_roster(team_name, year)
            count_added = 0
            count_updated = 0
            
            # Get team from database
            team = self.session.query(Team).filter(
                Team.name.ilike(f"%{team_name}%")
            ).first()
            
            if not team:
                logger.warning(f"Team not found in database: {team_name}")
                return 0
            
            for player_data in roster_data:
                transformed = transform_roster_data(player_data)
                
                if not validate_player_data(transformed):
                    continue
                
                # Check if player exists
                existing_player = None
                if transformed['cfb_id']:
                    existing_player = self.session.query(Player).filter_by(
                        cfb_id=transformed['cfb_id']
                    ).first()
                
                if existing_player:
                    # Update existing
                    for key, value in transformed.items():
                        if value is not None:
                            setattr(existing_player, key, value)
                    existing_player.current_team_id = team.id
                    count_updated += 1
                else:
                    # Add new
                    transformed['current_team_id'] = team.id
                    new_player = Player(**transformed)
                    self.session.add(new_player)
                    count_added += 1
            
            self.session.commit()
            logger.info(f"✓ Roster: {count_added} added, {count_updated} updated")
            
            self._log_refresh(f'roster_{team_name}', year, 'success', count_added, count_updated)
            return count_added + count_updated
        
        except Exception as e:
            logger.error(f"Failed to collect roster for {team_name}: {e}")
            self._log_refresh(f'roster_{team_name}', year, 'failed', error_message=str(e))
            self.session.rollback()
            return 0
    
    def collect_player_stats(self, year: int, team_name: str = None) -> int:
        """
        Collect player statistics for a season
        
        Args:
            year: Season year
            team_name: Optional team filter
        
        Returns:
            Number of stat records added/updated
        """
        logger.info(f"=== Collecting Player Stats: {year} ===")
        
        try:
            count_added = 0
            count_updated = 0
            count_failed = 0
            
            # Get all stat categories
            all_stats = self.cfb_api.get_all_player_stats_for_season(year)
            
            # Aggregate stats by player
            logger.info("Aggregating stats by player...")
            aggregated_players = aggregate_all_categories(all_stats, year)
            logger.info(f"Processing {len(aggregated_players)} players with stats")
            
            # Track processed players to avoid duplicates within this run
            processed_players = set()
            
            # Process each player's aggregated stats
            for player_stats in aggregated_players:
                player_name = player_stats.get('player')
                team = player_stats.get('team')
                
                if not player_name:
                    count_failed += 1
                    continue
                
                # Find player in database
                # Try exact match first, then fuzzy
                player = self.session.query(Player).filter(
                    Player.name == player_name
                ).first()
                
                if not player:
                    # Try fuzzy match
                    player = self.session.query(Player).filter(
                        Player.name.ilike(f"%{player_name}%")
                    ).first()
                
                if not player:
                    # Try matching by team as well
                    if team:
                        team_obj = self.session.query(Team).filter(
                            Team.name.ilike(f"%{team}%")
                        ).first()
                        
                        if team_obj:
                            player = self.session.query(Player).filter(
                                Player.name.ilike(f"%{player_name}%"),
                                Player.current_team_id == team_obj.id
                            ).first()
                
                if not player:
                    logger.debug(f"Player not found: {player_name} ({team})")
                    count_failed += 1
                    continue
                
                # Skip if we've already processed this player in this run
                if player.id in processed_players:
                    count_failed += 1
                    continue
                
                processed_players.add(player.id)
                
                # Check if stat record exists
                existing_stat = self.session.query(PerformanceStat).filter_by(
                    player_id=player.id,
                    season=year
                ).first()
                
                # Check if we have any stats
                has_stats = any([
                    player_stats.get('passing_stats'),
                    player_stats.get('rushing_stats'),
                    player_stats.get('receiving_stats'),
                    player_stats.get('defensive_stats')
                ])
                
                if not has_stats:
                    count_failed += 1
                    continue
                
                if existing_stat:
                    # Update existing stats - merge with existing data
                    if player_stats.get('passing_stats'):
                        existing_stat.passing_stats = player_stats['passing_stats']
                    if player_stats.get('rushing_stats'):
                        existing_stat.rushing_stats = player_stats['rushing_stats']
                    if player_stats.get('receiving_stats'):
                        existing_stat.receiving_stats = player_stats['receiving_stats']
                    if player_stats.get('defensive_stats'):
                        existing_stat.defensive_stats = player_stats['defensive_stats']
                    
                    existing_stat.team = team
                    count_updated += 1
                else:
                    # Add new stat record
                    new_stat = PerformanceStat(
                        player_id=player.id,
                        season=year,
                        team=team,
                        passing_stats=player_stats.get('passing_stats'),
                        rushing_stats=player_stats.get('rushing_stats'),
                        receiving_stats=player_stats.get('receiving_stats'),
                        defensive_stats=player_stats.get('defensive_stats')
                    )
                    self.session.add(new_stat)
                    count_added += 1
                
                # Commit in batches with error handling
                if (count_added + count_updated) % 100 == 0:
                    try:
                        self.session.commit()
                        logger.info(f"  Progress: {count_added} added, {count_updated} updated...")
                    except Exception as e:
                        logger.warning(f"  Batch commit error (likely duplicate), rolling back batch: {e}")
                        self.session.rollback()
                        # Continue with next batch
            
            self.session.commit()
            logger.info(f"✓ Stats: {count_added} added, {count_updated} updated, {count_failed} failed")
            
            self._log_refresh('player_stats', year, 'success', count_added, count_updated, count_failed)
            return count_added + count_updated
        
        except Exception as e:
            logger.error(f"Failed to collect player stats: {e}")
            import traceback
            traceback.print_exc()
            self._log_refresh('player_stats', year, 'failed', error_message=str(e))
            self.session.rollback()
            return 0
    
    def collect_transfers(self, year: int) -> int:
        """
        Collect transfer portal data
        
        Args:
            year: Season year
        
        Returns:
            Number of transfers added
        """
        logger.info(f"=== Collecting Transfer Portal: {year} ===")
        
        try:
            transfer_data = self.cfb_api.get_transfer_portal(year)
            count_added = 0
            
            for transfer in transfer_data:
                first_name = transfer.get('firstName', '').strip()
                last_name = transfer.get('lastName', '').strip()
                
                if not first_name or not last_name:
                    continue
                
                # Find player by first and last name
                player = self.session.query(Player).filter(
                    Player.first_name.ilike(f"%{first_name}%"),
                    Player.last_name.ilike(f"%{last_name}%")
                ).first()
                
                if not player:
                    logger.debug(f"Player not found for transfer: {first_name} {last_name}")
                    continue
                
                # Transform transfer data
                transformed = transform_transfer_data(transfer)
                transformed['player_id'] = player.id
                
                # Check if transfer already exists
                existing = self.session.query(Transfer).filter_by(
                    player_id=player.id,
                    season=year
                ).first()
                
                if not existing:
                    new_transfer = Transfer(**transformed)
                    self.session.add(new_transfer)
                    count_added += 1
                    
                    # Mark player as transfer
                    player.is_transfer = True
            
            self.session.commit()
            logger.info(f"✓ Transfers: {count_added} added")
            
            self._log_refresh('transfers', year, 'success', count_added)
            return count_added
        
        except Exception as e:
            logger.error(f"Failed to collect transfers: {e}")
            self._log_refresh('transfers', year, 'failed', error_message=str(e))
            self.session.rollback()
            return 0
    
    def collect_all_data_for_season(self, year: int, teams: List[str] = None) -> Dict:
        """
        Collect all data for a season
        
        Args:
            year: Season year
            teams: Optional list of team names to collect
        
        Returns:
            Summary dictionary
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"FULL DATA COLLECTION: {year} Season")
        logger.info(f"{'='*60}\n")
        
        summary = {
            'year': year,
            'teams_collected': 0,
            'rosters_collected': 0,
            'stats_collected': 0,
            'transfers_collected': 0,
            'started_at': datetime.now()
        }
        
        # Collect teams first
        summary['teams_collected'] = self.collect_teams()
        
        # Get list of teams to process
        if not teams:
            all_teams = self.session.query(Team.name).all()
            teams = [t[0] for t in all_teams]
        
        # Collect rosters
        for team in teams:
            roster_count = self.collect_roster(team, year)
            summary['rosters_collected'] += roster_count
        
        # Collect stats
        summary['stats_collected'] = self.collect_player_stats(year)
        
        # Collect transfers
        summary['transfers_collected'] = self.collect_transfers(year)
        
        summary['completed_at'] = datetime.now()
        summary['duration'] = (summary['completed_at'] - summary['started_at']).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"COLLECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Duration: {summary['duration']:.1f} seconds")
        logger.info(f"Teams: {summary['teams_collected']}")
        logger.info(f"Rosters: {summary['rosters_collected']}")
        logger.info(f"Stats: {summary['stats_collected']}")
        logger.info(f"Transfers: {summary['transfers_collected']}")
        logger.info(f"{'='*60}\n")
        
        return summary
    
    def close(self):
        """Close database session"""
        self.session.close()


# Example usage
if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Create pipeline
    pipeline = DataPipeline()
    
    try:
        # Collect data for 2023 season
        # Start with a few teams for testing
        test_teams = ['Alabama', 'Georgia', 'Ohio State', 'Michigan']
        summary = pipeline.collect_all_data_for_season(2023, teams=test_teams)
        
        print("\nData collection summary:")
        print(summary)
    
    finally:
        pipeline.close()


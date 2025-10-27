"""
College Basketball Data API Client
Handles data collection from collegebasketballdata.com
"""

import requests
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
from ratelimit import limits, sleep_and_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollegeBasketballDataAPI:
    """
    Client for collegebasketballdata.com API
    """
    
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.collegebasketballdata.com"
        self.api_key = api_key
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            })
    
    @sleep_and_retry
    @limits(calls=100, period=60)  # Rate limit: 100 calls per minute
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting and error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None
    
    # ========================================================================
    # TEAMS
    # ========================================================================
    
    def get_teams(self, year: int = None, conference: str = None) -> List[Dict]:
        """
        Get all college basketball teams
        
        Args:
            year: Season year (e.g., 2023 for 2023-24 season)
            conference: Filter by conference
            
        Returns:
            List of team dictionaries
        """
        logger.info(f"Fetching basketball teams for {year or 'current'} season...")
        
        params = {}
        if year:
            params['year'] = year
        if conference:
            params['conference'] = conference
        
        data = self._make_request('teams', params)
        
        if data:
            teams = data if isinstance(data, list) else data.get('teams', [])
            logger.info(f"  Retrieved {len(teams)} basketball teams")
            return teams
        
        return []
    
    # ========================================================================
    # ROSTERS
    # ========================================================================
    
    def get_team_roster(self, team: str, year: int = None) -> List[Dict]:
        """
        Get roster for a specific team
        
        Args:
            team: Team name or ID
            year: Season year
            
        Returns:
            List of player dictionaries
        """
        logger.info(f"Fetching roster for {team} ({year or 'current'})...")
        
        params = {'team': team}
        if year:
            params['year'] = year
        
        data = self._make_request('roster', params)
        
        if data:
            roster = data if isinstance(data, list) else data.get('roster', [])
            logger.info(f"  Retrieved {len(roster)} players")
            return roster
        
        return []
    
    # ========================================================================
    # PLAYER STATS
    # ========================================================================
    
    def get_player_season_stats(self, 
                                year: int,
                                team: str = None,
                                stat_category: str = None) -> List[Dict]:
        """
        Get player statistics for a season
        
        Args:
            year: Season year
            team: Filter by team (optional)
            stat_category: Category like 'scoring', 'rebounds', etc.
            
        Returns:
            List of player stat dictionaries
        """
        logger.info(f"Fetching player stats for {year} season...")
        
        params = {'year': year}
        if team:
            params['team'] = team
        if stat_category:
            params['category'] = stat_category
        
        data = self._make_request('stats/player/season', params)
        
        if data:
            stats = data if isinstance(data, list) else data.get('stats', [])
            logger.info(f"  Retrieved {len(stats)} stat records")
            return stats
        
        return []
    
    def get_all_player_stats(self, year: int) -> Dict[str, List[Dict]]:
        """
        Get all stat categories for a season
        
        Basketball stat categories:
        - Scoring (points, FG%, 3P%, FT%)
        - Rebounds (total, offensive, defensive)
        - Assists
        - Defense (steals, blocks)
        - Efficiency (PER, usage rate, etc.)
        """
        logger.info(f"Fetching all player stats for {year}...")
        
        categories = ['scoring', 'rebounds', 'assists', 'defense', 'efficiency']
        all_stats = {}
        
        for category in categories:
            stats = self.get_player_season_stats(year, stat_category=category)
            if stats:
                all_stats[category] = stats
            time.sleep(0.5)  # Small delay between requests
        
        return all_stats
    
    # ========================================================================
    # ADVANCED STATS
    # ========================================================================
    
    def get_advanced_stats(self, year: int, team: str = None) -> List[Dict]:
        """
        Get advanced metrics (PER, true shooting %, usage rate, etc.)
        
        Args:
            year: Season year
            team: Filter by team (optional)
            
        Returns:
            List of advanced stat dictionaries
        """
        logger.info(f"Fetching advanced stats for {year}...")
        
        params = {'year': year}
        if team:
            params['team'] = team
        
        data = self._make_request('stats/player/advanced', params)
        
        if data:
            stats = data if isinstance(data, list) else data.get('stats', [])
            logger.info(f"  Retrieved {len(stats)} advanced stat records")
            return stats
        
        return []
    
    # ========================================================================
    # TRANSFER PORTAL
    # ========================================================================
    
    def get_transfer_portal(self, year: int = None) -> List[Dict]:
        """
        Get players in transfer portal
        
        Args:
            year: Season year
            
        Returns:
            List of transfer player dictionaries
        """
        logger.info(f"Fetching transfer portal data...")
        
        params = {}
        if year:
            params['year'] = year
        
        data = self._make_request('transfer-portal', params)
        
        if data:
            transfers = data if isinstance(data, list) else data.get('transfers', [])
            logger.info(f"  Retrieved {len(transfers)} transfer portal entries")
            return transfers
        
        return []
    
    # ========================================================================
    # GAMES & SCHEDULES
    # ========================================================================
    
    def get_team_games(self, team: str, year: int) -> List[Dict]:
        """
        Get games for a team in a season
        
        Args:
            team: Team name or ID
            year: Season year
            
        Returns:
            List of game dictionaries
        """
        logger.info(f"Fetching games for {team} ({year})...")
        
        params = {
            'team': team,
            'year': year
        }
        
        data = self._make_request('games', params)
        
        if data:
            games = data if isinstance(data, list) else data.get('games', [])
            logger.info(f"  Retrieved {len(games)} games")
            return games
        
        return []
    
    # ========================================================================
    # TESTING & VALIDATION
    # ========================================================================
    
    def test_connection(self) -> bool:
        """Test API connection and authentication"""
        logger.info("Testing API connection...")
        
        try:
            # Try to fetch current teams
            teams = self.get_teams()
            if teams:
                logger.info(f"✓ API connection successful! Found {len(teams)} teams")
                return True
            else:
                logger.warning("⚠ API connected but no data returned")
                return False
        except Exception as e:
            logger.error(f"✗ API connection failed: {e}")
            return False


def main():
    """Test the basketball API client"""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from config import load_config
    
    print("="*80)
    print("COLLEGE BASKETBALL DATA API TEST")
    print("="*80)
    print()
    
    # Load config
    config = load_config()
    api_key = config.get('basketball_api', {}).get('api_key')
    
    if not api_key:
        print("[ERROR] No API key found in config/config.yaml")
        print("\nAdd your API key:")
        print("basketball_api:")
        print("  api_key: 'your_key_here'")
        return
    
    # Create client
    client = CollegeBasketballDataAPI(api_key=api_key)
    
    # Test connection
    if not client.test_connection():
        print("[ERROR] Failed to connect to API")
        return
    
    print("\n" + "="*80)
    print("TESTING DATA RETRIEVAL")
    print("="*80)
    
    # Test teams
    print("\n1. Fetching teams...")
    teams = client.get_teams(year=2024)
    if teams:
        print(f"   ✓ Found {len(teams)} teams")
        print(f"   Sample: {teams[0].get('school', 'N/A')}")
    
    # Test roster (using first team)
    if teams:
        print("\n2. Fetching roster...")
        first_team = teams[0].get('school', teams[0].get('team'))
        roster = client.get_team_roster(first_team, year=2024)
        if roster:
            print(f"   ✓ Found {len(roster)} players on {first_team}")
            if roster:
                player = roster[0]
                print(f"   Sample: {player.get('name', 'N/A')} - {player.get('position', 'N/A')}")
    
    # Test stats
    print("\n3. Fetching player stats...")
    stats = client.get_player_season_stats(2024)
    if stats:
        print(f"   ✓ Found {len(stats)} stat records")
        if stats:
            print(f"   Sample: {stats[0].get('player', 'N/A')} - {stats[0].get('team', 'N/A')}")
    
    print("\n" + "="*80)
    print("API TEST COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()


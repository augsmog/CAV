"""
College Football Data API Client
API Documentation: https://collegefootballdata.com/
"""

import requests
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollegeFootballDataAPI:
    """
    Client for collegefootballdata.com API
    """
    
    def __init__(self, api_key: str = None):
        self.config = get_config()
        self.api_key = api_key or self.config.cfb_api_key
        self.base_url = self.config.cfb_base_url
        
        if not self.api_key:
            raise ValueError(
                "API key not provided. Please add your collegefootballdata.com API key to config/config.yaml"
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        })
        
        # Rate limiting
        self.rate_limit = self.config.get('collegefootballdata.rate_limit_per_minute', 60)
        self.request_times = []
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting"""
        now = datetime.now()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        
        if len(self.request_times) >= self.rate_limit:
            # Wait until the oldest request is more than 1 minute old
            wait_time = 60 - (now - self.request_times[0]).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.request_times = []
        
        self.request_times.append(now)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Any:
        """Make API request with error handling"""
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid API key. Please check your configuration.")
            elif e.response.status_code == 429:
                logger.warning("Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            else:
                logger.error(f"HTTP error: {e}")
                raise
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # ========== ROSTER & PLAYER DATA ==========
    
    def get_roster(self, team: str, year: int) -> List[Dict]:
        """
        Get team roster for a specific year
        
        Args:
            team: Team name (e.g., 'Alabama', 'Ohio State')
            year: Season year
        
        Returns:
            List of player dictionaries
        """
        logger.info(f"Fetching roster for {team} ({year})")
        
        return self._make_request('/roster', {
            'team': team,
            'year': year
        })
    
    def get_player_usage(self, year: int, team: str = None, position: str = None) -> List[Dict]:
        """
        Get player usage statistics (snap counts, etc.)
        
        Args:
            year: Season year
            team: Optional team filter
            position: Optional position filter
        
        Returns:
            List of player usage data
        """
        params = {'year': year}
        if team:
            params['team'] = team
        if position:
            params['position'] = position
        
        logger.info(f"Fetching player usage for {year}")
        return self._make_request('/player/usage', params)
    
    def get_returning_production(self, year: int, team: str = None) -> List[Dict]:
        """
        Get returning production data
        
        Args:
            year: Season year
            team: Optional team filter
        
        Returns:
            List of returning production data
        """
        params = {'year': year}
        if team:
            params['team'] = team
        
        logger.info(f"Fetching returning production for {year}")
        return self._make_request('/player/returning', params)
    
    # ========== PLAYER STATISTICS ==========
    
    def get_player_season_stats(self, year: int, team: str = None, 
                                position: str = None, stat_category: str = None) -> List[Dict]:
        """
        Get player season statistics
        
        Args:
            year: Season year
            team: Optional team filter
            position: Optional position filter (QB, RB, WR, etc.)
            stat_category: Optional category (passing, rushing, receiving, defense, etc.)
        
        Returns:
            List of player statistics
        """
        params = {'year': year}
        if team:
            params['team'] = team
        if position:
            params['position'] = position
        if stat_category:
            params['category'] = stat_category
        
        logger.info(f"Fetching player stats for {year} (position={position}, category={stat_category})")
        return self._make_request('/stats/player/season', params)
    
    def get_advanced_stats(self, year: int, team: str = None) -> List[Dict]:
        """
        Get advanced player statistics (PFF-like metrics)
        
        Args:
            year: Season year
            team: Optional team filter
        
        Returns:
            List of advanced statistics
        """
        params = {'year': year}
        if team:
            params['team'] = team
        
        logger.info(f"Fetching advanced stats for {year}")
        return self._make_request('/stats/player/advanced', params)
    
    def get_ppa_player_stats(self, year: int, team: str = None, position: str = None) -> List[Dict]:
        """
        Get Predicted Points Added (PPA) player statistics
        
        Args:
            year: Season year
            team: Optional team filter
            position: Optional position filter
        
        Returns:
            List of PPA statistics
        """
        params = {'year': year}
        if team:
            params['team'] = team
        if position:
            params['position'] = position
        
        logger.info(f"Fetching PPA stats for {year}")
        return self._make_request('/ppa/players/season', params)
    
    # ========== TEAM DATA ==========
    
    def get_teams(self) -> List[Dict]:
        """
        Get all FBS teams
        
        Returns:
            List of team information
        """
        logger.info("Fetching all teams")
        return self._make_request('/teams/fbs')
    
    def get_team_info(self, team: str) -> List[Dict]:
        """
        Get detailed team information
        
        Args:
            team: Team name
        
        Returns:
            Team information
        """
        logger.info(f"Fetching team info for {team}")
        return self._make_request('/teams', {'school': team})
    
    def get_team_talent(self, year: int = None) -> List[Dict]:
        """
        Get team talent composite ratings
        
        Args:
            year: Optional year filter
        
        Returns:
            List of team talent ratings
        """
        params = {}
        if year:
            params['year'] = year
        
        logger.info(f"Fetching team talent ratings")
        return self._make_request('/talent', params)
    
    # ========== TRANSFER PORTAL ==========
    
    def get_transfer_portal(self, year: int) -> List[Dict]:
        """
        Get transfer portal entries
        
        Args:
            year: Season year
        
        Returns:
            List of transfer portal entries
        """
        logger.info(f"Fetching transfer portal data for {year}")
        return self._make_request('/player/portal', {'year': year})
    
    # ========== RECRUITING ==========
    
    def get_recruiting_players(self, year: int, team: str = None, 
                               position: str = None) -> List[Dict]:
        """
        Get recruiting class information
        
        Args:
            year: Recruiting class year
            team: Optional team filter
            position: Optional position filter
        
        Returns:
            List of recruited players
        """
        params = {'year': year}
        if team:
            params['team'] = team
        if position:
            params['position'] = position
        
        logger.info(f"Fetching recruiting data for {year}")
        return self._make_request('/recruiting/players', params)
    
    # ========== GAMES & SCHEDULES ==========
    
    def get_games(self, year: int, team: str = None, season_type: str = 'regular') -> List[Dict]:
        """
        Get game schedule and results
        
        Args:
            year: Season year
            team: Optional team filter
            season_type: 'regular', 'postseason', or 'both'
        
        Returns:
            List of games
        """
        params = {'year': year, 'seasonType': season_type}
        if team:
            params['team'] = team
        
        logger.info(f"Fetching games for {year}")
        return self._make_request('/games', params)
    
    # ========== COACHES ==========
    
    def get_coaches(self, team: str = None, year: int = None) -> List[Dict]:
        """
        Get coaching staff information
        
        Args:
            team: Optional team filter
            year: Optional year filter
        
        Returns:
            List of coaches
        """
        params = {}
        if team:
            params['team'] = team
        if year:
            params['year'] = year
        
        logger.info("Fetching coaching data")
        return self._make_request('/coaches', params)
    
    # ========== HELPER METHODS ==========
    
    def get_all_player_stats_for_season(self, year: int, positions: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Get all player statistics for a season across multiple categories
        
        Args:
            year: Season year
            positions: Optional list of positions to filter
        
        Returns:
            Dictionary with stat categories as keys
        """
        all_stats = {}
        
        categories = ['passing', 'rushing', 'receiving', 'defensive', 'kicking']
        
        for category in categories:
            try:
                stats = self.get_player_season_stats(year, stat_category=category)
                all_stats[category] = stats
                logger.info(f"  Retrieved {len(stats)} {category} records")
            except Exception as e:
                logger.error(f"Failed to fetch {category} stats: {e}")
                all_stats[category] = []
        
        return all_stats
    
    def test_connection(self) -> bool:
        """
        Test API connection and authentication
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            teams = self.get_teams()
            logger.info(f"✓ API connection successful! Found {len(teams)} teams.")
            return True
        except Exception as e:
            logger.error(f"✗ API connection failed: {e}")
            return False


# Example usage
if __name__ == '__main__':
    # Test the API client
    client = CollegeFootballDataAPI()
    
    if client.test_connection():
        # Example: Get Alabama's 2023 roster
        roster = client.get_roster('Alabama', 2023)
        print(f"\nAlabama 2023 Roster: {len(roster)} players")
        
        if roster:
            print(f"Sample player: {roster[0]}")


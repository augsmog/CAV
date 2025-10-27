"""
Enhanced Social Media Scraper
Collects social media metrics using multiple methods
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import Dict, Optional, List
from pathlib import Path
import sys
import csv
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSocialMediaScraper:
    """
    Multi-source social media scraper with rate limiting and fallbacks
    """
    
    def __init__(self):
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.request_delay = 2  # seconds between requests
        self.last_request_time = {}
    
    def _rate_limit(self, platform: str):
        """Enforce rate limiting per platform"""
        if platform in self.last_request_time:
            elapsed = time.time() - self.last_request_time[platform]
            if elapsed < self.request_delay:
                time.sleep(self.request_delay - elapsed)
        
        self.last_request_time[platform] = time.time()
    
    def search_player_handles(self, player_name: str, team_name: str = None) -> Dict:
        """
        Search for player social media handles using web search
        
        Args:
            player_name: Player's name
            team_name: Team name for context
        
        Returns:
            Dictionary with probable handles
        """
        logger.info(f"Searching social media handles for {player_name}")
        
        search_term = f"{player_name} {team_name} college football" if team_name else f"{player_name} college football"
        
        # Clean name for handle generation
        name_parts = player_name.lower().split()
        probable_handles = []
        
        # Common handle patterns
        if len(name_parts) >= 2:
            first = name_parts[0]
            last = name_parts[-1]
            
            # Generate likely handle patterns
            probable_handles = [
                f"{first}{last}",  # johnsmith
                f"{first}_{last}",  # john_smith
                f"{first}.{last}",  # john.smith
                f"{first[0]}{last}",  # jsmith
                f"{first}_{last[0]}",  # john_s
                f"{last}{first[0]}",  # smithj
            ]
        
        return {
            'player_name': player_name,
            'probable_handles': probable_handles,
            'search_term': search_term,
            'note': 'Manual verification required'
        }
    
    def scrape_instagram_public(self, handle: str) -> Optional[Dict]:
        """
        Scrape public Instagram data (limited by Instagram's restrictions)
        
        Note: Instagram heavily restricts scraping. This is best-effort only.
        For production, use Instagram Graph API with proper authentication.
        
        Args:
            handle: Instagram handle (without @)
        
        Returns:
            Dictionary with public data or None
        """
        self._rate_limit('instagram')
        
        try:
            url = f"https://www.instagram.com/{handle}/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Look for JSON data in page
                pattern = r'window\._sharedData = ({.*?});'
                match = re.search(pattern, response.text)
                
                if match:
                    data = json.loads(match.group(1))
                    user_data = data.get('entry_data', {}).get('ProfilePage', [{}])[0]
                    user = user_data.get('graphql', {}).get('user', {})
                    
                    if user:
                        return {
                            'handle': handle,
                            'platform': 'instagram',
                            'followers': user.get('edge_followed_by', {}).get('count', 0),
                            'following': user.get('edge_follow', {}).get('count', 0),
                            'posts': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                            'verified': user.get('is_verified', False),
                            'full_name': user.get('full_name'),
                            'bio': user.get('biography'),
                            'scraped_at': time.time()
                        }
            
            logger.warning(f"Could not scrape Instagram for {handle} (status: {response.status_code})")
            return None
        
        except Exception as e:
            logger.error(f"Error scraping Instagram {handle}: {e}")
            return None
    
    def scrape_twitter_public(self, handle: str) -> Optional[Dict]:
        """
        Scrape public Twitter/X data
        
        Note: Twitter also restricts scraping. For production use Twitter API v2.
        
        Args:
            handle: Twitter handle (without @)
        
        Returns:
            Dictionary with public data or None
        """
        self._rate_limit('twitter')
        
        try:
            url = f"https://twitter.com/{handle}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Twitter's structure changes frequently, this is best-effort
                return {
                    'handle': handle,
                    'platform': 'twitter',
                    'followers': None,  # Requires API or browser automation
                    'note': 'Use Twitter API for accurate data',
                    'profile_exists': True,
                    'scraped_at': time.time()
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error scraping Twitter {handle}: {e}")
            return None
    
    def load_handles_from_csv(self, csv_file: str) -> List[Dict]:
        """
        Load player social media handles from CSV file
        
        CSV Format:
        player_name,team,instagram_handle,twitter_handle,tiktok_handle,instagram_followers,twitter_followers,tiktok_followers
        
        Args:
            csv_file: Path to CSV file
        
        Returns:
            List of player social media data
        """
        data = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append({
                        'player_name': row.get('player_name'),
                        'team': row.get('team'),
                        'instagram_handle': row.get('instagram_handle'),
                        'twitter_handle': row.get('twitter_handle'),
                        'tiktok_handle': row.get('tiktok_handle'),
                        'instagram_followers': self._safe_int(row.get('instagram_followers')),
                        'twitter_followers': self._safe_int(row.get('twitter_followers')),
                        'tiktok_followers': self._safe_int(row.get('tiktok_followers')),
                        'engagement_rate': self._safe_float(row.get('engagement_rate', 0.03))
                    })
            
            logger.info(f"Loaded {len(data)} player social media records from {csv_file}")
            return data
        
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_file}")
            return []
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return []
    
    def create_sample_csv_template(self, output_file: str = "social_media_template.csv"):
        """
        Create a template CSV file for manual data entry
        
        Args:
            output_file: Path to output file
        """
        headers = [
            'player_name',
            'team',
            'instagram_handle',
            'twitter_handle',
            'tiktok_handle',
            'instagram_followers',
            'twitter_followers',
            'tiktok_followers',
            'engagement_rate',
            'notes'
        ]
        
        sample_data = [
            [
                'Caleb Williams',
                'USC',
                'calebwilliams',
                'CALEBcsw',
                'calebwilliams',
                '500000',
                '250000',
                '100000',
                '0.045',
                'Example data'
            ]
        ]
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(sample_data)
            
            logger.info(f"Created template CSV: {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None
    
    def calculate_total_metrics(self, social_data: Dict) -> Dict:
        """
        Calculate aggregate social media metrics
        
        Args:
            social_data: Dictionary with platform-specific data
        
        Returns:
            Dictionary with total metrics
        """
        instagram_followers = social_data.get('instagram_followers', 0) or 0
        twitter_followers = social_data.get('twitter_followers', 0) or 0
        tiktok_followers = social_data.get('tiktok_followers', 0) or 0
        
        total_followers = instagram_followers + twitter_followers + tiktok_followers
        
        # Weighted follower score (Instagram and TikTok have higher engagement)
        weighted_score = (
            instagram_followers * 1.5 +
            tiktok_followers * 1.3 +
            twitter_followers * 1.0
        )
        
        # Engagement rate (average across platforms if available)
        engagement_rates = []
        for platform in ['instagram', 'twitter', 'tiktok']:
            rate = social_data.get(f'{platform}_engagement_rate')
            if rate:
                engagement_rates.append(rate)
        
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.03
        
        return {
            'total_followers': total_followers,
            'weighted_follower_score': weighted_score,
            'average_engagement_rate': avg_engagement,
            'platform_count': sum([
                1 if instagram_followers > 0 else 0,
                1 if twitter_followers > 0 else 0,
                1 if tiktok_followers > 0 else 0
            ]),
            'largest_platform': max([
                ('instagram', instagram_followers),
                ('twitter', twitter_followers),
                ('tiktok', tiktok_followers)
            ], key=lambda x: x[1])[0] if total_followers > 0 else None
        }
    
    @staticmethod
    def _safe_int(value):
        """Safely convert to integer"""
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _safe_float(value):
        """Safely convert to float"""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None


# Example usage and testing
if __name__ == '__main__':
    scraper = EnhancedSocialMediaScraper()
    
    # Test 1: Search for handles
    print("="*70)
    print("TEST 1: Searching for player handles")
    print("="*70)
    results = scraper.search_player_handles("Caleb Williams", "USC")
    print(json.dumps(results, indent=2))
    
    # Test 2: Create CSV template
    print("\n" + "="*70)
    print("TEST 2: Creating CSV template")
    print("="*70)
    template_file = scraper.create_sample_csv_template("data/social_media_template.csv")
    if template_file:
        print(f"Template created: {template_file}")
    
    # Test 3: Calculate metrics
    print("\n" + "="*70)
    print("TEST 3: Calculate aggregate metrics")
    print("="*70)
    sample_data = {
        'instagram_followers': 500000,
        'twitter_followers': 250000,
        'tiktok_followers': 100000,
        'instagram_engagement_rate': 0.045,
        'twitter_engagement_rate': 0.032
    }
    metrics = scraper.calculate_total_metrics(sample_data)
    print(json.dumps(metrics, indent=2))
    
    print("\n" + "="*70)
    print("Social Media Scraper Tests Complete!")
    print("="*70)


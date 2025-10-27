"""
Main Data Collection Script
Run this to collect player and team data into the database
"""

import argparse
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_database
from etl.data_pipeline import DataPipeline
from config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Collect college football data from various sources'
    )
    
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize the database (creates tables)'
    )
    
    parser.add_argument(
        '--year',
        type=int,
        default=2023,
        help='Season year to collect (default: 2023)'
    )
    
    parser.add_argument(
        '--teams',
        nargs='+',
        help='Specific teams to collect (default: all)'
    )
    
    parser.add_argument(
        '--test-api',
        action='store_true',
        help='Test API connection only'
    )
    
    parser.add_argument(
        '--teams-only',
        action='store_true',
        help='Collect only team data'
    )
    
    parser.add_argument(
        '--rosters-only',
        action='store_true',
        help='Collect only roster data'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Collect only statistics'
    )
    
    parser.add_argument(
        '--transfers-only',
        action='store_true',
        help='Collect only transfer portal data'
    )
    
    args = parser.parse_args()
    
    # Check configuration
    config = get_config()
    if not config.cfb_api_key:
        print("\n⚠️  ERROR: API key not configured!")
        print("Please add your collegefootballdata.com API key to config/config.yaml\n")
        return
    
    # Initialize database if requested
    if args.init_db:
        logger.info("Initializing database...")
        init_database()
        logger.info("✓ Database initialized")
    
    # Test API connection if requested
    if args.test_api:
        logger.info("Testing API connection...")
        from scrapers.cfb_api_client import CollegeFootballDataAPI
        client = CollegeFootballDataAPI()
        if client.test_connection():
            logger.info("✓ API connection successful!")
        else:
            logger.error("✗ API connection failed!")
        return
    
    # Create pipeline
    pipeline = DataPipeline()
    
    try:
        if args.teams_only:
            # Collect only teams
            pipeline.collect_teams()
        
        elif args.rosters_only:
            # Collect only rosters
            teams = args.teams or ['Alabama', 'Georgia', 'Ohio State']
            for team in teams:
                pipeline.collect_roster(team, args.year)
        
        elif args.stats_only:
            # Collect only stats
            pipeline.collect_player_stats(args.year)
        
        elif args.transfers_only:
            # Collect only transfers
            pipeline.collect_transfers(args.year)
        
        else:
            # Collect all data
            pipeline.collect_all_data_for_season(args.year, teams=args.teams)
        
        logger.info("\n✓ Data collection completed successfully!")
    
    except KeyboardInterrupt:
        logger.info("\n\nData collection interrupted by user")
    
    except Exception as e:
        logger.error(f"\n✗ Data collection failed: {e}", exc_info=True)
    
    finally:
        pipeline.close()


if __name__ == '__main__':
    main()


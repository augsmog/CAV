"""
Collect Basketball Data
Initial data collection for college basketball
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.cbb_api_client import CollegeBasketballDataAPI
from database import get_session
from database.models_basketball import BasketballTeam, BasketballPlayer
import yaml

print("="*80)
print("BASKETBALL DATA COLLECTION")
print("="*80)
print()

# Load config
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

api_key = config.get('collegebasketballdata', {}).get('api_key', '')

if not api_key:
    print("[ERROR] No basketball API key in config")
    sys.exit(1)

# Create API client
client = CollegeBasketballDataAPI(api_key=api_key)

# Test connection
print("Testing API connection...")
if not client.test_connection():
    print("[ERROR] API connection failed")
    sys.exit(1)

print("\n" + "="*80)
print("COLLECTING TEAMS")
print("="*80)

# Get D1 teams for 2023-24 season
teams = client.get_teams(year=2024)
print(f"\nFound {len(teams)} basketball teams for 2024 season")

# Filter to D1 only if possible
d1_teams = [t for t in teams if t.get('classification') == 'NCAA Division I']
if d1_teams:
    print(f"Filtered to {len(d1_teams)} D1 teams")
    teams = d1_teams
else:
    print("Note: Unable to filter by division, using all teams")
    # Take top 350 (approximately D1 size)
    teams = teams[:350]
    print(f"Limited to top {len(teams)} teams")

# Display sample
print("\nSample teams:")
for i, team in enumerate(teams[:10]):
    school = team.get('school', team.get('team', 'Unknown'))
    conf = team.get('conference', 'Unknown')
    print(f"  {i+1}. {school:30} - {conf}")

# Initialize database (creates basketball tables if they don't exist)
print("\n" + "="*80)
print("DATABASE SETUP")
print("="*80)

try:
    # Import Base and engine
    from sqlalchemy import create_engine
    from database.models import Base
    from database.models_basketball import BasketballTeam, BasketballPlayer, BasketballPerformanceStat, BasketballTransfer
    
    # Get engine
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        db_config = yaml.safe_load(f)
    db_path = db_config.get('database', {}).get('sqlite', {}).get('path', 'database/cav_data.db')
    engine = create_engine(f'sqlite:///{db_path}')
    
    print("\nCreating basketball tables...")
    Base.metadata.create_all(engine, tables=[
        BasketballTeam.__table__,
        BasketballPlayer.__table__,
        BasketballPerformanceStat.__table__,
        BasketballTransfer.__table__
    ])
    print("[OK] Basketball tables created")
    
except Exception as e:
    print(f"[ERROR] Database setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Save teams to database
print("\n" + "="*80)
print("SAVING TEAMS TO DATABASE")
print("="*80)

session = get_session()
teams_added = 0
teams_updated = 0

for team_data in teams:
    try:
        school = team_data.get('school', team_data.get('team'))
        if not school:
            continue
        
        # Check if team exists
        existing = session.query(BasketballTeam).filter_by(school=school).first()
        
        if existing:
            # Update
            existing.conference = team_data.get('conference')
            existing.mascot = team_data.get('mascot')
            existing.abbreviation = team_data.get('abbreviation')
            teams_updated += 1
        else:
            # Create new
            team = BasketballTeam(
                school=school,
                conference=team_data.get('conference'),
                division='D1',  # Assuming D1 for now
                mascot=team_data.get('mascot'),
                abbreviation=team_data.get('abbreviation')
            )
            session.add(team)
            teams_added += 1
        
        if (teams_added + teams_updated) % 50 == 0:
            session.commit()
            print(f"  Progress: {teams_added} added, {teams_updated} updated...")
    
    except Exception as e:
        print(f"  [WARNING] Failed to save {school}: {e}")
        session.rollback()
        continue

# Final commit
session.commit()

print(f"\n[SUCCESS] Teams saved:")
print(f"  Added: {teams_added}")
print(f"  Updated: {teams_updated}")
print(f"  Total: {teams_added + teams_updated}")

session.close()

print("\n" + "="*80)
print("BASKETBALL DATA COLLECTION COMPLETE")
print("="*80)
print("\nNext steps:")
print("  1. Basketball teams are now in the database")
print("  2. Ready to collect rosters and player stats")
print("  3. Ready to build basketball valuation model")
print("\nTo see teams:")
print("  python -c \"from database import get_session; from database.models_basketball import BasketballTeam; s=get_session(); teams=s.query(BasketballTeam).limit(10).all(); [print(f'{t.school} - {t.conference}') for t in teams]\"")


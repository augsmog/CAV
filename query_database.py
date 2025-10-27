"""
Quick database query script
"""

from database import get_session
from database.models import Player, Team

session = get_session()

print("="*70)
print("DATABASE CONTENTS")
print("="*70)

# Count teams
team_count = session.query(Team).count()
print(f"\n✓ Teams: {team_count}")

# Count players
player_count = session.query(Player).count()
print(f"✓ Players: {player_count}")

# Show sample players by team
print("\n" + "-"*70)
print("Sample Players by Team:")
print("-"*70)

for team_name in ['Alabama', 'Georgia', 'Ohio State']:
    team = session.query(Team).filter(Team.name == team_name).first()
    if team:
        players = session.query(Player).filter_by(current_team_id=team.id).limit(5).all()
        print(f"\n{team_name} ({len(session.query(Player).filter_by(current_team_id=team.id).all())} players):")
        for p in players:
            print(f"  • {p.name} - {p.position} - {p.height}in/{p.weight}lbs - {p.hometown}, {p.state}")

# Show QBs
print("\n" + "-"*70)
print("Sample Quarterbacks:")
print("-"*70)
qbs = session.query(Player).filter_by(position='QB').limit(10).all()
for qb in qbs:
    team = session.query(Team).filter_by(id=qb.current_team_id).first()
    team_name = team.name if team else "Unknown"
    print(f"  • {qb.name} - {team_name} - #{qb.jersey_number}")

print("\n" + "="*70)
print("Data looks good! Ready for more collection.")
print("="*70)

session.close()


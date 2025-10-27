"""
Analyze Available Data - Check what stats we have for each position
"""

import sys
from pathlib import Path
import json
from collections import defaultdict

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models import Player, PerformanceStat

print("="*80)
print("DATA AVAILABILITY ANALYSIS")
print("="*80)
print()

session = get_session()

# Check each position
positions = ['QB', 'RB', 'WR', 'TE', 'DL', 'DT', 'DE', 'LB', 'CB', 'S']

for pos in positions:
    print(f"\n{'='*80}")
    print(f"POSITION: {pos}")
    print(f"{'='*80}")
    
    # Get a player with stats for this position
    result = session.query(Player, PerformanceStat).join(
        PerformanceStat, Player.id == PerformanceStat.player_id
    ).filter(
        Player.position == pos,
        PerformanceStat.season == 2023
    ).first()
    
    if not result:
        print(f"[X] No stats found for {pos}")
        continue
    
    player, stats = result
    print(f"Sample Player: {player.name}")
    print()
    
    # Check which stat categories are available
    stat_categories = {
        'Passing': stats.passing_stats,
        'Rushing': stats.rushing_stats,
        'Receiving': stats.receiving_stats,
        'Defensive': stats.defensive_stats
    }
    
    for cat_name, cat_data in stat_categories.items():
        if cat_data and cat_data != 'null':
            if isinstance(cat_data, dict):
                print(f"[OK] {cat_name} Stats Available:")
                for key, value in cat_data.items():
                    print(f"   - {key}: {value}")
            elif isinstance(cat_data, str):
                try:
                    parsed = json.loads(cat_data)
                    print(f"[OK] {cat_name} Stats Available:")
                    for key, value in parsed.items():
                        print(f"   - {key}: {value}")
                except:
                    print(f"[!] {cat_name}: Data format issue")
            print()
        else:
            print(f"[X] {cat_name} Stats: Not Available")

print("\n" + "="*80)
print("DATA AVAILABILITY SUMMARY")
print("="*80)
print()

# Summary by position
print("Position-wise stat availability:")
print()

for pos in positions:
    count = session.query(Player).join(
        PerformanceStat, Player.id == PerformanceStat.player_id
    ).filter(
        Player.position == pos,
        PerformanceStat.season == 2023
    ).count()
    
    print(f"{pos:4} - {count:4} players with 2023 stats")

print()
print("="*80)
print("FIELD-LEVEL ANALYSIS")
print("="*80)
print()

# Analyze what fields are in each stat type
passing_fields = set()
rushing_fields = set()
receiving_fields = set()
defensive_fields = set()

all_stats = session.query(PerformanceStat).filter(
    PerformanceStat.season == 2023
).limit(1000).all()

for stat in all_stats:
    if stat.passing_stats and isinstance(stat.passing_stats, dict):
        passing_fields.update(stat.passing_stats.keys())
    if stat.rushing_stats and isinstance(stat.rushing_stats, dict):
        rushing_fields.update(stat.rushing_stats.keys())
    if stat.receiving_stats and isinstance(stat.receiving_stats, dict):
        receiving_fields.update(stat.receiving_stats.keys())
    if stat.defensive_stats and isinstance(stat.defensive_stats, dict):
        defensive_fields.update(stat.defensive_stats.keys())

print("Available Fields by Stat Type:")
print()
print("PASSING:")
for field in sorted(passing_fields):
    print(f"  + {field}")
print()

print("RUSHING:")
for field in sorted(rushing_fields):
    print(f"  + {field}")
print()

print("RECEIVING:")
for field in sorted(receiving_fields):
    print(f"  + {field}")
print()

print("DEFENSIVE:")
for field in sorted(defensive_fields):
    print(f"  + {field}")

print()
print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)

session.close()


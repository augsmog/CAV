"""
Test Basketball Valuation System
Run valuations on basketball players and export results
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models_basketball import BasketballPlayer, BasketballPerformanceStat, BasketballTeam
from models.basketball_valuation import BasketballValuationEngine
from basketball_data_adapter import adapt_basketball_player_to_valuation_format, calculate_per_game_stats

print("="*80)
print("BASKETBALL PLAYER VALUATION TEST")
print("="*80)
print()

# Create valuation engine
engine = BasketballValuationEngine()

# Get database session
session = get_session()

# Query players with stats for 2023 season
print("Loading 2023 basketball players with stats...")
players_query = session.query(
    BasketballPlayer,
    BasketballPerformanceStat,
    BasketballTeam
).join(
    BasketballPerformanceStat,
    BasketballPlayer.id == BasketballPerformanceStat.player_id
).outerjoin(
    BasketballTeam,
    BasketballPlayer.team_id == BasketballTeam.id
).filter(
    BasketballPerformanceStat.season == 2023,
    BasketballPerformanceStat.games_played >= 10,  # At least 10 games
    BasketballPerformanceStat.minutes >= 200  # At least 200 minutes
).all()

print(f"Found {len(players_query)} players with sufficient data")
print()

# Run valuations
valuations = []
success_count = 0
fail_count = 0

print("Running valuations...")
for player, stat, team in players_query:
    try:
        # Adapt data
        player_data = adapt_basketball_player_to_valuation_format(player, stat, team)
        player_data = calculate_per_game_stats(player_data)
        
        # Calculate valuation
        valuation = engine.calculate_valuation(player_data)
        
        # Combine for output
        result = {
            'name': player.name,
            'team': team.school if team else 'Unknown',
            'position': player.position,
            'season': 2023,
            'conference': team.conference if team else '',
            
            # Valuation
            'player_value': valuation['player_value'],
            'nil_potential': valuation['nil_potential'],
            'war': valuation['war'],
            'war_tier': valuation['war_tier'],
            'performance_score': valuation['performance_score'],
            'confidence': valuation['confidence'],
            'classification': valuation['classification'],
            
            # Per-game stats
            'ppg': player_data.get('ppg', 0),
            'rpg': player_data.get('rpg', 0),
            'apg': player_data.get('apg', 0),
            'mpg': player_data.get('mpg', 0),
            'games': player_data.get('games', 0),
            
            # Advanced stats
            'per': player_data.get('per', 0),
            'ortg': player_data.get('ortg', 0),
            'drtg': player_data.get('drtg', 0),
            'ws': player_data.get('ws', 0),
        }
        
        valuations.append(result)
        success_count += 1
        
        # Progress indicator
        if success_count % 100 == 0:
            print(f"  Processed {success_count} players...")
            
    except Exception as e:
        fail_count += 1
        if fail_count <= 5:  # Only show first 5 errors
            print(f"  [WARNING] Failed to value {player.name}: {e}")

session.close()

print()
print(f"Valuation complete!")
print(f"  Success: {success_count}")
print(f"  Failed: {fail_count}")
print()

# Sort by player value
valuations_sorted = sorted(valuations, key=lambda x: x['player_value'], reverse=True)

# Export to JSON
output_dir = Path('outputs/valuations')
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / 'all_basketball_valuations_2023.json'
with open(output_file, 'w') as f:
    json.dump({
        'season': 2023,
        'sport': 'basketball',
        'total_players': len(valuations_sorted),
        'date_generated': '2025-10-28',
        'valuations': valuations_sorted
    }, f, indent=2)

print(f"Exported to: {output_file}")
print()

# Display top 20 players
print("="*80)
print("TOP 20 BASKETBALL PLAYERS BY VALUE (2023)")
print("="*80)
print()
print(f"{'Rank':<6}{'Player':<30}{'Team':<20}{'Pos':<6}{'Value':<12}{'WAR':<8}{'PPG':<8}")
print("-" * 90)

for i, player in enumerate(valuations_sorted[:20], 1):
    print(f"{i:<6}{player['name'][:28]:<30}{player['team'][:18]:<20}{player['position']:<6}"
          f"${player['player_value']:>10,.0f}  {player['war']:>6.2f}  {player['ppg']:>6.1f}")

print()
print("="*80)
print("TOP 20 BASKETBALL PLAYERS BY WAR (2023)")
print("="*80)
print()

war_sorted = sorted(valuations_sorted, key=lambda x: x['war'], reverse=True)
print(f"{'Rank':<6}{'Player':<30}{'Team':<20}{'WAR':<8}{'Tier':<25}")
print("-" * 90)

for i, player in enumerate(war_sorted[:20], 1):
    print(f"{i:<6}{player['name'][:28]:<30}{player['team'][:18]:<20}{player['war']:>6.2f}  {player['war_tier']}")

print()
print("="*80)
print(f"TEST COMPLETE - {len(valuations_sorted)} players valued!")
print("="*80)


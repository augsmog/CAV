"""
Test the Valuation Model with Real 2023 Data
Run valuations on all players with stats and generate reports
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models import Player, Team, PerformanceStat
from models.valuation_engine import create_valuation_engine
from data_adapter import transform_stats_for_model

print("="*80)
print("COLLEGE ATHLETE VALUATION MODEL - 2023 SEASON TEST")
print("="*80)
print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Initialize
session = get_session()
engine = create_valuation_engine()

# Get all players with stats
players_with_stats = session.query(Player, PerformanceStat).join(
    PerformanceStat, Player.id == PerformanceStat.player_id
).filter(
    PerformanceStat.season == 2023
).all()

print(f"Found {len(players_with_stats)} players with 2023 stats")
print("\nRunning valuations...\n")

# Store all valuations
valuations = []
errors = []

# Valuation categories
qb_valuations = []
rb_valuations = []
wr_valuations = []
te_valuations = []
ol_valuations = []
dl_valuations = []
lb_valuations = []
db_valuations = []
k_valuations = []

for i, (player, stats) in enumerate(players_with_stats, 1):
    try:
        # Get team info
        team = session.query(Team).filter_by(id=player.current_team_id).first()
        team_name = team.name if team else "Unknown"
        
        # Transform data to model format
        player_data = transform_stats_for_model(player, stats, team_name)
        
        # Run valuation
        valuation = engine.calculate_comprehensive_valuation(
            player_data,
            current_program=team_name
        )
        
        # Store result
        result = {
            'player': player.name,
            'position': player.position,
            'team': team_name,
            'class_year': player.class_year,
            'total_score': valuation.get('current_program_value', 0),
            'performance_score': valuation.get('performance_score', 0),
            'brand_score': valuation.get('brand_score', 0),
            'scheme_fit_score': valuation.get('scheme_fit_score', 0),
            'market_value': valuation.get('market_value', 0),
        }
        
        valuations.append(result)
        
        # Categorize by position
        pos = (player.position or '').upper()
        if pos == 'QB':
            qb_valuations.append(result)
        elif pos == 'RB':
            rb_valuations.append(result)
        elif pos in ['WR']:
            wr_valuations.append(result)
        elif pos in ['TE']:
            te_valuations.append(result)
        elif pos in ['OL', 'OT', 'OG', 'C']:
            ol_valuations.append(result)
        elif pos in ['DL', 'DE', 'DT', 'NT']:
            dl_valuations.append(result)
        elif pos in ['LB', 'ILB', 'OLB']:
            lb_valuations.append(result)
        elif pos in ['DB', 'CB', 'S', 'SS', 'FS']:
            db_valuations.append(result)
        elif pos in ['K', 'P']:
            k_valuations.append(result)
        
        # Progress update
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(players_with_stats)} players valued...")
        
    except Exception as e:
        errors.append({
            'player': player.name,
            'position': player.position,
            'error': str(e)
        })
        if len(errors) <= 10:  # Only print first 10 errors
            print(f"  ! Error valuing {player.name}: {e}")

print(f"\n[SUCCESS] Valuations complete: {len(valuations)} successful, {len(errors)} errors\n")

# Sort and display top players by position
print("="*80)
print("TOP 10 PLAYERS BY POSITION (Total Score)")
print("="*80)

def print_top_10(valuations_list, position_name):
    if not valuations_list:
        return
    
    sorted_list = sorted(valuations_list, key=lambda x: x['total_score'], reverse=True)
    print(f"\n{position_name}:")
    print("-" * 80)
    for i, v in enumerate(sorted_list[:10], 1):
        print(f"{i:2}. {v['player']:25} ({v['team']:20}) - Score: {v['total_score']:.1f}")

print_top_10(qb_valuations, "QUARTERBACKS")
print_top_10(rb_valuations, "RUNNING BACKS")
print_top_10(wr_valuations, "WIDE RECEIVERS")
print_top_10(te_valuations, "TIGHT ENDS")
print_top_10(dl_valuations, "DEFENSIVE LINE")
print_top_10(lb_valuations, "LINEBACKERS")
print_top_10(db_valuations, "DEFENSIVE BACKS")

# Overall top 25
print("\n" + "="*80)
print("TOP 25 OVERALL PLAYERS (All Positions)")
print("="*80)
sorted_all = sorted(valuations, key=lambda x: x['total_score'], reverse=True)
for i, v in enumerate(sorted_all[:25], 1):
    print(f"{i:2}. {v['player']:25} {v['position']:4} ({v['team']:15}) - Score: {v['total_score']:.1f}")

# Statistics summary
print("\n" + "="*80)
print("VALUATION STATISTICS")
print("="*80)

total_scores = [v['total_score'] for v in valuations if v['total_score'] > 0]
if total_scores:
    avg_score = sum(total_scores) / len(total_scores)
    max_score = max(total_scores)
    min_score = min(total_scores)
    
    print(f"\nTotal players valued: {len(valuations)}")
    print(f"Average score: {avg_score:.2f}")
    print(f"Max score: {max_score:.2f}")
    print(f"Min score: {min_score:.2f}")

# Export results
output_dir = Path(__file__).parent / 'outputs' / 'valuations'
output_dir.mkdir(parents=True, exist_ok=True)

# Export full valuation data
output_file = output_dir / f'all_valuations_2023.json'
with open(output_file, 'w') as f:
    json.dump({
        'generated': datetime.now().isoformat(),
        'season': 2023,
        'total_players': len(valuations),
        'valuations': valuations  # ALL valuations with full details
    }, f, indent=2)

print(f"\n[SUCCESS] Results exported to: {output_file}")

# Export top players by position
positions_file = output_dir / 'top_players_by_position_2023.json'
with open(positions_file, 'w') as f:
    json.dump({
        'generated': datetime.now().isoformat(),
        'season': 2023,
        'quarterbacks': sorted(qb_valuations, key=lambda x: x['total_score'], reverse=True)[:20],
        'running_backs': sorted(rb_valuations, key=lambda x: x['total_score'], reverse=True)[:20],
        'wide_receivers': sorted(wr_valuations, key=lambda x: x['total_score'], reverse=True)[:20],
        'tight_ends': sorted(te_valuations, key=lambda x: x['total_score'], reverse=True)[:20],
        'defensive_line': sorted(dl_valuations, key=lambda x: x['total_score'], reverse=True)[:20],
        'linebackers': sorted(lb_valuations, key=lambda x: x['total_score'], reverse=True)[:20],
        'defensive_backs': sorted(db_valuations, key=lambda x: x['total_score'], reverse=True)[:20],
    }, f, indent=2)

print(f"[SUCCESS] Position rankings exported to: {positions_file}")

print("\n" + "="*80)
print("MODEL VALIDATION COMPLETE!")
print("="*80)
print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

session.close()


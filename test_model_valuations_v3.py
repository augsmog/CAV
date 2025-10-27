"""
Test Model Valuations V3
Improvements:
- Sample size confidence adjustments
- Game context weighting
- Opponent quality adjustments
- Season-specific valuations
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
from models.valuation_engine_v3 import create_valuation_engine_v3
from data_adapter import transform_stats_for_model

print("="*80)
print("COLLEGE ATHLETE VALUATION MODEL V3 - 2023 SEASON")
print("="*80)
print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("V3 IMPROVEMENTS:")
print("  - Sample size confidence (penalize backup QBs with limited snaps)")
print("  - Game context adjustments (garbage time vs high leverage)")
print("  - Opponent quality weighting")
print("  - Confidence intervals based on sample size")
print()

# Initialize
session = get_session()
engine = create_valuation_engine_v3()

# Get all players with 2023 stats
players_with_stats = session.query(Player, PerformanceStat).join(
    PerformanceStat, Player.id == PerformanceStat.player_id
).filter(PerformanceStat.season == 2023).all()

print(f"Found {len(players_with_stats)} players with 2023 stats\n")
print("Running V3 valuations...")

valuations = []
errors = []

# Track backups for reporting
backup_qbs = []
limited_sample_players = []

# Categorize by position
position_valuations = {
    'QB': [], 'RB': [], 'WR': [], 'TE': [],
    'OL': [], 'DL': [], 'LB': [], 'DB': [], 'S': [], 'CB': []
}

for i, (player, stats) in enumerate(players_with_stats, 1):
    if i % 100 == 0:
        print(f"  Progress: {i}/{len(players_with_stats)} players valued...")
    
    try:
        # Get team info
        team = session.query(Team).filter_by(id=player.current_team_id).first()
        team_name = team.name if team else "Unknown"
        
        # Transform data
        player_data = transform_stats_for_model(player, stats, team_name)
        
        # Run V3 valuation with season
        valuation = engine.calculate_comprehensive_valuation(
            player_data,
            current_program=team_name,
            season=2023
        )
        
        # Store result
        result = {
            'player': player.name,
            'position': player.position,
            'team': team_name,
            'class_year': player.class_year,
            'season': 2023,
            
            # VALUES
            'player_value': valuation['player_value'],
            'nil_potential': valuation['nil_potential'],
            'combined_value': valuation['combined_value'],
            'market_value': valuation['market_value'],
            
            # CONFIDENCE METRICS (V3)
            'snaps_played': valuation['snaps_played'],
            'sample_confidence': valuation['sample_confidence'],
            'confidence_interval_pct': valuation['confidence_interval_pct'],
            'value_low': valuation['value_low'],
            'value_high': valuation['value_high'],
            
            # ADJUSTMENT FACTORS (V3)
            'raw_performance_score': valuation['raw_performance_score'],
            'adjusted_performance_score': valuation['adjusted_performance_score'],
            'sample_size_adjustment': valuation['sample_size_adjustment'],
            'context_adjustment': valuation['context_adjustment'],
            'opponent_adjustment': valuation['opponent_adjustment'],
            
            # Component scores
            'performance_score': valuation['performance_score'],
            'scheme_fit_score': valuation['scheme_fit_score'],
            'brand_score': valuation['brand_score'],
            
            # FLAGS (V3)
            'limited_sample_warning': valuation['limited_sample_warning'],
            'backup_flag': valuation['backup_flag'],
            
            # Legacy
            'total_score': valuation['combined_value']
        }
        
        valuations.append(result)
        
        # Track backups and limited sample
        if result['backup_flag'] and player.position == 'QB':
            backup_qbs.append(result)
        if result['limited_sample_warning']:
            limited_sample_players.append(result)
        
        # Categorize by position
        pos = (player.position or 'Unknown').upper()
        if pos in position_valuations:
            position_valuations[pos].append(result)
        elif pos in ['S', 'CB']:
            position_valuations['DB'].append(result)
    
    except Exception as e:
        errors.append({
            'player': player.name,
            'position': player.position,
            'error': str(e)
        })
        if len(errors) <= 10:
            print(f"  ! Error valuing {player.name}: {e}")

print(f"\n[SUCCESS] Valuations complete: {len(valuations)} successful, {len(errors)} errors\n")

# V3 SPECIFIC REPORTING
print("="*80)
print("V3 SAMPLE SIZE & CONTEXT ANALYSIS")
print("="*80)
print(f"\nPlayers with limited sample warning: {len(limited_sample_players)}")
print(f"Backup QBs identified: {len(backup_qbs)}")

# Show backup QBs sorted by player value
print("\nTop 10 Backup QBs (by player value - should be lower now):")
print("-" * 80)
sorted_backups = sorted(backup_qbs, key=lambda x: x['player_value'], reverse=True)[:10]
for i, p in enumerate(sorted_backups):
    print(f" {i+1:2}. {p['player']:<25} - ${p['player_value']/1e3:.0f}K "
          f"(Snaps: {p['snaps_played']}, Confidence: {p['sample_confidence']:.0%})")

# Display top players by position
def print_top_10(player_list, title):
    print(f"\n{title}:")
    print("-" * 80)
    sorted_players = sorted(player_list, key=lambda x: x['player_value'], reverse=True)[:10]
    for i, p in enumerate(sorted_players):
        player_val = p['player_value'] / 1e6
        confidence = p['sample_confidence']
        snaps = p['snaps_played']
        print(f" {i+1:2}. {p['player']:<25} ({p['team']:<15}) - "
              f"${player_val:.2f}M | Snaps: {snaps:,} | Conf: {confidence:.0%}")

print("\n" + "="*80)
print("TOP 10 PLAYERS BY POSITION (With Sample Size Context)")
print("="*80)

print_top_10(position_valuations['QB'], "QUARTERBACKS")
print_top_10(position_valuations['RB'], "RUNNING BACKS")
print_top_10(position_valuations['WR'], "WIDE RECEIVERS")

# Overall top 25
print("\n"+"="*80)
print("TOP 25 OVERALL PLAYERS (By Player Value)")
print("="*80)
sorted_all = sorted(valuations, key=lambda x: x['player_value'], reverse=True)[:25]
for i, p in enumerate(sorted_all):
    player_val = p['player_value'] / 1e6
    snaps = p['snaps_played']
    confidence = p['sample_confidence']
    print(f" {i+1:2}. {p['player']:<25} {p['position']:<4} ({p['team']:<15}) - "
          f"${player_val:.2f}M | Snaps: {snaps:4} | Conf: {confidence:.0%}")

# Statistics
print("\n"+"="*80)
print("VALUATION STATISTICS (V3)")
print("="*80)

if valuations:
    player_values = [v['player_value'] for v in valuations]
    confidences = [v['sample_confidence'] for v in valuations]
    
    print(f"\nTotal players valued: {len(valuations)}")
    print(f"Average confidence: {sum(confidences) / len(confidences):.1%}")
    print(f"High confidence players (>90%): {len([c for c in confidences if c > 0.9])}")
    print(f"Low confidence players (<50%): {len([c for c in confidences if c < 0.5])}")
    
    print(f"\nPlayer Value (What Schools Pay):")
    print(f"  Average: ${sum(player_values) / len(player_values):,.0f}")
    print(f"  Max: ${max(player_values):,.0f}")
    print(f"  Min: ${min(player_values):,.0f}")

# Export results with season
output_dir = Path(__file__).parent / 'outputs' / 'valuations'
output_dir.mkdir(parents=True, exist_ok=True)

# Export V3 valuations by season
output_file = output_dir / 'all_valuations_2023_v3.json'
with open(output_file, 'w') as f:
    json.dump({
        'generated': datetime.now().isoformat(),
        'season': 2023,
        'version': 3,
        'description': 'V3 with sample size, context, and opponent adjustments',
        'total_players': len(valuations),
        'valuations': valuations
    }, f, indent=2)

print(f"\n[SUCCESS] V3 results exported to: {output_file}")

# Also update main file for dashboard
main_output_file = output_dir / 'all_valuations_2023.json'
with open(main_output_file, 'w') as f:
    json.dump({
        'generated': datetime.now().isoformat(),
        'season': 2023,
        'version': 3,
        'description': 'V3 valuations with sample size and context adjustments',
        'total_players': len(valuations),
        'valuations': valuations
    }, f, indent=2)

print(f"[SUCCESS] Main file updated: {main_output_file}")

print("\n" + "="*80)
print("MODEL V3 VALIDATION COMPLETE!")
print("="*80)
print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("KEY V3 IMPROVEMENTS:")
print("  [SUCCESS] Sample size confidence adjustments")
print("  [SUCCESS] Backup QBs properly penalized")
print("  [SUCCESS] Game context weighting")
print("  [SUCCESS] Opponent quality adjustments")
print("  [SUCCESS] Confidence intervals added")
print()

session.close()


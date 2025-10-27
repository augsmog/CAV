"""
Test V4 WAR-Driven Valuation Engine
Run valuations on all players with WAR as primary value driver
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models import Player, Team, PerformanceStat
from models.valuation_engine_v4_war import create_valuation_engine_v4_war
from data_adapter import transform_stats_for_model

print("="*80)
print("COLLEGE ATHLETE VALUATION MODEL - V4 WAR-DRIVEN")
print("="*80)
print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Initialize
session = get_session()
engine = create_valuation_engine_v4_war()

# Get all players with stats for both 2022 and 2023
for year in [2023, 2022]:
    print(f"\n{'='*80}")
    print(f"PROCESSING {year} SEASON")
    print(f"{'='*80}\n")
    
    players_with_stats = session.query(Player, PerformanceStat).join(
        PerformanceStat, Player.id == PerformanceStat.player_id
    ).filter(PerformanceStat.season == year).all()
    
    print(f"Found {len(players_with_stats)} players with {year} stats\n")
    print("Running WAR-driven valuations...")
    
    valuations = []
    errors = []
    
    # Categorize by position
    qb_vals = []
    rb_vals = []
    wr_vals = []
    te_vals = []
    dl_vals = []
    lb_vals = []
    db_vals = []
    
    for i, (player, stats) in enumerate(players_with_stats, 1):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(players_with_stats)} players valued...")
        
        try:
            # Get team info
            team = session.query(Team).filter_by(id=player.current_team_id).first()
            team_name = team.name if team else "Unknown"
            
            # Transform data
            player_data = transform_stats_for_model(player, stats, team_name)
            
            # Run V4 WAR-driven valuation
            valuation = engine.calculate_comprehensive_valuation(
                player_data,
                current_program=team_name,
                season=year
            )
            
            # Store result with WAR metrics
            result = {
                'player': player.name,
                'position': player.position,
                'team': team_name,
                'class_year': player.class_year,
                'season': year,
                
                # V4 WAR METRICS (Primary)
                'war': valuation.get('war', 0),
                'wins_added': valuation.get('wins_added', 0),
                'war_tier': valuation.get('war_tier', 'Unknown'),
                'value_rating': valuation.get('value_rating', 'Unknown'),
                
                # Dollar values
                'player_value': valuation.get('player_value', 0),
                'nil_potential': valuation.get('nil_potential', 0),
                'combined_value': valuation.get('combined_value', 0),
                
                # Scores
                'performance_score': valuation.get('performance_score', 0),
                'scheme_fit_score': valuation.get('scheme_fit_score', 0),
                'brand_score': valuation.get('brand_score', 0),
                
                # WAR details
                'leverage_index': valuation.get('leverage_index', 1.0),
                'opponent_adjustment': valuation.get('opponent_adjustment', 1.0),
                'participation_factor': valuation.get('participation_factor', 0),
                'playoff_impact_pct': valuation.get('playoff_impact_pct', 0),
                
                # Confidence
                'war_uncertainty': valuation.get('war_uncertainty', 0),
                'value_low': valuation.get('value_low', 0),
                'value_high': valuation.get('value_high', 0),
                
                # Context
                'snaps_played': valuation.get('snaps_played', 0),
                'games_started': valuation.get('games_started', 0),
                'limited_sample_warning': valuation.get('limited_sample_warning', False),
                'backup_flag': valuation.get('backup_flag', False),
                
                # Full details
                'raw_valuation_details': valuation
            }
            
            valuations.append(result)
            
            # Categorize by position
            pos = (player.position or '').upper()
            if pos == 'QB': qb_vals.append(result)
            elif pos == 'RB': rb_vals.append(result)
            elif pos == 'WR': wr_vals.append(result)
            elif pos == 'TE': te_vals.append(result)
            elif pos in ['DT', 'DE', 'DL']: dl_vals.append(result)
            elif pos in ['LB', 'ILB', 'OLB']: lb_vals.append(result)
            elif pos in ['CB', 'S', 'DB']: db_vals.append(result)
        
        except Exception as e:
            errors.append({
                'player': player.name,
                'position': player.position,
                'error': str(e)
            })
            if len(errors) <= 5:
                print(f"  ! Error valuing {player.name}: {e}")
    
    print(f"\n[SUCCESS] Valuations complete: {len(valuations)} successful, {len(errors)} errors\n")
    
    # Display results sorted by WAR
    print("="*80)
    print(f"TOP PLAYERS BY WAR - {year} SEASON")
    print("="*80)
    
    def display_war_top_players(title, player_list, limit=10):
        print(f"\n{title}:")
        print("-" * 80)
        sorted_players = sorted(player_list, key=lambda x: x['war'], reverse=True)[:limit]
        for i, p in enumerate(sorted_players):
            war_flag = " [LIMITED]" if p.get('limited_sample_warning') else ""
            backup_flag = " [BACKUP]" if p.get('backup_flag') else ""
            print(f" {i+1:2}. {p['player']:<25} ({p['team']:<15}) - "
                  f"WAR: {p['war']:.3f} | Value: ${p['player_value']/1e6:.2f}M | "
                  f"{p['war_tier']}{war_flag}{backup_flag}")
    
    display_war_top_players("QUARTERBACKS", qb_vals)
    display_war_top_players("RUNNING BACKS", rb_vals)
    display_war_top_players("WIDE RECEIVERS", wr_vals)
    display_war_top_players("TIGHT ENDS", te_vals)
    display_war_top_players("DEFENSIVE LINE", dl_vals)
    display_war_top_players("LINEBACKERS", lb_vals)
    display_war_top_players("DEFENSIVE BACKS", db_vals)
    
    # Overall top 25 by WAR
    print("\n"+"="*80)
    print(f"TOP 25 PLAYERS BY WAR - {year} SEASON (All Positions)")
    print("="*80)
    sorted_all = sorted(valuations, key=lambda x: x['war'], reverse=True)[:25]
    for i, p in enumerate(sorted_all):
        print(f" {i+1:2}. {p['player']:<25} {p['position']:<4} ({p['team']:<15}) - "
              f"WAR: {p['war']:.3f} | +{p['wins_added']:.2f} wins | "
              f"Value: ${p['player_value']/1e6:.2f}M")
    
    # WAR Statistics
    print("\n"+"="*80)
    print(f"WAR DISTRIBUTION - {year} SEASON")
    print("="*80)
    
    if valuations:
        wars = [v['war'] for v in valuations]
        print(f"\nTotal players: {len(valuations)}")
        print(f"Average WAR: {np.mean(wars):.3f}")
        print(f"Median WAR: {np.median(wars):.3f}")
        print(f"Max WAR: {max(wars):.3f}")
        print(f"Min WAR: {min(wars):.3f}")
        print(f"Std Dev: {np.std(wars):.3f}")
        
        # WAR tiers
        elite = len([w for w in wars if w >= 2.0])
        all_conf = len([w for w in wars if 1.0 <= w < 2.0])
        above_avg = len([w for w in wars if 0.5 <= w < 1.0])
        avg = len([w for w in wars if 0.0 <= w < 0.5])
        below = len([w for w in wars if w < 0.0])
        
        print(f"\nWAR Tiers:")
        print(f"  Elite (WAR ≥ 2.0): {elite} players ({elite/len(wars)*100:.1f}%)")
        print(f"  All-Conference (1.0-2.0): {all_conf} players ({all_conf/len(wars)*100:.1f}%)")
        print(f"  Above Average (0.5-1.0): {above_avg} players ({above_avg/len(wars)*100:.1f}%)")
        print(f"  Average (0.0-0.5): {avg} players ({avg/len(wars)*100:.1f}%)")
        print(f"  Below Replacement (<0.0): {below} players ({below/len(wars)*100:.1f}%)")
    
    # Export results
    output_dir = Path(__file__).parent / 'outputs' / 'valuations'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'all_valuations_{year}.json'
    
    with open(output_file, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'season': year,
            'model_version': 'V4_WAR_Driven',
            'total_players': len(valuations),
            'valuations': valuations  # All players, not just top
        }, f, indent=2)
    
    print(f"\n[SUCCESS] Results exported to: {output_file}")

print("\n" + "="*80)
print("V4 WAR-DRIVEN VALUATION COMPLETE!")
print("="*80)
print(f"\nKey Changes in V4:")
print("  - WAR is now the PRIMARY value driver")
print("  - Each 1.0 WAR for a QB worth $1.5M")
print("  - Leverage index properly weights garbage time (0.3x)")
print("  - Backup QBs with limited snaps correctly valued low")
print("  - Position-specific $/WAR reflects market realities")
print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

import numpy as np  # For statistics


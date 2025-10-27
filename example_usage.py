"""
Example Usage Script
Demonstrates how to use the valuation model with sample data
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.valuation_engine import create_valuation_engine
from analysis.backtesting import BacktestingFramework, generate_backtest_report
import json
from datetime import date


def create_sample_player_data():
    """
    Create sample player data for demonstration
    """
    return {
        'player_id': 'QB001',
        'name': 'John Smith',
        'position': 'QB',
        'height': 75,  # inches
        'weight': 215,
        'hometown': 'Austin',
        'state': 'TX',
        'class_year': 2022,
        'eligibility_remaining': 2,
        'current_program': 'Texas A&M',
        'conference': 'SEC',
        
        # Performance stats
        'stats': {
            'completion_percentage': 67.5,
            'yards_per_attempt': 8.2,
            'td_int_ratio': 3.5,
            'qbr': 82.5,
            'success_rate': 0.52,
            'epa_per_play': 0.25
        },
        'pff_grade': 85.3,
        'snaps_played': 750,
        'games_played': 12,
        'games_started': 12,
        'team_wins': 9,
        'team_losses': 3,
        'team_total_snaps': 850,
        'strength_of_schedule': 1.15,
        'opponent_strength': 1.12,
        
        # Film evaluation
        'film_grade': 83,
        'skills': {
            'arm_strength': 8.0,
            'quick_release': 7.5,
            'accuracy_short': 8.5,
            'accuracy_medium': 8.0,
            'accuracy_deep': 7.0,
            'decision_making': 8.5,
            'mobility': 6.5,
            'pocket_presence': 8.0,
            'football_iq': 8.5,
            'pre_snap_reads': 8.0
        },
        'football_iq': 8.5,
        'years_playing': 3,
        
        # Scheme history
        'current_scheme': 'Spread',
        'scheme_history': ['Spread', 'Pro Style'],
        
        # Brand/NIL
        'instagram_followers': 125000,
        'twitter_followers': 85000,
        'tiktok_followers': 200000,
        'engagement_rate': 0.045,
        'follower_growth_rate': 0.12,
        'google_search_volume': 75000,
        'media_mentions_monthly': 35,
        'national_media_coverage': True,
        'personality_rating': 8,
        'media_skills_rating': 7,
        'community_engagement_hours': 25,
        'playing_in_home_state': True,
        'compelling_backstory': False,
        
        # Risk factors
        'injury_history': [
            {'season': 2023, 'injury_type': 'ankle sprain', 'games_missed': 1}
        ],
        'controversies': 0,
        'academic_concerns': False,
        
        # Depth chart
        'depth_chart_position': 1,
        'is_starter': True,
        
        # Career trajectory
        'career_trajectory': {
            'trend': 'improving',
            'slope': 3.5,
            'recent_vs_career': 5.2
        }
    }


def example_single_player_valuation():
    """
    Example: Value a single player
    """
    print("=" * 70)
    print("EXAMPLE 1: Single Player Valuation")
    print("=" * 70)
    print()
    
    # Create valuation engine
    engine = create_valuation_engine()
    
    # Create sample player
    player = create_sample_player_data()
    
    # Define target programs for transfer consideration
    target_programs = ['Alabama', 'Georgia', 'Ohio State', 'USC', 'Oregon']
    
    # Calculate valuation
    valuation = engine.calculate_comprehensive_valuation(
        player_data=player,
        current_program=player['current_program'],
        target_programs=target_programs,
        market_context={'supply_demand_ratio': 0.8}  # High demand market
    )
    
    # Display results
    print(f"Player: {valuation['player_name']}")
    print(f"Position: {valuation['position']}")
    print(f"Current Program: {valuation['current_program']}")
    print()
    
    print("COMPONENT SCORES (0-100):")
    print(f"  Performance Score:      {valuation['performance_score']:.1f}")
    print(f"  Brand/NIL Score:        {valuation['brand_score']:.1f}")
    print(f"  Scheme Fit Score:       {valuation['scheme_fit_score']:.1f}")
    print(f"  Positional Value:       {valuation['positional_value_score']:.1f}")
    print(f"  Win Impact Score:       {valuation['win_impact_score']:.1f}")
    print()
    
    print("VALUATION:")
    print(f"  Current Program Value:  ${valuation['current_program_value']:,.0f}")
    print(f"  Transfer Market Value:  ${valuation['market_value']:,.0f}")
    low, high = valuation['value_confidence_interval']
    print(f"  Confidence Interval:    ${low:,.0f} - ${high:,.0f}")
    print()
    
    print("NIL ESTIMATE:")
    nil = valuation['nil_value_estimate']
    print(f"  Annual Expected:        ${nil['annual_expected']:,.0f}")
    print(f"  Annual Range:           ${nil['annual_low']:,.0f} - ${nil['annual_high']:,.0f}")
    print(f"  Career Potential:       ${nil['career_potential']:,.0f}")
    print()
    
    print("RISK ASSESSMENT:")
    print(f"  Risk Category:          {valuation['risk_details']['risk_category']}")
    print(f"  Injury Risk:            {valuation['injury_risk_factor']:.2f}")
    print(f"  Performance Risk:       {valuation['performance_risk_factor']:.2f}")
    print(f"  Off-Field Risk:         {valuation['off_field_risk_factor']:.2f}")
    print()
    
    print("TOP VALUE DRIVERS:")
    for driver in valuation['key_value_drivers']:
        print(f"  • {driver}")
    print()
    
    print("ALTERNATIVE PROGRAM VALUES:")
    for prog, details in sorted(
        valuation['alternative_program_values'].items(),
        key=lambda x: x[1]['total_value'],
        reverse=True
    ):
        print(f"  {prog:20s} ${details['total_value']:>12,.0f}  "
              f"(Fit: {details['scheme_fit_score']:.0f}, "
              f"NIL: ${details['nil_potential']:,.0f})")
    print()
    
    print("TRANSFER RECOMMENDATION:")
    rec = valuation['transfer_recommendation']
    print(f"  Decision:               {rec['recommendation']}")
    print(f"  Confidence:             {rec['confidence']}")
    print(f"  Best Alternative:       {rec.get('best_alternative', 'N/A')}")
    if rec.get('projected_value_gain'):
        print(f"  Projected Value Gain:   ${rec['projected_value_gain']:,.0f} "
              f"({rec['percent_value_gain']:.1f}%)")
    print(f"  Reasoning:              {rec['reasoning']}")
    print()


def example_compare_players():
    """
    Example: Compare multiple players
    """
    print("=" * 70)
    print("EXAMPLE 2: Compare Multiple Players")
    print("=" * 70)
    print()
    
    engine = create_valuation_engine()
    
    # Create multiple players with variations
    players = []
    
    # Player 1: Elite QB
    player1 = create_sample_player_data()
    player1['player_id'] = 'QB001'
    player1['name'] = 'Elite QB'
    
    # Player 2: Good QB with lower brand
    player2 = create_sample_player_data()
    player2['player_id'] = 'QB002'
    player2['name'] = 'Solid QB'
    player2['stats']['completion_percentage'] = 63.0
    player2['stats']['yards_per_attempt'] = 7.5
    player2['instagram_followers'] = 30000
    player2['twitter_followers'] = 20000
    player2['national_media_coverage'] = False
    
    # Player 3: RB with high brand
    player3 = create_sample_player_data()
    player3['player_id'] = 'RB001'
    player3['name'] = 'Star RB'
    player3['position'] = 'RB'
    player3['stats'] = {
        'yards_per_carry': 6.2,
        'yards_after_contact': 3.5,
        'success_rate': 0.58,
        'receiving_grade': 75,
        'epa_per_play': 0.22
    }
    player3['instagram_followers'] = 300000
    player3['tiktok_followers'] = 500000
    
    players = [player1, player2, player3]
    
    comparisons = []
    for player in players:
        val = engine.calculate_comprehensive_valuation(
            player_data=player,
            current_program=player['current_program']
        )
        comparisons.append({
            'name': val['player_name'],
            'position': val['position'],
            'market_value': val['market_value'],
            'performance': val['performance_score'],
            'brand': val['brand_score'],
            'nil_estimate': val['nil_value_estimate']['annual_expected']
        })
    
    print(f"{'Player':<15} {'Pos':<5} {'Performance':<12} {'Brand':<10} "
          f"{'Market Value':<15} {'NIL Est':<15}")
    print("-" * 80)
    
    for comp in sorted(comparisons, key=lambda x: x['market_value'], reverse=True):
        print(f"{comp['name']:<15} {comp['position']:<5} "
              f"{comp['performance']:<12.1f} {comp['brand']:<10.1f} "
              f"${comp['market_value']:<14,.0f} ${comp['nil_estimate']:<14,.0f}")
    print()


def example_transfer_scenario():
    """
    Example: Evaluate transfer scenarios
    """
    print("=" * 70)
    print("EXAMPLE 3: Transfer Scenario Analysis")
    print("=" * 70)
    print()
    
    engine = create_valuation_engine()
    player = create_sample_player_data()
    
    # Scenario: QB considering transfer from Texas A&M
    scenarios = [
        ('Stay at Texas A&M', 'Texas A&M'),
        ('Transfer to Alabama', 'Alabama'),
        ('Transfer to USC', 'USC'),
        ('Transfer to Oregon', 'Oregon')
    ]
    
    print(f"Player: {player['name']} - {player['position']}")
    print(f"Current: {player['current_program']}")
    print()
    print("SCENARIO ANALYSIS:")
    print("-" * 70)
    
    results = []
    for scenario_name, program in scenarios:
        # Update player's current program for valuation
        temp_player = player.copy()
        
        if program == player['current_program']:
            val = engine.calculate_comprehensive_valuation(
                temp_player,
                program
            )
            is_current = True
        else:
            val = engine.calculate_comprehensive_valuation(
                temp_player,
                player['current_program'],
                target_programs=[program]
            )
            is_current = False
        
        if is_current:
            total_value = val['current_program_value']
            scheme_fit = val['scheme_fit_score']
            nil_value = val['nil_value_estimate']['annual_expected']
        else:
            alt_val = val['alternative_program_values'].get(program, {})
            total_value = alt_val.get('total_value', 0)
            scheme_fit = alt_val.get('scheme_fit_score', 0)
            nil_value = alt_val.get('nil_potential', 0)
        
        results.append({
            'scenario': scenario_name,
            'value': total_value,
            'fit': scheme_fit,
            'nil': nil_value,
            'program': program
        })
    
    for result in sorted(results, key=lambda x: x['value'], reverse=True):
        print(f"\n{result['scenario']}")
        print(f"  Total Value:    ${result['value']:>12,.0f}")
        print(f"  Scheme Fit:     {result['fit']:>12.1f}")
        print(f"  NIL Potential:  ${result['nil']:>12,.0f}")
    
    print()


def example_data_export():
    """
    Example: Export valuation data
    """
    print("=" * 70)
    print("EXAMPLE 4: Export Valuation Data")
    print("=" * 70)
    print()
    
    engine = create_valuation_engine()
    player = create_sample_player_data()
    
    valuation = engine.calculate_comprehensive_valuation(
        player_data=player,
        current_program=player['current_program'],
        target_programs=['Alabama', 'Georgia', 'Ohio State']
    )
    
    # Export to JSON
    output_dir = Path(__file__).parent / 'outputs' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'sample_valuation.json'
    
    # Convert date objects to strings for JSON serialization
    def default_serializer(obj):
        if isinstance(obj, date):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(str(output_file), 'w') as f:
        json.dump(valuation, f, indent=2, default=default_serializer)
    
    print(f"Valuation data exported to: {output_file}")
    print()


if __name__ == '__main__':
    """
    Run all examples
    """
    print("\n")
    print("#" * 70)
    print("# COLLEGE FOOTBALL PLAYER VALUATION MODEL")
    print("# Example Usage Demonstrations")
    print("#" * 70)
    print("\n")
    
    try:
        # Example 1: Single player valuation
        example_single_player_valuation()
        input("Press Enter to continue to next example...")
        print("\n")
        
        # Example 2: Compare players
        example_compare_players()
        input("Press Enter to continue to next example...")
        print("\n")
        
        # Example 3: Transfer scenarios
        example_transfer_scenario()
        input("Press Enter to continue to next example...")
        print("\n")
        
        # Example 4: Data export
        example_data_export()
        
        print("\n")
        print("=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print()
        print("Next Steps:")
        print("1. Load your historical transfer data")
        print("2. Run backtesting with: python analysis/backtesting.py")
        print("3. Refine model weights based on results")
        print("4. Build data pipeline for ongoing valuations")
        print()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

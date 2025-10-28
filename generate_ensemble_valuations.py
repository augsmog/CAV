"""
Generate Ensemble Valuations for All Players
Replaces WAR-based valuations with comprehensive 6-pillar ensemble analysis
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models import Player, Team, PerformanceStat
from models.pillars import (
    EnsembleValuationEngine,
    ProductionValueModel,
    PredictiveFuturePerformanceModel,
    PositionalScarcityModel,
    MarketContextModel,
    BrandIntangiblesModel,
    RiskAdjustmentModel
)

def convert_stats_to_ensemble_format(player_stats, position):
    """Convert database stats to ensemble model format"""
    stats = {}

    if not player_stats:
        return stats

    # Common stats
    stats['games_played'] = player_stats.games_played or 0
    stats['games_started'] = player_stats.games_started or 0

    # Position-specific conversions
    position = position.upper()

    if position == 'QB':
        stats['epa_per_play'] = player_stats.epa_play or 0
        stats['completion_pct'] = player_stats.completion_pct or 60
        stats['passing_touchdowns'] = player_stats.passing_touchdowns or 0
        stats['interceptions'] = player_stats.interceptions or 1
        stats['rushing_yards'] = player_stats.rushing_yards or 0
        stats['rushing_touchdowns'] = player_stats.rushing_touchdowns or 0
        stats['passer_rating'] = player_stats.passer_rating or 100

    elif position == 'RB':
        stats['yards_per_carry'] = player_stats.yards_per_carry or 0
        stats['rushing_yards'] = player_stats.rushing_yards or 0
        stats['rushing_touchdowns'] = player_stats.rushing_touchdowns or 0
        stats['receptions'] = player_stats.receptions or 0
        stats['receiving_yards'] = player_stats.receiving_yards or 0
        stats['carries'] = player_stats.carries or 1

    elif position in ['WR', 'TE']:
        stats['receptions'] = player_stats.receptions or 0
        stats['receiving_yards'] = player_stats.receiving_yards or 0
        stats['receiving_touchdowns'] = player_stats.receiving_touchdowns or 0
        stats['targets'] = player_stats.targets or 1
        stats['catch_rate'] = (player_stats.receptions / max(player_stats.targets, 1)) if player_stats.targets else 0.6

    elif position in ['OL', 'OT', 'OG', 'C']:
        stats['pass_block_grade'] = player_stats.pass_block_grade or 60
        stats['run_block_grade'] = player_stats.run_block_grade or 60
        stats['total_snaps'] = player_stats.snaps or 500

    elif position in ['DL', 'DE', 'DT', 'EDGE']:
        stats['sacks'] = player_stats.sacks or 0
        stats['tackles_for_loss'] = player_stats.tackles_for_loss or 0
        stats['pressures'] = player_stats.pressures or 0
        stats['pass_rush_snaps'] = player_stats.snaps or 200

    elif position == 'LB':
        stats['tackles'] = player_stats.tackles or 0
        stats['tackles_for_loss'] = player_stats.tackles_for_loss or 0
        stats['sacks'] = player_stats.sacks or 0
        stats['coverage_grade'] = getattr(player_stats, 'coverage_grade', 60)

    elif position in ['CB', 'S', 'DB']:
        stats['interceptions'] = player_stats.interceptions or 0
        stats['pass_breakups'] = getattr(player_stats, 'pass_breakups', 0)
        stats['tackles'] = player_stats.tackles or 0
        stats['coverage_snaps'] = player_stats.snaps or 400

    return stats

def get_player_conference_strength(team_name):
    """Map team to conference and get strength multiplier"""
    # This is a simplified mapping - in production, query from database
    conference_map = {
        'Alabama': 'SEC',
        'Georgia': 'SEC',
        'LSU': 'SEC',
        'Texas A&M': 'SEC',
        'Florida': 'SEC',
        'Auburn': 'SEC',
        'Tennessee': 'SEC',

        'Ohio State': 'Big Ten',
        'Michigan': 'Big Ten',
        'Penn State': 'Big Ten',
        'Wisconsin': 'Big Ten',
        'Iowa': 'Big Ten',

        'Clemson': 'ACC',
        'Miami': 'ACC',
        'Florida State': 'ACC',
        'North Carolina': 'ACC',

        'Oklahoma': 'Big 12',
        'Texas': 'Big 12',
        'Oklahoma State': 'Big 12',
        'Baylor': 'Big 12',
    }

    return conference_map.get(team_name, 'G5')

def generate_valuations_for_sport(sport='football', limit=None):
    """Generate ensemble valuations for all players in a sport"""

    print(f"\n{'='*80}")
    print(f"Generating Ensemble Valuations - {sport.upper()}")
    print(f"{'='*80}\n")

    session = get_session()
    engine = EnsembleValuationEngine(sport=sport)

    # Load all players with stats
    query = session.query(Player, PerformanceStat, Team).join(
        PerformanceStat, Player.id == PerformanceStat.player_id
    ).join(
        Team, Player.current_team_id == Team.id
    ).filter(
        PerformanceStat.season == 2023
    )

    if limit:
        query = query.limit(limit)

    results = query.all()

    print(f"Found {len(results)} players to value\n")

    valuations = []

    for idx, (player, stats, team) in enumerate(results, 1):
        try:
            print(f"[{idx}/{len(results)}] Valuing {player.name} ({player.position})...", end=' ')

            # Convert stats to ensemble format
            current_stats = convert_stats_to_ensemble_format(stats, player.position)

            # Get conference
            conference = get_player_conference_strength(team.school)

            # Determine class year (estimate from eligibility)
            class_year = 'JR'  # Default

            # Create minimal valuation (without full history for now)
            result = engine.calculate_valuation(
                player_name=player.name,
                position=player.position,
                class_year=class_year,
                current_stats=current_stats,
                historical_stats=[],  # Would need to query multiple seasons
                conference=conference,
                school_name=team.school,
                school_data={
                    'athletic_revenue': 100_000_000,  # Default
                    'depth_chart_position': 'starter',
                },
                recruiting_rank=None,
                injury_history=None,
                social_media=None,
                character_data=None,
                eligibility_data={'years_remaining': 2}
            )

            # Format for dashboard
            valuation = {
                'player': player.name,
                'position': player.position,
                'team': team.school,
                'conference': conference,

                # Ensemble values
                'market_value': result.total_market_value,
                'player_value': result.player_value,
                'nil_potential': result.nil_potential,

                # Confidence
                'confidence_low': result.confidence_interval_low,
                'confidence_high': result.confidence_interval_high,

                # Pillar scores
                'production_score': result.production_value.weighted_score,
                'production_percentile': result.production_value.percentile,

                'predictive_score': result.predictive_performance.expected_next_year_score,
                'trajectory': result.predictive_performance.trajectory,
                'prediction_confidence': result.predictive_performance.confidence,

                'scarcity_multiplier': result.positional_scarcity.scarcity_multiplier,
                'scarcity_tier': result.positional_scarcity.position_tier.value,
                'expected_offers': result.expected_offers,

                'brand_score': result.brand_value.brand_score,
                'brand_tier': result.brand_value.tier,
                'nil_premium': result.brand_value.nil_premium,

                'risk_level': result.risk_adjustment.risk_level.value,
                'risk_multiplier': result.risk_adjustment.total_risk_multiplier,

                # Market context
                'market_position': result.market_position,
                'negotiation_leverage': result.negotiation_leverage,

                # Value drivers
                'value_drivers': result.value_drivers,
                'risk_factors': result.risk_factors,

                # Recommendations
                'fair_value_low': result.fair_value_range[0],
                'fair_value_high': result.fair_value_range[1],
                'suggested_ask': result.suggested_ask,
                'overpay_threshold': result.overpay_threshold,

                # Legacy fields for compatibility
                'performance_score': result.production_value.weighted_score,
                'war': result.player_value / 500000,  # Rough estimate
                'scheme_fit_score': 75,  # Default
                'efficiency': result.production_value.weighted_score * 0.9,
                'percentile': result.production_value.percentile,
            }

            valuations.append(valuation)
            print(f"✓ ${valuation['market_value']/1e6:.2f}M")

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            continue

    # Save to JSON
    output_dir = Path('outputs/valuations')
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f'ensemble_valuations_{sport}_2023.json'
    output_path = output_dir / filename

    output_data = {
        'generated_at': datetime.now().isoformat(),
        'sport': sport,
        'model': 'ensemble_6_pillar',
        'version': '1.0',
        'player_count': len(valuations),
        'valuations': valuations
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n{'='*80}")
    print(f"✓ Saved {len(valuations)} valuations to: {output_path}")
    print(f"{'='*80}\n")

    return valuations

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("CAV ENSEMBLE VALUATION GENERATOR")
    print("Comprehensive 6-Pillar Player Valuation System")
    print("="*80)

    # Generate for football (limit to 100 for testing)
    print("\nGenerating Football valuations...")
    football_valuations = generate_valuations_for_sport('football', limit=100)

    # Generate for basketball (limit to 50 for testing)
    # print("\nGenerating Basketball valuations...")
    # basketball_valuations = generate_valuations_for_sport('basketball', limit=50)

    print("\n" + "="*80)
    print("GENERATION COMPLETE")
    print("="*80)
    print(f"\nFootball: {len(football_valuations)} players valued")
    # print(f"Basketball: {len(basketball_valuations)} players valued")
    print("\nNext steps:")
    print("1. Review valuations in outputs/valuations/")
    print("2. Update dashboard to load ensemble valuations")
    print("3. Restart dashboard to see new values")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

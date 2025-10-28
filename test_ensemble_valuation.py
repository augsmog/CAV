"""
Test Suite for Ensemble Valuation System
Tests all six pillars and the combined ensemble model
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

from models.pillars.pillar_1_production_value import ProductionValueModel
from models.pillars.pillar_2_predictive_performance import PredictiveFuturePerformanceModel
from models.pillars.pillar_3_positional_scarcity import PositionalScarcityModel
from models.pillars.pillar_4_market_context import MarketContextModel
from models.pillars.pillar_5_brand_intangibles import BrandIntangiblesModel
from models.pillars.pillar_6_risk_adjustment import RiskAdjustmentModel
from models.pillars.ensemble_valuation import EnsembleValuationEngine
from models.pillars.output_formatter import ValuationOutputFormatter


def test_pillar_1_football_qb():
    """Test Pillar 1: Production Value for Football QB"""
    print("\n" + "="*80)
    print("TEST: Pillar 1 - Football QB Production Value")
    print("="*80)

    model = ProductionValueModel(sport='football')

    # Sample QB stats
    stats = {
        'epa_per_play': 0.35,
        'completion_pct': 68.5,
        'passing_touchdowns': 32,
        'interceptions': 6,
        'rushing_yards': 425,
        'rushing_touchdowns': 5,
        'third_down_conversion_rate': 0.48,
        'red_zone_td_pct': 0.65,
        'plays_70_plus': 8,
        'sack_rate': 0.04
    }

    result = model.calculate_football_production(
        stats=stats,
        position='QB',
        conference='SEC'
    )

    print(f"\nProduction Score: {result.production_score:.1f}/100")
    print(f"Weighted Score (conf adjusted): {result.weighted_score:.1f}/100")
    print(f"Percentile: {result.percentile:.0f}th")
    print(f"Conference: {result.metadata['conference']} (Multiplier: {result.metadata['conference_multiplier']:.2f}x)")
    print("\nComponent Scores:")
    for component, score in result.components.items():
        print(f"  {component}: {score:.1f}")

    assert result.production_score > 0, "Production score should be positive"
    assert result.weighted_score > 0, "Weighted score should be positive"
    print("\n[PASS] Pillar 1 (Football QB) test passed!")


def test_pillar_1_basketball():
    """Test Pillar 1: Production Value for Basketball"""
    print("\n" + "="*80)
    print("TEST: Pillar 1 - Basketball Production Value")
    print("="*80)

    model = ProductionValueModel(sport='basketball')

    stats = {
        'points_per_game': 18.5,
        'true_shooting_pct': 0.585,
        'assist_turnover_ratio': 2.8,
        'rebounds_per_game': 5.2,
        'player_efficiency_rating': 24.5,
        'box_plus_minus': 6.2,
        'win_shares_per_40': 0.185
    }

    result = model.calculate_basketball_production(
        stats=stats,
        position='PG',
        conference='Big Ten'
    )

    print(f"\nProduction Score: {result.production_score:.1f}/100")
    print(f"Weighted Score: {result.weighted_score:.1f}/100")
    print(f"Percentile: {result.percentile:.0f}th")
    print("\n[PASS] Pillar 1 (Basketball) test passed!")


def test_pillar_2_predictive():
    """Test Pillar 2: Predictive Performance"""
    print("\n" + "="*80)
    print("TEST: Pillar 2 - Predictive Performance")
    print("="*80)

    model = PredictiveFuturePerformanceModel(sport='football')

    current_stats = {'production_score': 78}
    historical_stats = [
        {'production_score': 78, 'season': 2023},
        {'production_score': 68, 'season': 2022},
        {'production_score': 55, 'season': 2021}
    ]

    result = model.predict_future_performance(
        current_stats=current_stats,
        historical_stats=historical_stats,
        position='QB',
        class_year='JR',
        recruiting_rank=120
    )

    print(f"\nCurrent Production: {current_stats['production_score']:.1f}")
    print(f"Next Year Projection: {result.expected_next_year_score:.1f}")
    print(f"Two-Year Projection: {result.two_year_projection:.1f}")
    print(f"Trajectory: {result.trajectory}")
    print(f"Confidence: {result.confidence * 100:.0f}%")
    print(f"Outcome Range: P10={result.range_p10:.1f}, P50={result.range_p50:.1f}, P90={result.range_p90:.1f}")
    print("\nFactors:")
    for factor, value in result.factors.items():
        print(f"  {factor}: {value}")

    print("\n[PASS] Pillar 2 test passed!")


def test_pillar_3_scarcity():
    """Test Pillar 3: Positional Scarcity"""
    print("\n" + "="*80)
    print("TEST: Pillar 3 - Positional Scarcity")
    print("="*80)

    model = PositionalScarcityModel(sport='football')

    portal_data = {
        'total_at_position': 45,
        'p4_quality_count': 12,
        'player_rank_at_position': 5
    }

    result = model.calculate_scarcity(
        position='QB',
        player_quality=82,
        portal_data=portal_data,
        market_timing='mid'
    )

    print(f"\nScarcity Multiplier: {result.scarcity_multiplier:.2f}x")
    print(f"Position Tier: {result.position_tier.value}")
    print(f"Market Percentile: {result.market_percentile:.0f}th")
    print(f"Supply Count: {result.supply_count}")
    print(f"Demand Estimate: {result.demand_estimate} schools")
    print(f"Expected Offers: {result.expected_offers}")
    print("\nFactors:")
    for factor, value in result.factors.items():
        print(f"  {factor}: {value}")

    print("\n[PASS] Pillar 3 test passed!")


def test_pillar_4_market_context():
    """Test Pillar 4: Market Context"""
    print("\n" + "="*80)
    print("TEST: Pillar 4 - Market Context")
    print("="*80)

    model = MarketContextModel(sport='football')

    school_data = {
        'playoff_appearances_5yr': 2,
        'win_pct_3yr': 0.785,
        'athletic_revenue': 185_000_000,
        'depth_chart_position': 'starter',
        'position_competition': 'light'
    }

    result = model.calculate_market_context(
        base_value=650000,
        school_name='Alabama',
        conference='SEC',
        position='QB',
        school_data=school_data
    )

    print(f"\nBase Value: ${result.context['base_value']:,.0f}")
    print(f"School-Adjusted Value: ${result.school_adjusted_value:,.0f}")
    print(f"Total Multiplier: {result.total_multiplier:.2f}x")
    print("\nMultiplier Breakdown:")
    print(f"  Conference: {result.conference_multiplier:.2f}x")
    print(f"  School Success: {result.school_success_factor:.2f}x")
    print(f"  Market Size: {result.market_size_factor:.2f}x")
    print(f"  Development: {result.development_premium:.2f}x")
    print(f"  Playing Time: {result.playing_time_probability:.2f}x")

    print("\n[PASS] Pillar 4 test passed!")


def test_pillar_5_brand():
    """Test Pillar 5: Brand & Intangibles"""
    print("\n" + "="*80)
    print("TEST: Pillar 5 - Brand & Intangibles")
    print("="*80)

    model = BrandIntangiblesModel(sport='football')

    social_media = {
        'instagram_followers': 125000,
        'twitter_followers': 45000,
        'tiktok_followers': 80000,
        'engagement_rate': 0.065,
        'monthly_growth_rate': 0.12
    }

    personal_attributes = {
        'charisma': 'high',
        'community_involvement': 'high',
        'academic_standing': 'honor_roll',
        'controversy_level': 'none'
    }

    result = model.calculate_brand_value(
        position='QB',
        social_media=social_media,
        performance_score=78,
        personal_attributes=personal_attributes
    )

    print(f"\nBrand Score: {result.brand_score:.1f}/100")
    print(f"Brand Tier: {result.tier}")
    print(f"NIL Premium: +{result.nil_premium * 100:.0f}%")
    print(f"Total Brand Value: ${result.total_brand_value:,.0f}")
    print("\nComponent Scores:")
    print(f"  Social Media: {result.social_media_score:.1f}/100")
    print(f"  Marketability: {result.marketability_score:.1f}/100")
    print(f"  Visibility: {result.visibility_score:.1f}/100")

    print("\n[PASS] Pillar 5 test passed!")


def test_pillar_6_risk():
    """Test Pillar 6: Risk Adjustment"""
    print("\n" + "="*80)
    print("TEST: Pillar 6 - Risk Adjustment")
    print("="*80)

    model = RiskAdjustmentModel(sport='football')

    injury_history = [
        {'seasons_ago': 1, 'severity': 'minor', 'injury_type': 'ankle sprain', 'games_missed': 2}
    ]

    performance_history = [
        {'production_score': 78},
        {'production_score': 68},
        {'production_score': 55}
    ]

    character_data = {
        'risk_tier': 'clean',
        'suspensions': 0,
        'transfers': 0,
        'academic_issues': False
    }

    eligibility_data = {
        'years_remaining': 2,
        'academic_standing': 'good'
    }

    result = model.calculate_risk_adjustment(
        position='QB',
        injury_history=injury_history,
        performance_history=performance_history,
        character_data=character_data,
        eligibility_data=eligibility_data
    )

    print(f"\nRisk Level: {result.risk_level.value.upper()}")
    print(f"Total Risk Multiplier: {result.total_risk_multiplier:.3f}")
    print(f"Total Discount: {(1 - result.total_risk_multiplier) * 100:.1f}%")
    print("\nDiscount Breakdown:")
    print(f"  Injury: {result.injury_discount * 100:.1f}%")
    print(f"  Performance: {result.performance_risk_discount * 100:.1f}%")
    print(f"  Character: {result.character_discount * 100:.1f}%")
    print(f"  Eligibility: {result.eligibility_discount * 100:.1f}%")
    print(f"  Fit: {result.fit_risk_discount * 100:.1f}%")
    print("\nRisk Factors:")
    for factor in result.risk_factors:
        print(f"  [WARN] {factor}")

    print("\n[PASS] Pillar 6 test passed!")


def test_ensemble_full_valuation():
    """Test Full Ensemble Valuation"""
    print("\n" + "="*80)
    print("TEST: Full Ensemble Valuation - Elite QB")
    print("="*80)

    engine = EnsembleValuationEngine(sport='football')

    # Elite QB transferring to top program
    current_stats = {
        'epa_per_play': 0.38,
        'completion_pct': 69.5,
        'passing_touchdowns': 35,
        'interceptions': 7,
        'rushing_yards': 520,
        'rushing_touchdowns': 6,
        'third_down_conversion_rate': 0.51,
        'red_zone_td_pct': 0.68,
        'plays_70_plus': 12,
        'sack_rate': 0.035
    }

    historical_stats = [
        {'production_score': 82, 'season': 2023},
        {'production_score': 72, 'season': 2022}
    ]

    school_data = {
        'playoff_appearances_5yr': 3,
        'win_pct_3yr': 0.815,
        'athletic_revenue': 200_000_000,
        'depth_chart_position': 'starter',
        'position_competition': 'none',
        'ranked_weeks_per_year': 14
    }

    social_media = {
        'instagram_followers': 185000,
        'twitter_followers': 78000,
        'tiktok_followers': 120000,
        'engagement_rate': 0.075,
        'monthly_growth_rate': 0.15
    }

    portal_data = {
        'total_at_position': 42,
        'p4_quality_count': 14,
        'player_rank_at_position': 3
    }

    injury_history = [
        {'seasons_ago': 2, 'severity': 'minor', 'injury_type': 'shoulder', 'games_missed': 1}
    ]

    character_data = {
        'risk_tier': 'clean',
        'suspensions': 0,
        'transfers': 0,
        'academic_issues': False
    }

    eligibility_data = {
        'years_remaining': 2,
        'academic_standing': 'honor_roll'
    }

    result = engine.calculate_valuation(
        player_name="John Smith",
        position='QB',
        class_year='JR',
        current_stats=current_stats,
        historical_stats=historical_stats,
        conference='SEC',
        school_name='Georgia',
        school_data=school_data,
        portal_data=portal_data,
        recruiting_rank=85,
        injury_history=injury_history,
        social_media=social_media,
        character_data=character_data,
        eligibility_data=eligibility_data
    )

    # Print formatted output for schools
    print(ValuationOutputFormatter.format_for_schools(result, "John Smith"))

    # Print formatted output for players
    print("\n" + "="*80)
    print("PLAYER/AGENT VIEW")
    print("="*80)
    print(ValuationOutputFormatter.format_for_players(result, "John Smith"))

    # Compact summary
    print("\n" + "="*80)
    print("COMPACT SUMMARY")
    print("="*80)
    print(ValuationOutputFormatter.format_compact_summary(result, "John Smith"))

    # Assertions
    assert result.total_market_value > 0, "Total market value should be positive"
    assert result.player_value > 0, "Player value should be positive"
    assert result.nil_potential > 0, "NIL potential should be positive"
    assert len(result.value_drivers) > 0, "Should have value drivers"
    assert result.expected_offers > 0, "Should have expected offers"

    print("\n[PASS] Full Ensemble test passed!")


def test_basketball_ensemble():
    """Test Basketball Ensemble Valuation"""
    print("\n" + "="*80)
    print("TEST: Basketball Ensemble Valuation - Elite PG")
    print("="*80)

    engine = EnsembleValuationEngine(sport='basketball')

    current_stats = {
        'points_per_game': 19.8,
        'true_shooting_pct': 0.615,
        'assist_turnover_ratio': 3.2,
        'rebounds_per_game': 4.8,
        'player_efficiency_rating': 26.5,
        'box_plus_minus': 7.8,
        'win_shares_per_40': 0.215
    }

    historical_stats = [
        {'production_score': 85, 'season': 2023},
        {'production_score': 68, 'season': 2022}
    ]

    school_data = {
        'tournament_appearances_5yr': 5,
        'sweet_16_runs_5yr': 3,
        'win_pct_3yr': 0.742,
        'athletic_revenue': 135_000_000
    }

    social_media = {
        'instagram_followers': 95000,
        'twitter_followers': 42000,
        'tiktok_followers': 68000,
        'engagement_rate': 0.058
    }

    result = engine.calculate_valuation(
        player_name="Mike Johnson",
        position='PG',
        class_year='JR',
        current_stats=current_stats,
        historical_stats=historical_stats,
        conference='Big Ten',
        school_name='Michigan State',
        school_data=school_data,
        recruiting_rank=45,
        social_media=social_media
    )

    print(ValuationOutputFormatter.format_for_schools(result, "Mike Johnson"))

    assert result.total_market_value > 0, "Total market value should be positive"
    print("\n[PASS] Basketball Ensemble test passed!")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ENSEMBLE VALUATION SYSTEM - TEST SUITE")
    print("="*80)

    try:
        # Test individual pillars
        test_pillar_1_football_qb()
        test_pillar_1_basketball()
        test_pillar_2_predictive()
        test_pillar_3_scarcity()
        test_pillar_4_market_context()
        test_pillar_5_brand()
        test_pillar_6_risk()

        # Test full ensemble
        test_ensemble_full_valuation()
        test_basketball_ensemble()

        print("\n" + "="*80)
        print("ALL TESTS PASSED! [PASS]")
        print("="*80)

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

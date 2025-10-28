"""
Output Formatter for Ensemble Valuation Results
Provides comprehensive, user-friendly output with explainability
"""

from typing import Dict, Any, TYPE_CHECKING
from dataclasses import asdict
import json

if TYPE_CHECKING:
    from .ensemble_valuation import EnsembleValuationResult


class ValuationOutputFormatter:
    """
    Formats ensemble valuation results for different audiences
    - Schools/Recruiters
    - Players/Agents
    - JSON export
    - Dashboard display
    """

    @staticmethod
    def format_for_schools(result: 'EnsembleValuationResult', player_name: str) -> str:
        """
        Format output for schools/recruiters

        Returns:
            Formatted string output
        """
        output = []
        output.append("=" * 80)
        output.append(f"PLAYER VALUATION REPORT - {player_name.upper()}")
        output.append("=" * 80)
        output.append("")

        # === MARKET VALUE SUMMARY ===
        output.append("MARKET VALUE ESTIMATE")
        output.append("-" * 40)
        output.append(f"Total Market Value:     ${result.total_market_value:,.0f}")
        output.append(f"  Player Value:         ${result.player_value:,.0f}")
        output.append(f"  NIL Potential:        ${result.nil_potential:,.0f}")
        output.append("")
        output.append(f"Confidence Range (80%): ${result.confidence_interval_low:,.0f} - ${result.confidence_interval_high:,.0f}")
        output.append("")

        # === VALUE BREAKDOWN ===
        output.append("VALUE DRIVERS")
        output.append("-" * 40)
        for driver in result.value_drivers:
            output.append(f"  + {driver}")
        output.append("")

        # === RISK FACTORS ===
        if result.risk_factors:
            output.append("RISK FACTORS")
            output.append("-" * 40)
            for risk in result.risk_factors:
                output.append(f"  ! {risk}")
            output.append(f"\nRisk Level: {result.risk_adjustment.risk_level.value.upper()}")
            output.append(f"Risk Discount: {(1 - result.risk_adjustment.total_risk_multiplier) * 100:.1f}%")
            output.append("")

        # === PERFORMANCE ANALYSIS ===
        output.append("PERFORMANCE ANALYSIS")
        output.append("-" * 40)
        output.append(f"Current Production Score:  {result.production_value.weighted_score:.1f}/100")
        output.append(f"Performance Percentile:    {result.production_value.percentile:.0f}th")
        output.append(f"Next Year Projection:      {result.predictive_performance.expected_next_year_score:.1f}/100")
        output.append(f"Trajectory:                {result.predictive_performance.trajectory.capitalize()}")
        output.append(f"Prediction Confidence:     {result.predictive_performance.confidence * 100:.0f}%")
        output.append("")

        # === MARKET CONTEXT ===
        output.append("MARKET CONTEXT")
        output.append("-" * 40)
        output.append(f"Position:                  {result.market_position}")
        output.append(f"Expected Offers:           {result.expected_offers}")
        output.append(f"Positional Scarcity:       {result.positional_scarcity.position_tier.value.capitalize()}")
        output.append(f"Negotiation Leverage:      {result.negotiation_leverage}")
        if result.market_context:
            output.append(f"Conference Multiplier:     {result.market_context.conference_multiplier:.2f}x")
            output.append(f"School Success Factor:     {result.market_context.school_success_factor:.2f}x")
        output.append("")

        # === RECOMMENDATIONS ===
        output.append("RECRUITING RECOMMENDATIONS")
        output.append("-" * 40)
        output.append(f"Fair Value Range:          ${result.fair_value_range[0]:,.0f} - ${result.fair_value_range[1]:,.0f}")
        output.append(f"Overpay Threshold:         >${result.overpay_threshold:,.0f}")
        output.append("")
        output.append("Investment Assessment:")
        if result.risk_adjustment.risk_level.value in ['minimal', 'low']:
            output.append("  + LOW RISK - Recommended investment")
        elif result.risk_adjustment.risk_level.value == 'moderate':
            output.append("  ! MODERATE RISK - Proceed with caution")
        else:
            output.append("  X HIGH RISK - Significant concerns identified")
        output.append("")

        # === COMPARABLE PLAYERS ===
        if result.comparable_players:
            output.append("COMPARABLE PLAYERS")
            output.append("-" * 40)
            for comp in result.comparable_players[:3]:
                output.append(f"  - {comp.get('name', 'Unknown')} (Similarity: {comp.get('similarity_score', 0) * 100:.0f}%)")
                output.append(f"    {comp.get('trajectory', 'N/A')}")
            output.append("")

        output.append("=" * 80)

        return "\n".join(output)

    @staticmethod
    def format_for_players(result: 'EnsembleValuationResult', player_name: str) -> str:
        """
        Format output for players/agents

        Returns:
            Formatted string output
        """
        output = []
        output.append("=" * 80)
        output.append(f"YOUR MARKET VALUE REPORT - {player_name.upper()}")
        output.append("=" * 80)
        output.append("")

        # === YOUR VALUE ===
        output.append("YOUR ESTIMATED MARKET VALUE")
        output.append("-" * 40)
        output.append(f"Total Opportunity Value:   ${result.total_market_value:,.0f}")
        output.append(f"  NIL Earning Potential:   ${result.nil_potential:,.0f}/year")
        output.append(f"  School Investment Value: ${result.player_value:,.0f}")
        output.append("")
        output.append(f"Value Range (80% confidence): ${result.confidence_interval_low:,.0f} - ${result.confidence_interval_high:,.0f}")
        output.append("")

        # === MARKET POSITION ===
        output.append("YOUR MARKET POSITION")
        output.append("-" * 40)
        output.append(f"Market Ranking:            {result.market_position}")
        output.append(f"Expected High-Major Offers: {result.expected_offers}")
        output.append(f"Negotiation Leverage:      {result.negotiation_leverage}")
        output.append("")

        # === STRENGTHS ===
        output.append("YOUR KEY STRENGTHS")
        output.append("-" * 40)
        for driver in result.value_drivers:
            output.append(f"  + {driver}")
        output.append("")

        # === BRAND VALUE ===
        output.append("YOUR BRAND VALUE")
        output.append("-" * 40)
        output.append(f"Brand Score:               {result.brand_value.brand_score:.0f}/100")
        output.append(f"Brand Tier:                {result.brand_value.tier.replace('_', ' ').title()}")
        output.append(f"Social Media Score:        {result.brand_value.social_media_score:.0f}/100")
        output.append(f"NIL Premium:               +{result.brand_value.nil_premium * 100:.0f}%")
        output.append("")

        # === NEGOTIATION GUIDANCE ===
        output.append("NEGOTIATION GUIDANCE")
        output.append("-" * 40)
        output.append(f"Suggested Opening Ask:     ${result.suggested_ask:,.0f}")
        output.append(f"Fair Deal Range:           ${result.fair_value_range[0]:,.0f} - ${result.fair_value_range[1]:,.0f}")
        output.append(f"Walk-Away Number:          ${result.walk_away_number:,.0f}")
        output.append("")
        output.append("Negotiation Tips:")
        if result.negotiation_leverage in ['Very High', 'High']:
            output.append("  - You have strong leverage - multiple schools likely competing")
            output.append("  - Don't settle quickly - let market develop")
            output.append("  - Consider holding out for best offer")
        elif result.negotiation_leverage == 'Moderate':
            output.append("  - Moderate leverage - good options available")
            output.append("  - Balance best offer with fit and development")
            output.append("  - Don't wait too long - market may shift")
        else:
            output.append("  - Limited leverage - focus on best fit")
            output.append("  - Emphasize development and opportunity")
            output.append("  - Be realistic about market position")
        output.append("")

        # === AREAS TO IMPROVE ===
        if result.risk_factors:
            output.append("AREAS TO ADDRESS")
            output.append("-" * 40)
            for risk in result.risk_factors[:5]:
                output.append(f"  - {risk}")
            output.append("")

        # === TRAJECTORY ===
        output.append("PERFORMANCE TRAJECTORY")
        output.append("-" * 40)
        output.append(f"Current Performance:       {result.production_value.weighted_score:.0f}/100")
        output.append(f"Projected Next Year:       {result.predictive_performance.expected_next_year_score:.0f}/100")
        output.append(f"2-Year Projection:         {result.predictive_performance.two_year_projection:.0f}/100")
        output.append(f"Trend:                     {result.predictive_performance.trajectory.capitalize()}")
        output.append("")

        output.append("=" * 80)

        return "\n".join(output)

    @staticmethod
    def format_to_json(result: 'EnsembleValuationResult', player_name: str) -> str:
        """
        Export to JSON format

        Returns:
            JSON string
        """
        output_dict = {
            'player_name': player_name,
            'valuation': {
                'total_market_value': result.total_market_value,
                'player_value': result.player_value,
                'nil_potential': result.nil_potential,
                'confidence_interval': {
                    'low': result.confidence_interval_low,
                    'high': result.confidence_interval_high
                },
                'fair_value_range': {
                    'low': result.fair_value_range[0],
                    'high': result.fair_value_range[1]
                },
                'overpay_threshold': result.overpay_threshold,
                'suggested_ask': result.suggested_ask,
                'walk_away_number': result.walk_away_number
            },
            'performance': {
                'current_score': result.production_value.weighted_score,
                'percentile': result.production_value.percentile,
                'next_year_projection': result.predictive_performance.expected_next_year_score,
                'two_year_projection': result.predictive_performance.two_year_projection,
                'trajectory': result.predictive_performance.trajectory,
                'confidence': result.predictive_performance.confidence
            },
            'market_context': {
                'position_ranking': result.market_position,
                'expected_offers': result.expected_offers,
                'negotiation_leverage': result.negotiation_leverage,
                'scarcity_tier': result.positional_scarcity.position_tier.value,
                'scarcity_multiplier': result.positional_scarcity.scarcity_multiplier
            },
            'brand': {
                'brand_score': result.brand_value.brand_score,
                'brand_tier': result.brand_value.tier,
                'social_media_score': result.brand_value.social_media_score,
                'nil_premium': result.brand_value.nil_premium
            },
            'risk': {
                'risk_level': result.risk_adjustment.risk_level.value,
                'total_multiplier': result.risk_adjustment.total_risk_multiplier,
                'injury_discount': result.risk_adjustment.injury_discount,
                'character_discount': result.risk_adjustment.character_discount,
                'risk_factors': result.risk_factors
            },
            'value_drivers': result.value_drivers,
            'comparable_players': result.comparable_players
        }

        return json.dumps(output_dict, indent=2)

    @staticmethod
    def format_compact_summary(result: 'EnsembleValuationResult', player_name: str) -> str:
        """
        Compact one-line summary for dashboard/tables

        Returns:
            Compact summary string
        """
        return (
            f"{player_name} | "
            f"Value: ${result.total_market_value:,.0f} | "
            f"Position: {result.market_position} | "
            f"Offers: {result.expected_offers} | "
            f"Risk: {result.risk_adjustment.risk_level.value.capitalize()}"
        )

    @staticmethod
    def format_detailed_breakdown(result: 'EnsembleValuationResult') -> Dict[str, Any]:
        """
        Detailed breakdown for dashboard display

        Returns:
            Dictionary with all components
        """
        return {
            'summary': {
                'total_market_value': result.total_market_value,
                'player_value': result.player_value,
                'nil_potential': result.nil_potential,
                'confidence_range': (result.confidence_interval_low, result.confidence_interval_high)
            },
            'pillar_scores': {
                'production': {
                    'score': result.production_value.weighted_score,
                    'percentile': result.production_value.percentile,
                    'components': result.production_value.components
                },
                'predictive': {
                    'next_year': result.predictive_performance.expected_next_year_score,
                    'two_year': result.predictive_performance.two_year_projection,
                    'trajectory': result.predictive_performance.trajectory,
                    'confidence': result.predictive_performance.confidence
                },
                'scarcity': {
                    'multiplier': result.positional_scarcity.scarcity_multiplier,
                    'tier': result.positional_scarcity.position_tier.value,
                    'market_percentile': result.positional_scarcity.market_percentile,
                    'expected_offers': result.expected_offers
                },
                'market': {
                    'conference_multiplier': result.market_context.conference_multiplier if result.market_context else 1.0,
                    'school_success': result.market_context.school_success_factor if result.market_context else 1.0,
                    'total_multiplier': result.market_context.total_multiplier if result.market_context else 1.0
                } if result.market_context else None,
                'brand': {
                    'brand_score': result.brand_value.brand_score,
                    'tier': result.brand_value.tier,
                    'social_media': result.brand_value.social_media_score,
                    'nil_premium': result.brand_value.nil_premium
                },
                'risk': {
                    'risk_level': result.risk_adjustment.risk_level.value,
                    'multiplier': result.risk_adjustment.total_risk_multiplier,
                    'discount_pct': (1 - result.risk_adjustment.total_risk_multiplier) * 100
                }
            },
            'value_drivers': result.value_drivers,
            'risk_factors': result.risk_factors,
            'recommendations': {
                'fair_value_range': result.fair_value_range,
                'suggested_ask': result.suggested_ask,
                'walk_away': result.walk_away_number,
                'overpay_threshold': result.overpay_threshold,
                'negotiation_leverage': result.negotiation_leverage
            }
        }

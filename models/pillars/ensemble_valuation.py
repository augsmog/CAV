"""
Ensemble Valuation Model
Combines all six pillars into comprehensive player market value
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .pillar_1_production_value import ProductionValueModel, ProductionValueResult
from .pillar_2_predictive_performance import PredictiveFuturePerformanceModel, PredictiveResult
from .pillar_3_positional_scarcity import PositionalScarcityModel, ScarcityResult
from .pillar_4_market_context import MarketContextModel, MarketContextResult
from .pillar_5_brand_intangibles import BrandIntangiblesModel, BrandValueResult
from .pillar_6_risk_adjustment import RiskAdjustmentModel, RiskAdjustmentResult


@dataclass
class EnsembleValuationResult:
    """Comprehensive valuation result from ensemble model"""
    # Final values
    total_market_value: float
    player_value: float  # What schools pay
    nil_potential: float  # What players earn from NIL
    confidence_interval_low: float
    confidence_interval_high: float

    # Pillar results
    production_value: ProductionValueResult
    predictive_performance: PredictiveResult
    positional_scarcity: ScarcityResult
    market_context: MarketContextResult
    brand_value: BrandValueResult
    risk_adjustment: RiskAdjustmentResult

    # Value drivers (explainability)
    value_drivers: List[str]
    risk_factors: List[str]
    comparable_players: List[Dict[str, Any]]

    # Market context
    expected_offers: int
    market_position: str  # "Top 5 QB in portal", etc.
    negotiation_leverage: str  # "High", "Moderate", "Low"

    # Recommendations
    fair_value_range: tuple  # (low, high)
    overpay_threshold: float
    suggested_ask: float  # For players/agents
    walk_away_number: float  # Minimum acceptable


class EnsembleValuationEngine:
    """
    Master valuation engine combining all six pillars

    Weighting structure (configurable by sport/position):
    - Production Value: 30-35%
    - Predictive Performance: 25-30%
    - Positional Scarcity: 15%
    - Market Context: 10-15%
    - Brand/Intangibles: 10%
    - Risk Adjustment: Applied as multiplier
    """

    # Sport-specific base weights
    FOOTBALL_WEIGHTS = {
        'production': 0.35,
        'predictive': 0.25,
        'scarcity': 0.15,
        'market': 0.10,
        'brand': 0.10,
        'risk': 0.05  # Applied as multiplier, not additive
    }

    BASKETBALL_WEIGHTS = {
        'production': 0.30,
        'predictive': 0.25,
        'scarcity': 0.15,
        'market': 0.15,
        'brand': 0.10,
        'risk': 0.05
    }

    # Player type adjustments
    PLAYER_TYPE_ADJUSTMENTS = {
        'established_star': {
            'production': 0.40,
            'predictive': 0.20,
            'scarcity': 0.15,
            'market': 0.10,
            'brand': 0.10,
            'risk': 0.05
        },
        'young_prospect': {
            'production': 0.25,
            'predictive': 0.35,
            'scarcity': 0.15,
            'market': 0.10,
            'brand': 0.10,
            'risk': 0.05
        },
        'influencer_athlete': {
            'production': 0.30,
            'predictive': 0.20,
            'scarcity': 0.10,
            'market': 0.10,
            'brand': 0.25,
            'risk': 0.05
        }
    }

    def __init__(self, sport: str = 'football'):
        """
        Initialize ensemble valuation engine

        Args:
            sport: 'football' or 'basketball'
        """
        self.sport = sport.lower()

        # Initialize all pillar models
        self.production_model = ProductionValueModel(sport)
        self.predictive_model = PredictiveFuturePerformanceModel(sport)
        self.scarcity_model = PositionalScarcityModel(sport)
        self.market_model = MarketContextModel(sport)
        self.brand_model = BrandIntangiblesModel(sport)
        self.risk_model = RiskAdjustmentModel(sport)

        # Set base weights
        self.weights = (
            self.FOOTBALL_WEIGHTS if sport == 'football'
            else self.BASKETBALL_WEIGHTS
        )

    def calculate_valuation(
        self,
        # Player basic info
        player_name: str,
        position: str,
        class_year: str,

        # Performance data
        current_stats: Dict[str, Any],
        historical_stats: List[Dict[str, Any]],
        conference: str,

        # Market data
        school_name: Optional[str] = None,
        school_data: Optional[Dict[str, Any]] = None,
        portal_data: Optional[Dict[str, Any]] = None,

        # Additional factors
        recruiting_rank: Optional[int] = None,
        injury_history: Optional[List[Dict[str, Any]]] = None,
        social_media: Optional[Dict[str, Any]] = None,
        character_data: Optional[Dict[str, Any]] = None,
        eligibility_data: Optional[Dict[str, Any]] = None,

        # Overrides
        player_type: Optional[str] = None,  # 'established_star', 'young_prospect', 'influencer_athlete'
        custom_weights: Optional[Dict[str, float]] = None
    ) -> EnsembleValuationResult:
        """
        Calculate comprehensive player valuation

        Returns:
            EnsembleValuationResult with complete analysis
        """
        # Adjust weights based on player type if specified
        weights = self._determine_weights(player_type, custom_weights)

        # ========== PILLAR 1: Production Value ==========
        production_result = self.production_model.calculate_football_production(
            stats=current_stats,
            position=position,
            conference=conference
        ) if self.sport == 'football' else self.production_model.calculate_basketball_production(
            stats=current_stats,
            position=position,
            conference=conference
        )

        # ========== PILLAR 2: Predictive Performance ==========
        predictive_result = self.predictive_model.predict_future_performance(
            current_stats={'production_score': production_result.weighted_score, **current_stats},
            historical_stats=historical_stats,
            position=position,
            class_year=class_year,
            recruiting_rank=recruiting_rank,
            injury_history=injury_history
        )

        # ========== PILLAR 3: Positional Scarcity ==========
        scarcity_result = self.scarcity_model.calculate_scarcity(
            position=position,
            player_quality=production_result.weighted_score,
            portal_data=portal_data
        )

        # ========== PILLAR 4: Market Context ==========
        # Calculate base value first (needed for market context)
        base_value = self._calculate_base_value(
            production_result, predictive_result, scarcity_result, weights
        )

        market_result = self.market_model.calculate_market_context(
            base_value=base_value,
            school_name=school_name or "Unknown",
            conference=conference,
            position=position,
            school_data=school_data
        ) if school_name else None

        # ========== PILLAR 5: Brand/Intangibles ==========
        brand_result = self.brand_model.calculate_brand_value(
            position=position,
            social_media=social_media,
            performance_score=production_result.weighted_score,
            school_data=school_data
        )

        # ========== PILLAR 6: Risk Adjustment ==========
        risk_result = self.risk_model.calculate_risk_adjustment(
            position=position,
            injury_history=injury_history,
            performance_history=historical_stats,
            character_data=character_data,
            eligibility_data=eligibility_data
        )

        # ========== COMBINE PILLARS ==========
        total_value, player_value, nil_value = self._combine_pillars(
            production_result=production_result,
            predictive_result=predictive_result,
            scarcity_result=scarcity_result,
            market_result=market_result,
            brand_result=brand_result,
            risk_result=risk_result,
            weights=weights
        )

        # Calculate confidence intervals
        confidence = predictive_result.confidence
        ci_low, ci_high = self._calculate_confidence_intervals(
            total_value, confidence, risk_result
        )

        # Generate value drivers and explainability
        value_drivers = self._generate_value_drivers(
            production_result, predictive_result, scarcity_result,
            market_result, brand_result, risk_result
        )

        # Market positioning
        market_position = self._determine_market_position(
            position, scarcity_result, production_result
        )

        negotiation_leverage = self._determine_leverage(
            scarcity_result, predictive_result, risk_result
        )

        # Recommendations
        fair_range = self._calculate_fair_value_range(total_value, ci_low, ci_high)
        overpay = total_value * 1.30  # 30% over = overpay
        suggested_ask = total_value * 1.10  # Start 10% higher
        walk_away = total_value * 0.75  # Don't accept less than 75% of fair value

        return EnsembleValuationResult(
            total_market_value=total_value,
            player_value=player_value,
            nil_potential=nil_value,
            confidence_interval_low=ci_low,
            confidence_interval_high=ci_high,
            production_value=production_result,
            predictive_performance=predictive_result,
            positional_scarcity=scarcity_result,
            market_context=market_result,
            brand_value=brand_result,
            risk_adjustment=risk_result,
            value_drivers=value_drivers,
            risk_factors=risk_result.risk_factors,
            comparable_players=predictive_result.comparable_players,
            expected_offers=scarcity_result.expected_offers,
            market_position=market_position,
            negotiation_leverage=negotiation_leverage,
            fair_value_range=fair_range,
            overpay_threshold=overpay,
            suggested_ask=suggested_ask,
            walk_away_number=walk_away
        )

    def _determine_weights(
        self,
        player_type: Optional[str],
        custom_weights: Optional[Dict[str, float]]
    ) -> Dict[str, float]:
        """Determine weights based on player type or custom input"""
        if custom_weights:
            return custom_weights

        if player_type and player_type in self.PLAYER_TYPE_ADJUSTMENTS:
            return self.PLAYER_TYPE_ADJUSTMENTS[player_type]

        return self.weights

    def _calculate_base_value(
        self,
        production: ProductionValueResult,
        predictive: PredictiveResult,
        scarcity: ScarcityResult,
        weights: Dict[str, float]
    ) -> float:
        """
        Calculate base value before market/risk adjustments

        Combines production, predictive, and scarcity
        """
        # Normalize scores to dollar values
        production_score = production.weighted_score
        predictive_score = predictive.expected_next_year_score

        # Average of current and projected
        combined_score = (
            production_score * weights['production'] +
            predictive_score * weights['predictive']
        ) / (weights['production'] + weights['predictive'])

        # Convert to dollars (position-specific)
        if self.sport == 'football':
            # Base conversion: 100 score = $1.5M for QB, $500K for others
            position_multipliers = {
                'QB': 15000,
                'EDGE': 10000,
                'LT': 9000,
                'CB': 8000,
                'WR': 7000,
                'OT': 7000,
                'DL': 7000,
                'S': 6000,
                'TE': 6000,
                'LB': 6000,
                'RB': 5000,
                'OG': 4000,
                'C': 4000,
                'K': 2000,
                'P': 2000
            }
        else:
            # Basketball
            position_multipliers = {
                'PG': 8000,
                'C': 7500,
                'SG': 7000,
                'SF': 7000,
                'PF': 6500
            }

        position_norm = self._normalize_position(production.metadata['position'])
        multiplier = position_multipliers.get(position_norm, 6000)

        base_value = combined_score * multiplier

        # Apply scarcity multiplier
        base_value *= scarcity.scarcity_multiplier

        return base_value

    def _combine_pillars(
        self,
        production_result: ProductionValueResult,
        predictive_result: PredictiveResult,
        scarcity_result: ScarcityResult,
        market_result: Optional[MarketContextResult],
        brand_result: BrandValueResult,
        risk_result: RiskAdjustmentResult,
        weights: Dict[str, float]
    ) -> tuple:
        """
        Combine all pillars into final valuation

        Returns:
            (total_value, player_value, nil_value)
        """
        # Calculate base player value (what schools pay)
        base_value = self._calculate_base_value(
            production_result, predictive_result, scarcity_result, weights
        )

        # Apply market context if available
        if market_result:
            player_value = market_result.school_adjusted_value
        else:
            player_value = base_value

        # Apply risk adjustment
        player_value *= risk_result.total_risk_multiplier

        # Calculate NIL potential (separate stream)
        nil_base = brand_result.total_brand_value
        nil_value = nil_base * (1 + brand_result.nil_premium)

        # Also factor in brand premium on player value
        player_value *= (1 + brand_result.nil_premium * 0.20)  # 20% of brand premium

        # Total market value = player value + NIL potential
        total_value = player_value + nil_value

        return (total_value, player_value, nil_value)

    def _calculate_confidence_intervals(
        self,
        total_value: float,
        confidence: float,
        risk_result: RiskAdjustmentResult
    ) -> tuple:
        """
        Calculate confidence intervals (P10, P90)

        Returns:
            (low, high)
        """
        # Lower confidence = wider range
        spread_pct = (1 - confidence) * 0.35  # Up to 35% spread

        # Risk increases spread
        risk_spread = (1 - risk_result.total_risk_multiplier) * 0.15

        total_spread = spread_pct + risk_spread

        low = total_value * (1 - total_spread)
        high = total_value * (1 + total_spread)

        return (low, high)

    def _generate_value_drivers(
        self,
        production: ProductionValueResult,
        predictive: PredictiveResult,
        scarcity: ScarcityResult,
        market: Optional[MarketContextResult],
        brand: BrandValueResult,
        risk: RiskAdjustmentResult
    ) -> List[str]:
        """Generate human-readable value drivers"""
        drivers = []

        # Production
        if production.percentile >= 90:
            drivers.append(f"Elite production ({int(production.percentile)}th percentile)")
        elif production.percentile >= 75:
            drivers.append(f"Strong production ({int(production.percentile)}th percentile)")

        # Trajectory
        if predictive.trajectory == 'improving':
            drivers.append("Improving trajectory (upward trend)")
        elif predictive.trajectory == 'peaking':
            drivers.append("Peak performance expected")

        # Scarcity
        if scarcity.scarcity_multiplier >= 1.5:
            drivers.append(f"High positional scarcity ({scarcity.position_tier.value})")

        if scarcity.expected_offers >= 15:
            drivers.append(f"High demand (est. {scarcity.expected_offers}+ offers)")

        # Brand
        if brand.tier in ['mega-influencer', 'strong']:
            drivers.append(f"Strong brand ({brand.tier})")

        if brand.social_media_score >= 75:
            drivers.append(f"High social media presence")

        # Market
        if market:
            if market.conference_multiplier >= 1.25:
                drivers.append("Elite conference premium")
            if market.development_premium > 1.10:
                drivers.append("Development program premium")

        return drivers

    def _determine_market_position(
        self,
        position: str,
        scarcity: ScarcityResult,
        production: ProductionValueResult
    ) -> str:
        """Determine market position string"""
        percentile = scarcity.market_percentile

        if percentile >= 95:
            rank = "Top 5"
        elif percentile >= 90:
            rank = "Top 10"
        elif percentile >= 80:
            rank = "Top 20"
        elif percentile >= 70:
            rank = "Top 30"
        elif percentile >= 50:
            rank = "Top 50"
        else:
            rank = "Mid-tier"

        return f"{rank} {position} in portal"

    def _determine_leverage(
        self,
        scarcity: ScarcityResult,
        predictive: PredictiveResult,
        risk: RiskAdjustmentResult
    ) -> str:
        """Determine negotiation leverage"""
        # High scarcity + low risk = high leverage
        if scarcity.scarcity_multiplier >= 1.5 and risk.risk_level.value in ['minimal', 'low']:
            if scarcity.expected_offers >= 15:
                return "Very High"
            return "High"
        elif scarcity.scarcity_multiplier >= 1.2 and risk.risk_level.value != 'high':
            return "Moderate-High"
        elif risk.risk_level.value in ['high', 'severe']:
            return "Low"
        else:
            return "Moderate"

    def _calculate_fair_value_range(
        self, total_value: float, ci_low: float, ci_high: float
    ) -> tuple:
        """Calculate fair value range (tighter than confidence interval)"""
        # Fair value = within 15% of estimate
        low = total_value * 0.85
        high = total_value * 1.15

        return (low, high)

    def _normalize_position(self, position: str) -> str:
        """Normalize position to standard key"""
        position = position.upper()

        football_map = {
            'QB': 'QB',
            'RB': 'RB', 'FB': 'RB',
            'WR': 'WR',
            'TE': 'TE',
            'LT': 'LT', 'RT': 'OT',
            'OT': 'OT',
            'LG': 'OG', 'RG': 'OG', 'OG': 'OG',
            'C': 'C',
            'DE': 'EDGE', 'EDGE': 'EDGE',
            'DT': 'DL', 'DL': 'DL',
            'LB': 'LB', 'ILB': 'LB', 'OLB': 'LB',
            'CB': 'CB',
            'S': 'S', 'FS': 'S', 'SS': 'S',
            'K': 'K',
            'P': 'P'
        }

        basketball_map = {
            'PG': 'PG',
            'SG': 'SG',
            'SF': 'SF',
            'PF': 'PF',
            'C': 'C'
        }

        if self.sport == 'football':
            return football_map.get(position, 'WR')
        else:
            return basketball_map.get(position, 'SF')

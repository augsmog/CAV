"""
Pillar 2: Predictive Future Performance Model
Forecasts expected value trajectory and future production
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class PredictiveResult:
    """Result from predictive performance model"""
    expected_next_year_score: float  # Predicted production score
    two_year_projection: float  # 2-year outlook
    trajectory: str  # 'improving', 'peaking', 'declining', 'stable'
    confidence: float  # 0-1 confidence in prediction
    range_p10: float  # 10th percentile outcome
    range_p50: float  # 50th percentile (median)
    range_p90: float  # 90th percentile outcome
    factors: Dict[str, Any]  # Contributing factors
    comparable_players: List[Dict[str, Any]]  # Similar historical players


class PredictiveFuturePerformanceModel:
    """
    Predicts future performance trajectory for college athletes
    Uses age curves, statistical trends, and comparable player analysis
    """

    # Typical development patterns by position and class year
    FOOTBALL_AGE_CURVES = {
        'QB': {
            'FR': 0.60,  # Freshmen typically at 60% of peak
            'SO': 0.75,
            'JR': 0.95,  # Peak years
            'SR': 1.00,
            'R-SR': 0.98  # Slight decline for 5th year
        },
        'RB': {
            'FR': 0.70,
            'SO': 0.90,
            'JR': 1.00,  # Peak early
            'SR': 0.95,  # Wear and tear
            'R-SR': 0.88
        },
        'WR': {
            'FR': 0.65,
            'SO': 0.80,
            'JR': 0.95,
            'SR': 1.00,
            'R-SR': 0.98
        },
        'OL': {
            'FR': 0.50,  # Longer development curve
            'SO': 0.70,
            'JR': 0.90,
            'SR': 1.00,
            'R-SR': 1.00  # Maintain strength
        },
        'DL': {
            'FR': 0.60,
            'SO': 0.80,
            'JR': 0.95,
            'SR': 1.00,
            'R-SR': 0.98
        },
        'LB': {
            'FR': 0.60,
            'SO': 0.75,
            'JR': 0.95,
            'SR': 1.00,
            'R-SR': 0.98
        },
        'DB': {
            'FR': 0.65,
            'SO': 0.80,
            'JR': 0.95,
            'SR': 1.00,
            'R-SR': 0.98
        }
    }

    BASKETBALL_AGE_CURVES = {
        'PG': {
            'FR': 0.65,
            'SO': 0.85,
            'JR': 0.98,
            'SR': 1.00,
            'R-SR': 0.98
        },
        'SG': {
            'FR': 0.70,
            'SO': 0.88,
            'JR': 1.00,
            'SR': 0.98,
            'R-SR': 0.95
        },
        'SF': {
            'FR': 0.68,
            'SO': 0.86,
            'JR': 0.98,
            'SR': 1.00,
            'R-SR': 0.97
        },
        'PF': {
            'FR': 0.65,
            'SO': 0.82,
            'JR': 0.95,
            'SR': 1.00,
            'R-SR': 0.98
        },
        'C': {
            'FR': 0.60,
            'SO': 0.78,
            'JR': 0.93,
            'SR': 1.00,
            'R-SR': 1.00
        }
    }

    def __init__(self, sport: str = 'football'):
        """
        Initialize predictive model

        Args:
            sport: 'football' or 'basketball'
        """
        self.sport = sport.lower()
        self.age_curves = (
            self.FOOTBALL_AGE_CURVES if sport == 'football'
            else self.BASKETBALL_AGE_CURVES
        )

    def predict_future_performance(
        self,
        current_stats: Dict[str, Any],
        historical_stats: List[Dict[str, Any]],
        position: str,
        class_year: str,
        recruiting_rank: Optional[int] = None,
        injury_history: Optional[List[Dict[str, Any]]] = None,
        coaching_changes: Optional[Dict[str, Any]] = None,
        roster_context: Optional[Dict[str, Any]] = None
    ) -> PredictiveResult:
        """
        Predict future performance trajectory

        Args:
            current_stats: Current season statistics
            historical_stats: List of previous season stats (most recent first)
            position: Player position
            class_year: FR, SO, JR, SR, R-SR
            recruiting_rank: National recruiting rank (lower is better)
            injury_history: List of injuries
            coaching_changes: New coordinator/system info
            roster_context: Surrounding talent, competition for PT

        Returns:
            PredictiveResult with projections and analysis
        """
        position_group = self._get_position_group(position)

        # 1. Calculate baseline trajectory from age/experience curve
        age_curve_projection = self._calculate_age_curve_projection(
            position_group, class_year
        )

        # 2. Analyze year-over-year improvement trend
        improvement_trend = self._calculate_improvement_trend(historical_stats)

        # 3. Factor in recruiting pedigree (ceiling indicator)
        recruiting_factor = self._calculate_recruiting_factor(recruiting_rank)

        # 4. Assess injury risk impact
        injury_factor = self._calculate_injury_impact(injury_history)

        # 5. Adjust for coaching/system changes
        system_factor = self._calculate_system_change_impact(
            coaching_changes, position_group
        )

        # 6. Evaluate roster context (playing time, supporting cast)
        context_factor = self._calculate_context_factor(roster_context, position_group)

        # 7. Combine factors to create projection
        current_production = current_stats.get('production_score', 65)

        # Base projection
        expected_next_year = current_production * age_curve_projection

        # Apply adjustments
        expected_next_year *= improvement_trend
        expected_next_year *= recruiting_factor
        expected_next_year *= injury_factor
        expected_next_year *= system_factor
        expected_next_year *= context_factor

        # Cap at reasonable range
        expected_next_year = max(20, min(expected_next_year, 100))

        # Two-year projection (with more uncertainty)
        two_year_projection = self._project_two_years(
            expected_next_year, position_group, class_year
        )

        # Determine trajectory
        trajectory = self._determine_trajectory(
            current_production, expected_next_year, improvement_trend
        )

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(
            historical_stats, injury_history, coaching_changes
        )

        # Generate outcome ranges (P10, P50, P90)
        range_p10, range_p50, range_p90 = self._generate_outcome_ranges(
            expected_next_year, confidence
        )

        # Find comparable players (placeholder - would need historical DB)
        comparable_players = self._find_comparable_players(
            current_stats, position, recruiting_rank
        )

        return PredictiveResult(
            expected_next_year_score=expected_next_year,
            two_year_projection=two_year_projection,
            trajectory=trajectory,
            confidence=confidence,
            range_p10=range_p10,
            range_p50=range_p50,
            range_p90=range_p90,
            factors={
                'age_curve': age_curve_projection,
                'improvement_trend': improvement_trend,
                'recruiting_factor': recruiting_factor,
                'injury_factor': injury_factor,
                'system_factor': system_factor,
                'context_factor': context_factor,
                'current_production': current_production
            },
            comparable_players=comparable_players
        )

    def _get_position_group(self, position: str) -> str:
        """Map specific position to position group"""
        position = position.upper()

        football_mapping = {
            'QB': 'QB',
            'RB': 'RB', 'FB': 'RB',
            'WR': 'WR', 'TE': 'WR',
            'OT': 'OL', 'OG': 'OL', 'C': 'OL', 'OL': 'OL',
            'DT': 'DL', 'DE': 'DL', 'EDGE': 'DL', 'DL': 'DL',
            'LB': 'LB', 'ILB': 'LB', 'OLB': 'LB',
            'CB': 'DB', 'S': 'DB', 'DB': 'DB'
        }

        basketball_mapping = {
            'PG': 'PG', 'SG': 'SG', 'SF': 'SF', 'PF': 'PF', 'C': 'C'
        }

        if self.sport == 'football':
            return football_mapping.get(position, 'WR')
        else:
            return basketball_mapping.get(position, 'SF')

    def _calculate_age_curve_projection(
        self, position_group: str, class_year: str
    ) -> float:
        """
        Calculate expected improvement based on typical age/experience curve

        Returns:
            Multiplier for next year (e.g., 1.15 = 15% improvement expected)
        """
        class_year = class_year.upper()
        if class_year not in ['FR', 'SO', 'JR', 'SR', 'R-SR']:
            class_year = 'JR'  # Default

        # Get current year performance factor
        current_factor = self.age_curves.get(position_group, {}).get(class_year, 0.85)

        # Get next year factor
        next_year_map = {
            'FR': 'SO',
            'SO': 'JR',
            'JR': 'SR',
            'SR': 'R-SR',
            'R-SR': 'R-SR'  # No more improvement
        }
        next_year = next_year_map[class_year]
        next_factor = self.age_curves.get(position_group, {}).get(next_year, 0.95)

        # Return ratio
        if current_factor == 0:
            return 1.0
        return next_factor / current_factor

    def _calculate_improvement_trend(
        self, historical_stats: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate year-over-year improvement trend

        Returns:
            Multiplier (>1.0 = improving, <1.0 = declining, 1.0 = stable)
        """
        if not historical_stats or len(historical_stats) < 2:
            return 1.0  # No trend data

        # Extract production scores
        scores = [
            s.get('production_score', 50)
            for s in historical_stats[:3]  # Last 3 seasons
        ]

        if len(scores) < 2:
            return 1.0

        # Calculate year-over-year changes
        yoy_changes = []
        for i in range(len(scores) - 1):
            if scores[i+1] > 0:
                change = scores[i] / scores[i+1]
                yoy_changes.append(change)

        if not yoy_changes:
            return 1.0

        # Average improvement rate, weighted toward recent
        if len(yoy_changes) == 1:
            avg_improvement = yoy_changes[0]
        else:
            # Weight recent 60%, older 40%
            avg_improvement = (yoy_changes[0] * 0.6) + (statistics.mean(yoy_changes[1:]) * 0.4)

        # Cap at reasonable range (0.85 to 1.20)
        return max(0.85, min(avg_improvement, 1.20))

    def _calculate_recruiting_factor(self, recruiting_rank: Optional[int]) -> float:
        """
        Factor in recruiting rank as ceiling indicator

        Returns:
            Multiplier (higher for blue-chip recruits)
        """
        if recruiting_rank is None:
            return 1.0

        # 5-star (top 32): 1.10x ceiling
        # 4-star (top 300): 1.05x
        # 3-star: 1.00x
        # 2-star+: 0.95x
        if recruiting_rank <= 32:
            return 1.10
        elif recruiting_rank <= 300:
            return 1.05
        elif recruiting_rank <= 1000:
            return 1.00
        else:
            return 0.98

    def _calculate_injury_impact(
        self, injury_history: Optional[List[Dict[str, Any]]]
    ) -> float:
        """
        Calculate injury risk discount

        Returns:
            Multiplier (<1.0 if injury concerns)
        """
        if not injury_history:
            return 1.0

        # Count recent injuries (last 2 years)
        recent_injuries = [
            inj for inj in injury_history
            if inj.get('seasons_ago', 10) <= 2
        ]

        if not recent_injuries:
            return 1.0

        # Major injuries (ACL, Achilles, etc.) = bigger discount
        major_injuries = [
            inj for inj in recent_injuries
            if inj.get('severity', 'minor') in ['major', 'severe']
        ]

        # Minor injuries
        minor_injuries = len(recent_injuries) - len(major_injuries)

        # Calculate discount
        discount = 1.0
        discount -= len(major_injuries) * 0.08  # 8% per major injury
        discount -= minor_injuries * 0.03  # 3% per minor injury

        return max(0.75, discount)  # Cap at 25% discount

    def _calculate_system_change_impact(
        self,
        coaching_changes: Optional[Dict[str, Any]],
        position_group: str
    ) -> float:
        """
        Adjust for new coaching staff or system changes

        Returns:
            Multiplier (typically 0.90-1.10)
        """
        if not coaching_changes:
            return 1.0

        new_coordinator = coaching_changes.get('new_coordinator', False)
        system_fit = coaching_changes.get('system_fit', 'average')

        if not new_coordinator:
            return 1.0

        # System fit impact
        fit_multipliers = {
            'perfect': 1.10,
            'good': 1.05,
            'average': 0.98,  # Slight uncertainty discount
            'poor': 0.90
        }

        return fit_multipliers.get(system_fit, 0.98)

    def _calculate_context_factor(
        self,
        roster_context: Optional[Dict[str, Any]],
        position_group: str
    ) -> float:
        """
        Evaluate roster context impact

        Returns:
            Multiplier based on supporting cast and competition
        """
        if not roster_context:
            return 1.0

        # Playing time probability
        pt_probability = roster_context.get('playing_time_probability', 0.80)

        # Supporting cast quality (for skill positions)
        supporting_cast = roster_context.get('supporting_cast_quality', 'average')
        cast_multipliers = {
            'elite': 1.08,  # Great OL, receivers, etc.
            'good': 1.04,
            'average': 1.00,
            'poor': 0.96
        }

        # Competition for playing time
        competition = roster_context.get('competition', 'moderate')
        comp_multipliers = {
            'none': 1.05,  # Guaranteed starter
            'light': 1.02,
            'moderate': 1.00,
            'heavy': 0.95  # May lose snaps
        }

        base = pt_probability
        base *= cast_multipliers.get(supporting_cast, 1.0)
        base *= comp_multipliers.get(competition, 1.0)

        return base

    def _project_two_years(
        self, next_year_score: float, position_group: str, class_year: str
    ) -> float:
        """
        Project performance two years out (more uncertainty)

        Returns:
            Two-year projected score
        """
        # Get year-after-next age curve
        year_map = {
            'FR': 'JR',
            'SO': 'SR',
            'JR': 'R-SR',
            'SR': 'R-SR',
            'R-SR': 'R-SR'
        }
        two_years_ahead = year_map.get(class_year.upper(), 'SR')

        next_year_class = {
            'FR': 'SO', 'SO': 'JR', 'JR': 'SR', 'SR': 'R-SR', 'R-SR': 'R-SR'
        }.get(class_year.upper(), 'JR')

        next_year_factor = self.age_curves.get(position_group, {}).get(next_year_class, 0.95)
        two_year_factor = self.age_curves.get(position_group, {}).get(two_years_ahead, 1.0)

        if next_year_factor == 0:
            return next_year_score

        ratio = two_year_factor / next_year_factor
        two_year_score = next_year_score * ratio

        return max(20, min(two_year_score, 100))

    def _determine_trajectory(
        self, current: float, projected: float, trend: float
    ) -> str:
        """
        Classify trajectory

        Returns:
            'improving', 'peaking', 'declining', or 'stable'
        """
        change = projected - current

        if change >= 8 and trend >= 1.05:
            return 'improving'
        elif change <= -5 or trend <= 0.92:
            return 'declining'
        elif abs(change) < 3:
            return 'stable'
        elif change > 0 and change < 8:
            return 'peaking'
        else:
            return 'stable'

    def _calculate_confidence(
        self,
        historical_stats: List[Dict[str, Any]],
        injury_history: Optional[List[Dict[str, Any]]],
        coaching_changes: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence in prediction

        Returns:
            Confidence score 0-1 (higher = more confident)
        """
        confidence = 0.70  # Base

        # More historical data = more confidence
        if len(historical_stats) >= 3:
            confidence += 0.15
        elif len(historical_stats) >= 2:
            confidence += 0.10
        elif len(historical_stats) >= 1:
            confidence += 0.05

        # Injury history reduces confidence
        if injury_history and len(injury_history) > 0:
            confidence -= 0.10

        # Coaching changes reduce confidence
        if coaching_changes and coaching_changes.get('new_coordinator'):
            confidence -= 0.08

        return max(0.40, min(confidence, 0.95))

    def _generate_outcome_ranges(
        self, expected: float, confidence: float
    ) -> Tuple[float, float, float]:
        """
        Generate P10, P50, P90 outcome ranges

        Returns:
            (p10, p50, p90) tuple
        """
        # Lower confidence = wider range
        spread = (1 - confidence) * 30  # Up to 30 points spread

        p10 = max(20, expected - spread)
        p50 = expected
        p90 = min(100, expected + spread)

        return (p10, p50, p90)

    def _find_comparable_players(
        self,
        current_stats: Dict[str, Any],
        position: str,
        recruiting_rank: Optional[int]
    ) -> List[Dict[str, Any]]:
        """
        Find historical comparable players (placeholder)

        In production, this would query a database of historical players
        with similar profiles and track their trajectories

        Returns:
            List of comparable player dicts
        """
        # Placeholder - would need historical database
        return [
            {
                'name': 'Historical Player A',
                'position': position,
                'similarity_score': 0.85,
                'trajectory': 'Improved 15% in year 2',
                'final_outcome': 'NFL Draft 3rd round'
            },
            {
                'name': 'Historical Player B',
                'position': position,
                'similarity_score': 0.78,
                'trajectory': 'Stable performance',
                'final_outcome': 'All-Conference selection'
            }
        ]

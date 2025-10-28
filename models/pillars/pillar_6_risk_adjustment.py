"""
Pillar 6: Risk Adjustment Model
Applies discounts for injury risk, performance variance, character concerns,
eligibility issues, and fit risks
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Overall risk classification"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


@dataclass
class RiskAdjustmentResult:
    """Result from risk adjustment analysis"""
    total_risk_multiplier: float  # 0.50 - 1.00 (discount applied)
    risk_level: RiskLevel
    injury_discount: float
    performance_risk_discount: float
    character_discount: float
    eligibility_discount: float
    fit_risk_discount: float
    risk_factors: List[str]  # List of identified risk factors
    components: Dict[str, Any]


class RiskAdjustmentModel:
    """
    Calculates risk-adjusted value
    Applies discounts for various risk categories
    """

    # Position-specific injury rates (annual probability)
    FOOTBALL_INJURY_RATES = {
        'RB': 0.35,   # Highest injury risk
        'LB': 0.30,
        'WR': 0.28,
        'TE': 0.27,
        'S': 0.26,
        'CB': 0.25,
        'DL': 0.28,
        'EDGE': 0.27,
        'OL': 0.24,
        'QB': 0.20,   # Lower risk (protected)
        'K': 0.08,
        'P': 0.08
    }

    BASKETBALL_INJURY_RATES = {
        'C': 0.25,    # Size = more injury risk
        'PF': 0.22,
        'SF': 0.20,
        'SG': 0.18,
        'PG': 0.18
    }

    # Injury severity impact
    INJURY_SEVERITY = {
        'major': 0.15,      # 15% discount per injury (ACL, Achilles, etc.)
        'moderate': 0.08,   # 8% discount
        'minor': 0.03       # 3% discount
    }

    # Character/behavior risk tiers
    CHARACTER_RISK_TIERS = {
        'clean': 0.00,           # No discount
        'minor_concerns': 0.07,  # 7% discount
        'moderate_concerns': 0.18,  # 18% discount
        'major_concerns': 0.35,  # 35% discount
        'severe': 0.60           # 60% discount (near-DNU)
    }

    def __init__(self, sport: str = 'football'):
        """
        Initialize risk adjustment model

        Args:
            sport: 'football' or 'basketball'
        """
        self.sport = sport.lower()
        self.position_injury_rates = (
            self.FOOTBALL_INJURY_RATES if sport == 'football'
            else self.BASKETBALL_INJURY_RATES
        )

    def calculate_risk_adjustment(
        self,
        position: str,
        injury_history: Optional[List[Dict[str, Any]]] = None,
        performance_history: Optional[List[Dict[str, Any]]] = None,
        character_data: Optional[Dict[str, Any]] = None,
        eligibility_data: Optional[Dict[str, Any]] = None,
        fit_data: Optional[Dict[str, Any]] = None
    ) -> RiskAdjustmentResult:
        """
        Calculate comprehensive risk adjustments

        Args:
            position: Player position
            injury_history: List of injuries
            performance_history: Historical performance (for variance analysis)
            character_data: Character/behavior information
            eligibility_data: Eligibility and availability info
            fit_data: Scheme/system fit information

        Returns:
            RiskAdjustmentResult with discounts and risk level
        """
        risk_factors = []

        # 1. Injury risk
        injury_discount = self._calculate_injury_risk(
            position, injury_history, risk_factors
        )

        # 2. Performance risk (variance/consistency)
        performance_discount = self._calculate_performance_risk(
            performance_history, risk_factors
        )

        # 3. Character/behavior risk
        character_discount = self._calculate_character_risk(
            character_data, risk_factors
        )

        # 4. Eligibility/availability risk
        eligibility_discount = self._calculate_eligibility_risk(
            eligibility_data, risk_factors
        )

        # 5. Fit risk (scheme/culture)
        fit_discount = self._calculate_fit_risk(
            fit_data, risk_factors
        )

        # Combine discounts (multiplicative)
        total_multiplier = (
            (1 - injury_discount) *
            (1 - performance_discount) *
            (1 - character_discount) *
            (1 - eligibility_discount) *
            (1 - fit_discount)
        )

        # Determine overall risk level
        total_discount = 1 - total_multiplier
        risk_level = self._determine_risk_level(total_discount)

        return RiskAdjustmentResult(
            total_risk_multiplier=total_multiplier,
            risk_level=risk_level,
            injury_discount=injury_discount,
            performance_risk_discount=performance_discount,
            character_discount=character_discount,
            eligibility_discount=eligibility_discount,
            fit_risk_discount=fit_discount,
            risk_factors=risk_factors,
            components={
                'position': position,
                'total_discount_pct': total_discount * 100,
                'risk_count': len(risk_factors)
            }
        )

    def _calculate_injury_risk(
        self,
        position: str,
        injury_history: Optional[List[Dict[str, Any]]],
        risk_factors: List[str]
    ) -> float:
        """
        Calculate injury risk discount

        Returns:
            Discount (0-0.40)
        """
        # Base position injury rate
        position_norm = self._normalize_position(position)
        base_rate = self.position_injury_rates.get(position_norm, 0.20)

        if not injury_history:
            # No injury history = just base position risk (minimal discount)
            return base_rate * 0.15  # 15% of position risk

        # Analyze injury history
        recent_injuries = [
            inj for inj in injury_history
            if inj.get('seasons_ago', 10) <= 2  # Last 2 years
        ]

        if not recent_injuries:
            return base_rate * 0.10  # Low discount for clean recent history

        total_discount = 0.0

        # Count by severity
        for injury in recent_injuries:
            severity = injury.get('severity', 'minor')
            discount = self.INJURY_SEVERITY.get(severity, 0.03)
            total_discount += discount

            # Add to risk factors
            injury_type = injury.get('injury_type', 'injury')
            risk_factors.append(f"Recent {severity} injury: {injury_type}")

        # Check for re-injury risk (same injury multiple times)
        injury_types = [inj.get('injury_type') for inj in recent_injuries]
        unique_injuries = set(injury_types)
        if len(injury_types) > len(unique_injuries):
            total_discount *= 1.25  # 25% additional discount for re-injuries
            risk_factors.append("Re-injury pattern detected")

        # Age/wear-and-tear for RBs
        if position_norm == 'RB':
            carries = sum(inj.get('carries_before_injury', 0) for inj in injury_history)
            if carries >= 600:  # High workload
                total_discount += 0.05
                risk_factors.append("High career workload (RB wear)")

        # Cap at 40% total injury discount
        return min(total_discount, 0.40)

    def _calculate_performance_risk(
        self,
        performance_history: Optional[List[Dict[str, Any]]],
        risk_factors: List[str]
    ) -> float:
        """
        Calculate performance variance/consistency risk

        Returns:
            Discount (0-0.20)
        """
        if not performance_history or len(performance_history) < 2:
            return 0.05  # Small discount for lack of track record

        # Extract performance scores
        scores = [
            p.get('production_score', 50)
            for p in performance_history[:3]  # Last 3 years
        ]

        if len(scores) < 2:
            return 0.05

        # Calculate variance (standard deviation)
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        # High variance = inconsistent = risk
        if std_dev >= 20:
            risk_factors.append("High performance variance (inconsistent)")
            return 0.15
        elif std_dev >= 15:
            risk_factors.append("Moderate performance variance")
            return 0.10
        elif std_dev >= 10:
            return 0.05
        else:
            return 0.0  # Consistent performer = no discount

        # Check for one-year wonder
        if len(scores) >= 2:
            recent = scores[0]
            previous = scores[1]
            if recent >= 80 and previous <= 55:
                risk_factors.append("Potential one-year wonder (limited track record)")
                return 0.12

        return 0.0

    def _calculate_character_risk(
        self,
        character_data: Optional[Dict[str, Any]],
        risk_factors: List[str]
    ) -> float:
        """
        Calculate character/behavior risk

        Returns:
            Discount (0-0.60)
        """
        if not character_data:
            return 0.0  # No data = assume clean

        # Overall risk tier
        risk_tier = character_data.get('risk_tier', 'clean')
        base_discount = self.CHARACTER_RISK_TIERS.get(risk_tier, 0.0)

        if base_discount > 0:
            risk_factors.append(f"Character concerns: {risk_tier}")

        # Specific issues
        suspensions = character_data.get('suspensions', 0)
        if suspensions >= 2:
            risk_factors.append(f"{suspensions} prior suspensions")
            base_discount += 0.08
        elif suspensions == 1:
            base_discount += 0.03

        # Arrests/legal issues
        arrests = character_data.get('arrests', 0)
        if arrests >= 1:
            risk_factors.append(f"{arrests} arrest(s)")
            base_discount += 0.15

        # Transfer history (multiple transfers = potential red flag)
        transfers = character_data.get('transfer_count', 0)
        if transfers >= 2:
            risk_factors.append("Multiple transfers (potential culture fit issue)")
            base_discount += 0.08

        # Academic issues
        academic_issues = character_data.get('academic_issues', False)
        if academic_issues:
            risk_factors.append("Academic eligibility concerns")
            base_discount += 0.05

        # Locker room concerns (qualitative)
        locker_room = character_data.get('locker_room_concerns', False)
        if locker_room:
            risk_factors.append("Reported locker room issues")
            base_discount += 0.10

        # Cap at 60% (anything more = don't recruit)
        return min(base_discount, 0.60)

    def _calculate_eligibility_risk(
        self,
        eligibility_data: Optional[Dict[str, Any]],
        risk_factors: List[str]
    ) -> float:
        """
        Calculate eligibility/availability risk

        Returns:
            Discount (0-0.30)
        """
        if not eligibility_data:
            return 0.0

        total_discount = 0.0

        # Remaining eligibility
        years_remaining = eligibility_data.get('years_remaining', 2)
        if years_remaining == 1:
            # Only 1 year left = less valuable (especially for rebuilding teams)
            total_discount += 0.10
            risk_factors.append("Only 1 year of eligibility remaining")

        # Graduate transfer (one-year rental)
        is_grad_transfer = eligibility_data.get('graduate_transfer', False)
        if is_grad_transfer and years_remaining == 1:
            total_discount += 0.05  # Additional discount for one-year rental
            risk_factors.append("Graduate transfer (one-year only)")

        # Academic standing
        academic_standing = eligibility_data.get('academic_standing', 'good')
        if academic_standing == 'probation':
            total_discount += 0.12
            risk_factors.append("Academic probation")
        elif academic_standing == 'at_risk':
            total_discount += 0.06
            risk_factors.append("At-risk academic standing")

        # COVID eligibility complications (if any)
        covid_eligibility = eligibility_data.get('covid_eligibility_unclear', False)
        if covid_eligibility:
            total_discount += 0.05
            risk_factors.append("COVID eligibility uncertainty")

        # Pending investigations/NCAA issues
        ncaa_investigation = eligibility_data.get('ncaa_investigation', False)
        if ncaa_investigation:
            total_discount += 0.20
            risk_factors.append("Pending NCAA investigation")

        return min(total_discount, 0.30)

    def _calculate_fit_risk(
        self,
        fit_data: Optional[Dict[str, Any]],
        risk_factors: List[str]
    ) -> float:
        """
        Calculate scheme/culture fit risk

        Returns:
            Discount (0-0.15)
        """
        if not fit_data:
            return 0.0

        total_discount = 0.0

        # Scheme fit
        scheme_fit = fit_data.get('scheme_fit', 'average')
        if scheme_fit == 'poor':
            total_discount += 0.12
            risk_factors.append("Poor scheme fit (requires system adjustment)")
        elif scheme_fit == 'below_average':
            total_discount += 0.06
            risk_factors.append("Below-average scheme fit")

        # Pace adjustment (basketball: fast to slow or vice versa)
        pace_adjustment = fit_data.get('pace_adjustment', 'none')
        if pace_adjustment == 'significant':
            total_discount += 0.05
            risk_factors.append("Significant pace/style adjustment needed")

        # Culture fit
        culture_fit = fit_data.get('culture_fit', 'average')
        if culture_fit == 'poor':
            total_discount += 0.08
            risk_factors.append("Culture fit concerns")

        return min(total_discount, 0.15)

    def _normalize_position(self, position: str) -> str:
        """Normalize position for injury rate lookup"""
        position = position.upper()

        if self.sport == 'football':
            mapping = {
                'QB': 'QB',
                'RB': 'RB', 'FB': 'RB',
                'WR': 'WR',
                'TE': 'TE',
                'OT': 'OL', 'OG': 'OL', 'C': 'OL', 'OL': 'OL',
                'DE': 'EDGE', 'EDGE': 'EDGE',
                'DT': 'DL', 'DL': 'DL',
                'LB': 'LB', 'ILB': 'LB', 'OLB': 'LB',
                'CB': 'CB',
                'S': 'S', 'FS': 'S', 'SS': 'S',
                'K': 'K',
                'P': 'P'
            }
            return mapping.get(position, 'WR')
        else:
            return position if position in ['PG', 'SG', 'SF', 'PF', 'C'] else 'SF'

    def _determine_risk_level(self, total_discount: float) -> RiskLevel:
        """
        Determine overall risk level from total discount

        Args:
            total_discount: Total discount percentage (0-1.0)

        Returns:
            RiskLevel enum
        """
        if total_discount >= 0.40:
            return RiskLevel.SEVERE
        elif total_discount >= 0.25:
            return RiskLevel.HIGH
        elif total_discount >= 0.15:
            return RiskLevel.MODERATE
        elif total_discount >= 0.05:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    def calculate_position_adjusted_risk(
        self, position: str
    ) -> Dict[str, Any]:
        """
        Get position-specific risk profile

        Returns:
            Dict with position risk information
        """
        position_norm = self._normalize_position(position)
        base_rate = self.position_injury_rates.get(position_norm, 0.20)

        # Career length expectations
        if self.sport == 'football':
            career_length = {
                'QB': 'long',
                'OL': 'long',
                'K': 'long',
                'P': 'long',
                'WR': 'medium',
                'TE': 'medium',
                'DL': 'medium',
                'LB': 'medium',
                'CB': 'medium',
                'S': 'medium',
                'RB': 'short',  # Shortest career
                'EDGE': 'medium'
            }
        else:
            career_length = {
                'PG': 'long',
                'SG': 'long',
                'SF': 'long',
                'PF': 'medium',
                'C': 'medium'
            }

        return {
            'position': position_norm,
            'base_injury_rate': base_rate,
            'expected_career_length': career_length.get(position_norm, 'medium'),
            'injury_risk_tier': 'high' if base_rate >= 0.30 else 'medium' if base_rate >= 0.20 else 'low'
        }

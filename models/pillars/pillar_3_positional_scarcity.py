"""
Pillar 3: Positional Scarcity & Market Demand Model
Analyzes supply/demand dynamics in the transfer portal and recruiting market
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ScarcityTier(Enum):
    """Scarcity tier classification"""
    PREMIUM = "premium"  # Elite, scarce positions
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REPLACEMENT = "replacement"  # Easily replaceable


@dataclass
class ScarcityResult:
    """Result from positional scarcity analysis"""
    scarcity_multiplier: float  # 0.6x - 2.5x based on supply/demand
    position_tier: ScarcityTier
    market_percentile: float  # Where player ranks in position market (0-100)
    supply_count: int  # Number of similar players available
    demand_estimate: int  # Estimated number of teams seeking position
    expected_offers: int  # Expected number of P4/high-major offers
    factors: Dict[str, Any]


class PositionalScarcityModel:
    """
    Calculates positional scarcity and market demand
    Adjusts player value based on supply/demand dynamics
    """

    # Position scarcity base values (before market analysis)
    FOOTBALL_POSITION_SCARCITY = {
        'QB': {'tier': ScarcityTier.PREMIUM, 'base_multiplier': 2.0},
        'LT': {'tier': ScarcityTier.PREMIUM, 'base_multiplier': 1.8},
        'EDGE': {'tier': ScarcityTier.PREMIUM, 'base_multiplier': 1.7},
        'CB': {'tier': ScarcityTier.PREMIUM, 'base_multiplier': 1.6},
        'WR': {'tier': ScarcityTier.HIGH, 'base_multiplier': 1.4},
        'OT': {'tier': ScarcityTier.HIGH, 'base_multiplier': 1.5},
        'DL': {'tier': ScarcityTier.HIGH, 'base_multiplier': 1.4},
        'S': {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.2},
        'RB': {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.1},
        'TE': {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.2},
        'LB': {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.2},
        'OG': {'tier': ScarcityTier.LOW, 'base_multiplier': 0.9},
        'C': {'tier': ScarcityTier.LOW, 'base_multiplier': 0.9},
        'K': {'tier': ScarcityTier.REPLACEMENT, 'base_multiplier': 0.6},
        'P': {'tier': ScarcityTier.REPLACEMENT, 'base_multiplier': 0.6},
    }

    BASKETBALL_POSITION_SCARCITY = {
        'PG': {'tier': ScarcityTier.PREMIUM, 'base_multiplier': 1.8},  # Elite playmakers scarce
        'C': {'tier': ScarcityTier.PREMIUM, 'base_multiplier': 1.7},  # Skilled bigs scarce
        'Wing3D': {'tier': ScarcityTier.HIGH, 'base_multiplier': 1.5},  # 3-and-D wings
        'StretchBig': {'tier': ScarcityTier.HIGH, 'base_multiplier': 1.6},  # Stretch 4/5
        'SG': {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.2},
        'SF': {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.2},
        'PF': {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.1},
    }

    # Transfer portal timing impact
    PORTAL_TIMING_MULTIPLIERS = {
        'early': 0.85,  # Early portal = more competition
        'mid': 1.00,
        'late': 1.20,  # Late portal = scarcity premium
    }

    def __init__(self, sport: str = 'football'):
        """
        Initialize scarcity model

        Args:
            sport: 'football' or 'basketball'
        """
        self.sport = sport.lower()
        self.position_scarcity = (
            self.FOOTBALL_POSITION_SCARCITY if sport == 'football'
            else self.BASKETBALL_POSITION_SCARCITY
        )

    def calculate_scarcity(
        self,
        position: str,
        player_quality: float,  # 0-100 production score
        portal_data: Optional[Dict[str, Any]] = None,
        market_timing: str = 'mid'
    ) -> ScarcityResult:
        """
        Calculate positional scarcity and market demand

        Args:
            position: Player position
            player_quality: Player's production/quality score (0-100)
            portal_data: Transfer portal supply data
            market_timing: 'early', 'mid', 'late' in portal cycle

        Returns:
            ScarcityResult with multiplier and analysis
        """
        # Get base position scarcity
        position_key = self._normalize_position(position)
        base_info = self.position_scarcity.get(
            position_key,
            {'tier': ScarcityTier.MEDIUM, 'base_multiplier': 1.0}
        )

        base_multiplier = base_info['base_multiplier']
        tier = base_info['tier']

        # Analyze portal market if data available
        if portal_data:
            supply_count = portal_data.get('total_at_position', 50)
            p4_quality_count = portal_data.get('p4_quality_count', 10)
            player_rank = portal_data.get('player_rank_at_position', 25)
        else:
            # Use defaults
            supply_count = 50
            p4_quality_count = 15
            player_rank = 25

        # Calculate market percentile
        market_percentile = self._calculate_market_percentile(
            player_rank, supply_count
        )

        # Estimate demand (teams needing this position)
        demand_estimate = self._estimate_position_demand(position_key)

        # Calculate supply/demand ratio
        supply_demand_ratio = demand_estimate / max(p4_quality_count, 1)

        # Adjust multiplier based on supply/demand
        scarcity_multiplier = base_multiplier * self._calculate_supply_demand_adjustment(
            supply_demand_ratio, market_percentile
        )

        # Apply timing adjustment
        timing_mult = self.PORTAL_TIMING_MULTIPLIERS.get(market_timing, 1.0)
        scarcity_multiplier *= timing_mult

        # Quality tier adjustment (elite players = higher premium)
        quality_adjustment = self._calculate_quality_premium(
            player_quality, market_percentile
        )
        scarcity_multiplier *= quality_adjustment

        # Estimate expected offers
        expected_offers = self._estimate_expected_offers(
            position_key, market_percentile, player_quality
        )

        return ScarcityResult(
            scarcity_multiplier=scarcity_multiplier,
            position_tier=tier,
            market_percentile=market_percentile,
            supply_count=supply_count,
            demand_estimate=demand_estimate,
            expected_offers=expected_offers,
            factors={
                'base_multiplier': base_multiplier,
                'supply_demand_ratio': supply_demand_ratio,
                'timing_multiplier': timing_mult,
                'quality_adjustment': quality_adjustment,
                'p4_quality_count': p4_quality_count,
                'player_rank': player_rank
            }
        )

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

    def _calculate_market_percentile(self, player_rank: int, total_supply: int) -> float:
        """
        Calculate where player ranks in market

        Returns:
            Percentile (0-100, higher = better)
        """
        if total_supply == 0:
            return 50.0

        percentile = (1 - (player_rank / total_supply)) * 100
        return max(0, min(percentile, 100))

    def _estimate_position_demand(self, position: str) -> int:
        """
        Estimate number of teams seeking this position

        Returns:
            Estimated demand count
        """
        if self.sport == 'football':
            # Assume ~130 FBS teams
            demand_rates = {
                'QB': 40,  # ~40 teams need starting QB
                'LT': 35,
                'EDGE': 50,  # Most teams need EDGE help
                'CB': 60,  # Always need CBs
                'WR': 70,  # Most teams want WRs
                'OT': 45,
                'DL': 55,
                'S': 50,
                'RB': 40,
                'TE': 35,
                'LB': 50,
                'OG': 30,
                'C': 25,
                'K': 15,
                'P': 10
            }
        else:
            # ~350 D1 basketball teams
            demand_rates = {
                'PG': 150,  # Most teams want PG help
                'C': 120,  # Skilled bigs hard to find
                'Wing3D': 100,
                'StretchBig': 90,
                'SG': 140,
                'SF': 130,
                'PF': 110
            }

        return demand_rates.get(position, 50)

    def _calculate_supply_demand_adjustment(
        self, supply_demand_ratio: float, market_percentile: float
    ) -> float:
        """
        Adjust multiplier based on supply/demand dynamics

        Args:
            supply_demand_ratio: demand / supply (higher = more scarcity)
            market_percentile: Player's market position (0-100)

        Returns:
            Adjustment multiplier (0.7x - 1.5x)
        """
        # High demand / low supply = premium
        if supply_demand_ratio >= 3.0:
            base_adj = 1.40
        elif supply_demand_ratio >= 2.0:
            base_adj = 1.25
        elif supply_demand_ratio >= 1.5:
            base_adj = 1.10
        elif supply_demand_ratio >= 1.0:
            base_adj = 1.00
        elif supply_demand_ratio >= 0.7:
            base_adj = 0.90
        else:
            base_adj = 0.80

        # Top players benefit more from scarcity
        if market_percentile >= 90:
            base_adj *= 1.15
        elif market_percentile >= 75:
            base_adj *= 1.08
        elif market_percentile <= 25:
            base_adj *= 0.92

        return base_adj

    def _calculate_quality_premium(
        self, player_quality: float, market_percentile: float
    ) -> float:
        """
        Elite players command premium even in less scarce positions

        Returns:
            Quality adjustment multiplier (0.9x - 1.3x)
        """
        # Top-tier players (90th+ percentile, 85+ quality)
        if market_percentile >= 90 and player_quality >= 85:
            return 1.30
        elif market_percentile >= 80 and player_quality >= 80:
            return 1.20
        elif market_percentile >= 70 and player_quality >= 75:
            return 1.10
        elif market_percentile >= 50:
            return 1.00
        elif market_percentile >= 30:
            return 0.95
        else:
            return 0.90

    def _estimate_expected_offers(
        self, position: str, market_percentile: float, player_quality: float
    ) -> int:
        """
        Estimate number of high-major offers player will receive

        Returns:
            Expected offer count
        """
        if self.sport == 'football':
            # P4 offers
            if market_percentile >= 95 and player_quality >= 85:
                base_offers = 25  # Top players get tons of interest
            elif market_percentile >= 90:
                base_offers = 18
            elif market_percentile >= 80:
                base_offers = 12
            elif market_percentile >= 70:
                base_offers = 8
            elif market_percentile >= 50:
                base_offers = 5
            elif market_percentile >= 30:
                base_offers = 2
            else:
                base_offers = 0

        else:
            # Basketball high-major offers
            if market_percentile >= 95 and player_quality >= 85:
                base_offers = 30
            elif market_percentile >= 90:
                base_offers = 22
            elif market_percentile >= 80:
                base_offers = 15
            elif market_percentile >= 70:
                base_offers = 10
            elif market_percentile >= 50:
                base_offers = 6
            elif market_percentile >= 30:
                base_offers = 3
            else:
                base_offers = 1

        # Premium positions get more interest
        position_boost = {
            'QB': 1.4, 'LT': 1.2, 'EDGE': 1.2, 'CB': 1.1,
            'PG': 1.3, 'C': 1.2
        }
        multiplier = position_boost.get(position, 1.0)

        return int(base_offers * multiplier)

    def analyze_portal_market(
        self,
        position: str,
        all_portal_players: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze entire portal market for a position

        Args:
            position: Position to analyze
            all_portal_players: List of all players in portal at position

        Returns:
            Market analysis dict
        """
        position_key = self._normalize_position(position)

        # Filter to position
        position_players = [
            p for p in all_portal_players
            if self._normalize_position(p.get('position', '')) == position_key
        ]

        total_count = len(position_players)

        # Count P4-quality players (production score >= 70)
        p4_quality = [
            p for p in position_players
            if p.get('production_score', 0) >= 70
        ]
        p4_quality_count = len(p4_quality)

        # Count elite players (90+)
        elite_count = len([
            p for p in position_players
            if p.get('production_score', 0) >= 90
        ])

        # Average quality
        if position_players:
            avg_quality = sum(p.get('production_score', 50) for p in position_players) / total_count
        else:
            avg_quality = 50

        return {
            'position': position_key,
            'total_at_position': total_count,
            'p4_quality_count': p4_quality_count,
            'elite_count': elite_count,
            'average_quality': avg_quality,
            'demand_estimate': self._estimate_position_demand(position_key),
            'supply_demand_ratio': self._estimate_position_demand(position_key) / max(p4_quality_count, 1)
        }

"""
Pillar 4: Market Context & School-Specific Adjustments
Value varies by school, conference, market size, and specific team needs
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ConferenceTier(Enum):
    """Conference tier classification"""
    ELITE = "elite"  # SEC, Big Ten top tier
    POWER = "power"  # ACC, Big 12, upper P4
    GROUP_FIVE = "g5"
    FCS = "fcs"


@dataclass
class MarketContextResult:
    """Result from market context analysis"""
    school_adjusted_value: float  # Value adjusted for specific school
    conference_multiplier: float
    school_success_factor: float
    playing_time_probability: float
    market_size_factor: float
    development_premium: float
    total_multiplier: float  # Combined multiplier
    context: Dict[str, Any]


class MarketContextModel:
    """
    Adjusts player value based on school-specific factors
    Conference prestige, school success, market size, development track record
    """

    # Conference premium/discount multipliers
    FOOTBALL_CONFERENCE_MULTIPLIERS = {
        'SEC': 1.40,
        'Big Ten': 1.35,
        'Big 12': 1.15,
        'ACC': 1.15,
        'Pac-12': 1.05,  # Post-realignment
        'American': 0.75,
        'Mountain West': 0.70,
        'Sun Belt': 0.68,
        'MAC': 0.65,
        'C-USA': 0.65,
        'Independent': 1.00,
        'FCS': 0.45
    }

    BASKETBALL_CONFERENCE_MULTIPLIERS = {
        # Blue blood conferences
        'ACC': 1.30,
        'Big Ten': 1.30,
        'Big 12': 1.25,
        'Big East': 1.25,
        'SEC': 1.20,
        'Pac-12': 1.15,
        # Mid-major power conferences
        'WCC': 1.00,
        'Atlantic 10': 0.95,
        'American': 0.95,
        'Mountain West': 0.90,
        'Missouri Valley': 0.85,
        # Lower conferences
        'Summit': 0.60,
        'WAC': 0.65,
        'Big Sky': 0.55,
        'Southland': 0.50
    }

    # Athletic department revenue tiers (ability to pay NIL)
    REVENUE_TIERS = {
        'elite': {'min_revenue': 150_000_000, 'multiplier': 1.30},  # $150M+
        'high': {'min_revenue': 100_000_000, 'multiplier': 1.15},   # $100-150M
        'medium': {'min_revenue': 70_000_000, 'multiplier': 1.00},  # $70-100M
        'low': {'min_revenue': 50_000_000, 'multiplier': 0.85},     # $50-70M
        'minimal': {'min_revenue': 0, 'multiplier': 0.70}           # <$50M
    }

    # Market size impact (local NIL opportunities)
    MARKET_SIZE_MULTIPLIERS = {
        'tier_1': 1.25,  # LA, NYC, Chicago, Dallas, etc.
        'tier_2': 1.15,  # Phoenix, Seattle, Denver, etc.
        'tier_3': 1.05,  # Mid-size metros
        'tier_4': 0.95,  # Small cities
        'tier_5': 0.85   # Rural
    }

    # Development track record by position (known "developer" schools)
    DEVELOPMENT_PREMIUMS = {
        'football': {
            'QB': ['USC', 'Oklahoma', 'Clemson', 'Alabama', 'Ohio State'],
            'OL': ['Iowa', 'Wisconsin', 'Alabama', 'Notre Dame', 'Stanford'],
            'WR': ['Baylor', 'USC', 'Alabama', 'Ohio State', 'LSU'],
            'RB': ['Alabama', 'Georgia', 'Wisconsin', 'Ohio State'],
            'DL': ['Alabama', 'Georgia', 'Clemson', 'Ohio State'],
            'DB': ['Alabama', 'Ohio State', 'LSU', 'Florida']
        },
        'basketball': {
            'PG': ['Duke', 'Kentucky', 'UNC', 'Kansas', 'Villanova'],
            'Wing': ['Duke', 'Kansas', 'Kentucky', 'Villanova', 'Gonzaga'],
            'Big': ['Kentucky', 'Kansas', 'Duke', 'UNC', 'Purdue']
        }
    }

    def __init__(self, sport: str = 'football'):
        """
        Initialize market context model

        Args:
            sport: 'football' or 'basketball'
        """
        self.sport = sport.lower()
        self.conference_multipliers = (
            self.FOOTBALL_CONFERENCE_MULTIPLIERS if sport == 'football'
            else self.BASKETBALL_CONFERENCE_MULTIPLIERS
        )

    def calculate_market_context(
        self,
        base_value: float,
        school_name: str,
        conference: str,
        position: str,
        school_data: Optional[Dict[str, Any]] = None
    ) -> MarketContextResult:
        """
        Calculate school-specific market adjustments

        Args:
            base_value: Base player value before school adjustments
            school_name: School name (e.g., 'Alabama', 'Duke')
            conference: Conference name
            position: Player position
            school_data: Additional school context (revenue, success, etc.)

        Returns:
            MarketContextResult with adjusted value
        """
        # 1. Conference multiplier
        conference_mult = self.conference_multipliers.get(conference, 1.0)

        # 2. School success factor (recent performance)
        school_success = self._calculate_school_success_factor(
            school_name, school_data
        )

        # 3. Revenue/NIL budget capacity
        revenue_mult = self._calculate_revenue_multiplier(school_data)

        # 4. Market size factor
        market_mult = self._calculate_market_size_factor(school_name, school_data)

        # 5. Development track record
        development_mult = self._calculate_development_premium(
            school_name, position
        )

        # 6. Playing time probability
        pt_probability = self._calculate_playing_time_factor(school_data, position)

        # Combine multipliers
        total_multiplier = (
            conference_mult *
            school_success *
            revenue_mult *
            market_mult *
            development_mult *
            pt_probability
        )

        # Apply to base value
        school_adjusted_value = base_value * total_multiplier

        return MarketContextResult(
            school_adjusted_value=school_adjusted_value,
            conference_multiplier=conference_mult,
            school_success_factor=school_success,
            playing_time_probability=pt_probability,
            market_size_factor=market_mult,
            development_premium=development_mult,
            total_multiplier=total_multiplier,
            context={
                'school': school_name,
                'conference': conference,
                'position': position,
                'revenue_multiplier': revenue_mult,
                'base_value': base_value
            }
        )

    def _calculate_school_success_factor(
        self,
        school_name: str,
        school_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate multiplier based on recent school success

        Returns:
            Multiplier (0.85 - 1.30)
        """
        if not school_data:
            return 1.0

        if self.sport == 'football':
            # Recent playoff/NY6 success
            playoff_appearances = school_data.get('playoff_appearances_5yr', 0)
            bowl_wins = school_data.get('bowl_wins_3yr', 0)
            win_pct = school_data.get('win_pct_3yr', 0.500)

            # Elite programs (playoff contenders)
            if playoff_appearances >= 2 and win_pct >= 0.750:
                return 1.30  # Premium for championship contenders
            elif playoff_appearances >= 1 or win_pct >= 0.700:
                return 1.20
            elif win_pct >= 0.600 or bowl_wins >= 2:
                return 1.10
            elif win_pct >= 0.500:
                return 1.00
            elif win_pct >= 0.400:
                return 0.92
            else:
                return 0.85  # Rebuilding programs

        else:
            # Basketball: tournament success
            tournament_appearances = school_data.get('tournament_appearances_5yr', 0)
            sweet_16_runs = school_data.get('sweet_16_runs_5yr', 0)
            win_pct = school_data.get('win_pct_3yr', 0.500)

            # Elite programs
            if sweet_16_runs >= 3 or tournament_appearances >= 4:
                return 1.40  # Blue bloods
            elif sweet_16_runs >= 1 or tournament_appearances >= 3:
                return 1.25
            elif tournament_appearances >= 2:
                return 1.10
            elif win_pct >= 0.600:
                return 1.00
            else:
                return 0.88

    def _calculate_revenue_multiplier(
        self, school_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate multiplier based on athletic department revenue (NIL capacity)

        Returns:
            Multiplier (0.70 - 1.30)
        """
        if not school_data:
            return 1.0

        revenue = school_data.get('athletic_revenue', 80_000_000)

        # Determine tier
        for tier_name, tier_info in self.REVENUE_TIERS.items():
            if revenue >= tier_info['min_revenue']:
                return tier_info['multiplier']

        return 1.0

    def _calculate_market_size_factor(
        self,
        school_name: str,
        school_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate market size impact (local NIL opportunities)

        Returns:
            Multiplier (0.85 - 1.25)
        """
        # Tier 1: Major metros
        tier_1_schools = [
            'USC', 'UCLA', 'Miami', 'Georgia Tech', 'Northwestern',
            'Rutgers', 'Maryland', 'Arizona State', 'SMU', 'TCU'
        ]

        # Tier 2: Large metros
        tier_2_schools = [
            'Texas', 'Houston', 'Washington', 'Colorado', 'Minnesota',
            'Arizona', 'Pitt', 'Temple', 'Vanderbilt', 'Florida State'
        ]

        # Tier 5: Rural
        tier_5_schools = [
            'Iowa State', 'Kansas State', 'Oklahoma State', 'Oregon State',
            'Washington State', 'Wyoming', 'Montana'
        ]

        if school_name in tier_1_schools:
            return self.MARKET_SIZE_MULTIPLIERS['tier_1']
        elif school_name in tier_2_schools:
            return self.MARKET_SIZE_MULTIPLIERS['tier_2']
        elif school_name in tier_5_schools:
            return self.MARKET_SIZE_MULTIPLIERS['tier_5']
        else:
            # Default to tier 3/4
            return self.MARKET_SIZE_MULTIPLIERS.get('tier_3', 1.0)

    def _calculate_development_premium(
        self, school_name: str, position: str
    ) -> float:
        """
        Schools known for developing certain positions get premium

        Returns:
            Multiplier (0.95 - 1.15)
        """
        dev_premiums = self.DEVELOPMENT_PREMIUMS.get(self.sport, {})

        # Normalize position to development category
        if self.sport == 'football':
            position = position.upper()
            if position in ['OT', 'OG', 'C']:
                dev_position = 'OL'
            elif position in ['DE', 'DT', 'EDGE']:
                dev_position = 'DL'
            elif position in ['CB', 'S']:
                dev_position = 'DB'
            else:
                dev_position = position
        else:
            # Basketball
            if position in ['PF', 'C']:
                dev_position = 'Big'
            elif position in ['SG', 'SF']:
                dev_position = 'Wing'
            else:
                dev_position = position

        # Check if school is known developer
        developer_schools = dev_premiums.get(dev_position, [])

        if school_name in developer_schools:
            return 1.15  # 15% premium
        else:
            return 1.00

    def _calculate_playing_time_factor(
        self,
        school_data: Optional[Dict[str, Any]],
        position: str
    ) -> float:
        """
        Adjust for expected playing time opportunity

        Returns:
            Multiplier (0.60 - 1.10)
        """
        if not school_data:
            return 1.0

        # Depth chart position
        depth_position = school_data.get('depth_chart_position', 'starter')

        # Competition level
        competition = school_data.get('position_competition', 'moderate')

        # Starter = full value
        if depth_position == 'starter':
            if competition == 'none':
                return 1.10  # Guaranteed starter, no competition
            elif competition == 'light':
                return 1.05
            else:
                return 1.00

        # Backup/rotation
        elif depth_position == 'backup':
            if competition == 'heavy':
                return 0.75  # May not see field much
            else:
                return 0.85

        # Depth piece
        else:
            return 0.60  # Limited playing time expected

    def calculate_school_tiers(
        self,
        schools: List[str],
        school_database: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Categorize schools into tiers for market analysis

        Args:
            schools: List of school names
            school_database: Database of school info

        Returns:
            Dict mapping school to tier info
        """
        tiers = {}

        for school in schools:
            school_data = school_database.get(school, {})
            conference = school_data.get('conference', 'Independent')

            # Calculate composite score
            conf_mult = self.conference_multipliers.get(conference, 1.0)
            success_mult = self._calculate_school_success_factor(school, school_data)
            revenue_mult = self._calculate_revenue_multiplier(school_data)

            composite = conf_mult * success_mult * revenue_mult

            # Assign tier
            if composite >= 1.50:
                tier = 'Elite'
            elif composite >= 1.20:
                tier = 'High'
            elif composite >= 0.90:
                tier = 'Medium'
            else:
                tier = 'Low'

            tiers[school] = {
                'tier': tier,
                'composite_score': composite,
                'conference': conference,
                'conference_multiplier': conf_mult,
                'success_multiplier': success_mult,
                'revenue_multiplier': revenue_mult
            }

        return tiers

    def estimate_nil_budget_tier(
        self, school_data: Optional[Dict[str, Any]]
    ) -> str:
        """
        Estimate NIL collective budget tier

        Returns:
            Budget tier: 'elite', 'high', 'medium', 'low', 'minimal'
        """
        if not school_data:
            return 'medium'

        revenue = school_data.get('athletic_revenue', 80_000_000)

        if revenue >= 150_000_000:
            return 'elite'
        elif revenue >= 100_000_000:
            return 'high'
        elif revenue >= 70_000_000:
            return 'medium'
        elif revenue >= 50_000_000:
            return 'low'
        else:
            return 'minimal'

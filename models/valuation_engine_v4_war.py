"""
Player Valuation Engine V4 - WAR-Driven

Primary change: WAR is now the core value driver
- Player value based on WAR (wins contributed)
- Dollar value per WAR based on position and market
- NIL potential remains separate
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, date
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PlayerValuationEngineV4WAR:
    """
    WAR-Driven valuation engine
    Each win is worth money to programs - we calculate value from wins added
    """
    
    def __init__(self,
                 performance_calculator,
                 scheme_fit_calculator,
                 brand_calculator,
                 war_calculator):
        self.performance_calc = performance_calculator
        self.scheme_calc = scheme_fit_calculator
        self.brand_calc = brand_calculator
        self.war_calc = war_calculator
        
        # Market value per WAR by position (what schools pay per win contributed)
        # Based on market analysis: elite QB (2.0 WAR) worth $2-3M
        self.dollar_per_war = {
            'QB': 1_500_000,   # $1.5M per WAR (elite QB = $3M)
            'OL': 900_000,     # OL WAR very valuable
            'DL': 900_000,     # Pass rush premium
            'CB': 800_000,     # Coverage critical
            'WR': 700_000,
            'LB': 650_000,
            'S': 600_000,
            'TE': 600_000,
            'RB': 500_000      # Most replaceable
        }
        
        # Scheme fit can add value multiplier
        self.scheme_fit_multipliers = {
            'perfect': 1.20,    # +20% for perfect scheme fit
            'good': 1.10,       # +10% for good fit
            'average': 1.00,    # No adjustment
            'poor': 0.90        # -10% for poor fit
        }
    
    def calculate_comprehensive_valuation(self,
                                        player_data: Dict,
                                        current_program: str,
                                        season: int = 2023,
                                        target_programs: Optional[List[str]] = None,
                                        market_context: Optional[Dict] = None) -> Dict:
        """
        Calculate player valuation with WAR as primary driver
        
        Flow:
        1. Calculate WAR (wins above replacement)
        2. Convert WAR to dollar value
        3. Apply scheme fit multiplier
        4. Add NIL potential (separate)
        5. Calculate confidence intervals
        """
        
        position = player_data.get('position', 'Unknown')
        conference = player_data.get('conference', 'Independent')
        
        # ============================================================================
        # 1. CALCULATE WAR (Core Value Driver)
        # ============================================================================
        
        # Get performance score
        performance_result = self.performance_calc.calculate_performance_score(
            player_data.get('stats', {}),
            position,
            conference,
            player_data.get('opponent_strength', 1.0)
        )
        performance_score = max(0, performance_result.get('overall_score', 50))
        
        # Calculate comprehensive WAR
        team_wins = player_data.get('team_wins', 8)
        team_losses = player_data.get('team_losses', 4)
        
        war_result = self.war_calc.calculate_comprehensive_war(
            player_performance_score=performance_score,
            position=position,
            snaps_played=player_data.get('snaps_played', 0),
            games_played=player_data.get('games_played', 0),
            games_started=player_data.get('games_started', 0),
            team_record=(team_wins, team_losses),
            conference=conference,
            player_stats=player_data.get('stats', {}),
            opponent_quality_avg=player_data.get('opponent_strength', 0.500)
        )
        
        war = war_result['war']
        war_low = war_result['war_low']
        war_high = war_result['war_high']
        
        # ============================================================================
        # 2. CONVERT WAR TO DOLLAR VALUE
        # ============================================================================
        
        # Base value from WAR
        dollar_per_war_position = self.dollar_per_war.get(position, 700_000)
        
        # WAR-based player value
        # Negative WAR players still have minimum value (can improve)
        if war >= 0:
            war_based_value = war * dollar_per_war_position
        else:
            # Below replacement: heavily discounted
            war_based_value = max(10_000, war * dollar_per_war_position * 0.3)
        
        # Ensure minimum value
        war_based_value = max(10_000, war_based_value)
        
        # ============================================================================
        # 3. SCHEME FIT MULTIPLIER
        # ============================================================================
        
        scheme_fit_result = self.scheme_calc.calculate_scheme_fit(
            player_data,
            player_data.get('current_scheme', 'Pro Style'),
            position
        )
        scheme_fit_score = max(0, scheme_fit_result.get('overall_fit_score', 70))
        
        # Scheme fit affects value to specific programs
        if scheme_fit_score >= 85:
            scheme_multiplier = self.scheme_fit_multipliers['perfect']
        elif scheme_fit_score >= 70:
            scheme_multiplier = self.scheme_fit_multipliers['good']
        elif scheme_fit_score >= 55:
            scheme_multiplier = self.scheme_fit_multipliers['average']
        else:
            scheme_multiplier = self.scheme_fit_multipliers['poor']
        
        player_value = war_based_value * scheme_multiplier
        
        # ============================================================================
        # 4. RISK ADJUSTMENT
        # ============================================================================
        
        injury_history = player_data.get('injury_history', [])
        injury_risk = len(injury_history) * 0.05
        risk_adjustment = max(0.7, 1.0 - injury_risk)
        
        player_value_adjusted = player_value * risk_adjustment
        
        # ============================================================================
        # 5. NIL POTENTIAL (Separate Stream)
        # ============================================================================
        
        brand_result = self.brand_calc.calculate_brand_score(
            player_data,
            current_program,
            performance_score
        )
        brand_score = max(0, brand_result.get('brand_score', 0))
        
        nil_estimate = brand_result.get('nil_value_estimate', {})
        nil_potential = nil_estimate.get('annual_expected', 0)
        
        # NIL floor
        if performance_score > 70:
            nil_floor = 25000 if position == 'QB' else 15000
        else:
            nil_floor = 5000
        
        nil_potential = max(nil_floor, nil_potential)
        
        # ============================================================================
        # 6. CONFIDENCE INTERVALS (Based on WAR uncertainty)
        # ============================================================================
        
        war_uncertainty = war_result['war_uncertainty']
        
        value_low = war_low * dollar_per_war_position * scheme_multiplier * risk_adjustment
        value_high = war_high * dollar_per_war_position * scheme_multiplier * risk_adjustment
        
        # ============================================================================
        # 7. COMBINED METRICS
        # ============================================================================
        
        combined_value = player_value_adjusted + nil_potential
        market_value = player_value_adjusted * 1.1  # 10% premium for competition
        
        return {
            # Player Identity
            'player_id': player_data.get('player_id', 'unknown'),
            'player_name': player_data.get('name', 'Unknown'),
            'position': position,
            'team': current_program,
            'season': season,
            'valuation_date': date.today().isoformat(),
            
            # PRIMARY VALUE (WAR-DRIVEN) - V4
            'war': round(war, 3),
            'wins_added': round(war_result['wins_added'], 2),
            'war_tier': war_result['war_tier'],
            'value_rating': war_result['value_rating'],
            
            # DOLLAR VALUES
            'player_value': round(player_value_adjusted, 2),
            'nil_potential': round(nil_potential, 2),
            'combined_value': round(combined_value, 2),
            'market_value': round(market_value, 2),
            
            # VALUE BREAKDOWN (V4 WAR-Based)
            'dollar_per_war': dollar_per_war_position,
            'war_based_value': round(war_based_value, 2),
            'scheme_fit_multiplier': round(scheme_multiplier, 2),
            'risk_adjustment': round(risk_adjustment, 2),
            
            # CONFIDENCE METRICS
            'war_uncertainty': round(war_uncertainty, 2),
            'value_low': round(max(10000, value_low), 2),
            'value_high': round(value_high, 2),
            'confidence_interval_pct': round(war_uncertainty, 2),
            
            # COMPONENT SCORES
            'performance_score': round(performance_score, 2),
            'scheme_fit_score': round(scheme_fit_score, 2),
            'brand_score': round(brand_score, 2),
            
            # WAR DETAILS (V4)
            'leverage_index': war_result['leverage_index'],
            'opponent_adjustment': war_result['opponent_adjustment'],
            'conference_multiplier': war_result['conference_multiplier'],
            'participation_factor': war_result['participation_factor'],
            'position_win_impact': war_result['position_win_impact'],
            'playoff_impact_pct': war_result['playoff_impact_pct'],
            
            # SAMPLE SIZE METRICS
            'snaps_played': player_data.get('snaps_played', 0),
            'games_played': player_data.get('games_played', 0),
            'games_started': player_data.get('games_started', 0),
            'snap_share': war_result['snap_share'],
            'starter_rate': war_result['starter_rate'],
            
            # FLAGS
            'limited_sample_warning': war_uncertainty >= 0.30,
            'backup_flag': war_result['participation_factor'] < 0.3,
            
            # Legacy compatibility
            'current_program_value': round(player_value_adjusted, 2),
            'total_score': round(combined_value, 2)
        }


def create_valuation_engine_v4_war():
    """Factory function for V4 WAR-driven engine"""
    # Try to use all-positions calculator first, fall back to original if not available
    try:
        from models.performance_all_positions import AllPositionsPerformanceCalculator
        performance_calc = AllPositionsPerformanceCalculator()
    except ImportError:
        from models.performance import PerformanceCalculator
        performance_calc = PerformanceCalculator()
    
    from models.scheme_fit import SchemeFitCalculator
    from models.brand_valuation import BrandValuationCalculator
    from models.cfb_war_calculator import CFBWARCalculator
    
    scheme_calc = SchemeFitCalculator()
    brand_calc = BrandValuationCalculator()
    war_calc = CFBWARCalculator()
    
    return PlayerValuationEngineV4WAR(
        performance_calc,
        scheme_calc,
        brand_calc,
        war_calc
    )


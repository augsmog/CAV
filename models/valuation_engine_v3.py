"""
Player Valuation Engine V3
Improvements:
- Sample size adjustments (penalize limited snaps)
- Game context weighting (high leverage vs garbage time)
- Opponent quality adjustments
- Confidence intervals based on sample size
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, date
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PlayerValuationEngineV3:
    """
    Enhanced valuation engine with sample size and context adjustments
    """
    
    def __init__(self,
                 performance_calculator,
                 scheme_fit_calculator,
                 brand_calculator,
                 win_impact_calculator):
        self.performance_calc = performance_calculator
        self.scheme_calc = scheme_fit_calculator
        self.brand_calc = brand_calculator
        self.win_impact_calculator = win_impact_calculator
        
        # Position base values (market rates for average starter)
        self.position_base_values = {
            'QB': 500000,
            'OL': 300000,
            'DL': 280000,
            'CB': 250000,
            'WR': 200000,
            'LB': 180000,
            'S': 170000,
            'TE': 160000,
            'RB': 150000
        }
        
        # Minimum snap thresholds for full valuation
        self.min_snaps_for_full_value = {
            'QB': 300,   # ~25% of season snaps
            'RB': 200,
            'WR': 250,
            'TE': 200,
            'OL': 400,
            'DL': 300,
            'LB': 300,
            'CB': 300,
            'S': 250
        }
        
        # Position scarcity multipliers
        self.position_scarcity = {
            'QB': 2.0,
            'OL': 1.7,
            'DL': 1.6,
            'CB': 1.5,
            'LB': 1.3,
            'WR': 1.2,
            'S': 1.2,
            'TE': 1.3,
            'RB': 1.0
        }
    
    def calculate_sample_size_confidence(self, snaps_played: int, position: str) -> float:
        """
        Calculate confidence multiplier based on sample size
        
        Returns: 0.3 - 1.0 multiplier
        - Full confidence (1.0) at minimum snap threshold
        - Reduced confidence for limited snaps
        - Minimum 0.3 for very limited action
        """
        min_snaps = self.min_snaps_for_full_value.get(position, 250)
        
        if snaps_played >= min_snaps:
            return 1.0
        elif snaps_played >= min_snaps * 0.5:
            # 50-100% of threshold: 0.7-1.0 confidence
            return 0.7 + (0.3 * (snaps_played / min_snaps))
        elif snaps_played >= min_snaps * 0.25:
            # 25-50% of threshold: 0.5-0.7 confidence
            return 0.5 + (0.2 * (snaps_played / (min_snaps * 0.5)))
        else:
            # < 25% of threshold: 0.3-0.5 confidence
            return max(0.3, 0.3 + (0.2 * (snaps_played / (min_snaps * 0.25))))
    
    def calculate_game_context_adjustment(self, player_data: Dict) -> float:
        """
        Adjust for game context (garbage time vs high leverage)
        
        Factors:
        - Score differential when player was on field
        - High leverage situations (close games, critical downs)
        - Quality of opponent
        
        Returns: 0.6 - 1.2 multiplier
        """
        # Default to neutral if no context data
        if 'high_leverage_snaps' not in player_data and 'garbage_time_snaps' not in player_data:
            return 1.0
        
        total_snaps = player_data.get('snaps_played', 1)
        if total_snaps == 0:
            return 0.6
        
        # High leverage snaps bonus
        high_leverage_snaps = player_data.get('high_leverage_snaps', total_snaps * 0.5)
        high_leverage_pct = high_leverage_snaps / total_snaps
        
        # Garbage time penalty
        garbage_time_snaps = player_data.get('garbage_time_snaps', 0)
        garbage_time_pct = garbage_time_snaps / total_snaps
        
        # Calculate adjustment
        # High leverage: +20% max
        # Garbage time: -40% max
        adjustment = 1.0 + (high_leverage_pct * 0.2) - (garbage_time_pct * 0.4)
        
        # Clamp to reasonable range
        return max(0.6, min(1.2, adjustment))
    
    def calculate_opponent_quality_adjustment(self, player_data: Dict, conference: str) -> float:
        """
        Adjust for strength of opponents faced
        
        Factors:
        - Conference strength (P5 vs G5)
        - Specific opponent rankings
        - In-conference vs out-of-conference stats
        
        Returns: 0.7 - 1.2 multiplier
        """
        # Conference strength baseline
        conference_factors = {
            'SEC': 1.15,
            'Big Ten': 1.12,
            'Big 12': 1.10,
            'ACC': 1.08,
            'Pac-12': 1.08,
            'American': 0.95,
            'Mountain West': 0.90,
            'Sun Belt': 0.88,
            'MAC': 0.85,
            'C-USA': 0.85,
            'Independent': 1.00
        }
        
        base_factor = conference_factors.get(conference, 1.0)
        
        # If we have opponent strength data, use it
        opponent_strength = player_data.get('opponent_strength', None)
        if opponent_strength:
            # opponent_strength should be 0.5 - 1.5 range
            return base_factor * opponent_strength
        
        return base_factor
    
    def calculate_comprehensive_valuation(self,
                                        player_data: Dict,
                                        current_program: str,
                                        season: int = 2023,
                                        target_programs: Optional[List[str]] = None,
                                        market_context: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive player valuation with V3 improvements
        
        New in V3:
        - Sample size confidence adjustments
        - Game context weighting
        - Opponent quality adjustments
        - Confidence intervals
        """
        position = player_data.get('position', 'Unknown')
        
        # Get position base value or default
        base_value = self.position_base_values.get(position, 150000)
        
        # ============================================================================
        # V3 ADJUSTMENTS: Sample Size & Context
        # ============================================================================
        
        snaps_played = player_data.get('snaps_played', 0)
        games_played = player_data.get('games_played', 0)
        
        # 1. Sample Size Confidence
        sample_confidence = self.calculate_sample_size_confidence(snaps_played, position)
        
        # 2. Game Context Adjustment
        context_adjustment = self.calculate_game_context_adjustment(player_data)
        
        # 3. Opponent Quality Adjustment
        conference = player_data.get('conference', 'Independent')
        opponent_adjustment = self.calculate_opponent_quality_adjustment(player_data, conference)
        
        # ============================================================================
        # PERFORMANCE SCORE (with V3 adjustments)
        # ============================================================================
        
        performance_result = self.performance_calc.calculate_performance_score(
            player_data.get('stats', {}),
            position,
            conference,
            player_data.get('opponent_strength', 1.0)
        )
        raw_performance_score = max(0, performance_result.get('overall_score', 50))
        
        # Apply V3 adjustments to performance score
        adjusted_performance_score = (
            raw_performance_score *
            sample_confidence *      # Penalize limited snaps
            context_adjustment *     # Penalize garbage time
            opponent_adjustment      # Adjust for opponent quality
        )
        
        # Clamp to 0-100
        adjusted_performance_score = max(0, min(100, adjusted_performance_score))
        
        # ============================================================================
        # SCHEME FIT SCORE
        # ============================================================================
        
        scheme_fit_result = self.scheme_calc.calculate_scheme_fit(
            player_data,
            player_data.get('current_scheme', 'Pro Style'),
            position
        )
        scheme_fit_score = max(0, scheme_fit_result.get('overall_fit_score', 70))
        
        # ============================================================================
        # PLAYER VALUE CALCULATION
        # ============================================================================
        
        # Performance Multiplier: 0.3x (limited action) to 2.0x (elite with full action)
        performance_multiplier = 0.3 + (adjusted_performance_score / 100) * 1.7
        
        # Scheme Fit Multiplier: 0.9x (poor fit) to 1.15x (perfect fit)
        scheme_fit_multiplier = 0.9 + (scheme_fit_score / 100) * 0.25
        
        # Position Scarcity Multiplier
        scarcity_multiplier = self.position_scarcity.get(position, 1.0)
        
        # Calculate base player value
        player_value = (
            base_value *
            performance_multiplier *
            scheme_fit_multiplier *
            scarcity_multiplier
        )
        
        # Ensure minimum value
        player_value = max(10000, player_value)
        
        # ============================================================================
        # NIL POTENTIAL
        # ============================================================================
        
        brand_result = self.brand_calc.calculate_brand_score(
            player_data,
            current_program,
            adjusted_performance_score  # Use adjusted performance
        )
        brand_score = max(0, brand_result.get('brand_score', 0))
        
        nil_estimate = brand_result.get('nil_value_estimate', {})
        nil_potential = nil_estimate.get('annual_expected', 0)
        
        # NIL floor based on position and performance
        if adjusted_performance_score > 70:
            nil_floor = 25000 if position == 'QB' else 15000
        else:
            nil_floor = 5000
        
        nil_potential = max(nil_floor, nil_potential)
        
        # ============================================================================
        # RISK FACTORS
        # ============================================================================
        
        injury_history = player_data.get('injury_history', [])
        injury_risk = len(injury_history) * 0.05
        risk_adjustment = max(0.7, 1.0 - injury_risk)
        
        player_value_adjusted = player_value * risk_adjustment
        
        # ============================================================================
        # CONFIDENCE INTERVAL
        # ============================================================================
        
        # Calculate value confidence based on sample size
        # More snaps = tighter confidence interval
        if snaps_played >= self.min_snaps_for_full_value.get(position, 250):
            confidence_interval_pct = 0.15  # ±15% for full sample
        elif snaps_played >= self.min_snaps_for_full_value.get(position, 250) * 0.5:
            confidence_interval_pct = 0.30  # ±30% for partial sample
        else:
            confidence_interval_pct = 0.50  # ±50% for limited sample
        
        value_low = player_value_adjusted * (1 - confidence_interval_pct)
        value_high = player_value_adjusted * (1 + confidence_interval_pct)
        
        # ============================================================================
        # COMBINED METRICS
        # ============================================================================
        
        combined_value = player_value_adjusted + nil_potential
        market_value = player_value_adjusted * 1.1
        
        return {
            # Player Identity
            'player_id': player_data.get('player_id', 'unknown'),
            'player_name': player_data.get('name', 'Unknown'),
            'position': position,
            'team': current_program,
            'season': season,
            'valuation_date': date.today().isoformat(),
            
            # PRIMARY VALUES
            'player_value': round(player_value_adjusted, 2),
            'nil_potential': round(nil_potential, 2),
            'combined_value': round(combined_value, 2),
            'market_value': round(market_value, 2),
            
            # CONFIDENCE METRICS (V3)
            'sample_confidence': round(sample_confidence, 2),
            'confidence_interval_pct': round(confidence_interval_pct, 2),
            'value_low': round(value_low, 2),
            'value_high': round(value_high, 2),
            
            # Component Scores
            'raw_performance_score': round(raw_performance_score, 2),
            'adjusted_performance_score': round(adjusted_performance_score, 2),
            'performance_score': round(adjusted_performance_score, 2),  # For compatibility
            'scheme_fit_score': round(scheme_fit_score, 2),
            'brand_score': round(brand_score, 2),
            
            # V3 ADJUSTMENT FACTORS
            'snaps_played': snaps_played,
            'games_played': games_played,
            'sample_size_adjustment': round(sample_confidence, 2),
            'context_adjustment': round(context_adjustment, 2),
            'opponent_adjustment': round(opponent_adjustment, 2),
            'risk_adjustment': round(risk_adjustment, 2),
            
            # Warnings/Flags
            'limited_sample_warning': snaps_played < self.min_snaps_for_full_value.get(position, 250) * 0.5,
            'backup_flag': snaps_played < self.min_snaps_for_full_value.get(position, 250) * 0.3,
            
            # Legacy compatibility
            'current_program_value': round(player_value_adjusted, 2),
            'total_score': round(combined_value, 2)
        }


def create_valuation_engine_v3():
    """Factory function to create V3 valuation engine"""
    from models.performance import PerformanceCalculator, WinImpactCalculator
    from models.scheme_fit import SchemeFitCalculator
    from models.brand_valuation import BrandValuationCalculator
    
    performance_calc = PerformanceCalculator()
    scheme_calc = SchemeFitCalculator()
    brand_calc = BrandValuationCalculator()
    win_calc = WinImpactCalculator()
    
    return PlayerValuationEngineV3(
        performance_calc,
        scheme_calc,
        brand_calc,
        win_calc
    )


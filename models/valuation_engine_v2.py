"""
Improved Player Valuation Engine V2
Separates:
- Player Valuation (what schools/collectives pay for on-field value)
- NIL Potential (what players can earn through marketing/endorsements)
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, date
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PlayerValuationEngineV2:
    """
    Improved valuation engine with separated player value and NIL potential
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
            'QB': 500000,   # Quarterbacks command premium
            'OL': 300000,   # Offensive line
            'DL': 280000,   # Defensive line
            'CB': 250000,   # Cornerbacks
            'WR': 200000,   # Wide receivers
            'LB': 180000,   # Linebackers
            'S': 170000,    # Safeties
            'TE': 160000,   # Tight ends
            'RB': 150000    # Running backs (most abundant)
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
    
    def calculate_comprehensive_valuation(self,
                                        player_data: Dict,
                                        current_program: str,
                                        target_programs: Optional[List[str]] = None,
                                        market_context: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive player valuation with separated components
        
        Returns:
            Dictionary with:
            - player_value: What schools/collectives pay (performance-based)
            - nil_potential: What player can earn via marketing (brand-based)
            - combined_value: Total opportunity value
        """
        position = player_data.get('position', 'Unknown')
        
        # Get position base value or default
        base_value = self.position_base_values.get(position, 150000)
        
        # ============================================================================
        # 1. PLAYER VALUE (What Schools/Collectives Pay)
        # ============================================================================
        
        # Performance Score (0-100)
        performance_result = self.performance_calc.calculate_performance_score(
            player_data.get('stats', {}),
            position,
            player_data.get('conference', 'Independent'),
            player_data.get('opponent_strength', 1.0)
        )
        performance_score = max(0, performance_result.get('overall_score', 50))  # Floor at 0
        
        # Scheme Fit Score (0-100)
        scheme_fit_result = self.scheme_calc.calculate_scheme_fit(
            player_data,
            player_data.get('current_scheme', 'Pro Style'),
            position
        )
        scheme_fit_score = max(0, scheme_fit_result.get('overall_fit_score', 70))  # Floor at 0
        
        # Calculate player value components
        # Performance Multiplier: 0.5x (terrible) to 2.0x (elite)
        performance_multiplier = 0.5 + (performance_score / 100) * 1.5
        
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
        
        # Ensure minimum value (no negative or zero values)
        player_value = max(10000, player_value)  # Minimum $10K
        
        # ============================================================================
        # 2. NIL POTENTIAL (What Player Can Earn Through Marketing)
        # ============================================================================
        
        # Brand/NIL calculation (completely separate)
        brand_result = self.brand_calc.calculate_brand_score(
            player_data,
            current_program,
            performance_score
        )
        brand_score = max(0, brand_result.get('brand_score', 0))  # Floor at 0
        
        nil_estimate = brand_result.get('nil_value_estimate', {})
        nil_potential = nil_estimate.get('annual_expected', 0)
        
        # NIL floor based on position and performance
        if performance_score > 70:  # Good players have baseline NIL
            nil_floor = 25000 if position == 'QB' else 15000
        else:
            nil_floor = 5000
        
        nil_potential = max(nil_floor, nil_potential)
        
        # ============================================================================
        # 3. ADDITIONAL CONTEXT METRICS
        # ============================================================================
        
        # Win Impact (WAR)
        try:
            war_result = self.win_impact_calculator.calculate_war(
                performance_score,
                position,
                player_data.get('snaps_played', 0),
                player_data.get('team_total_snaps', 800),
                player_data.get('team_wins', 0),
                player_data.get('team_losses', 0)
            )
            war = war_result.get('war', 0)
        except:
            war = 0
        
        # Risk factors
        injury_history = player_data.get('injury_history', [])
        injury_risk = len(injury_history) * 0.05  # 5% reduction per injury
        risk_adjustment = max(0.7, 1.0 - injury_risk)  # Floor at 70%
        
        # Apply risk adjustment to player value only
        player_value_adjusted = player_value * risk_adjustment
        
        # ============================================================================
        # 4. COMBINED METRICS
        # ============================================================================
        
        combined_value = player_value_adjusted + nil_potential
        
        # Market value (average of what top programs would pay)
        market_value = player_value_adjusted * 1.1  # 10% premium for competition
        
        return {
            # Player Identity
            'player_id': player_data.get('player_id', 'unknown'),
            'player_name': player_data.get('name', 'Unknown'),
            'position': position,
            'team': current_program,
            'valuation_date': date.today().isoformat(),
            
            # PRIMARY VALUES (Separated)
            'player_value': round(player_value_adjusted, 2),  # What schools pay
            'nil_potential': round(nil_potential, 2),          # What player earns
            'combined_value': round(combined_value, 2),        # Total opportunity
            'market_value': round(market_value, 2),            # Expected market rate
            
            # Component Scores (0-100 scale)
            'performance_score': round(performance_score, 2),
            'scheme_fit_score': round(scheme_fit_score, 2),
            'brand_score': round(brand_score, 2),
            
            # Additional Metrics
            'win_impact_score': round(war * 20, 2),  # Scale WAR to 0-100
            'risk_adjustment': round(risk_adjustment, 2),
            
            # Breakdowns
            'value_breakdown': {
                'base_position_value': base_value,
                'performance_multiplier': round(performance_multiplier, 2),
                'scheme_fit_multiplier': round(scheme_fit_multiplier, 2),
                'scarcity_multiplier': round(scarcity_multiplier, 2),
                'risk_adjustment': round(risk_adjustment, 2)
            },
            
            # Context
            'scheme_fit_details': scheme_fit_result,
            'performance_details': performance_result,
            
            # Legacy compatibility
            'current_program_value': round(player_value_adjusted, 2),
            'total_score': round(combined_value, 2)
        }


def create_valuation_engine_v2():
    """Factory function to create valuation engine with all dependencies"""
    from models.performance import PerformanceCalculator, WinImpactCalculator
    from models.scheme_fit import SchemeFitCalculator
    from models.brand_valuation import BrandValuationCalculator
    
    performance_calc = PerformanceCalculator()
    scheme_calc = SchemeFitCalculator()
    brand_calc = BrandValuationCalculator()
    win_calc = WinImpactCalculator()
    
    return PlayerValuationEngineV2(
        performance_calc,
        scheme_calc,
        brand_calc,
        win_calc
    )


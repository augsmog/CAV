"""
Comprehensive Player Valuation Engine
Integrates performance, scheme fit, brand, and market dynamics
to produce complete player valuations
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, date
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PlayerValuationEngine:
    """
    Main valuation engine that combines all components
    """
    
    def __init__(self,
                 performance_calculator,
                 scheme_fit_calculator,
                 brand_calculator,
                 win_impact_calculator):
        self.performance_calc = performance_calculator
        self.scheme_calc = scheme_fit_calculator
        self.brand_calc = brand_calculator
        self.win_calc = win_impact_calculator
        
        # Risk factors
        self.injury_risk_weights = self._initialize_injury_weights()
        self.position_scarcity = self._initialize_position_scarcity()
    
    def _initialize_injury_weights(self) -> Dict:
        """Position-specific injury risk multipliers"""
        return {
            'QB': 1.2,
            'RB': 1.5,  # Highest injury risk
            'WR': 1.1,
            'TE': 1.2,
            'OL': 1.3,
            'DL': 1.3,
            'LB': 1.4,
            'CB': 1.0,
            'S': 1.1
        }
    
    def _initialize_position_scarcity(self) -> Dict:
        """Position scarcity multipliers (supply/demand)"""
        return {
            'QB': 2.0,  # Most scarce, highest premium
            'OL': 1.7,
            'DL': 1.6,
            'CB': 1.5,
            'LB': 1.3,
            'WR': 1.2,
            'S': 1.2,
            'TE': 1.3,
            'RB': 1.0  # Most abundant
        }
    
    def calculate_comprehensive_valuation(self,
                                        player_data: Dict,
                                        current_program: str,
                                        target_programs: Optional[List[str]] = None,
                                        market_context: Optional[Dict] = None) -> Dict:
        """
        Calculate complete player valuation
        
        Args:
            player_data: All player information (bio, stats, brand, etc.)
            current_program: Current school
            target_programs: List of potential transfer destinations
            market_context: Transfer portal market conditions
            
        Returns:
            Comprehensive valuation with all components
        """
        position = player_data['position']
        
        # 1. Performance Valuation
        performance_result = self.performance_calc.calculate_performance_score(
            player_data.get('stats', {}),
            position,
            player_data.get('conference', 'Independent'),
            player_data.get('opponent_strength', 1.0)
        )
        performance_score = performance_result['overall_score']
        
        # 2. Scheme Fit for Current Program
        current_scheme_fit = self.scheme_calc.calculate_scheme_fit(
            player_data,
            player_data.get('current_scheme', 'Pro Style'),
            position
        )
        
        # 3. Brand/NIL Valuation
        brand_result = self.brand_calc.calculate_brand_score(
            player_data,
            current_program,
            performance_score
        )
        brand_score = brand_result['brand_score']
        nil_estimate = brand_result['nil_value_estimate']
        
        # 4. Win Impact
        war_result = self.win_calc.calculate_war(
            performance_score,
            position,
            player_data.get('snaps_played', 0),
            player_data.get('team_total_snaps', 800),
            player_data.get('team_wins', 0),
            player_data.get('team_losses', 0)
        )
        
        # 5. Positional Value
        positional_value_score = self._calculate_positional_value(
            position,
            player_data,
            market_context
        )
        
        # 6. Risk Assessment
        risk_factors = self._calculate_risk_factors(
            player_data,
            position,
            performance_result
        )
        
        # 7. Current Program Value
        current_program_value = self._calculate_program_value(
            performance_score,
            brand_score,
            current_scheme_fit['overall_fit_score'],
            positional_value_score,
            war_result['war'],
            current_program,
            player_data,
            is_current=True
        )
        
        # 8. Transfer Portal Market Value
        market_value = self._calculate_market_value(
            performance_score,
            brand_score,
            positional_value_score,
            war_result['war'],
            player_data,
            market_context
        )
        
        # 9. Alternative Program Valuations
        alternative_valuations = {}
        if target_programs:
            alternative_valuations = self._calculate_alternative_program_values(
                player_data,
                target_programs,
                performance_score,
                brand_score,
                positional_value_score,
                war_result['war']
            )
        
        # 10. Value Confidence Intervals
        confidence_intervals = self._calculate_confidence_intervals(
            market_value,
            risk_factors,
            player_data
        )
        
        # 11. Identify Key Value Drivers
        value_drivers = self._identify_value_drivers(
            performance_score,
            brand_score,
            current_scheme_fit['overall_fit_score'],
            positional_value_score,
            war_result,
            player_data
        )
        
        return {
            'player_id': player_data.get('player_id', 'unknown'),
            'player_name': player_data.get('name', 'Unknown'),
            'position': position,
            'valuation_date': date.today().isoformat(),
            'current_program': current_program,
            
            # Component Scores
            'performance_score': performance_score,
            'brand_score': brand_score,
            'scheme_fit_score': current_scheme_fit['overall_fit_score'],
            'positional_value_score': positional_value_score,
            'win_impact_score': war_result['war'] * 20,  # Scale to 0-100
            
            # Risk Factors
            'injury_risk_factor': risk_factors['injury_risk'],
            'performance_risk_factor': risk_factors['performance_risk'],
            'off_field_risk_factor': risk_factors['off_field_risk'],
            'total_risk_score': risk_factors['total_risk'],
            
            # Final Valuations
            'current_program_value': current_program_value,
            'market_value': market_value,
            'value_confidence_interval': confidence_intervals,
            
            # NIL Information
            'nil_value_estimate': nil_estimate,
            
            # Alternative Programs
            'alternative_program_values': alternative_valuations,
            
            # Detailed Breakdowns
            'performance_details': performance_result,
            'scheme_fit_details': current_scheme_fit,
            'brand_details': brand_result,
            'war_details': war_result,
            'risk_details': risk_factors,
            
            # Value Drivers
            'key_value_drivers': value_drivers['key_drivers'],
            'value_component_breakdown': value_drivers['component_values'],
            
            # Recommendations
            'transfer_recommendation': self._generate_transfer_recommendation(
                current_program_value,
                market_value,
                alternative_valuations,
                risk_factors
            ),
            
            'model_version': '1.0',
            'notes': ''
        }
    
    def _calculate_positional_value(self,
                                   position: str,
                                   player_data: Dict,
                                   market_context: Optional[Dict]) -> float:
        """
        Calculate positional value considering scarcity and strategic importance
        """
        base_scarcity = self.position_scarcity.get(position, 1.0)
        
        # Adjust for market conditions
        if market_context and 'position_supply' in market_context:
            position_supply = market_context['position_supply'].get(position, 1.0)
            # Lower supply = higher value
            scarcity_adjustment = 2.0 - position_supply
        else:
            scarcity_adjustment = 1.0
        
        # Depth chart position matters
        depth_position = player_data.get('depth_chart_position', 2)
        if depth_position == 1:
            depth_multiplier = 1.5
        elif depth_position == 2:
            depth_multiplier = 1.0
        else:
            depth_multiplier = 0.6
        
        # Years of eligibility
        eligibility = player_data.get('eligibility_remaining', 1)
        eligibility_multiplier = 1.0 + (eligibility - 1) * 0.1  # Bonus for more years
        
        positional_value = (base_scarcity * scarcity_adjustment * 
                          depth_multiplier * eligibility_multiplier)
        
        # Normalize to 0-100 scale
        normalized_value = min(positional_value * 25, 100)
        
        return normalized_value
    
    def _calculate_risk_factors(self,
                               player_data: Dict,
                               position: str,
                               performance_result: Dict) -> Dict:
        """
        Calculate comprehensive risk assessment
        """
        # 1. Injury Risk
        injury_history = player_data.get('injury_history', [])
        games_missed = sum([inj.get('games_missed', 0) for inj in injury_history])
        
        position_injury_weight = self.injury_risk_weights.get(position, 1.0)
        
        if games_missed == 0:
            injury_risk = 0.9  # Low risk
        elif games_missed < 3:
            injury_risk = 1.0  # Average risk
        elif games_missed < 6:
            injury_risk = 1.2  # Elevated risk
        else:
            injury_risk = 1.5  # High risk
        
        injury_risk *= position_injury_weight
        
        # 2. Performance Risk
        consistency = performance_result.get('adjustments', {}).get('consistency_factor', 1.0)
        
        # Check for declining trajectory
        career_trend = player_data.get('career_trajectory', {})
        if career_trend.get('trend') == 'declining':
            performance_risk = 1.3
        elif career_trend.get('trend') == 'rapidly_declining':
            performance_risk = 1.5
        elif consistency < 0.95:
            performance_risk = 1.2  # Inconsistent
        else:
            performance_risk = 1.0
        
        # 3. Off-Field Risk
        controversies = player_data.get('controversies', 0)
        academic_issues = player_data.get('academic_concerns', False)
        
        if controversies > 2 or academic_issues:
            off_field_risk = 1.4
        elif controversies > 0:
            off_field_risk = 1.2
        else:
            off_field_risk = 1.0
        
        # Total risk score (lower is better)
        total_risk = (injury_risk * 0.4 + 
                     performance_risk * 0.4 + 
                     off_field_risk * 0.2)
        
        return {
            'injury_risk': injury_risk,
            'performance_risk': performance_risk,
            'off_field_risk': off_field_risk,
            'total_risk': total_risk,
            'risk_category': self._categorize_risk(total_risk)
        }
    
    def _categorize_risk(self, total_risk: float) -> str:
        """Categorize overall risk level"""
        if total_risk < 1.0:
            return "Low Risk"
        elif total_risk < 1.15:
            return "Average Risk"
        elif total_risk < 1.3:
            return "Elevated Risk"
        else:
            return "High Risk"
    
    def _calculate_program_value(self,
                                performance_score: float,
                                brand_score: float,
                                scheme_fit_score: float,
                                positional_value_score: float,
                                war: float,
                                program: str,
                                player_data: Dict,
                                is_current: bool = False) -> float:
        """
        Calculate total value to a specific program
        Combines all factors into dollar value
        """
        # Base value from performance
        base_value = performance_score * 5000  # $5k per performance point
        
        # Brand/NIL value addition
        nil_value = self.brand_calc.calculate_brand_score(
            player_data,
            program,
            performance_score
        )['nil_value_estimate']['annual_expected']
        
        # Scheme fit multiplier
        fit_multiplier = 0.8 + (scheme_fit_score / 100) * 0.4  # 0.8 to 1.2 range
        
        # Positional value addition
        position_value = positional_value_score * 3000  # $3k per position value point
        
        # Win impact value (revenue per win consideration)
        program_revenue_per_win = self._get_program_revenue_per_win(program)
        win_value = war * program_revenue_per_win
        
        # Current program loyalty/familiarity bonus
        if is_current:
            familiarity_bonus = base_value * 0.15
        else:
            familiarity_bonus = 0
        
        # Total value calculation
        total_value = (
            (base_value + position_value) * fit_multiplier +
            nil_value +
            win_value +
            familiarity_bonus
        )
        
        # Years of eligibility multiplier
        years_remaining = player_data.get('eligibility_remaining', 1)
        
        # Return annual value
        return total_value
    
    def _calculate_market_value(self,
                               performance_score: float,
                               brand_score: float,
                               positional_value_score: float,
                               war: float,
                               player_data: Dict,
                               market_context: Optional[Dict]) -> float:
        """
        Calculate expected transfer portal market value
        This is what programs would likely pay
        """
        # Average value across top programs
        top_programs = ['Alabama', 'Georgia', 'Ohio State', 'Michigan', 
                       'Texas', 'USC', 'Oregon']
        
        program_values = []
        for prog in top_programs:
            value = self._calculate_program_value(
                performance_score,
                brand_score,
                75,  # Assume reasonable fit
                positional_value_score,
                war,
                prog,
                player_data,
                is_current=False
            )
            program_values.append(value)
        
        # Market value is around 75th percentile
        market_value = np.percentile(program_values, 75)
        
        # Adjust for market conditions
        if market_context:
            supply_demand_ratio = market_context.get('supply_demand_ratio', 1.0)
            market_value *= (2.0 - supply_demand_ratio)  # More demand = higher value
        
        return market_value
    
    def _calculate_alternative_program_values(self,
                                            player_data: Dict,
                                            target_programs: List[str],
                                            performance_score: float,
                                            brand_score: float,
                                            positional_value_score: float,
                                            war: float) -> Dict:
        """
        Calculate value to each alternative program
        """
        valuations = {}
        position = player_data['position']
        
        for program in target_programs:
            # Get program's scheme
            program_scheme = self._get_program_scheme(program)
            
            # Calculate scheme fit for this program
            scheme_fit = self.scheme_calc.calculate_scheme_fit(
                player_data,
                program_scheme,
                position
            )
            
            # Calculate value to this program
            program_value = self._calculate_program_value(
                performance_score,
                brand_score,
                scheme_fit['overall_fit_score'],
                positional_value_score,
                war,
                program,
                player_data,
                is_current=False
            )
            
            # NIL comparison
            nil_comparison = self.brand_calc.compare_nil_markets(
                player_data,
                player_data.get('current_program', ''),
                [program],
                performance_score
            )
            
            valuations[program] = {
                'total_value': program_value,
                'scheme_fit_score': scheme_fit['overall_fit_score'],
                'nil_potential': nil_comparison['comparisons'][program]['nil_value'],
                'scheme_notes': scheme_fit.get('scheme_specific_notes', ''),
                'key_strengths': scheme_fit.get('key_strengths', []),
                'key_concerns': scheme_fit.get('key_concerns', [])
            }
        
        return valuations
    
    def _calculate_confidence_intervals(self,
                                      market_value: float,
                                      risk_factors: Dict,
                                      player_data: Dict) -> tuple:
        """
        Calculate confidence intervals for valuation
        """
        # Base uncertainty
        base_uncertainty = 0.25  # 25% base uncertainty
        
        # Increase uncertainty based on risk
        total_risk = risk_factors['total_risk']
        risk_uncertainty = (total_risk - 1.0) * 0.3
        
        # Data completeness affects confidence
        data_completeness = self._assess_data_completeness(player_data)
        data_uncertainty = (1.0 - data_completeness) * 0.2
        
        # Total uncertainty
        total_uncertainty = base_uncertainty + risk_uncertainty + data_uncertainty
        
        # Calculate intervals
        low_value = market_value * (1 - total_uncertainty)
        high_value = market_value * (1 + total_uncertainty)
        
        return (round(low_value, -3), round(high_value, -3))
    
    def _assess_data_completeness(self, player_data: Dict) -> float:
        """Assess how complete the player data is"""
        required_fields = [
            'stats', 'height', 'weight', 'position', 'snaps_played',
            'instagram_followers', 'twitter_followers', 'film_grade'
        ]
        
        completeness = sum([1 for field in required_fields if field in player_data and player_data[field]]) / len(required_fields)
        return completeness
    
    def _identify_value_drivers(self,
                               performance_score: float,
                               brand_score: float,
                               scheme_fit_score: float,
                               positional_value_score: float,
                               war_result: Dict,
                               player_data: Dict) -> Dict:
        """
        Identify what's driving the player's value
        """
        components = {
            'Performance': performance_score,
            'Brand/NIL': brand_score,
            'Scheme Fit': scheme_fit_score,
            'Positional Value': positional_value_score,
            'Win Impact': war_result['war'] * 20
        }
        
        # Sort by value
        sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
        
        # Top 3 drivers
        key_drivers = [f"{comp[0]} ({comp[1]:.1f})" for comp in sorted_components[:3]]
        
        return {
            'key_drivers': key_drivers,
            'component_values': components
        }
    
    def _generate_transfer_recommendation(self,
                                        current_value: float,
                                        market_value: float,
                                        alternative_values: Dict,
                                        risk_factors: Dict) -> Dict:
        """
        Generate recommendation about transfer portal decision
        """
        if not alternative_values:
            return {
                'recommendation': 'Stay',
                'confidence': 'Medium',
                'reasoning': 'Insufficient data on alternative programs'
            }
        
        # Find best alternative
        best_alt = max(alternative_values.items(), key=lambda x: x[1]['total_value'])
        best_program = best_alt[0]
        best_value = best_alt[1]['total_value']
        
        # Value differential
        value_gain = best_value - current_value
        percent_gain = (value_gain / current_value) * 100
        
        # Risk assessment
        risk_level = risk_factors['risk_category']
        
        # Decision logic
        if percent_gain > 30 and risk_level in ['Low Risk', 'Average Risk']:
            recommendation = 'Strong Transfer'
            confidence = 'High'
            reasoning = f"Significant value increase ({percent_gain:.1f}%) at {best_program} with acceptable risk"
        elif percent_gain > 15 and risk_level in ['Low Risk', 'Average Risk']:
            recommendation = 'Consider Transfer'
            confidence = 'Medium'
            reasoning = f"Moderate value increase ({percent_gain:.1f}%) possible at {best_program}"
        elif percent_gain > 0:
            recommendation = 'Marginal Transfer'
            confidence = 'Low'
            reasoning = f"Small value increase ({percent_gain:.1f}%), current program may be preferable"
        else:
            recommendation = 'Stay'
            confidence = 'High'
            reasoning = "Current program provides best value opportunity"
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'reasoning': reasoning,
            'best_alternative': best_program,
            'projected_value_gain': value_gain,
            'percent_value_gain': percent_gain
        }
    
    def _get_program_revenue_per_win(self, program: str) -> float:
        """Estimate program's revenue per win"""
        # Top tier programs
        tier_1 = ['Alabama', 'Ohio State', 'Texas', 'Michigan', 'Georgia', 
                 'Notre Dame', 'USC', 'Texas A&M']
        tier_2 = ['Penn State', 'Florida', 'LSU', 'Oregon', 'Oklahoma',
                 'Clemson', 'Florida State', 'Miami']
        
        if program in tier_1:
            return 5000000  # $5M per win
        elif program in tier_2:
            return 3000000  # $3M per win
        else:
            return 2000000  # $2M per win
    
    def _get_program_scheme(self, program: str) -> str:
        """Get program's primary offensive/defensive scheme"""
        # Would be a comprehensive database lookup
        scheme_map = {
            'Alabama': 'Pro Style',
            'Georgia': 'Pro Style',
            'Ohio State': 'Spread',
            'Michigan': 'Pro Style',
            'Oregon': 'Spread',
            'Texas': 'Spread',
            'USC': 'Air Raid',
            # etc...
        }
        return scheme_map.get(program, 'Pro Style')


def create_valuation_engine():
    """Factory function to create a configured valuation engine"""
    from models.performance import PerformanceCalculator, WinImpactCalculator
    from models.scheme_fit import SchemeFitCalculator
    from models.brand_valuation import BrandValuationCalculator
    
    performance_calc = PerformanceCalculator()
    scheme_calc = SchemeFitCalculator()
    brand_calc = BrandValuationCalculator()
    win_calc = WinImpactCalculator()
    
    return PlayerValuationEngine(
        performance_calc,
        scheme_calc,
        brand_calc,
        win_calc
    )

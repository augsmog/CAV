"""
Performance Metrics Module
Calculates and normalizes player performance metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PositionBenchmarks:
    """Statistical benchmarks by position"""
    position: str
    elite_threshold: Dict[str, float]  # 90th percentile
    good_threshold: Dict[str, float]   # 70th percentile
    average_threshold: Dict[str, float]  # 50th percentile


class PerformanceCalculator:
    """
    Calculates comprehensive performance scores for players
    """
    
    def __init__(self):
        self.position_weights = self._initialize_position_weights()
        self.benchmarks = self._initialize_benchmarks()
    
    def _initialize_position_weights(self) -> Dict:
        """Define how different stats contribute to overall performance score"""
        return {
            'QB': {
                'completion_percentage': 0.15,
                'yards_per_attempt': 0.20,
                'td_int_ratio': 0.15,
                'qbr': 0.15,
                'success_rate': 0.15,
                'epa_per_play': 0.20
            },
            'RB': {
                'yards_per_carry': 0.25,
                'yards_after_contact': 0.20,
                'success_rate': 0.20,
                'receiving_grade': 0.15,
                'epa_per_play': 0.20
            },
            'WR': {
                'yards_per_route_run': 0.25,
                'catch_rate': 0.15,
                'yards_after_catch': 0.15,
                'contested_catch_rate': 0.15,
                'separation_score': 0.15,
                'drop_rate': 0.15
            },
            'TE': {
                'yards_per_route_run': 0.20,
                'blocking_grade': 0.25,
                'catch_rate': 0.15,
                'yards_after_catch': 0.15,
                'versatility_score': 0.25
            },
            'OL': {
                'pass_block_grade': 0.35,
                'run_block_grade': 0.35,
                'pressure_rate_allowed': 0.15,
                'penalty_rate': 0.15
            },
            'DL': {
                'pressure_rate': 0.30,
                'run_stop_rate': 0.25,
                'pass_rush_win_rate': 0.25,
                'tackle_efficiency': 0.20
            },
            'LB': {
                'tackle_efficiency': 0.25,
                'coverage_grade': 0.25,
                'run_defense_grade': 0.25,
                'pass_rush_grade': 0.15,
                'versatility_score': 0.10
            },
            'CB': {
                'coverage_grade': 0.35,
                'completion_pct_allowed': 0.20,
                'yards_per_coverage_snap': 0.20,
                'interception_rate': 0.15,
                'penalty_rate': 0.10
            },
            'S': {
                'coverage_grade': 0.30,
                'run_defense_grade': 0.25,
                'tackle_efficiency': 0.20,
                'versatility_score': 0.25
            }
        }
    
    def _initialize_benchmarks(self) -> Dict:
        """Initialize statistical benchmarks (would be populated from historical data)"""
        # These are placeholder values - would be calculated from actual data
        return {
            'QB': {
                'completion_percentage': {'elite': 70, 'good': 65, 'avg': 60},
                'yards_per_attempt': {'elite': 9.0, 'good': 8.0, 'avg': 7.0},
                'td_int_ratio': {'elite': 4.0, 'good': 2.5, 'avg': 1.5},
            },
            # Additional benchmarks would be defined for each position
        }
    
    def calculate_performance_score(self, 
                                   player_stats: Dict,
                                   position: str,
                                   conference: str,
                                   opponent_strength: float = 1.0) -> Dict:
        """
        Calculate comprehensive performance score
        
        Args:
            player_stats: Dictionary of player statistics
            position: Player position
            conference: Conference for adjustment factors
            opponent_strength: Strength of schedule multiplier
            
        Returns:
            Dictionary with overall score and component breakdowns
        """
        if position not in self.position_weights:
            raise ValueError(f"Position {position} not supported")
        
        weights = self.position_weights[position]
        component_scores = {}
        
        # Calculate each component score
        for stat_name, weight in weights.items():
            if stat_name in player_stats:
                raw_value = player_stats[stat_name]
                normalized_score = self._normalize_stat(stat_name, raw_value, position)
                component_scores[stat_name] = normalized_score * weight
        
        # Base performance score
        base_score = sum(component_scores.values()) * 100
        
        # Apply conference adjustment
        conference_factor = self._get_conference_adjustment(conference)
        
        # Apply strength of schedule adjustment
        sos_adjusted_score = base_score * opponent_strength
        
        # Apply conference competitiveness
        final_score = sos_adjusted_score * conference_factor
        
        # Add consistency penalty/bonus
        if 'game_by_game_variance' in player_stats:
            consistency_factor = self._calculate_consistency_factor(
                player_stats['game_by_game_variance']
            )
            final_score *= consistency_factor
        
        return {
            'overall_score': min(final_score, 100),  # Cap at 100
            'base_score': base_score,
            'sos_adjusted': sos_adjusted_score,
            'component_scores': component_scores,
            'adjustments': {
                'conference_factor': conference_factor,
                'opponent_strength': opponent_strength,
                'consistency_factor': consistency_factor if 'game_by_game_variance' in player_stats else 1.0
            }
        }
    
    def _normalize_stat(self, stat_name: str, value: float, position: str) -> float:
        """
        Normalize a stat to 0-1 scale based on position benchmarks
        """
        if position not in self.benchmarks:
            return 0.5  # Default to average if no benchmarks
        
        if stat_name not in self.benchmarks[position]:
            return 0.5
        
        benchmarks = self.benchmarks[position][stat_name]
        
        # Linear interpolation between benchmarks
        if value >= benchmarks['elite']:
            return 1.0
        elif value >= benchmarks['good']:
            # Between good and elite
            range_size = benchmarks['elite'] - benchmarks['good']
            position_in_range = value - benchmarks['good']
            return 0.7 + (0.3 * (position_in_range / range_size))
        elif value >= benchmarks['avg']:
            # Between average and good
            range_size = benchmarks['good'] - benchmarks['avg']
            position_in_range = value - benchmarks['avg']
            return 0.5 + (0.2 * (position_in_range / range_size))
        else:
            # Below average
            return 0.5 * (value / benchmarks['avg'])
    
    def _get_conference_adjustment(self, conference: str) -> float:
        """
        Adjust scores based on conference strength
        """
        conference_factors = {
            'SEC': 1.10,
            'Big Ten': 1.08,
            'Big 12': 1.05,
            'ACC': 1.03,
            'Pac-12': 1.02,
            'American': 0.95,
            'Mountain West': 0.92,
            'Sun Belt': 0.90,
            'MAC': 0.88,
            'CUSA': 0.85,
            'Independent': 1.00
        }
        return conference_factors.get(conference, 1.0)
    
    def _calculate_consistency_factor(self, variance: float) -> float:
        """
        Reward consistency, penalize high variance
        variance is coefficient of variation (std dev / mean)
        """
        if variance < 0.15:  # Very consistent
            return 1.10
        elif variance < 0.25:  # Moderately consistent
            return 1.05
        elif variance < 0.40:  # Average consistency
            return 1.00
        elif variance < 0.60:  # Somewhat inconsistent
            return 0.95
        else:  # Very inconsistent
            return 0.90
    
    def calculate_clutch_performance(self, 
                                    clutch_stats: Dict,
                                    regular_stats: Dict) -> float:
        """
        Calculate clutch performance bonus/penalty
        Compare performance in high-leverage situations vs regular
        """
        clutch_score = 0
        
        if 'success_rate_4th_quarter' in clutch_stats:
            clutch_vs_regular = (clutch_stats['success_rate_4th_quarter'] / 
                                regular_stats.get('success_rate', 0.5))
            clutch_score += (clutch_vs_regular - 1.0) * 10  # +/- 10 points max
        
        if 'success_rate_3rd_down' in clutch_stats:
            third_down_factor = clutch_stats['success_rate_3rd_down'] / 0.40  # 40% is average
            clutch_score += (third_down_factor - 1.0) * 5
        
        if 'red_zone_efficiency' in clutch_stats:
            rz_factor = clutch_stats['red_zone_efficiency'] / 0.55  # 55% is average
            clutch_score += (rz_factor - 1.0) * 5
        
        return np.clip(clutch_score, -10, 10)  # Cap bonus/penalty


class WinImpactCalculator:
    """
    Calculate a player's contribution to team wins
    Similar to WAR (Wins Above Replacement) in baseball
    """
    
    def calculate_war(self,
                     player_performance_score: float,
                     position: str,
                     snaps_played: int,
                     team_total_snaps: int,
                     team_wins: int,
                     team_losses: int) -> Dict:
        """
        Calculate Wins Above Replacement
        """
        # Position importance multipliers
        position_multipliers = {
            'QB': 3.5,
            'WR': 1.2,
            'RB': 1.3,
            'TE': 1.1,
            'OL': 1.8,
            'DL': 2.0,
            'LB': 1.5,
            'CB': 1.6,
            'S': 1.3,
            'SPEC': 0.8
        }
        
        # Snap share calculation
        snap_share = snaps_played / max(team_total_snaps, 1)
        
        # Replacement level is approximately 40th percentile
        replacement_level = 40
        performance_above_replacement = player_performance_score - replacement_level
        
        # Base WAR calculation
        position_multiplier = position_multipliers.get(position, 1.0)
        base_war = (performance_above_replacement / 100) * snap_share * position_multiplier
        
        # Adjust based on team context
        team_win_pct = team_wins / max(team_wins + team_losses, 1)
        
        # Players on better teams have slightly inflated WAR due to supporting cast
        team_adjustment = 1.0 - (team_win_pct - 0.5) * 0.2
        
        adjusted_war = base_war * team_adjustment
        
        # Calculate win probability added
        wins_added = adjusted_war * (team_wins + team_losses) / 12  # Normalized to 12 game season
        
        return {
            'war': adjusted_war,
            'wins_added': wins_added,
            'position_value': position_multiplier,
            'snap_impact': snap_share,
            'team_context_adjustment': team_adjustment
        }
    
    def calculate_championship_impact(self,
                                     player_war: float,
                                     team_wins: int,
                                     conference_strength: float) -> float:
        """
        Estimate impact on championship/playoff probability
        """
        # Base playoff probability from wins (simplified model)
        base_playoff_prob = self._win_to_playoff_probability(team_wins, conference_strength)
        
        # Marginal impact of player
        counterfactual_wins = team_wins - player_war
        counterfactual_playoff_prob = self._win_to_playoff_probability(
            counterfactual_wins, 
            conference_strength
        )
        
        playoff_prob_impact = base_playoff_prob - counterfactual_playoff_prob
        
        return playoff_prob_impact * 100  # Return as percentage points
    
    def _win_to_playoff_probability(self, wins: float, conference_strength: float) -> float:
        """
        Estimate playoff probability based on wins and conference
        Uses logistic function
        """
        # Adjust win threshold based on conference strength
        adjusted_wins = wins * conference_strength
        
        # Logistic function centered around 11 wins
        playoff_prob = 1 / (1 + np.exp(-(adjusted_wins - 10.5)))
        
        return playoff_prob


def load_performance_benchmarks(historical_data_path: str) -> Dict:
    """
    Load and calculate performance benchmarks from historical data
    This would process years of player data to establish percentiles
    """
    # Placeholder - would actually load and process data
    print(f"Loading benchmarks from {historical_data_path}")
    return {}


def calculate_career_trajectory(historical_performances: List[Dict]) -> Dict:
    """
    Analyze player's performance trajectory over time
    """
    if len(historical_performances) < 2:
        return {'trend': 'insufficient_data'}
    
    scores = [p['overall_score'] for p in historical_performances]
    seasons = list(range(len(scores)))
    
    # Linear regression for trend
    slope = np.polyfit(seasons, scores, 1)[0]
    
    # Recent performance weight
    recent_avg = np.mean(scores[-2:]) if len(scores) >= 2 else scores[-1]
    career_avg = np.mean(scores)
    
    if slope > 5:
        trend = 'rapidly_improving'
    elif slope > 2:
        trend = 'improving'
    elif slope > -2:
        trend = 'stable'
    elif slope > -5:
        trend = 'declining'
    else:
        trend = 'rapidly_declining'
    
    return {
        'trend': trend,
        'slope': slope,
        'recent_vs_career': recent_avg - career_avg,
        'peak_score': max(scores),
        'current_score': scores[-1],
        'consistency': np.std(scores)
    }

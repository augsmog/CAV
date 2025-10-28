"""
Basketball WAR (Wins Above Replacement) Calculator
Calculates a player's contribution to team wins above a replacement-level player
"""

import math
from typing import Dict

class BasketballWARCalculator:
    """Calculate WAR for college basketball players"""
    
    # Replacement level baselines by position (per 40 minutes)
    REPLACEMENT_BASELINE = {
        'PG': {'pts': 8.0, 'ast': 3.0, 'reb': 2.5, 'stl': 0.8, 'tov': 2.0, 'ortg': 95, 'drtg': 110},
        'SG': {'pts': 9.0, 'ast': 1.5, 'reb': 3.0, 'stl': 0.7, 'tov': 1.5, 'ortg': 95, 'drtg': 110},
        'SF': {'pts': 8.5, 'ast': 1.5, 'reb': 4.0, 'stl': 0.7, 'tov': 1.5, 'ortg': 95, 'drtg': 110},
        'PF': {'pts': 7.5, 'ast': 1.0, 'reb': 5.0, 'stl': 0.5, 'tov': 1.2, 'ortg': 95, 'drtg': 110},
        'C': {'pts': 7.0, 'ast': 0.5, 'reb': 6.0, 'blk': 0.8, 'tov': 1.0, 'ortg': 95, 'drtg': 110},
    }
    
    # Position impact multipliers (offensive/defensive importance)
    POSITION_IMPACT = {
        'PG': {'offensive': 1.15, 'defensive': 0.95},  # PGs drive offense
        'SG': {'offensive': 1.10, 'defensive': 0.95},
        'SF': {'offensive': 1.05, 'defensive': 1.00},
        'PF': {'offensive': 0.95, 'defensive': 1.10},
        'C': {'offensive': 0.90, 'defensive': 1.15},   # Centers anchor defense
    }
    
    # Conference strength adjustments
    CONFERENCE_STRENGTH = {
        'ACC': 1.10, 'Big Ten': 1.10, 'Big 12': 1.10, 'SEC': 1.10, 'Pac-12': 1.08,
        'Big East': 1.08, 'AAC': 1.00, 'Mountain West': 0.98, 'WCC': 0.98,
        'Atlantic 10': 0.96, 'Missouri Valley': 0.94, 'C-USA': 0.92, 
        'MAC': 0.90, 'Sun Belt': 0.90, 'WAC': 0.88, 'Summit': 0.85,
        'SWAC': 0.82, 'MEAC': 0.82, 'Southland': 0.85, 'Big South': 0.88,
    }
    
    def calculate_war(self, player_stats: dict, performance_score: float) -> dict:
        """
        Calculate comprehensive WAR for a basketball player
        
        Args:
            player_stats: Dict with position, games, minutes, stats
            performance_score: Output from BasketballPerformanceCalculator
        
        Returns:
            Dict with WAR, components, and confidence metrics
        """
        position = self._normalize_position(player_stats.get('position', 'G'))
        games = player_stats.get('games', 0)
        minutes = player_stats.get('minutes', 0)
        
        if games == 0 or minutes == 0:
            return self._return_zero_war()
        
        # Calculate per-40-minute stats (standardized pace)
        per_40 = self._calculate_per_40_stats(player_stats, minutes)
        
        # Get replacement baseline
        baseline = self.REPLACEMENT_BASELINE.get(position, self.REPLACEMENT_BASELINE['SF'])
        
        # Calculate value above replacement
        offensive_var = self._calculate_offensive_var(per_40, baseline, position)
        defensive_var = self._calculate_defensive_var(per_40, baseline, position)
        
        # Apply position impact multipliers
        impact = self.POSITION_IMPACT.get(position, self.POSITION_IMPACT['SF'])
        offensive_var *= impact['offensive']
        defensive_var *= impact['defensive']
        
        # Calculate total value above replacement (per 40 min)
        total_var = offensive_var + defensive_var
        
        # Convert to season total based on minutes played
        season_var = total_var * (minutes / 40.0)
        
        # Apply conference strength adjustment
        conference = player_stats.get('conference', '')
        conf_multiplier = self.CONFERENCE_STRENGTH.get(conference, 1.0)
        adjusted_var = season_var * conf_multiplier
        
        # Convert VAR to wins (roughly 30 points of VAR = 1 win)
        war = adjusted_var / 30.0
        
        # Calculate confidence based on sample size
        confidence = self._calculate_confidence(games, minutes)
        
        # Determine WAR tier
        war_tier = self._get_war_tier(war)
        
        return {
            'war': round(war, 2),
            'wins_added': round(war, 2),
            'war_tier': war_tier,
            'confidence': round(confidence, 3),
            'components': {
                'offensive_var': round(offensive_var, 2),
                'defensive_var': round(defensive_var, 2),
                'total_var_per_40': round(total_var, 2),
                'season_var': round(season_var, 2),
                'conference_adj': round(conf_multiplier, 3)
            },
            'context': {
                'minutes': round(minutes, 1),
                'games': games,
                'mpg': round(minutes / games if games > 0 else 0, 1),
                'position': position,
                'conference': conference
            }
        }
    
    def _calculate_per_40_stats(self, stats: dict, total_minutes: float) -> dict:
        """Convert season totals to per-40-minute rates"""
        if total_minutes == 0:
            return {}
        
        factor = 40.0 / total_minutes
        
        return {
            'pts': stats.get('pts', 0) * factor,
            'reb': stats.get('reb', 0) * factor,
            'ast': stats.get('ast', 0) * factor,
            'stl': stats.get('stl', 0) * factor,
            'blk': stats.get('blk', 0) * factor,
            'tov': stats.get('tov', 0) * factor,
            'fg_pct': stats.get('fg_pct', 0),
            'tp_pct': stats.get('tp_pct', 0),
            'ortg': stats.get('ortg', 100),
            'drtg': stats.get('drtg', 105),
            'per': stats.get('per', 15.0),
            'ws': stats.get('ws', 0),
            'usage': stats.get('usage_rate', 20.0)
        }
    
    def _calculate_offensive_var(self, per_40: dict, baseline: dict, position: str) -> float:
        """Calculate offensive value above replacement (per 40 min)"""
        var = 0
        
        # Scoring value
        pts_diff = per_40.get('pts', 0) - baseline.get('pts', 8.0)
        var += pts_diff * 0.5  # Each point worth 0.5 VAR
        
        # Playmaking value (especially for guards)
        ast_diff = per_40.get('ast', 0) - baseline.get('ast', 1.5)
        if position in ['PG', 'SG']:
            var += ast_diff * 1.5  # Assists very valuable for guards
        else:
            var += ast_diff * 1.0
        
        # Turnover penalty
        tov_diff = baseline.get('tov', 1.5) - per_40.get('tov', 0)
        var += tov_diff * 0.8
        
        # Offensive rating bonus
        ortg = per_40.get('ortg', 100)
        if ortg > baseline.get('ortg', 95):
            var += (ortg - baseline['ortg']) * 0.15
        
        # PER bonus
        per = per_40.get('per', 15.0)
        if per > 15.0:
            var += (per - 15.0) * 0.3
        
        return max(var, 0)  # Can't be negative
    
    def _calculate_defensive_var(self, per_40: dict, baseline: dict, position: str) -> float:
        """Calculate defensive value above replacement (per 40 min)"""
        var = 0
        
        # Steals value
        stl_diff = per_40.get('stl', 0) - baseline.get('stl', 0.7)
        var += stl_diff * 2.0  # Steals create possessions
        
        # Blocks value (especially for bigs)
        blk_diff = per_40.get('blk', 0) - baseline.get('blk', 0.5)
        if position in ['PF', 'C']:
            var += blk_diff * 2.5  # Blocks very valuable for bigs
        else:
            var += blk_diff * 1.5
        
        # Defensive rebound value
        reb = per_40.get('reb', 0)
        reb_baseline = baseline.get('reb', 4.0)
        if reb > reb_baseline:
            var += (reb - reb_baseline) * 0.4
        
        # Defensive rating bonus
        drtg = per_40.get('drtg', 105)
        if drtg < baseline.get('drtg', 110):
            var += (baseline['drtg'] - drtg) * 0.2
        
        return max(var, 0)  # Can't be negative
    
    def _calculate_confidence(self, games: int, minutes: float) -> float:
        """Calculate confidence score based on sample size"""
        # Full confidence at 25+ games and 600+ minutes
        games_confidence = min(games / 25.0, 1.0)
        minutes_confidence = min(minutes / 600.0, 1.0)
        
        # Average the two
        return (games_confidence + minutes_confidence) / 2.0
    
    def _get_war_tier(self, war: float) -> str:
        """Classify player by WAR tier"""
        if war >= 6.0:
            return "Elite (All-American)"
        elif war >= 4.0:
            return "Excellent (All-Conference)"
        elif war >= 2.5:
            return "Good Starter"
        elif war >= 1.0:
            return "Solid Contributor"
        elif war >= 0.0:
            return "Rotation Player"
        else:
            return "Below Replacement"
    
    def _normalize_position(self, position: str) -> str:
        """Normalize position to PG, SG, SF, PF, C"""
        pos_map = {
            'PG': 'PG', 'POINT GUARD': 'PG',
            'SG': 'SG', 'SHOOTING GUARD': 'SG', 'G': 'SG',
            'SF': 'SF', 'SMALL FORWARD': 'SF', 'F': 'SF',
            'PF': 'PF', 'POWER FORWARD': 'PF',
            'C': 'C', 'CENTER': 'C'
        }
        return pos_map.get(position.upper(), 'SF')
    
    def _return_zero_war(self) -> dict:
        """Return zero WAR with structure"""
        return {
            'war': 0.0,
            'wins_added': 0.0,
            'war_tier': 'Insufficient Data',
            'confidence': 0.0,
            'components': {
                'offensive_var': 0.0,
                'defensive_var': 0.0,
                'total_var_per_40': 0.0,
                'season_var': 0.0,
                'conference_adj': 1.0
            },
            'context': {
                'minutes': 0.0,
                'games': 0,
                'mpg': 0.0,
                'position': 'Unknown',
                'conference': ''
            }
        }


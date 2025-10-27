"""
College Football WAR (Wins Above Replacement) Calculator

Measures the additional wins a player contributes to their team compared to a 
replacement-level player, adjusted for:
- Game context (leverage situations vs garbage time)
- Opponent quality
- Position-specific impact on wins
- Conference strength
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class GameContext:
    """Context for a specific game or play"""
    score_differential: int
    time_remaining: float  # Minutes
    down: int
    distance: int
    field_position: int  # Yards from own goal line
    is_conference_game: bool
    is_rivalry: bool


class CFBWARCalculator:
    """
    Comprehensive WAR calculator for college football players
    """
    
    def __init__(self):
        # Replacement level benchmarks by position (40th percentile)
        self.replacement_levels = {
            'QB': 45,    # QBs have highest bar
            'WR': 42,
            'RB': 43,
            'TE': 42,
            'OL': 40,
            'DL': 41,
            'LB': 40,
            'CB': 42,
            'S': 41
        }
        
        # Position impact on wins (research-based multipliers)
        self.position_win_impact = {
            'QB': 4.0,   # QB accounts for ~40% of team wins
            'OL': 2.5,   # Collective OL impact
            'DL': 2.3,   # Pass rush critical
            'CB': 2.0,   # Coverage critical
            'WR': 1.5,   # Playmakers
            'LB': 1.4,
            'S': 1.3,
            'TE': 1.2,
            'RB': 1.0    # Most replaceable
        }
        
        # Conference strength multipliers (based on historical data)
        self.conference_multipliers = {
            'SEC': 1.20,
            'Big Ten': 1.15,
            'Big 12': 1.12,
            'ACC': 1.10,
            'Pac-12': 1.10,
            'American': 0.95,
            'Mountain West': 0.90,
            'Sun Belt': 0.88,
            'MAC': 0.85,
            'C-USA': 0.85,
            'Independent': 1.00
        }
    
    def calculate_leverage_index(self, context: Optional[GameContext] = None) -> float:
        """
        Calculate leverage index (game importance) for a situation
        Based on win probability sensitivity
        
        High leverage: Close games, 4th quarter, critical downs
        Low leverage: Blowouts (garbage time)
        
        Returns: 0.3 to 2.0 multiplier
        """
        if not context:
            return 1.0  # Neutral
        
        score_diff = abs(context.score_differential)
        
        # Garbage time detection
        if score_diff >= 28:
            return 0.3  # Very low leverage (blowout)
        elif score_diff >= 21:
            return 0.5  # Low leverage
        elif score_diff >= 14 and context.time_remaining < 10:
            return 0.7  # Somewhat low
        
        # High leverage situations
        leverage = 1.0
        
        # Close game bonus
        if score_diff <= 7:
            leverage += 0.3
        if score_diff <= 3:
            leverage += 0.3
        
        # Late game pressure
        if context.time_remaining < 5:
            leverage += 0.2
        if context.time_remaining < 2:
            leverage += 0.2
        
        # Critical downs
        if context.down >= 3:
            leverage += 0.2
        
        # Red zone
        if context.field_position >= 80:
            leverage += 0.1
        
        # Important games
        if context.is_rivalry:
            leverage += 0.1
        
        return min(2.0, max(0.3, leverage))
    
    def calculate_opponent_adjustment(self, 
                                     opponent_win_pct: float,
                                     opponent_conference: str,
                                     is_conference_game: bool) -> float:
        """
        Adjust performance based on opponent quality
        
        Returns: 0.7 to 1.3 multiplier
        """
        # Base adjustment from opponent win percentage
        # 0.800+ win% = 1.25x (elite opponent)
        # 0.500 win% = 1.00x (average)
        # 0.200 win% = 0.75x (weak opponent)
        
        base_adj = 0.75 + (opponent_win_pct * 0.5)
        
        # Conference strength adjustment
        conf_adj = self.conference_multipliers.get(opponent_conference, 1.0)
        
        # Conference games are slightly more important
        conf_game_bonus = 1.05 if is_conference_game else 1.0
        
        total_adj = base_adj * ((conf_adj - 1.0) * 0.5 + 1.0) * conf_game_bonus
        
        return max(0.7, min(1.3, total_adj))
    
    def calculate_epa_contribution(self,
                                  player_stats: Dict,
                                  position: str,
                                  snaps_played: int) -> float:
        """
        Calculate Expected Points Added contribution
        Simplified EPA model for CFB
        
        Returns: EPA per snap played
        """
        if position == 'QB':
            # QB EPA from passing efficiency
            comp_pct = player_stats.get('completion_percentage', 60) / 100
            ypa = player_stats.get('yards_per_attempt', 7)
            td_int_ratio = player_stats.get('td_int_ratio', 2)
            
            # Simplified EPA model
            # Good QB: ~0.15 EPA/play
            # Average: ~0.05 EPA/play
            # Poor: ~-0.05 EPA/play
            
            base_epa = (
                (comp_pct - 0.55) * 0.3 +  # Completion bonus
                (ypa - 6.5) * 0.05 +        # YPA contribution
                (td_int_ratio - 2.0) * 0.02 # TD/INT ratio
            )
            
            return base_epa
        
        elif position == 'RB':
            ypc = player_stats.get('yards_per_carry', 4.0)
            # Good RB: ~0.08 EPA/play
            base_epa = (ypc - 4.0) * 0.02
            return base_epa
        
        elif position == 'WR':
            ypr = player_stats.get('yards_per_reception', 12)
            catch_rate = player_stats.get('catch_rate', 0.60)
            # Good WR: ~0.10 EPA/play
            base_epa = (ypr - 11) * 0.01 + (catch_rate - 0.60) * 0.15
            return base_epa
        
        elif position in ['DL', 'LB', 'CB', 'S']:
            # Defense EPA is negative for offense
            # Good defender: -0.10 EPA/play allowed
            # Use tackle efficiency, pass defense as proxies
            base_epa = 0.05  # Placeholder, would need detailed stats
            return base_epa
        
        return 0.0
    
    def calculate_comprehensive_war(self,
                                   player_performance_score: float,
                                   position: str,
                                   snaps_played: int,
                                   games_played: int,
                                   games_started: int,
                                   team_record: tuple,  # (wins, losses)
                                   conference: str,
                                   player_stats: Dict = None,
                                   game_contexts: List[GameContext] = None,
                                   opponent_quality_avg: float = 0.500) -> Dict:
        """
        Calculate comprehensive WAR for a player
        
        This is the primary valuation metric that drives player value
        """
        
        # 1. REPLACEMENT LEVEL BASELINE
        replacement_level = self.replacement_levels.get(position, 42)
        performance_above_replacement = player_performance_score - replacement_level
        
        # Players below replacement have negative WAR
        if performance_above_replacement < 0:
            performance_above_replacement *= 1.5  # Penalize more heavily
        
        # 2. SNAP SHARE & PARTICIPATION
        # Assume ~850 snaps per season for full-time starter
        position_snap_expectations = {
            'QB': 850, 'RB': 500, 'WR': 600, 'TE': 500,
            'OL': 850, 'DL': 550, 'LB': 650, 'CB': 750, 'S': 700
        }
        
        expected_snaps = position_snap_expectations.get(position, 650)
        snap_share = min(1.0, snaps_played / expected_snaps)
        
        # Starter bonus (games started matters)
        if games_played > 0:
            starter_rate = games_started / games_played
            participation_factor = snap_share * (0.7 + 0.3 * starter_rate)
        else:
            starter_rate = 0.0
            participation_factor = snap_share
        
        # 3. LEVERAGE ADJUSTMENT
        # If we have game context, use it. Otherwise estimate.
        if game_contexts:
            avg_leverage = np.mean([self.calculate_leverage_index(ctx) for ctx in game_contexts])
        else:
            # Estimate: starters in close games = higher leverage
            if starter_rate > 0.8:
                avg_leverage = 1.1  # Likely in important situations
            elif starter_rate > 0.5:
                avg_leverage = 1.0
            else:
                avg_leverage = 0.8  # Backups often in garbage time
        
        # 4. OPPONENT QUALITY ADJUSTMENT
        opponent_adj = 0.75 + (opponent_quality_avg * 0.5)  # 0.75 to 1.25
        
        # 5. CONFERENCE STRENGTH
        conf_multiplier = self.conference_multipliers.get(conference, 1.0)
        
        # 6. POSITION-SPECIFIC WIN IMPACT
        position_impact = self.position_win_impact.get(position, 1.0)
        
        # 7. CALCULATE BASE WAR
        # Formula: (Performance Above Replacement / 100) * Participation * Position Impact * Context
        base_war = (
            (performance_above_replacement / 100) *
            participation_factor *
            position_impact *
            avg_leverage *
            opponent_adj *
            ((conf_multiplier - 1.0) * 0.5 + 1.0)  # Moderate conference impact
        )
        
        # 8. TEAM CONTEXT ADJUSTMENT
        team_wins, team_losses = team_record
        team_win_pct = team_wins / max(team_wins + team_losses, 1)
        
        # Players on better teams have slightly inflated stats due to supporting cast
        # But we don't want to penalize too much for being on a good team
        team_adjustment = 1.0 - (team_win_pct - 0.5) * 0.15
        
        adjusted_war = base_war * team_adjustment
        
        # 9. CONFIDENCE INTERVAL
        # Lower snap counts = higher uncertainty
        if snaps_played >= expected_snaps:
            war_uncertainty = 0.15  # ±15%
        elif snaps_played >= expected_snaps * 0.5:
            war_uncertainty = 0.30  # ±30%
        else:
            war_uncertainty = 0.50  # ±50%
        
        war_low = adjusted_war * (1 - war_uncertainty)
        war_high = adjusted_war * (1 + war_uncertainty)
        
        # 10. WINS ADDED CALCULATION
        # Convert WAR to actual wins added over 12-game season
        games_in_season = team_wins + team_losses
        season_factor = games_in_season / 12.0 if games_in_season > 0 else 1.0
        
        wins_added = adjusted_war * season_factor
        
        # 11. CHAMPIONSHIP IMPACT
        # How much does this player improve playoff/championship probability?
        playoff_impact = self._calculate_playoff_impact(
            adjusted_war, team_wins, team_losses, conference
        )
        
        return {
            # Core WAR metrics
            'war': round(adjusted_war, 3),
            'war_low': round(war_low, 3),
            'war_high': round(war_high, 3),
            'war_uncertainty': round(war_uncertainty, 2),
            'wins_added': round(wins_added, 2),
            
            # Component breakdowns
            'performance_above_replacement': round(performance_above_replacement, 2),
            'replacement_level': replacement_level,
            'participation_factor': round(participation_factor, 3),
            'snap_share': round(snap_share, 3),
            'starter_rate': round(starter_rate, 3) if games_played > 0 else 0,
            
            # Adjustments
            'leverage_index': round(avg_leverage, 2),
            'opponent_adjustment': round(opponent_adj, 2),
            'conference_multiplier': round(conf_multiplier, 2),
            'team_adjustment': round(team_adjustment, 2),
            
            # Position context
            'position_win_impact': position_impact,
            
            # Strategic value
            'playoff_impact_pct': round(playoff_impact, 2),
            
            # Value tiers
            'war_tier': self._get_war_tier(adjusted_war),
            'value_rating': self._get_value_rating(adjusted_war, position)
        }
    
    def _calculate_playoff_impact(self, war: float, wins: int, losses: int, conference: str) -> float:
        """Calculate impact on playoff probability (percentage points)"""
        total_games = wins + losses
        if total_games == 0:
            return 0.0
        
        current_win_pct = wins / total_games
        
        # Conference matters for playoff access
        if conference in ['SEC', 'Big Ten', 'Big 12', 'ACC', 'Pac-12']:
            # P5 schools: ~10+ wins needed for playoff consideration
            playoff_threshold = 0.833  # 10-2
        else:
            # G5 schools: need to be undefeated or 1-loss
            playoff_threshold = 0.917  # 11-1
        
        # Marginal impact of player
        # WAR > 1.0 = Elite (moves needle significantly)
        # WAR 0.5-1.0 = Good starter
        # WAR 0.0-0.5 = Average starter
        # WAR < 0.0 = Below replacement
        
        if current_win_pct >= playoff_threshold:
            # Already in playoff contention, player helps maintain/improve seeding
            impact = war * 3.0
        elif current_win_pct >= playoff_threshold - 0.15:
            # Bubble team, player could push over the edge
            impact = war * 5.0
        else:
            # Not in contention, but player improves win total
            impact = war * 2.0
        
        return min(impact, 15.0)  # Cap at 15 percentage points
    
    def _get_war_tier(self, war: float) -> str:
        """Classify player by WAR tier"""
        if war >= 2.0:
            return "Elite/All-American"
        elif war >= 1.0:
            return "All-Conference"
        elif war >= 0.5:
            return "Above Average Starter"
        elif war >= 0.0:
            return "Average Starter"
        elif war >= -0.5:
            return "Below Average/Backup"
        else:
            return "Replacement Level"
    
    def _get_value_rating(self, war: float, position: str) -> str:
        """Overall value rating"""
        # Adjust expectations by position
        position_war_expectations = {
            'QB': 1.5,   # Elite QBs can have 2+ WAR
            'OL': 0.8,
            'DL': 0.8,
            'CB': 0.7,
            'WR': 0.6,
            'LB': 0.6,
            'S': 0.5,
            'TE': 0.5,
            'RB': 0.4
        }
        
        expected = position_war_expectations.get(position, 0.6)
        
        if war >= expected * 1.5:
            return "Elite Value"
        elif war >= expected:
            return "High Value"
        elif war >= expected * 0.5:
            return "Good Value"
        elif war >= 0:
            return "Fair Value"
        else:
            return "Below Value"


def create_cfb_war_calculator():
    """Factory function"""
    return CFBWARCalculator()


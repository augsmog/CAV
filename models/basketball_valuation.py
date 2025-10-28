"""
Basketball Player Valuation Engine
Calculates player value and NIL potential for college basketball players
Based on WAR-driven valuation model
"""

from models.basketball_performance import BasketballPerformanceCalculator
from models.basketball_war import BasketballWARCalculator

class BasketballValuationEngine:
    """
    Comprehensive basketball player valuation engine
    Separates Player Value (team/collective) and NIL Potential (player earnings)
    """
    
    # NIL market size by conference (average annual earning potential in thousands)
    NIL_MARKET_SIZE = {
        'ACC': 150, 'Big Ten': 150, 'Big 12': 140, 'SEC': 145, 'Pac-12': 130,
        'Big East': 120, 'AAC': 80, 'Mountain West': 70, 'WCC': 75,
        'Atlantic 10': 65, 'Missouri Valley': 50, 'C-USA': 45,
        'MAC': 40, 'Sun Belt': 40, 'WAC': 35, 'Summit': 30,
    }
    
    # Position NIL multipliers (visibility/marketability)
    POSITION_NIL_MULTIPLIER = {
        'PG': 1.15,  # Floor generals get attention
        'SG': 1.10,  # Scorers are marketable
        'SF': 1.05,
        'PF': 0.95,
        'C': 0.90,   # Centers less visible in highlights
    }
    
    # NIL boost factors
    NIL_BOOSTS = {
        'all_american': 2.5,      # Consensus All-American
        'all_conference': 1.8,     # All-Conference selection
        'high_scorer': 1.5,        # 18+ PPG
        'efficient': 1.3,          # 55+ TS% or 20+ PER
        'defensive_star': 1.4,     # 2+ SPG or 2+ BPG
        'tournament_team': 1.2,    # NCAA Tournament team
    }
    
    def __init__(self):
        self.performance_calc = BasketballPerformanceCalculator()
        self.war_calc = BasketballWARCalculator()
    
    def calculate_valuation(self, player_stats: dict) -> dict:
        """
        Calculate comprehensive player valuation
        
        Args:
            player_stats: Dict with all player information and stats
        
        Returns:
            Dict with player_value, nil_potential, confidence, and details
        """
        # Calculate performance score
        performance = self.performance_calc.calculate_performance_score(player_stats)
        performance_score = performance['performance_score']
        
        # Calculate WAR
        war_result = self.war_calc.calculate_war(player_stats, performance_score)
        war = war_result['war']
        
        # Calculate Player Value (WAR-driven)
        player_value = self._calculate_player_value(
            war, 
            performance,
            player_stats
        )
        
        # Calculate NIL Potential (separate from team value)
        nil_potential = self._calculate_nil_potential(
            performance,
            war_result,
            player_stats
        )
        
        # Overall confidence
        confidence = min(
            performance.get('confidence', 0.5),
            war_result.get('confidence', 0.5)
        )
        
        # Classification
        classification = self._classify_player(player_value, war)
        
        return {
            'player_value': round(player_value, 0),
            'nil_potential': round(nil_potential, 0),
            'war': war,
            'war_tier': war_result['war_tier'],
            'confidence': round(confidence, 3),
            'classification': classification,
            'performance_score': performance_score,
            'components': {
                'war_value': round(war * 50000, 0),  # $50K per WAR
                'performance_bonus': round((performance_score / 100) * 25000, 0),
                'position_adjustment': player_stats.get('position', 'SF'),
            },
            'nil_components': {
                'base_market': self._get_base_nil_market(player_stats),
                'performance_multiplier': round(performance_score / 100, 2),
                'visibility_boost': self._calculate_visibility_boost(player_stats, performance),
            },
            'details': {
                'season': player_stats.get('season', 2023),
                'team': player_stats.get('team', ''),
                'position': player_stats.get('position', ''),
                'conference': player_stats.get('conference', ''),
                'games': player_stats.get('games', 0),
                'minutes': player_stats.get('minutes', 0),
            }
        }
    
    def _calculate_player_value(self, war: float, performance: dict, stats: dict) -> float:
        """
        Calculate player value for teams/collectives (WAR-driven)
        This is what a school/collective should value the player at
        """
        # Base value from WAR ($50K per WAR)
        war_value = war * 50000
        
        # Performance bonus (up to $25K)
        perf_score = performance.get('performance_score', 0)
        perf_bonus = (perf_score / 100) * 25000
        
        # Position adjustment
        position = stats.get('position', 'SF')
        pos_multiplier = {
            'PG': 1.10,  # Ball handlers more valuable to teams
            'SG': 1.05,
            'SF': 1.00,
            'PF': 1.05,
            'C': 1.10,   # Rim protectors valuable
        }.get(position, 1.0)
        
        # Conference strength adjustment
        conference = stats.get('conference', '')
        conf_multiplier = self.war_calc.CONFERENCE_STRENGTH.get(conference, 1.0)
        
        # Calculate total
        total_value = (war_value + perf_bonus) * pos_multiplier * conf_multiplier
        
        # Floor at $10K, cap at $500K
        return max(min(total_value, 500000), 10000)
    
    def _calculate_nil_potential(self, performance: dict, war_result: dict, stats: dict) -> float:
        """
        Calculate NIL earning potential (separate from team value)
        This is what a player can potentially earn through endorsements/deals
        """
        # Base market by conference
        base_market = self._get_base_nil_market(stats)
        
        # Performance multiplier
        perf_score = performance.get('performance_score', 0)
        perf_multiplier = perf_score / 100
        
        # WAR tier bonus
        war = war_result.get('war', 0)
        if war >= 6.0:
            war_bonus = 2.5
        elif war >= 4.0:
            war_bonus = 2.0
        elif war >= 2.5:
            war_bonus = 1.5
        elif war >= 1.0:
            war_bonus = 1.2
        else:
            war_bonus = 1.0
        
        # Position marketability
        position = stats.get('position', 'SF')
        pos_multiplier = self.POSITION_NIL_MULTIPLIER.get(position, 1.0)
        
        # Visibility boosts
        visibility_boost = self._calculate_visibility_boost(stats, performance)
        
        # Calculate total NIL potential (in thousands)
        nil_potential = base_market * perf_multiplier * war_bonus * pos_multiplier * visibility_boost
        
        # Convert to actual dollars and cap
        nil_dollars = nil_potential * 1000
        return max(min(nil_dollars, 400000), 5000)
    
    def _get_base_nil_market(self, stats: dict) -> float:
        """Get base NIL market size by conference (in thousands)"""
        conference = stats.get('conference', '')
        return self.NIL_MARKET_SIZE.get(conference, 50)
    
    def _calculate_visibility_boost(self, stats: dict, performance: dict) -> float:
        """Calculate visibility/marketability boost"""
        boost = 1.0
        
        # High scorer
        games = stats.get('games', 0)
        if games > 0:
            ppg = stats.get('pts', 0) / games
            if ppg >= 20:
                boost *= 1.5
            elif ppg >= 15:
                boost *= 1.3
        
        # Efficiency
        per = stats.get('per', 0)
        if per >= 25:
            boost *= 1.3
        elif per >= 20:
            boost *= 1.2
        
        # High usage (star player)
        usage = stats.get('usage_rate', 0)
        if usage >= 30:
            boost *= 1.2
        
        return boost
    
    def _classify_player(self, player_value: float, war: float) -> str:
        """Classify player by value tier"""
        if player_value >= 300000 or war >= 6.0:
            return "Elite (High Major Star)"
        elif player_value >= 200000 or war >= 4.0:
            return "Premium (All-Conference)"
        elif player_value >= 100000 or war >= 2.5:
            return "Quality Starter"
        elif player_value >= 50000 or war >= 1.0:
            return "Solid Contributor"
        else:
            return "Role Player"


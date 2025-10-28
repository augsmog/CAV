"""
Basketball Performance Calculator
Position-specific scoring for college basketball players
"""

class BasketballPerformanceCalculator:
    """Calculate performance scores for basketball players by position"""
    
    # Position weights for different stat categories
    POSITION_WEIGHTS = {
        'PG': {  # Point Guard
            'scoring': 0.25,
            'playmaking': 0.40,
            'efficiency': 0.20,
            'defense': 0.15
        },
        'SG': {  # Shooting Guard
            'scoring': 0.40,
            'playmaking': 0.20,
            'efficiency': 0.25,
            'defense': 0.15
        },
        'SF': {  # Small Forward
            'scoring': 0.35,
            'playmaking': 0.20,
            'efficiency': 0.25,
            'defense': 0.20
        },
        'PF': {  # Power Forward
            'scoring': 0.30,
            'playmaking': 0.10,
            'efficiency': 0.30,
            'defense': 0.30
        },
        'C': {  # Center
            'scoring': 0.25,
            'playmaking': 0.05,
            'efficiency': 0.35,
            'defense': 0.35
        }
    }
    
    # Benchmarks for D1 starters
    BENCHMARKS = {
        'PG': {'pts': 12.0, 'ast': 4.0, 'reb': 3.5, 'stl': 1.2, 'tov': 2.5, 'fg_pct': 42.0, 'tp_pct': 33.0},
        'SG': {'pts': 14.0, 'ast': 2.5, 'reb': 4.0, 'stl': 1.0, 'tov': 2.0, 'fg_pct': 43.0, 'tp_pct': 35.0},
        'SF': {'pts': 13.0, 'ast': 2.0, 'reb': 5.0, 'stl': 1.0, 'tov': 1.8, 'fg_pct': 45.0, 'tp_pct': 33.0},
        'PF': {'pts': 11.0, 'ast': 1.5, 'reb': 6.5, 'stl': 0.8, 'tov': 1.5, 'fg_pct': 50.0, 'blk': 1.2},
        'C': {'pts': 10.0, 'ast': 1.0, 'reb': 7.5, 'stl': 0.5, 'tov': 1.5, 'fg_pct': 55.0, 'blk': 1.5},
    }
    
    def calculate_performance_score(self, player_stats: dict) -> dict:
        """
        Calculate comprehensive performance score for a basketball player
        
        Args:
            player_stats: Dict with keys: position, games, minutes, pts, reb, ast, stl, blk, tov, fg_pct, tp_pct, per, ortg, drtg, ws, usage_rate
        
        Returns:
            Dict with performance_score, component scores, and details
        """
        position = self._normalize_position(player_stats.get('position', 'G'))
        games = player_stats.get('games', 0)
        
        if games == 0:
            return {'performance_score': 0.0, 'confidence': 0.0}
        
        # Calculate per-game averages
        ppg = player_stats.get('pts', 0) / games
        rpg = player_stats.get('reb', 0) / games
        apg = player_stats.get('ast', 0) / games
        spg = player_stats.get('stl', 0) / games
        bpg = player_stats.get('blk', 0) / games
        topg = player_stats.get('tov', 0) / games
        
        # Get efficiency stats
        fg_pct = player_stats.get('fg_pct', 0)
        tp_pct = player_stats.get('tp_pct', 0)
        per = player_stats.get('per', 15.0)
        ortg = player_stats.get('ortg', 100.0)
        drtg = player_stats.get('drtg', 105.0)
        ws = player_stats.get('ws', 0)
        usage = player_stats.get('usage_rate', 20.0)
        
        # Calculate component scores
        scoring_score = self._calculate_scoring(position, ppg, fg_pct, tp_pct, per, usage)
        playmaking_score = self._calculate_playmaking(position, apg, topg, usage)
        efficiency_score = self._calculate_efficiency(position, fg_pct, tp_pct, per, ortg)
        defense_score = self._calculate_defense(position, spg, bpg, drtg, rpg)
        
        # Get position weights
        weights = self.POSITION_WEIGHTS.get(position, self.POSITION_WEIGHTS['SF'])
        
        # Calculate weighted total
        performance_score = (
            scoring_score * weights['scoring'] +
            playmaking_score * weights['playmaking'] +
            efficiency_score * weights['efficiency'] +
            defense_score * weights['defense']
        )
        
        # Sample size confidence
        confidence = min(games / 30.0, 1.0)  # Full confidence at 30+ games
        
        return {
            'performance_score': round(performance_score, 2),
            'confidence': round(confidence, 3),
            'components': {
                'scoring': round(scoring_score, 2),
                'playmaking': round(playmaking_score, 2),
                'efficiency': round(efficiency_score, 2),
                'defense': round(defense_score, 2)
            },
            'per_game_stats': {
                'ppg': round(ppg, 1),
                'rpg': round(rpg, 1),
                'apg': round(apg, 1),
                'spg': round(spg, 1),
                'bpg': round(bpg, 1)
            },
            'advanced_stats': {
                'per': round(per, 1),
                'ortg': round(ortg, 1),
                'drtg': round(drtg, 1),
                'ws': round(ws, 2),
                'usage': round(usage, 1)
            }
        }
    
    def _normalize_position(self, position: str) -> str:
        """Normalize position to PG, SG, SF, PF, C"""
        pos_map = {
            'PG': 'PG', 'POINT GUARD': 'PG',
            'SG': 'SG', 'SHOOTING GUARD': 'SG', 'G': 'SG',  # Default guards to SG
            'SF': 'SF', 'SMALL FORWARD': 'SF', 'F': 'SF',  # Default forwards to SF
            'PF': 'PF', 'POWER FORWARD': 'PF',
            'C': 'C', 'CENTER': 'C'
        }
        return pos_map.get(position.upper(), 'SF')
    
    def _calculate_scoring(self, position: str, ppg: float, fg_pct: float, tp_pct: float, per: float, usage: float) -> float:
        """Calculate scoring component (0-100)"""
        benchmark = self.POSITION_WEIGHTS[position]
        bench_pts = self.BENCHMARKS[position]['pts']
        
        # Points above benchmark
        pts_score = min((ppg / bench_pts) * 50, 70)  # Cap at 70 for volume
        
        # Efficiency bonus
        eff_score = 0
        if fg_pct > self.BENCHMARKS[position]['fg_pct']:
            eff_score += 15
        if per > 15.0:
            eff_score += 10
        if usage > 25.0:
            eff_score += 5  # High usage with good efficiency
        
        return min(pts_score + eff_score, 100)
    
    def _calculate_playmaking(self, position: str, apg: float, topg: float, usage: float) -> float:
        """Calculate playmaking component (0-100)"""
        bench_ast = self.BENCHMARKS[position]['ast']
        bench_tov = self.BENCHMARKS[position]['tov']
        
        # Assists score
        ast_score = min((apg / bench_ast) * 50, 60)
        
        # Assist-to-turnover ratio
        if topg > 0:
            ratio = apg / topg
            if ratio > 2.0:
                ast_score += 30
            elif ratio > 1.5:
                ast_score += 20
            elif ratio > 1.0:
                ast_score += 10
        
        return min(ast_score, 100)
    
    def _calculate_efficiency(self, position: str, fg_pct: float, tp_pct: float, per: float, ortg: float) -> float:
        """Calculate efficiency component (0-100)"""
        score = 0
        
        # Shooting efficiency
        bench_fg = self.BENCHMARKS[position].get('fg_pct', 45.0)
        if fg_pct > bench_fg:
            score += min(((fg_pct - bench_fg) / bench_fg) * 100, 30)
        
        # PER score
        if per > 20:
            score += 30
        elif per > 15:
            score += 20
        elif per > 10:
            score += 10
        
        # Offensive rating
        if ortg > 115:
            score += 30
        elif ortg > 110:
            score += 20
        elif ortg > 105:
            score += 10
        
        return min(score, 100)
    
    def _calculate_defense(self, position: str, spg: float, bpg: float, drtg: float, rpg: float) -> float:
        """Calculate defense component (0-100)"""
        score = 0
        
        # Steals
        bench_stl = self.BENCHMARKS[position].get('stl', 1.0)
        if spg > bench_stl:
            score += 20
        elif spg > bench_stl * 0.75:
            score += 10
        
        # Blocks (especially for bigs)
        if position in ['PF', 'C']:
            bench_blk = self.BENCHMARKS[position].get('blk', 1.0)
            if bpg > bench_blk:
                score += 25
            elif bpg > bench_blk * 0.75:
                score += 15
        
        # Defensive rating
        if drtg < 100:
            score += 35
        elif drtg < 105:
            score += 25
        elif drtg < 110:
            score += 15
        
        # Rebounds (especially for bigs)
        bench_reb = self.BENCHMARKS[position].get('reb', 5.0)
        if rpg > bench_reb:
            score += 20
        elif rpg > bench_reb * 0.75:
            score += 10
        
        return min(score, 100)


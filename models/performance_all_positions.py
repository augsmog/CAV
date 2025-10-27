"""
Enhanced Performance Calculator - All Positions
Extends the base calculator with position-specific evaluation
"""

import numpy as np
from typing import Dict, Optional


class AllPositionsPerformanceCalculator:
    """
    Performance calculator with specialized methods for each position
    Uses available stats from collegefootballdata.com API
    """
    
    def __init__(self):
        self.position_calculators = {
            'QB': self._calculate_qb_score,
            'RB': self._calculate_rb_score,
            'WR': self._calculate_wr_score,
            'TE': self._calculate_te_score,
            'DL': self._calculate_dl_score,
            'DT': self._calculate_dl_score,
            'DE': self._calculate_dl_score,
            'LB': self._calculate_lb_score,
            'ILB': self._calculate_lb_score,
            'OLB': self._calculate_lb_score,
            'CB': self._calculate_db_score,
            'S': self._calculate_db_score,
            'DB': self._calculate_db_score,
        }
    
    def calculate_performance_score(self, 
                                   player_stats: Dict,
                                   position: str,
                                   conference: str = 'FBS',
                                   opponent_strength: float = 1.0) -> Dict:
        """
        Calculate performance score for any position
        """
        position = position.upper()
        
        if position not in self.position_calculators:
            # Default to average score for unsupported positions
            return {
                'overall_score': 50.0,
                'position': position,
                'method': 'default',
                'raw_metrics': player_stats
            }
        
        calculator = self.position_calculators[position]
        base_score = calculator(player_stats)
        
        # Apply conference adjustment
        conference_factor = self._get_conference_adjustment(conference)
        adjusted_score = base_score * conference_factor
        
        # Apply strength of schedule
        final_score = adjusted_score * opponent_strength
        
        return {
            'overall_score': min(final_score, 100.0),
            'base_score': base_score,
            'conference_factor': conference_factor,
            'opponent_strength': opponent_strength,
            'position': position,
            'raw_metrics': player_stats
        }
    
    # ========================================================================
    # QUARTERBACK
    # ========================================================================
    
    def _calculate_qb_score(self, stats: Dict) -> float:
        """Calculate QB performance score"""
        score = 0.0
        
        # Completion percentage (20 points max)
        comp_pct = stats.get('completion_percentage', 0) * 100
        if comp_pct >= 70: score += 20
        elif comp_pct >= 65: score += 17
        elif comp_pct >= 60: score += 14
        elif comp_pct >= 55: score += 10
        else: score += max(comp_pct / 5, 0)
        
        # Yards per attempt (25 points max)
        ypa = stats.get('yards_per_attempt', 0)
        if ypa >= 9.0: score += 25
        elif ypa >= 8.0: score += 22
        elif ypa >= 7.5: score += 18
        elif ypa >= 7.0: score += 14
        elif ypa >= 6.5: score += 10
        else: score += max(ypa * 1.5, 0)
        
        # TD/INT ratio (20 points max)
        td_int_ratio = stats.get('td_int_ratio', 1.0)
        if td_int_ratio >= 4.0: score += 20
        elif td_int_ratio >= 3.0: score += 17
        elif td_int_ratio >= 2.5: score += 14
        elif td_int_ratio >= 2.0: score += 11
        elif td_int_ratio >= 1.5: score += 8
        else: score += max(td_int_ratio * 4, 0)
        
        # Total production (25 points max)
        passing_yards = stats.get('passing_yards', 0)
        passing_tds = stats.get('passing_tds', 0)
        
        if passing_yards >= 3500: score += 15
        elif passing_yards >= 3000: score += 12
        elif passing_yards >= 2500: score += 9
        elif passing_yards >= 2000: score += 6
        else: score += max(passing_yards / 400, 0)
        
        score += min(passing_tds * 0.5, 10)
        
        # Dual-threat bonus (10 points max)
        rushing_yards = stats.get('rushing_yards', 0)
        rushing_tds = stats.get('rushing_tds', 0)
        if rushing_yards >= 500:
            score += 10
        elif rushing_yards >= 300:
            score += 7
        elif rushing_yards >= 100:
            score += 4
        score += min(rushing_tds * 2, 5)
        
        return min(score, 100.0)
    
    # ========================================================================
    # RUNNING BACK
    # ========================================================================
    
    def _calculate_rb_score(self, stats: Dict) -> float:
        """Calculate RB performance score"""
        score = 0.0
        
        # Yards per carry (30 points max) - MOST IMPORTANT
        ypc = stats.get('yards_per_carry', 0)
        if ypc >= 6.5: score += 30
        elif ypc >= 6.0: score += 27
        elif ypc >= 5.5: score += 24
        elif ypc >= 5.0: score += 20
        elif ypc >= 4.5: score += 15
        elif ypc >= 4.0: score += 10
        else: score += max(ypc * 2, 0)
        
        # Total rushing production (35 points max)
        rush_yards = stats.get('rushing_yards', 0)
        rush_tds = stats.get('rushing_touchdowns', 0)
        
        if rush_yards >= 1500: score += 25
        elif rush_yards >= 1200: score += 22
        elif rush_yards >= 1000: score += 18
        elif rush_yards >= 800: score += 14
        elif rush_yards >= 600: score += 10
        else: score += max(rush_yards / 80, 0)
        
        score += min(rush_tds * 1.5, 10)
        
        # Receiving value (20 points max)
        rec_yards = stats.get('receiving_yards', 0)
        receptions = stats.get('receptions', 0)
        rec_tds = stats.get('receiving_touchdowns', 0)
        
        if receptions >= 50: score += 10
        elif receptions >= 35: score += 7
        elif receptions >= 20: score += 4
        
        score += min(rec_yards / 50, 5)
        score += min(rec_tds * 2, 5)
        
        # Carries (workload indicator - 15 points max)
        carries = stats.get('carries', 0)
        if carries >= 250: score += 15
        elif carries >= 200: score += 12
        elif carries >= 150: score += 9
        elif carries >= 100: score += 6
        else: score += max(carries / 20, 0)
        
        return min(score, 100.0)
    
    # ========================================================================
    # WIDE RECEIVER
    # ========================================================================
    
    def _calculate_wr_score(self, stats: Dict) -> float:
        """Calculate WR performance score"""
        score = 0.0
        
        # Receiving yards (35 points max)
        rec_yards = stats.get('receiving_yards', 0)
        if rec_yards >= 1200: score += 35
        elif rec_yards >= 1000: score += 30
        elif rec_yards >= 800: score += 25
        elif rec_yards >= 600: score += 18
        elif rec_yards >= 400: score += 12
        else: score += max(rec_yards / 40, 0)
        
        # Receptions (volume - 25 points max)
        receptions = stats.get('receptions', 0)
        if receptions >= 80: score += 25
        elif receptions >= 70: score += 22
        elif receptions >= 60: score += 19
        elif receptions >= 50: score += 15
        elif receptions >= 35: score += 10
        else: score += max(receptions / 4, 0)
        
        # Touchdowns (20 points max)
        rec_tds = stats.get('receiving_touchdowns', 0)
        if rec_tds >= 12: score += 20
        elif rec_tds >= 10: score += 18
        elif rec_tds >= 8: score += 15
        elif rec_tds >= 6: score += 12
        else: score += rec_tds * 2
        
        # Yards per reception (efficiency - 20 points max)
        if receptions > 0:
            ypr = rec_yards / receptions
            if ypr >= 18.0: score += 20
            elif ypr >= 16.0: score += 17
            elif ypr >= 14.0: score += 14
            elif ypr >= 12.0: score += 10
            elif ypr >= 10.0: score += 6
            else: score += max(ypr * 0.5, 0)
        
        return min(score, 100.0)
    
    # ========================================================================
    # TIGHT END
    # ========================================================================
    
    def _calculate_te_score(self, stats: Dict) -> float:
        """Calculate TE performance score"""
        score = 0.0
        
        # Receiving production (40 points max)
        rec_yards = stats.get('receiving_yards', 0)
        receptions = stats.get('receptions', 0)
        rec_tds = stats.get('receiving_touchdowns', 0)
        
        if rec_yards >= 800: score += 25
        elif rec_yards >= 600: score += 20
        elif rec_yards >= 400: score += 14
        elif rec_yards >= 200: score += 8
        else: score += max(rec_yards / 30, 0)
        
        if receptions >= 60: score += 15
        elif receptions >= 45: score += 12
        elif receptions >= 30: score += 8
        else: score += max(receptions / 4, 0)
        
        # TDs (15 points max)
        score += min(rec_tds * 2.5, 15)
        
        # YPR (15 points max)
        if receptions > 0:
            ypr = rec_yards / receptions
            if ypr >= 14.0: score += 15
            elif ypr >= 12.0: score += 12
            elif ypr >= 10.0: score += 9
            else: score += max(ypr * 0.8, 0)
        
        # Blocking (placeholder - 30 points)
        # Note: We don't have blocking stats, so give benefit of doubt to high-volume receivers
        # Assume if they're getting targets, they're blocking too
        if receptions >= 40:
            score += 20  # Getting lots of snaps, likely blocking too
        elif receptions >= 20:
            score += 15
        else:
            score += 10  # Minimum blocking credit
        
        return min(score, 100.0)
    
    # ========================================================================
    # DEFENSIVE LINE
    # ========================================================================
    
    def _calculate_dl_score(self, stats: Dict) -> float:
        """Calculate DL performance score"""
        score = 0.0
        
        # Sacks (35 points max) - PREMIER STAT
        sacks = stats.get('sacks', 0)
        if sacks >= 10: score += 35  # Double-digit sacks = elite
        elif sacks >= 8: score += 32
        elif sacks >= 6: score += 28
        elif sacks >= 4: score += 22
        elif sacks >= 2: score += 15
        else: score += sacks * 6
        
        # Tackles for loss (30 points max)
        tfl = stats.get('tackles_for_loss', 0)
        if tfl >= 15: score += 30
        elif tfl >= 12: score += 26
        elif tfl >= 10: score += 22
        elif tfl >= 7: score += 16
        elif tfl >= 4: score += 10
        else: score += tfl * 2.5
        
        # Total tackles (20 points max)
        tackles = stats.get('tackles', 0)
        if tackles >= 70: score += 20
        elif tackles >= 60: score += 17
        elif tackles >= 50: score += 14
        elif tackles >= 40: score += 11
        elif tackles >= 30: score += 8
        else: score += max(tackles * 0.25, 0)
        
        # QB hurries/pressures (15 points max)
        qb_hur = stats.get('qb_hurries', 0)
        score += min(qb_hur * 1.5, 15)
        
        return min(score, 100.0)
    
    # ========================================================================
    # LINEBACKER
    # ========================================================================
    
    def _calculate_lb_score(self, stats: Dict) -> float:
        """Calculate LB performance score"""
        score = 0.0
        
        # Total tackles (40 points max) - PREMIER STAT for LB
        tackles = stats.get('tackles', 0)
        if tackles >= 100: score += 40  # Elite tackler
        elif tackles >= 90: score += 37
        elif tackles >= 80: score += 33
        elif tackles >= 70: score += 28
        elif tackles >= 60: score += 22
        elif tackles >= 50: score += 16
        else: score += max(tackles * 0.3, 0)
        
        # Solo tackles (15 points max)
        solo = stats.get('solo_tackles', 0)
        if solo >= 60: score += 15
        elif solo >= 50: score += 12
        elif solo >= 40: score += 9
        elif solo >= 30: score += 6
        else: score += max(solo * 0.2, 0)
        
        # Tackles for loss (20 points max)
        tfl = stats.get('tackles_for_loss', 0)
        if tfl >= 12: score += 20
        elif tfl >= 9: score += 16
        elif tfl >= 6: score += 12
        elif tfl >= 3: score += 8
        else: score += tfl * 2.5
        
        # Sacks (15 points max)
        sacks = stats.get('sacks', 0)
        if sacks >= 5: score += 15
        elif sacks >= 3: score += 10
        else: score += sacks * 3
        
        # Pass deflections (10 points max) - coverage ability
        pd = stats.get('passes_deflected', 0)
        score += min(pd * 1.5, 10)
        
        return min(score, 100.0)
    
    # ========================================================================
    # DEFENSIVE BACKS (CB/S)
    # ========================================================================
    
    def _calculate_db_score(self, stats: Dict) -> float:
        """Calculate DB (CB/S) performance score"""
        score = 0.0
        
        # Pass deflections (30 points max) - PREMIER STAT
        pd = stats.get('passes_deflected', 0)
        if pd >= 12: score += 30
        elif pd >= 10: score += 26
        elif pd >= 8: score += 22
        elif pd >= 6: score += 17
        elif pd >= 4: score += 12
        else: score += pd * 3
        
        # Interceptions (25 points max)
        ints = stats.get('interceptions', 0)
        if ints >= 5: score += 25
        elif ints >= 4: score += 22
        elif ints >= 3: score += 18
        elif ints >= 2: score += 12
        elif ints >= 1: score += 7
        
        # Tackles (25 points max)
        tackles = stats.get('tackles', 0)
        if tackles >= 80: score += 25  # Elite box safety
        elif tackles >= 60: score += 20
        elif tackles >= 40: score += 14
        elif tackles >= 25: score += 8
        else: score += max(tackles * 0.3, 0)
        
        # TFL (10 points max) - blitzing/run support
        tfl = stats.get('tackles_for_loss', 0)
        score += min(tfl * 2, 10)
        
        # Defensive TDs (10 points max) - game-changers
        def_tds = stats.get('defensive_touchdowns', 0)
        score += min(def_tds * 10, 10)
        
        return min(score, 100.0)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_conference_adjustment(self, conference: str) -> float:
        """Conference strength adjustment"""
        conference_factors = {
            'SEC': 1.10,
            'Big Ten': 1.08,
            'Big 12': 1.05,
            'ACC': 1.03,
            'Pac-12': 1.02,
            'American': 0.98,
            'Mountain West': 0.96,
            'Sun Belt': 0.95,
            'MAC': 0.94,
            'C-USA': 0.93,
        }
        return conference_factors.get(conference, 1.0)


def create_all_positions_calculator():
    """Factory function"""
    return AllPositionsPerformanceCalculator()


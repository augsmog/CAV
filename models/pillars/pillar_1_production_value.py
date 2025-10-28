"""
Pillar 1: Production Value Model (Historical Performance)
Quantifies on-field contribution using position-specific metrics
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import statistics


@dataclass
class ProductionValueResult:
    """Result from production value calculation"""
    production_score: float  # 0-100 normalized score
    weighted_score: float  # Conference/competition adjusted
    percentile: float  # Percentile vs. position (0-100)
    components: Dict[str, float]  # Individual metric scores
    metadata: Dict[str, Any]  # Additional context


class ProductionValueModel:
    """
    Calculates historical production value for college athletes
    Supports both Football and Basketball with position-specific metrics
    """

    # Conference strength multipliers
    FOOTBALL_CONFERENCE_MULTIPLIERS = {
        'SEC': 1.20,
        'Big Ten': 1.15,
        'Big 12': 1.10,
        'ACC': 1.10,
        'Pac-12': 1.05,
        'American': 0.95,
        'Mountain West': 0.90,
        'Sun Belt': 0.90,
        'MAC': 0.85,
        'C-USA': 0.85,
        'Independent': 1.00,
        'FCS': 0.60
    }

    BASKETBALL_CONFERENCE_MULTIPLIERS = {
        'ACC': 1.10,
        'Big Ten': 1.10,
        'Big 12': 1.10,
        'Big East': 1.10,
        'SEC': 1.05,
        'Pac-12': 1.05,
        'American': 0.95,
        'Mountain West': 0.90,
        'WCC': 0.95,
        'Atlantic 10': 0.95,
        'Missouri Valley': 0.90,
        'Summit': 0.85,
        'WAC': 0.85,
    }

    # Competition tier multipliers
    COMPETITION_MULTIPLIERS = {
        'P4': 1.20,  # Power 4 opponents
        'G5': 0.90,  # Group of 5
        'FCS': 0.60,  # FCS opponents
    }

    def __init__(self, sport: str = 'football'):
        """
        Initialize production value model

        Args:
            sport: 'football' or 'basketball'
        """
        self.sport = sport.lower()

    def calculate_football_production(
        self,
        stats: Dict[str, Any],
        position: str,
        conference: str,
        opponent_tiers: Optional[Dict[str, int]] = None
    ) -> ProductionValueResult:
        """
        Calculate football production value

        Args:
            stats: Player statistics dictionary
            position: Player position (QB, RB, WR, etc.)
            conference: Player's conference
            opponent_tiers: Dict of games by tier (P4, G5, FCS)

        Returns:
            ProductionValueResult with scores and breakdowns
        """
        position = position.upper()

        # Route to position-specific calculator
        if position == 'QB':
            components = self._calculate_qb_production(stats)
        elif position == 'RB':
            components = self._calculate_rb_production(stats)
        elif position in ['WR', 'TE']:
            components = self._calculate_receiver_production(stats, position)
        elif position in ['OT', 'OG', 'C', 'OL']:
            components = self._calculate_ol_production(stats)
        elif position in ['DT', 'DE', 'EDGE', 'DL']:
            components = self._calculate_dl_production(stats)
        elif position == 'LB':
            components = self._calculate_lb_production(stats)
        elif position in ['CB', 'S', 'DB']:
            components = self._calculate_db_production(stats)
        elif position == 'K':
            components = self._calculate_kicker_production(stats)
        elif position == 'P':
            components = self._calculate_punter_production(stats)
        else:
            components = {'overall': 50.0}  # Default

        # Calculate base production score (0-100)
        production_score = self._aggregate_components(components)

        # Apply conference adjustment
        conf_multiplier = self.FOOTBALL_CONFERENCE_MULTIPLIERS.get(conference, 1.0)

        # Apply opponent tier weighting if available
        competition_adjustment = self._calculate_competition_adjustment(
            opponent_tiers
        ) if opponent_tiers else 1.0

        # Calculate weighted score
        weighted_score = production_score * conf_multiplier * competition_adjustment

        # Cap at 100
        weighted_score = min(weighted_score, 100.0)

        # Calculate percentile (placeholder - would need historical data)
        percentile = self._estimate_percentile(weighted_score)

        # Calculate 3-year rolling average with recency weighting if historical data
        # For now, just use current season

        return ProductionValueResult(
            production_score=production_score,
            weighted_score=weighted_score,
            percentile=percentile,
            components=components,
            metadata={
                'position': position,
                'conference': conference,
                'conference_multiplier': conf_multiplier,
                'competition_adjustment': competition_adjustment,
                'sport': 'football'
            }
        )

    def calculate_basketball_production(
        self,
        stats: Dict[str, Any],
        position: str,
        conference: str,
        opponent_quality: Optional[List[int]] = None
    ) -> ProductionValueResult:
        """
        Calculate basketball production value

        Args:
            stats: Player statistics dictionary
            position: Player position (PG, SG, SF, PF, C)
            conference: Player's conference
            opponent_quality: List of opponent NET rankings or similar

        Returns:
            ProductionValueResult with scores and breakdowns
        """
        # Core metrics (position-agnostic)
        components = {}

        # Offensive rating (points per 100 possessions)
        ppg = stats.get('points_per_game', 0)
        components['offensive_rating'] = self._normalize_stat(ppg, 0, 30, 100)

        # Efficiency
        ts_pct = stats.get('true_shooting_pct', stats.get('fg_pct', 0))
        components['shooting_efficiency'] = ts_pct * 100

        # Playmaking
        ast_to_ratio = stats.get('assist_turnover_ratio', 1.0)
        components['playmaking'] = self._normalize_stat(ast_to_ratio, 0, 4, 100)

        # Rebounding
        rpg = stats.get('rebounds_per_game', 0)
        components['rebounding'] = self._normalize_stat(rpg, 0, 12, 100)

        # Advanced metrics if available
        per = stats.get('player_efficiency_rating', None)
        if per:
            components['per'] = self._normalize_stat(per, 0, 35, 100)

        bpm = stats.get('box_plus_minus', None)
        if bpm:
            components['bpm'] = self._normalize_stat(bpm, -10, 15, 100)

        ws_per_40 = stats.get('win_shares_per_40', None)
        if ws_per_40:
            components['win_shares'] = self._normalize_stat(ws_per_40, 0, 0.30, 100)

        # Position-specific emphasis
        position = position.upper()
        weights = self._get_basketball_position_weights(position)

        # Calculate base production score
        production_score = self._aggregate_components(components, weights)

        # Apply conference adjustment
        conf_multiplier = self.BASKETBALL_CONFERENCE_MULTIPLIERS.get(conference, 1.0)

        # Apply opponent quality adjustment if available
        competition_adjustment = self._calculate_basketball_competition_adjustment(
            opponent_quality
        ) if opponent_quality else 1.0

        # Calculate weighted score
        weighted_score = production_score * conf_multiplier * competition_adjustment
        weighted_score = min(weighted_score, 100.0)

        # Estimate percentile
        percentile = self._estimate_percentile(weighted_score)

        return ProductionValueResult(
            production_score=production_score,
            weighted_score=weighted_score,
            percentile=percentile,
            components=components,
            metadata={
                'position': position,
                'conference': conference,
                'conference_multiplier': conf_multiplier,
                'competition_adjustment': competition_adjustment,
                'sport': 'basketball'
            }
        )

    # ==================== Football Position-Specific Calculators ====================

    def _calculate_qb_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate QB production components"""
        components = {}

        # Passing efficiency (EPA per play if available, else passer rating)
        epa_per_play = stats.get('epa_per_play', None)
        if epa_per_play is not None:
            components['passing_efficiency'] = self._normalize_stat(epa_per_play, -0.3, 0.5, 100)
        else:
            passer_rating = stats.get('passer_rating', 100)
            components['passing_efficiency'] = self._normalize_stat(passer_rating, 50, 180, 100)

        # Completion percentage over expectation
        comp_pct = stats.get('completion_pct', 60)
        components['completion_pct'] = self._normalize_stat(comp_pct, 50, 75, 100)

        # TD:INT ratio
        td = stats.get('passing_touchdowns', 0)
        interceptions = stats.get('interceptions', 1)  # Avoid div by zero
        td_int_ratio = td / max(interceptions, 1)
        components['td_int_ratio'] = self._normalize_stat(td_int_ratio, 0, 6, 100)

        # Rushing value added (dual threat)
        rush_yards = stats.get('rushing_yards', 0)
        rush_td = stats.get('rushing_touchdowns', 0)
        rushing_value = rush_yards + (rush_td * 100)
        components['rushing_value'] = self._normalize_stat(rushing_value, 0, 800, 100)

        # Third down conversion rate
        third_down_conv = stats.get('third_down_conversion_rate', 0.35)
        components['third_down'] = third_down_conv * 100

        # Red zone efficiency
        rz_td_pct = stats.get('red_zone_td_pct', 0.50)
        components['red_zone'] = rz_td_pct * 100

        # Explosive plays (70+ yards)
        explosive_plays = stats.get('plays_70_plus', 0)
        components['explosiveness'] = self._normalize_stat(explosive_plays, 0, 10, 100)

        # Sack rate (lower is better)
        sack_rate = stats.get('sack_rate', 0.05)
        components['sack_avoidance'] = (1 - min(sack_rate, 0.15)) * 100 / 0.85

        return components

    def _calculate_rb_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate RB production components"""
        components = {}

        # Yards after contact per attempt
        yac_per_att = stats.get('yards_after_contact_per_att', 2.5)
        components['yards_after_contact'] = self._normalize_stat(yac_per_att, 1, 5, 100)

        # Success rate
        success_rate = stats.get('success_rate', 0.40)
        components['success_rate'] = success_rate * 100

        # Yards per carry
        ypc = stats.get('yards_per_carry', 4.0)
        components['yards_per_carry'] = self._normalize_stat(ypc, 2, 8, 100)

        # Receiving value
        receptions = stats.get('receptions', 0)
        receiving_yards = stats.get('receiving_yards', 0)
        receiving_value = (receptions * 5) + receiving_yards
        components['receiving_value'] = self._normalize_stat(receiving_value, 0, 600, 100)

        # Broken tackles forced
        broken_tackles = stats.get('broken_tackles', 0)
        carries = stats.get('carries', 1)
        bt_rate = broken_tackles / max(carries, 1)
        components['broken_tackles'] = self._normalize_stat(bt_rate, 0, 0.3, 100)

        # Red zone production
        rz_td = stats.get('red_zone_touchdowns', 0)
        components['red_zone'] = self._normalize_stat(rz_td, 0, 15, 100)

        # Third down conversion
        third_down_conv = stats.get('third_down_conversion_rate', 0.40)
        components['third_down'] = third_down_conv * 100

        return components

    def _calculate_receiver_production(self, stats: Dict[str, Any], position: str) -> Dict[str, float]:
        """Calculate WR/TE production components"""
        components = {}

        # Yards per route run (YPRR)
        yprr = stats.get('yards_per_route_run', 1.5)
        components['yprr'] = self._normalize_stat(yprr, 0.5, 3.5, 100)

        # Catch rate
        catch_rate = stats.get('catch_rate', 0.60)
        components['catch_rate'] = catch_rate * 100

        # Yards after catch
        yac = stats.get('yards_after_catch', 0)
        receptions = stats.get('receptions', 1)
        yac_per_rec = yac / max(receptions, 1)
        components['yac'] = self._normalize_stat(yac_per_rec, 2, 10, 100)

        # Contested catch rate
        contested_catch_rate = stats.get('contested_catch_rate', 0.40)
        components['contested_catches'] = contested_catch_rate * 100

        # Drop rate (lower is better)
        drop_rate = stats.get('drop_rate', 0.05)
        components['hands'] = (1 - min(drop_rate, 0.15)) * 100 / 0.85

        # Red zone production
        rz_td = stats.get('red_zone_touchdowns', 0)
        components['red_zone'] = self._normalize_stat(rz_td, 0, 12, 100)

        # Total production
        receiving_yards = stats.get('receiving_yards', 0)
        rec_td = stats.get('receiving_touchdowns', 0)
        total_value = receiving_yards + (rec_td * 100)
        components['total_production'] = self._normalize_stat(total_value, 0, 1400, 100)

        return components

    def _calculate_ol_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate OL production components"""
        components = {}

        # Pass blocking (pressures/sacks allowed - lower is better)
        pressures_allowed = stats.get('pressures_allowed', 20)
        snaps = stats.get('pass_block_snaps', 500)
        pressure_rate = pressures_allowed / max(snaps, 1)
        components['pass_protection'] = (1 - min(pressure_rate, 0.10)) * 100 / 0.90

        # Run blocking grade
        run_block_grade = stats.get('run_block_grade', 60)
        components['run_blocking'] = run_block_grade

        # Penalties per snap (lower is better)
        penalties = stats.get('penalties', 5)
        total_snaps = stats.get('total_snaps', 600)
        penalty_rate = penalties / max(total_snaps, 1)
        components['discipline'] = (1 - min(penalty_rate, 0.05)) * 100 / 0.95

        # Versatility bonus (can play multiple positions)
        positions_played = stats.get('positions_played', 1)
        components['versatility'] = min(positions_played * 20, 100)

        return components

    def _calculate_dl_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate DL/EDGE production components"""
        components = {}

        # Pass rush efficiency
        pressures = stats.get('pressures', 0)
        sacks = stats.get('sacks', 0)
        pass_rush_snaps = stats.get('pass_rush_snaps', 200)
        pressure_rate = (pressures + sacks) / max(pass_rush_snaps, 1)
        components['pass_rush'] = self._normalize_stat(pressure_rate, 0.05, 0.25, 100)

        # Run stop rate
        run_stops = stats.get('run_stops', 0)
        run_snaps = stats.get('run_defense_snaps', 300)
        run_stop_rate = run_stops / max(run_snaps, 1)
        components['run_defense'] = self._normalize_stat(run_stop_rate, 0.05, 0.20, 100)

        # Tackles for loss
        tfl = stats.get('tackles_for_loss', 0)
        components['tfl'] = self._normalize_stat(tfl, 0, 20, 100)

        # Total sacks
        components['sacks'] = self._normalize_stat(sacks, 0, 15, 100)

        return components

    def _calculate_lb_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate LB production components"""
        components = {}

        # Tackling efficiency
        tackles = stats.get('tackles', 0)
        missed_tackles = stats.get('missed_tackles', 0)
        tackle_rate = tackles / max(tackles + missed_tackles, 1)
        components['tackling'] = tackle_rate * 100

        # Coverage ability
        coverage_grade = stats.get('coverage_grade', 60)
        components['coverage'] = coverage_grade

        # Run stop rate
        run_stops = stats.get('run_stops', 0)
        components['run_defense'] = self._normalize_stat(run_stops, 0, 50, 100)

        # Blitz effectiveness
        blitz_pressures = stats.get('blitz_pressures', 0)
        components['blitz'] = self._normalize_stat(blitz_pressures, 0, 15, 100)

        # Versatility
        coverage_snaps = stats.get('coverage_snaps', 0)
        total_snaps = stats.get('total_snaps', 1)
        versatility = min(coverage_snaps / total_snaps, 0.5) * 200
        components['versatility'] = versatility

        return components

    def _calculate_db_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate DB (CB/S) production components"""
        components = {}

        # Completion % allowed when targeted (lower is better)
        comp_allowed = stats.get('completion_pct_allowed', 0.60)
        components['coverage'] = (1 - comp_allowed) * 100

        # Yards per coverage snap (lower is better)
        yards_allowed = stats.get('yards_allowed', 400)
        coverage_snaps = stats.get('coverage_snaps', 400)
        yards_per_snap = yards_allowed / max(coverage_snaps, 1)
        components['yards_allowed'] = (1 - min(yards_per_snap, 1.5) / 1.5) * 100

        # Interceptions + pass breakups
        interceptions = stats.get('interceptions', 0)
        pbu = stats.get('pass_breakups', 0)
        playmaking = interceptions * 2 + pbu
        components['playmaking'] = self._normalize_stat(playmaking, 0, 20, 100)

        # Missed tackle rate (lower is better)
        missed_tackles = stats.get('missed_tackles', 0)
        tackle_attempts = stats.get('tackle_attempts', 50)
        missed_rate = missed_tackles / max(tackle_attempts, 1)
        components['tackling'] = (1 - min(missed_rate, 0.20)) * 100 / 0.80

        return components

    def _calculate_kicker_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Kicker production components"""
        components = {}

        # FG% by distance
        fg_pct = stats.get('fg_pct', 0.75)
        components['fg_pct'] = fg_pct * 100

        # Long FGs made (50+)
        fg_50_plus = stats.get('fg_50_plus_made', 0)
        components['long_range'] = self._normalize_stat(fg_50_plus, 0, 8, 100)

        # Clutch performance (FG in final 2 min of half)
        clutch_fg_pct = stats.get('clutch_fg_pct', 0.70)
        components['clutch'] = clutch_fg_pct * 100

        return components

    def _calculate_punter_production(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Punter production components"""
        components = {}

        # Net punting average
        net_avg = stats.get('net_punting_avg', 38)
        components['net_avg'] = self._normalize_stat(net_avg, 30, 45, 100)

        # Coffin corner rate (inside 20)
        inside_20 = stats.get('inside_20', 0)
        total_punts = stats.get('total_punts', 1)
        inside_20_rate = inside_20 / max(total_punts, 1)
        components['coffin_corner'] = inside_20_rate * 100

        return components

    # ==================== Basketball Position Weights ====================

    def _get_basketball_position_weights(self, position: str) -> Dict[str, float]:
        """Get position-specific weights for basketball metrics"""
        base_weights = {
            'offensive_rating': 0.25,
            'shooting_efficiency': 0.20,
            'playmaking': 0.15,
            'rebounding': 0.15,
            'per': 0.10,
            'bpm': 0.10,
            'win_shares': 0.05
        }

        # Adjust based on position
        if position == 'PG':
            base_weights['playmaking'] = 0.25
            base_weights['offensive_rating'] = 0.20
        elif position in ['SF', 'PF']:
            base_weights['rebounding'] = 0.20
        elif position == 'C':
            base_weights['rebounding'] = 0.25
            base_weights['shooting_efficiency'] = 0.15

        return base_weights

    # ==================== Helper Methods ====================

    def _normalize_stat(self, value: float, min_val: float, max_val: float, scale: float = 100) -> float:
        """Normalize a stat to 0-scale range"""
        if max_val == min_val:
            return scale / 2
        normalized = (value - min_val) / (max_val - min_val)
        return max(0, min(normalized * scale, scale))

    def _aggregate_components(
        self,
        components: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """Aggregate component scores into overall score"""
        if not components:
            return 50.0

        if weights:
            # Weighted average
            total_weight = sum(weights.get(k, 1.0) for k in components.keys())
            weighted_sum = sum(
                v * weights.get(k, 1.0)
                for k, v in components.items()
            )
            return weighted_sum / total_weight if total_weight > 0 else 50.0
        else:
            # Simple average
            return statistics.mean(components.values())

    def _calculate_competition_adjustment(
        self,
        opponent_tiers: Dict[str, int]
    ) -> float:
        """
        Calculate adjustment based on opponent quality

        Args:
            opponent_tiers: Dict with keys 'P4', 'G5', 'FCS' and game counts

        Returns:
            Adjustment multiplier (typically 0.9-1.2)
        """
        total_games = sum(opponent_tiers.values())
        if total_games == 0:
            return 1.0

        weighted_sum = sum(
            opponent_tiers.get(tier, 0) * self.COMPETITION_MULTIPLIERS[tier]
            for tier in ['P4', 'G5', 'FCS']
        )

        return weighted_sum / total_games

    def _calculate_basketball_competition_adjustment(
        self,
        opponent_quality: List[int]
    ) -> float:
        """
        Calculate adjustment based on opponent NET rankings

        Args:
            opponent_quality: List of opponent NET rankings (lower is better)

        Returns:
            Adjustment multiplier
        """
        if not opponent_quality:
            return 1.0

        avg_opponent_rank = statistics.mean(opponent_quality)

        # Top 50 opponents = 1.2x, 50-100 = 1.1x, 100-200 = 1.0x, 200+ = 0.9x
        if avg_opponent_rank < 50:
            return 1.20
        elif avg_opponent_rank < 100:
            return 1.10
        elif avg_opponent_rank < 200:
            return 1.00
        else:
            return 0.90

    def _estimate_percentile(self, weighted_score: float) -> float:
        """
        Estimate percentile based on weighted score
        Would ideally use historical distribution, but using approximation

        Args:
            weighted_score: 0-100 score

        Returns:
            Estimated percentile (0-100)
        """
        # Approximate normal distribution mapping
        # 50 = 50th percentile, 70 = 84th, 85 = 95th, 60 = 69th
        if weighted_score >= 90:
            return 99
        elif weighted_score >= 85:
            return 95
        elif weighted_score >= 80:
            return 90
        elif weighted_score >= 70:
            return 84
        elif weighted_score >= 60:
            return 69
        elif weighted_score >= 50:
            return 50
        elif weighted_score >= 40:
            return 31
        elif weighted_score >= 30:
            return 16
        else:
            return 5

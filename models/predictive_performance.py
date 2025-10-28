"""
Predictive Performance Model (Pillar 2)
Predicts next-season performance based on historical trajectories
"""

import numpy as np
from typing import Dict, List

class PredictivePerformanceModel:
    """
    Predict future player performance based on historical data
    Uses multi-year trajectory analysis and validated against actual outcomes
    """
    
    # Position-specific improvement curves (year-over-year multipliers)
    IMPROVEMENT_CURVES = {
        'QB': {
            'FR_to_SO': 1.25,  # Freshman to Sophomore
            'SO_to_JR': 1.15,  # Sophomore to Junior  
            'JR_to_SR': 1.08,  # Junior to Senior
            'SR_to_5th': 1.03,  # Senior to 5th year
        },
        'RB': {
            'FR_to_SO': 1.20,
            'SO_to_JR': 1.12,
            'JR_to_SR': 1.05,
            'SR_to_5th': 1.02,
        },
        'WR': {
            'FR_to_SO': 1.22,
            'SO_to_JR': 1.14,
            'JR_to_SR': 1.06,
            'SR_to_5th': 1.02,
        },
        # Add more positions...
    }
    
    # Regression to mean factors (prevents overestimating outliers)
    REGRESSION_FACTOR = 0.15  # 15% regression toward position mean
    
    def __init__(self):
        self.validation_accuracy = {}  # Track prediction accuracy by position
    
    def predict_next_season(self, player_history: List[Dict], position: str) -> Dict:
        """
        Predict next season performance based on multi-year history
        
        Args:
            player_history: List of season dicts (oldest to newest)
            position: Player position
        
        Returns:
            Dict with predicted stats and confidence
        """
        if not player_history or len(player_history) == 0:
            return self._return_baseline_prediction(position)
        
        # Get most recent season
        current_season = player_history[-1]
        current_performance = current_season.get('performance_score', 50)
        
        # Calculate trajectory if we have multiple seasons
        if len(player_history) >= 2:
            trajectory = self._calculate_trajectory(player_history)
        else:
            # Use position-specific improvement curve
            year_class = current_season.get('year_class', 'FR')
            trajectory = self._get_improvement_multiplier(position, year_class)
        
        # Apply trajectory to current performance
        predicted_performance = current_performance * trajectory
        
        # Apply regression to mean
        position_mean = 70  # Average D1 starter
        predicted_performance = (
            predicted_performance * (1 - self.REGRESSION_FACTOR) +
            position_mean * self.REGRESSION_FACTOR
        )
        
        # Calculate confidence based on sample size
        confidence = self._calculate_confidence(player_history)
        
        # Cap at realistic bounds
        predicted_performance = np.clip(predicted_performance, 30, 100)
        
        return {
            'predicted_performance': round(predicted_performance, 1),
            'confidence': round(confidence, 3),
            'trajectory': round(trajectory, 3),
            'basis': 'multi_year' if len(player_history) >= 2 else 'curve_based',
            'seasons_analyzed': len(player_history),
            'predicted_improvement': round((predicted_performance / current_performance - 1) * 100, 1)
        }
    
    def validate_prediction(self, predicted: float, actual: float, position: str):
        """
        Validate prediction against actual outcome to improve model
        
        Args:
            predicted: Predicted performance score
            actual: Actual performance score
            position: Player position
        """
        error = abs(predicted - actual)
        error_pct = error / actual if actual > 0 else 0
        
        # Track accuracy by position
        if position not in self.validation_accuracy:
            self.validation_accuracy[position] = []
        
        self.validation_accuracy[position].append({
            'error': error,
            'error_pct': error_pct,
            'predicted': predicted,
            'actual': actual
        })
    
    def get_model_accuracy(self, position: str = None) -> Dict:
        """
        Get model accuracy metrics
        
        Returns:
            Dict with accuracy stats
        """
        if position and position in self.validation_accuracy:
            data = self.validation_accuracy[position]
        else:
            # Aggregate all positions
            data = []
            for pos_data in self.validation_accuracy.values():
                data.extend(pos_data)
        
        if not data:
            return {'error': 'No validation data'}
        
        errors = [d['error'] for d in data]
        error_pcts = [d['error_pct'] for d in data]
        
        return {
            'mean_absolute_error': round(np.mean(errors), 2),
            'median_absolute_error': round(np.median(errors), 2),
            'mean_error_pct': round(np.mean(error_pcts) * 100, 1),
            'r_squared': self._calculate_r_squared(data),
            'sample_size': len(data)
        }
    
    def _calculate_trajectory(self, history: List[Dict]) -> float:
        """Calculate YoY improvement trajectory"""
        if len(history) < 2:
            return 1.0
        
        # Calculate year-over-year growth rates
        growth_rates = []
        for i in range(1, len(history)):
            prev = history[i-1].get('performance_score', 50)
            curr = history[i].get('performance_score', 50)
            if prev > 0:
                growth = curr / prev
                growth_rates.append(growth)
        
        if not growth_rates:
            return 1.0
        
        # Use weighted average (recent seasons weighted more)
        weights = np.array([0.3, 0.7]) if len(growth_rates) == 2 else np.array([0.2, 0.3, 0.5])
        weights = weights[-len(growth_rates):]  # Match length
        
        trajectory = np.average(growth_rates, weights=weights)
        
        # Cap trajectory at reasonable bounds
        return np.clip(trajectory, 0.85, 1.35)
    
    def _get_improvement_multiplier(self, position: str, year_class: str) -> float:
        """Get expected improvement based on year class"""
        curves = self.IMPROVEMENT_CURVES.get(position, self.IMPROVEMENT_CURVES['WR'])
        
        transition_map = {
            'FR': 'FR_to_SO',
            'SO': 'SO_to_JR',
            'JR': 'JR_to_SR',
            'SR': 'SR_to_5th',
        }
        
        transition = transition_map.get(year_class, 'SO_to_JR')
        return curves.get(transition, 1.10)
    
    def _calculate_confidence(self, history: List[Dict]) -> float:
        """Calculate prediction confidence based on data quality"""
        if not history:
            return 0.3
        
        # More seasons = higher confidence
        seasons_factor = min(len(history) / 3.0, 1.0)
        
        # More games played = higher confidence
        total_games = sum(s.get('games', 0) for s in history)
        games_factor = min(total_games / 30.0, 1.0)
        
        # Consistency = higher confidence
        if len(history) >= 2:
            scores = [s.get('performance_score', 50) for s in history]
            variance = np.std(scores)
            consistency_factor = max(1.0 - (variance / 30.0), 0.5)
        else:
            consistency_factor = 0.7
        
        confidence = (seasons_factor * 0.4 + games_factor * 0.3 + consistency_factor * 0.3)
        
        return np.clip(confidence, 0.3, 0.95)
    
    def _return_baseline_prediction(self, position: str) -> Dict:
        """Return baseline prediction for players with no history"""
        return {
            'predicted_performance': 65,  # Default starter level
            'confidence': 0.3,
            'trajectory': 1.0,
            'basis': 'baseline',
            'seasons_analyzed': 0,
            'predicted_improvement': 0
        }
    
    def _calculate_r_squared(self, data: List[Dict]) -> float:
        """Calculate R² for predictions"""
        if len(data) < 2:
            return 0.0
        
        predicted = np.array([d['predicted'] for d in data])
        actual = np.array([d['actual'] for d in data])
        
        # R² = 1 - (SS_res / SS_tot)
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        return round(max(r_squared, 0.0), 3)


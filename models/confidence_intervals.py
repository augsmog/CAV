"""
Confidence Interval Calculator
Provides statistical confidence ranges for player valuations
Based on historical prediction accuracy
"""

import numpy as np
from typing import Dict, Tuple
from scipy import stats

class ConfidenceIntervalCalculator:
    """
    Calculates confidence intervals for player valuations
    based on historical prediction accuracy and data quality
    """
    
    def __init__(self):
        # Historical validation results (to be updated as model improves)
        self.historical_mae = {
            'QB': 125000,   # Mean Absolute Error for QBs
            'RB': 85000,
            'WR': 95000,
            'TE': 75000,
            'OL': 65000,
            'DL': 70000,
            'LB': 68000,
            'DB': 72000,
            'default': 90000
        }
        
        # R² scores by position (model fit quality)
        self.r_squared = {
            'QB': 0.76,
            'RB': 0.71,
            'WR': 0.73,
            'TE': 0.68,
            'OL': 0.65,
            'DL': 0.67,
            'LB': 0.66,
            'DB': 0.69,
            'default': 0.70
        }
    
    def calculate_interval(
        self,
        predicted_value: float,
        position: str,
        sample_size: int = 100,
        confidence_level: float = 0.80
    ) -> Tuple[float, float, Dict]:
        """
        Calculate confidence interval for a player valuation
        
        Args:
            predicted_value: The model's predicted value
            position: Player position
            sample_size: Number of snaps/games (data quality indicator)
            confidence_level: Confidence level (0.80 = 80%, 0.90 = 90%, etc.)
        
        Returns:
            (lower_bound, upper_bound, metadata)
        """
        # Get position-specific error
        mae = self.historical_mae.get(position, self.historical_mae['default'])
        r2 = self.r_squared.get(position, self.r_squared['default'])
        
        # Calculate standard error
        # SE increases for positions with worse fit (lower R²)
        se = mae / np.sqrt(r2)
        
        # Adjust for sample size (more data = tighter interval)
        # Sample size factor: 1.0 at 300 snaps, scales down for less, up for more
        sample_factor = np.sqrt(300 / max(sample_size, 10))
        adjusted_se = se * sample_factor
        
        # Calculate z-score for confidence level
        # 80% CI -> z=1.28, 90% CI -> z=1.645, 95% CI -> z=1.96
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        # Calculate margin of error
        margin = z_score * adjusted_se
        
        # Calculate bounds
        lower_bound = max(0, predicted_value - margin)
        upper_bound = predicted_value + margin
        
        # Calculate interval width as percentage
        interval_width_pct = (margin / predicted_value) * 100 if predicted_value > 0 else 0
        
        # Metadata
        metadata = {
            'confidence_level': confidence_level,
            'margin_of_error': margin,
            'interval_width_pct': interval_width_pct,
            'sample_size': sample_size,
            'sample_factor': sample_factor,
            'position_mae': mae,
            'position_r2': r2,
            'z_score': z_score
        }
        
        return (lower_bound, upper_bound, metadata)
    
    def get_confidence_label(self, interval_width_pct: float) -> str:
        """
        Get human-readable confidence label
        
        Args:
            interval_width_pct: Width of interval as % of predicted value
        
        Returns:
            Label like "Very High", "High", "Medium", "Low"
        """
        if interval_width_pct < 15:
            return "Very High"
        elif interval_width_pct < 25:
            return "High"
        elif interval_width_pct < 40:
            return "Medium"
        else:
            return "Low"
    
    def format_interval_display(
        self,
        predicted_value: float,
        lower_bound: float,
        upper_bound: float,
        confidence_level: float = 0.80
    ) -> str:
        """
        Format confidence interval for display
        
        Returns:
            String like "$725K - $975K (80% CI)"
        """
        if predicted_value < 1e6:
            # Display in thousands
            lower_k = lower_bound / 1000
            upper_k = upper_bound / 1000
            return f"${lower_k:.0f}K - ${upper_k:.0f}K ({confidence_level:.0%} CI)"
        else:
            # Display in millions
            lower_m = lower_bound / 1e6
            upper_m = upper_bound / 1e6
            return f"${lower_m:.2f}M - ${upper_m:.2f}M ({confidence_level:.0%} CI)"
    
    def update_historical_accuracy(self, position: str, mae: float, r2: float):
        """
        Update historical accuracy metrics as model improves
        
        Args:
            position: Position to update
            mae: New mean absolute error
            r2: New R² score
        """
        self.historical_mae[position] = mae
        self.r_squared[position] = r2
        
        print(f"Updated {position}: MAE=${mae:,.0f}, R²={r2:.3f}")

# Example usage
if __name__ == "__main__":
    calculator = ConfidenceIntervalCalculator()
    
    # Example: QB with $850K predicted value, 450 snaps
    predicted = 850000
    position = 'QB'
    snaps = 450
    
    # 80% confidence interval
    lower_80, upper_80, meta_80 = calculator.calculate_interval(
        predicted, position, snaps, confidence_level=0.80
    )
    
    print(f"\nPlayer: QB, Predicted Value: ${predicted:,}, Snaps: {snaps}")
    print(f"\n80% Confidence Interval: ${lower_80:,.0f} - ${upper_80:,.0f}")
    print(f"Interval Width: ±{meta_80['interval_width_pct']:.1f}%")
    print(f"Confidence: {calculator.get_confidence_label(meta_80['interval_width_pct'])}")
    
    # 90% confidence interval (wider)
    lower_90, upper_90, meta_90 = calculator.calculate_interval(
        predicted, position, snaps, confidence_level=0.90
    )
    
    print(f"\n90% Confidence Interval: ${lower_90:,.0f} - ${upper_90:,.0f}")
    print(f"Interval Width: ±{meta_90['interval_width_pct']:.1f}%")
    
    # Display format
    print(f"\nFormatted: {calculator.format_interval_display(predicted, lower_80, upper_80, 0.80)}")
    
    # Example with less data (100 snaps) - wider interval
    lower_low, upper_low, meta_low = calculator.calculate_interval(
        predicted, position, 100, confidence_level=0.80
    )
    print(f"\nWith Only 100 Snaps:")
    print(f"80% CI: ${lower_low:,.0f} - ${upper_low:,.0f}")
    print(f"Interval Width: ±{meta_low['interval_width_pct']:.1f}%")
    print(f"Confidence: {calculator.get_confidence_label(meta_low['interval_width_pct'])}")


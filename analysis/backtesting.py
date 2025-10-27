"""
Backtesting and Validation Framework
Tests model predictions against historical outcomes
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class BacktestResult:
    """Results from a single backtest"""
    player_id: str
    prediction_date: date
    actual_date: date
    
    predicted_value: float
    actual_value: float
    value_error: float
    value_error_pct: float
    
    predicted_destination: str
    actual_destination: str
    destination_correct: bool
    
    predicted_performance: float
    actual_performance: float
    performance_error: float


class BacktestingFramework:
    """
    Framework for backtesting model predictions
    """
    
    def __init__(self, valuation_engine):
        self.engine = valuation_engine
        self.results = []
    
    def backtest_transfers(self,
                          historical_transfers: List[Dict],
                          historical_player_data: Dict,
                          test_period: Tuple[date, date]) -> pd.DataFrame:
        """
        Backtest model on historical transfer data
        
        Args:
            historical_transfers: List of actual transfer records
            historical_player_data: Player data at time of transfer
            test_period: (start_date, end_date) for testing
            
        Returns:
            DataFrame with backtesting results
        """
        results = []
        
        for transfer in historical_transfers:
            transfer_date = transfer['transfer_date']
            
            # Only test transfers in test period
            if not (test_period[0] <= transfer_date <= test_period[1]):
                continue
            
            player_id = transfer['player_id']
            
            # Get player data as of transfer date
            player_data = historical_player_data.get(player_id, {})
            if not player_data:
                continue
            
            # Make prediction
            try:
                valuation = self.engine.calculate_comprehensive_valuation(
                    player_data,
                    transfer['from_program'],
                    target_programs=transfer.get('reported_finalists', [])
                )
                
                # Compare prediction to actual
                result = self._evaluate_prediction(
                    valuation,
                    transfer,
                    player_data
                )
                
                results.append(result)
            
            except Exception as e:
                print(f"Error processing player {player_id}: {e}")
                continue
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([vars(r) for r in results])
        return df
    
    def _evaluate_prediction(self,
                           valuation: Dict,
                           actual_transfer: Dict,
                           player_data: Dict) -> BacktestResult:
        """
        Evaluate a single prediction against actual outcome
        """
        # Value prediction
        predicted_value = valuation['market_value']
        actual_value = actual_transfer.get('nil_deal_value', None)
        
        if actual_value:
            value_error = abs(predicted_value - actual_value)
            value_error_pct = (value_error / actual_value) * 100
        else:
            value_error = None
            value_error_pct = None
        
        # Destination prediction
        alternative_values = valuation.get('alternative_program_values', {})
        if alternative_values:
            predicted_dest = max(alternative_values.items(), 
                               key=lambda x: x[1]['total_value'])[0]
        else:
            predicted_dest = None
        
        actual_dest = actual_transfer['to_program']
        destination_correct = (predicted_dest == actual_dest)
        
        # Performance prediction (use first season performance)
        predicted_performance = valuation['performance_score']
        actual_performance = actual_transfer.get('first_season_performance_grade', None)
        
        if actual_performance:
            performance_error = abs(predicted_performance - actual_performance)
        else:
            performance_error = None
        
        return BacktestResult(
            player_id=player_data['player_id'],
            prediction_date=actual_transfer['transfer_date'],
            actual_date=actual_transfer['transfer_date'],
            predicted_value=predicted_value,
            actual_value=actual_value,
            value_error=value_error,
            value_error_pct=value_error_pct,
            predicted_destination=predicted_dest,
            actual_destination=actual_dest,
            destination_correct=destination_correct,
            predicted_performance=predicted_performance,
            actual_performance=actual_performance,
            performance_error=performance_error
        )
    
    def calculate_accuracy_metrics(self, results_df: pd.DataFrame) -> Dict:
        """
        Calculate overall model accuracy metrics
        """
        metrics = {}
        
        # Value prediction accuracy
        valid_value_predictions = results_df[results_df['actual_value'].notna()]
        if len(valid_value_predictions) > 0:
            metrics['mean_absolute_error'] = valid_value_predictions['value_error'].mean()
            metrics['median_absolute_error'] = valid_value_predictions['value_error'].median()
            metrics['mean_absolute_pct_error'] = valid_value_predictions['value_error_pct'].mean()
            metrics['rmse'] = np.sqrt((valid_value_predictions['value_error'] ** 2).mean())
            
            # Predictions within X%
            metrics['pct_within_20pct'] = (valid_value_predictions['value_error_pct'] <= 20).mean() * 100
            metrics['pct_within_30pct'] = (valid_value_predictions['value_error_pct'] <= 30).mean() * 100
        
        # Destination prediction accuracy
        valid_dest_predictions = results_df[results_df['predicted_destination'].notna()]
        if len(valid_dest_predictions) > 0:
            metrics['destination_accuracy'] = valid_dest_predictions['destination_correct'].mean() * 100
        
        # Performance prediction accuracy
        valid_perf_predictions = results_df[results_df['actual_performance'].notna()]
        if len(valid_perf_predictions) > 0:
            metrics['performance_mae'] = valid_perf_predictions['performance_error'].mean()
            metrics['performance_rmse'] = np.sqrt((valid_perf_predictions['performance_error'] ** 2).mean())
        
        # Sample size
        metrics['n_value_predictions'] = len(valid_value_predictions)
        metrics['n_destination_predictions'] = len(valid_dest_predictions)
        metrics['n_performance_predictions'] = len(valid_perf_predictions)
        
        return metrics
    
    def analyze_by_position(self, results_df: pd.DataFrame, 
                           player_data: Dict) -> pd.DataFrame:
        """
        Analyze accuracy by position
        """
        # Add position to results
        results_df['position'] = results_df['player_id'].map(
            lambda pid: player_data.get(pid, {}).get('position', 'Unknown')
        )
        
        # Group by position
        position_analysis = []
        
        for position in results_df['position'].unique():
            pos_df = results_df[results_df['position'] == position]
            
            valid_values = pos_df[pos_df['actual_value'].notna()]
            
            if len(valid_values) > 0:
                position_analysis.append({
                    'position': position,
                    'n_samples': len(pos_df),
                    'mean_error_pct': valid_values['value_error_pct'].mean(),
                    'destination_accuracy': pos_df['destination_correct'].mean() * 100,
                    'median_predicted_value': pos_df['predicted_value'].median(),
                    'median_actual_value': valid_values['actual_value'].median()
                })
        
        return pd.DataFrame(position_analysis)
    
    def identify_model_weaknesses(self, results_df: pd.DataFrame) -> Dict:
        """
        Identify where the model performs poorly
        """
        weaknesses = {
            'high_error_players': [],
            'missed_destinations': [],
            'systematic_biases': {}
        }
        
        # Players with high error
        high_error = results_df[results_df['value_error_pct'] > 40]
        weaknesses['high_error_players'] = high_error['player_id'].tolist()
        
        # Commonly missed destinations
        wrong_dest = results_df[~results_df['destination_correct']]
        if len(wrong_dest) > 0:
            missed_dests = wrong_dest.groupby('actual_destination').size().sort_values(ascending=False)
            weaknesses['missed_destinations'] = missed_dests.head(5).to_dict()
        
        # Check for systematic over/under prediction
        valid_values = results_df[results_df['actual_value'].notna()]
        if len(valid_values) > 0:
            bias = (valid_values['predicted_value'] - valid_values['actual_value']).mean()
            weaknesses['systematic_biases']['value_bias'] = bias
            
            if bias > 0:
                weaknesses['systematic_biases']['direction'] = 'Over-prediction'
            else:
                weaknesses['systematic_biases']['direction'] = 'Under-prediction'
        
        return weaknesses
    
    def cross_validate(self,
                      all_transfers: List[Dict],
                      player_data: Dict,
                      n_folds: int = 5) -> Dict:
        """
        Perform k-fold cross-validation
        """
        # Sort transfers by date
        sorted_transfers = sorted(all_transfers, key=lambda x: x['transfer_date'])
        
        # Split into folds
        fold_size = len(sorted_transfers) // n_folds
        fold_results = []
        
        for i in range(n_folds):
            # Test fold
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < n_folds - 1 else len(sorted_transfers)
            test_transfers = sorted_transfers[test_start:test_end]
            
            # Run backtest on this fold
            test_dates = (
                test_transfers[0]['transfer_date'],
                test_transfers[-1]['transfer_date']
            )
            
            fold_df = self.backtest_transfers(
                test_transfers,
                player_data,
                test_dates
            )
            
            # Calculate metrics
            fold_metrics = self.calculate_accuracy_metrics(fold_df)
            fold_metrics['fold'] = i + 1
            fold_results.append(fold_metrics)
        
        # Aggregate across folds
        cv_results = pd.DataFrame(fold_results)
        
        return {
            'fold_results': cv_results,
            'mean_mae': cv_results['mean_absolute_error'].mean(),
            'std_mae': cv_results['mean_absolute_error'].std(),
            'mean_destination_accuracy': cv_results['destination_accuracy'].mean(),
            'std_destination_accuracy': cv_results['destination_accuracy'].std()
        }


class ModelCalibrator:
    """
    Calibrate and improve model based on backtesting results
    """
    
    def __init__(self, backtesting_framework):
        self.backtest_framework = backtesting_framework
    
    def suggest_improvements(self, results_df: pd.DataFrame) -> List[str]:
        """
        Suggest model improvements based on backtest results
        """
        suggestions = []
        
        # Check overall accuracy
        metrics = self.backtest_framework.calculate_accuracy_metrics(results_df)
        
        if metrics.get('mean_absolute_pct_error', 100) > 30:
            suggestions.append(
                "High value prediction error - consider refining NIL valuation components"
            )
        
        if metrics.get('destination_accuracy', 0) < 50:
            suggestions.append(
                "Low destination accuracy - scheme fit weights may need adjustment"
            )
        
        # Check for biases
        weaknesses = self.backtest_framework.identify_model_weaknesses(results_df)
        bias = weaknesses['systematic_biases'].get('value_bias', 0)
        
        if abs(bias) > 50000:
            if bias > 0:
                suggestions.append(
                    f"Model over-predicts value by ~${bias:,.0f} - reduce value multipliers"
                )
            else:
                suggestions.append(
                    f"Model under-predicts value by ~${abs(bias):,.0f} - increase value multipliers"
                )
        
        return suggestions
    
    def optimize_weights(self, 
                        results_df: pd.DataFrame,
                        player_data: Dict) -> Dict:
        """
        Suggest optimized weights for model components
        Uses grid search to find better weights
        """
        # This would implement actual optimization
        # For now, placeholder returning current weights
        
        suggested_weights = {
            'performance_weight': 0.30,
            'brand_weight': 0.25,
            'scheme_fit_weight': 0.20,
            'positional_value_weight': 0.15,
            'win_impact_weight': 0.10
        }
        
        return suggested_weights


def generate_backtest_report(results_df: pd.DataFrame,
                            metrics: Dict,
                            player_data: Dict) -> str:
    """
    Generate human-readable backtest report
    """
    report = []
    report.append("=" * 60)
    report.append("COLLEGE FOOTBALL PLAYER VALUATION MODEL")
    report.append("BACKTESTING REPORT")
    report.append("=" * 60)
    report.append("")
    
    # Overall metrics
    report.append("OVERALL ACCURACY METRICS")
    report.append("-" * 60)
    report.append(f"Sample Size: {metrics['n_value_predictions']} transfers")
    report.append("")
    report.append(f"Value Prediction:")
    report.append(f"  Mean Absolute Error: ${metrics.get('mean_absolute_error', 0):,.0f}")
    report.append(f"  Median Absolute Error: ${metrics.get('median_absolute_error', 0):,.0f}")
    report.append(f"  Mean Absolute % Error: {metrics.get('mean_absolute_pct_error', 0):.1f}%")
    report.append(f"  RMSE: ${metrics.get('rmse', 0):,.0f}")
    report.append(f"  Within 20%: {metrics.get('pct_within_20pct', 0):.1f}%")
    report.append(f"  Within 30%: {metrics.get('pct_within_30pct', 0):.1f}%")
    report.append("")
    report.append(f"Destination Prediction:")
    report.append(f"  Accuracy: {metrics.get('destination_accuracy', 0):.1f}%")
    report.append("")
    
    # Add more sections as needed
    
    return "\n".join(report)

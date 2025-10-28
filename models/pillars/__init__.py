"""
Six-Pillar Ensemble Valuation System

This package implements a comprehensive multi-model ensemble approach for
college athlete valuation, combining:

1. Production Value Model - Historical on-field performance
2. Predictive Future Performance Model - Trajectory and projections
3. Positional Scarcity & Market Demand Model - Supply/demand dynamics
4. Market Context & School-Specific Adjustments - Institutional factors
5. Intangible Factors & Brand Value Model - Off-field value
6. Risk Adjustment Model - Comprehensive risk analysis

The ensemble model combines these pillars using configurable weights to
produce comprehensive market valuations with full explainability.
"""

from .pillar_1_production_value import ProductionValueModel, ProductionValueResult
from .pillar_2_predictive_performance import PredictiveFuturePerformanceModel, PredictiveResult
from .pillar_3_positional_scarcity import PositionalScarcityModel, ScarcityResult, ScarcityTier
from .pillar_4_market_context import MarketContextModel, MarketContextResult, ConferenceTier
from .pillar_5_brand_intangibles import BrandIntangiblesModel, BrandValueResult
from .pillar_6_risk_adjustment import RiskAdjustmentModel, RiskAdjustmentResult, RiskLevel
from .ensemble_valuation import EnsembleValuationEngine, EnsembleValuationResult
from .output_formatter import ValuationOutputFormatter

__all__ = [
    # Models
    'ProductionValueModel',
    'PredictiveFuturePerformanceModel',
    'PositionalScarcityModel',
    'MarketContextModel',
    'BrandIntangiblesModel',
    'RiskAdjustmentModel',
    'EnsembleValuationEngine',
    'ValuationOutputFormatter',

    # Results
    'ProductionValueResult',
    'PredictiveResult',
    'ScarcityResult',
    'MarketContextResult',
    'BrandValueResult',
    'RiskAdjustmentResult',
    'EnsembleValuationResult',

    # Enums
    'ScarcityTier',
    'ConferenceTier',
    'RiskLevel',
]

__version__ = '1.0.0'
__author__ = 'CAV Team'

"""
Quick Test Script - Verify CAV Model Setup
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("  ✓ numpy imported successfully")
    except ImportError as e:
        print(f"  ✗ numpy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("  ✓ pandas imported successfully")
    except ImportError as e:
        print(f"  ✗ pandas import failed: {e}")
        return False
    
    try:
        from models.performance import PerformanceCalculator
        print("  ✓ PerformanceCalculator imported")
    except ImportError as e:
        print(f"  ✗ PerformanceCalculator import failed: {e}")
        return False
    
    try:
        from models.scheme_fit import SchemeFitCalculator
        print("  ✓ SchemeFitCalculator imported")
    except ImportError as e:
        print(f"  ✗ SchemeFitCalculator import failed: {e}")
        return False
    
    try:
        from models.brand_valuation import BrandValuationCalculator
        print("  ✓ BrandValuationCalculator imported")
    except ImportError as e:
        print(f"  ✗ BrandValuationCalculator import failed: {e}")
        return False
    
    try:
        from models.valuation_engine import create_valuation_engine
        print("  ✓ create_valuation_engine imported")
    except ImportError as e:
        print(f"  ✗ create_valuation_engine import failed: {e}")
        return False
    
    return True


def test_data_files():
    """Test that sample data files exist"""
    print("\nTesting data files...")
    
    project_root = Path(__file__).parent
    
    sample_players = project_root / 'data' / 'raw' / 'sample_players.csv'
    if sample_players.exists():
        print(f"  ✓ sample_players.csv found")
    else:
        print(f"  ✗ sample_players.csv not found at {sample_players}")
        return False
    
    sample_transfers = project_root / 'data' / 'raw' / 'sample_transfers.csv'
    if sample_transfers.exists():
        print(f"  ✓ sample_transfers.csv found")
    else:
        print(f"  ✗ sample_transfers.csv not found at {sample_transfers}")
        return False
    
    return True


def test_engine_creation():
    """Test that valuation engine can be created"""
    print("\nTesting engine creation...")
    
    try:
        from models.valuation_engine import create_valuation_engine
        engine = create_valuation_engine()
        print("  ✓ Valuation engine created successfully")
        return True
    except Exception as e:
        print(f"  ✗ Engine creation failed: {e}")
        return False


def test_simple_valuation():
    """Test a simple player valuation"""
    print("\nTesting simple valuation...")
    
    try:
        from models.valuation_engine import create_valuation_engine
        
        engine = create_valuation_engine()
        
        # Minimal player data
        player = {
            'player_id': 'TEST001',
            'name': 'Test Player',
            'position': 'QB',
            'height': 75,
            'weight': 215,
            'current_program': 'Texas',
            'eligibility_remaining': 2,
            'stats': {
                'completion_percentage': 65.0,
                'yards_per_attempt': 8.0,
            },
            'instagram_followers': 50000,
            'twitter_followers': 30000,
            'snaps_played': 500,
            'games_played': 10,
            'team_wins': 7,
            'team_losses': 3,
        }
        
        # Calculate valuation
        result = engine.calculate_comprehensive_valuation(
            player_data=player,
            current_program='Texas'
        )
        
        print(f"  ✓ Valuation completed")
        print(f"    - Market Value: ${result['market_value']:,.0f}")
        print(f"    - Performance Score: {result['performance_score']:.1f}")
        print(f"    - Brand Score: {result['brand_score']:.1f}")
        
        return True
    except Exception as e:
        print(f"  ✗ Valuation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("CAV MODEL SETUP VERIFICATION")
    print("=" * 70)
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Data Files Test", test_data_files),
        ("Engine Creation Test", test_engine_creation),
        ("Simple Valuation Test", test_simple_valuation),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! The CAV model is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run: python example_usage.py")
        print("  2. Review: README.md and QUICKSTART.md")
        print("  3. Explore: data/raw/sample_*.csv")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    print("=" * 70)


if __name__ == '__main__':
    main()


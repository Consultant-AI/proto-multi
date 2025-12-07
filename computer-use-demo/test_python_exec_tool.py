"""
Test suite for PythonExecutionTool.

Tests:
- Basic code execution
- Variable persistence across calls
- Error handling
- Library imports
- Reset functionality
"""

import asyncio
from computer_use_demo.tools.coding.python_exec import PythonExecutionTool


async def test_basic_execution():
    """Test basic Python code execution."""
    print("=" * 80)
    print("TEST 1: Basic Code Execution")
    print("=" * 80)

    tool = PythonExecutionTool()

    # Simple calculation
    result = await tool(code="print(2 + 2)")
    print(f"Output: {result.output}")
    print(f"Error: {result.error}")
    assert result.output == "4", f"Expected '4', got '{result.output}'"
    assert not result.error

    print("✅ Test passed\n")


async def test_variable_persistence():
    """Test that variables persist across executions."""
    print("=" * 80)
    print("TEST 2: Variable Persistence")
    print("=" * 80)

    tool = PythonExecutionTool()

    # First execution - set variable
    result1 = await tool(code="""
x = 100
y = 200
print(f"x={x}, y={y}")
""")
    print(f"First execution output: {result1.output}")
    assert "x=100, y=200" in result1.output

    # Second execution - use variables from first execution
    result2 = await tool(code="""
z = x + y
print(f"z={z}")
""")
    print(f"Second execution output: {result2.output}")
    assert "z=300" in result2.output

    print("✅ Test passed\n")


async def test_pandas_integration():
    """Test pandas library pre-loading."""
    print("=" * 80)
    print("TEST 3: Pandas Integration")
    print("=" * 80)

    tool = PythonExecutionTool()

    result = await tool(code="""
import pandas as pd
df = pd.DataFrame({'revenue': [100, 150, 200, 175]})
avg = df['revenue'].mean()
print(f"Average revenue: ${avg:.2f}")
""")
    print(f"Output: {result.output}")
    assert "Average revenue: $156.25" in result.output
    assert not result.error

    print("✅ Test passed\n")


async def test_numpy_calculations():
    """Test numpy pre-loading."""
    print("=" * 80)
    print("TEST 4: NumPy Calculations")
    print("=" * 80)

    tool = PythonExecutionTool()

    result = await tool(code="""
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
mean_val = np.mean(arr)
std_val = np.std(arr)
print(f"Mean: {mean_val}, Std: {std_val:.2f}")
""")
    print(f"Output: {result.output}")
    assert "Mean: 3.0" in result.output
    assert not result.error

    print("✅ Test passed\n")


async def test_error_handling():
    """Test error handling for syntax and runtime errors."""
    print("=" * 80)
    print("TEST 5: Error Handling")
    print("=" * 80)

    tool = PythonExecutionTool()

    # Syntax error
    result1 = await tool(code="print('hello'")
    print(f"Syntax error output: {result1.error}")
    assert "SyntaxError" in result1.error
    assert not result1.output

    # Runtime error
    result2 = await tool(code="x = 1 / 0")
    print(f"Runtime error output: {result2.error}")
    assert "ZeroDivisionError" in result2.error

    print("✅ Test passed\n")


async def test_reset_functionality():
    """Test environment reset."""
    print("=" * 80)
    print("TEST 6: Reset Functionality")
    print("=" * 80)

    tool = PythonExecutionTool()

    # Set a variable
    await tool(code="my_var = 42")

    # Verify variable exists
    result1 = await tool(code="print(my_var)")
    print(f"Before reset: {result1.output}")
    assert "42" in result1.output

    # Reset environment
    await tool(code="", reset=True)

    # Try to access variable (should fail)
    result2 = await tool(code="print(my_var)")
    print(f"After reset error: {result2.error}")
    assert "NameError" in result2.error

    print("✅ Test passed\n")


async def test_complex_data_analysis():
    """Test complex data analysis workflow."""
    print("=" * 80)
    print("TEST 7: Complex Data Analysis Workflow")
    print("=" * 80)

    tool = PythonExecutionTool()

    # Step 1: Load data
    result1 = await tool(code="""
import pandas as pd
import numpy as np

# Simulated customer data
np.random.seed(42)
df = pd.DataFrame({
    'customer_id': range(1, 101),
    'revenue': np.random.randint(50, 500, 100),
    'churn': np.random.choice([True, False], 100, p=[0.2, 0.8])
})

print(f"Loaded {len(df)} customers")
""")
    print(f"Step 1 - Load data: {result1.output}")
    assert "Loaded 100 customers" in result1.output

    # Step 2: Calculate metrics
    result2 = await tool(code="""
avg_revenue = df['revenue'].mean()
churn_rate = df['churn'].mean() * 100
total_revenue = df['revenue'].sum()

print(f"Average Revenue: ${avg_revenue:.2f}")
print(f"Churn Rate: {churn_rate:.1f}%")
print(f"Total Revenue: ${total_revenue:,.2f}")
""")
    print(f"Step 2 - Metrics:\n{result2.output}")
    assert "Average Revenue:" in result2.output
    assert "Churn Rate:" in result2.output

    # Step 3: Segment analysis
    result3 = await tool(code="""
# High-value customers (top 25%)
high_value_threshold = df['revenue'].quantile(0.75)
high_value_df = df[df['revenue'] >= high_value_threshold]

print(f"High-value customers: {len(high_value_df)}")
print(f"High-value avg revenue: ${high_value_df['revenue'].mean():.2f}")
print(f"High-value churn rate: {high_value_df['churn'].mean() * 100:.1f}%")
""")
    print(f"Step 3 - Segmentation:\n{result3.output}")
    assert "High-value customers: 25" in result3.output

    print("✅ Test passed\n")


async def test_statistical_analysis():
    """Test statistical analysis capabilities."""
    print("=" * 80)
    print("TEST 8: Statistical Analysis")
    print("=" * 80)

    tool = PythonExecutionTool()

    result = await tool(code="""
from scipy import stats
import numpy as np

# A/B test simulation
control = np.array([12.5, 12.3, 12.7, 12.4, 12.6])
variant = np.array([14.2, 14.0, 14.5, 14.1, 14.3])

# T-test
t_stat, p_value = stats.ttest_ind(variant, control)

print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")
print(f"Statistically significant: {p_value < 0.05}")
""")
    print(f"Output:\n{result.output}")
    assert "T-statistic:" in result.output
    assert "P-value:" in result.output

    print("✅ Test passed\n")


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PYTHON EXECUTION TOOL TEST SUITE")
    print("=" * 80 + "\n")

    tests = [
        test_basic_execution,
        test_variable_persistence,
        test_pandas_integration,
        test_numpy_calculations,
        test_error_handling,
        test_reset_functionality,
        test_complex_data_analysis,
        test_statistical_analysis,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {e}\n")
            failed += 1

    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)

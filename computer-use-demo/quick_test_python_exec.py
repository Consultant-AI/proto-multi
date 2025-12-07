"""
Quick interactive test of PythonExecutionTool.
"""

import asyncio
from computer_use_demo.tools.coding.python_exec import PythonExecutionTool


async def main():
    print("🧪 Testing PythonExecutionTool\n")

    tool = PythonExecutionTool()

    # Test 1: Simple calculation
    print("=" * 60)
    print("Test 1: Simple Calculation")
    print("=" * 60)
    result = await tool(code="print(2 + 2 * 10)")
    print(f"Code: print(2 + 2 * 10)")
    print(f"Output: {result.output}")
    print()

    # Test 2: Variable persistence
    print("=" * 60)
    print("Test 2: Variable Persistence")
    print("=" * 60)

    result1 = await tool(code="""
revenue = [100, 150, 200, 175, 225]
total = sum(revenue)
print(f"Total revenue: ${total}")
""")
    print("First execution:")
    print(f"Output: {result1.output}")
    print()

    result2 = await tool(code="""
avg = total / len(revenue)
print(f"Average revenue: ${avg:.2f}")
print(f"Revenue values: {revenue}")
""")
    print("Second execution (using variables from first!):")
    print(f"Output: {result2.output}")
    print()

    # Test 3: Data analysis
    print("=" * 60)
    print("Test 3: Data Analysis")
    print("=" * 60)
    result3 = await tool(code="""
# Customer churn analysis
total_customers = 1000
churned = 150
churn_rate = (churned / total_customers) * 100
retention_rate = 100 - churn_rate

print(f"Total Customers: {total_customers:,}")
print(f"Churned: {churned:,}")
print(f"Churn Rate: {churn_rate:.1f}%")
print(f"Retention Rate: {retention_rate:.1f}%")
""")
    print(f"Output:\n{result3.output}")
    print()

    # Test 4: Reset environment
    print("=" * 60)
    print("Test 4: Environment Reset")
    print("=" * 60)
    await tool(code="", reset=True)
    print("Environment reset!")

    result4 = await tool(code="print(revenue)")  # Should fail
    print("Trying to access 'revenue' after reset:")
    print(f"Error: {result4.error[:100]}..." if result4.error else "No error?")
    print()

    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

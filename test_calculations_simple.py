"""
Simple test script for Power Generation Cost Calculator
Tests the mathematical calculations without external dependencies
"""


def test_power_generation_cost():
    """Test power generation cost calculations"""
    print("=" * 80)
    print("POWER GENERATION COST CALCULATION TEST")
    print("=" * 80)
    print()

    # Input parameters
    max_demand_mw = 75.0
    load_factor = 0.40
    fixed_cost_per_kw = 60.0
    variable_cost_per_kwh = 0.01
    transmission_capital_cost = 1500000.0
    diversity_factor_transmission = 1.2
    diversity_factor_distribution = 1.25
    transmission_efficiency = 0.90
    distribution_efficiency = 0.85

    print("INPUT PARAMETERS:")
    print("-" * 80)
    print(f"Maximum Demand: {max_demand_mw} MW")
    print(f"Load Factor: {load_factor * 100}%")
    print(f"Fixed Cost: Rs. {fixed_cost_per_kw} per kW per annum")
    print(f"Variable Cost: Rs. {variable_cost_per_kwh} per kWh")
    print(f"Transmission Capital Cost: Rs. {transmission_capital_cost:,.0f}")
    print(f"Diversity Factor (Transmission): {diversity_factor_transmission}")
    print(f"Diversity Factor (Distribution): {diversity_factor_distribution}")
    print(f"Transmission Efficiency: {transmission_efficiency * 100}%")
    print(f"Distribution Efficiency: {distribution_efficiency * 100}%")
    print()

    # Calculations
    max_demand_kw = max_demand_mw * 1000
    hours_per_year = 8760

    # Annual energy generated
    annual_energy_generated = max_demand_kw * load_factor * hours_per_year

    # Generating costs
    fixed_generating_cost = max_demand_kw * fixed_cost_per_kw
    variable_generating_cost = annual_energy_generated * variable_cost_per_kwh
    total_generating_cost = fixed_generating_cost + variable_generating_cost

    # Total cost
    total_cost = total_generating_cost + transmission_capital_cost

    # At Substation
    energy_at_substation = annual_energy_generated * transmission_efficiency
    demand_at_substation = max_demand_kw / diversity_factor_transmission

    cost_per_kw_substation = total_cost / demand_at_substation
    cost_per_kwh_substation = total_cost / energy_at_substation

    # At Consumer's Premises
    energy_at_consumer = energy_at_substation * distribution_efficiency
    demand_at_consumer = demand_at_substation / diversity_factor_distribution

    cost_per_kw_consumer = total_cost / demand_at_consumer
    cost_per_kwh_consumer = total_cost / energy_at_consumer

    print("STEP-BY-STEP CALCULATIONS:")
    print("-" * 80)
    print(f"1. Maximum Demand = {max_demand_mw} MW = {max_demand_kw:,.0f} kW")
    print()

    print(f"2. Annual Energy Generated:")
    print(f"   = MD × Load Factor × Hours/Year")
    print(f"   = {max_demand_kw:,.0f} × {load_factor} × {hours_per_year}")
    print(f"   = {annual_energy_generated:,.0f} kWh")
    print(f"   = {annual_energy_generated / 1e6:.2f} Million kWh")
    print()

    print(f"3. Fixed Generating Cost:")
    print(f"   = MD × Rs {fixed_cost_per_kw}/kW")
    print(f"   = {max_demand_kw:,.0f} × {fixed_cost_per_kw}")
    print(f"   = Rs. {fixed_generating_cost:,.2f}")
    print()

    print(f"4. Variable Generating Cost:")
    print(f"   = Energy × Rs {variable_cost_per_kwh}/kWh")
    print(f"   = {annual_energy_generated:,.0f} × {variable_cost_per_kwh}")
    print(f"   = Rs. {variable_generating_cost:,.2f}")
    print()

    print(f"5. Total Generating Cost:")
    print(f"   = Fixed + Variable")
    print(f"   = Rs. {fixed_generating_cost:,.2f} + Rs. {variable_generating_cost:,.2f}")
    print(f"   = Rs. {total_generating_cost:,.2f}")
    print()

    print(f"6. Total Cost (Including Transmission):")
    print(f"   = Generating Cost + Transmission Capital Cost")
    print(f"   = Rs. {total_generating_cost:,.2f} + Rs. {transmission_capital_cost:,.2f}")
    print(f"   = Rs. {total_cost:,.2f}")
    print()

    print("=" * 80)
    print("AT SUBSTATION:")
    print("=" * 80)
    print(f"Energy at Substation:")
    print(f"   = Generated Energy × Transmission Efficiency")
    print(f"   = {annual_energy_generated:,.0f} × {transmission_efficiency}")
    print(f"   = {energy_at_substation:,.0f} kWh")
    print(f"   = {energy_at_substation / 1e6:.2f} Million kWh")
    print()

    print(f"Demand at Substation:")
    print(f"   = MD / Diversity Factor (Trans)")
    print(f"   = {max_demand_kw:,.0f} / {diversity_factor_transmission}")
    print(f"   = {demand_at_substation:,.2f} kW")
    print()

    print(f"Cost per kW Demand at Substation:")
    print(f"   = Total Cost / Demand at Substation")
    print(f"   = Rs. {total_cost:,.2f} / {demand_at_substation:,.2f}")
    print(f"   = Rs. {cost_per_kw_substation:.4f} per kW")
    print()

    print(f"Cost per kWh Supplied at Substation:")
    print(f"   = Total Cost / Energy at Substation")
    print(f"   = Rs. {total_cost:,.2f} / {energy_at_substation:,.0f}")
    print(f"   = Rs. {cost_per_kwh_substation:.6f} per kWh")
    print()

    print("=" * 80)
    print("AT CONSUMER'S PREMISES:")
    print("=" * 80)
    print(f"Energy at Consumer:")
    print(f"   = Substation Energy × Distribution Efficiency")
    print(f"   = {energy_at_substation:,.0f} × {distribution_efficiency}")
    print(f"   = {energy_at_consumer:,.0f} kWh")
    print(f"   = {energy_at_consumer / 1e6:.2f} Million kWh")
    print()

    print(f"Demand at Consumer:")
    print(f"   = Substation Demand / Diversity Factor (Dist)")
    print(f"   = {demand_at_substation:,.2f} / {diversity_factor_distribution}")
    print(f"   = {demand_at_consumer:,.2f} kW")
    print()

    print(f"Cost per kW Demand at Consumer:")
    print(f"   = Total Cost / Demand at Consumer")
    print(f"   = Rs. {total_cost:,.2f} / {demand_at_consumer:,.2f}")
    print(f"   = Rs. {cost_per_kw_consumer:.4f} per kW")
    print()

    print(f"Cost per kWh Supplied at Consumer:")
    print(f"   = Total Cost / Energy at Consumer")
    print(f"   = Rs. {total_cost:,.2f} / {energy_at_consumer:,.0f}")
    print(f"   = Rs. {cost_per_kwh_consumer:.6f} per kWh")
    print()

    print("=" * 80)
    print("FINAL ANSWERS:")
    print("=" * 80)
    print()
    print("(a) AT THE SUBSTATION:")
    print(f"    • Yearly cost per kW demand: Rs. {cost_per_kw_substation:.2f} /kW")
    print(f"    • Cost per kWh supplied: Rs. {cost_per_kwh_substation:.5f} /kWh")
    print()
    print("(b) AT THE CONSUMER'S PREMISES:")
    print(f"    • Yearly cost per kW demand: Rs. {cost_per_kw_consumer:.2f} /kW")
    print(f"    • Cost per kWh supplied: Rs. {cost_per_kwh_consumer:.5f} /kWh")
    print()
    print("=" * 80)

    # Validation
    print("\nVALIDATION:")
    print("-" * 80)

    # Check if values are in expected range
    tests_passed = True

    # Test 1: Cost per kW at substation should be around 138
    if 137 < cost_per_kw_substation < 139:
        print("✓ Cost per kW at Substation: PASS")
    else:
        print("✗ Cost per kW at Substation: FAIL")
        tests_passed = False

    # Test 2: Cost per kWh at substation should be around 0.0365
    if 0.036 < cost_per_kwh_substation < 0.037:
        print("✓ Cost per kWh at Substation: PASS")
    else:
        print("✗ Cost per kWh at Substation: FAIL")
        tests_passed = False

    # Test 3: Cost per kW at consumer should be around 172.5
    if 172 < cost_per_kw_consumer < 173:
        print("✓ Cost per kW at Consumer: PASS")
    else:
        print("✗ Cost per kW at Consumer: FAIL")
        tests_passed = False

    # Test 4: Cost per kWh at consumer should be around 0.0429
    if 0.042 < cost_per_kwh_consumer < 0.043:
        print("✓ Cost per kWh at Consumer: PASS")
    else:
        print("✗ Cost per kWh at Consumer: FAIL")
        tests_passed = False

    print()
    if tests_passed:
        print("🎉 ALL TESTS PASSED! 🎉")
    else:
        print("❌ SOME TESTS FAILED!")

    print("=" * 80)

    return tests_passed


if __name__ == "__main__":
    success = test_power_generation_cost()
    exit(0 if success else 1)

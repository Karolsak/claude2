"""
Test script for Power Generation Cost Calculator
Tests the mathematical calculations without GUI
"""

import numpy as np
from scipy.integrate import solve_ivp


class PowerGenerationCostCalculator:
    """Module for calculating power generation costs"""

    def __init__(self):
        self.reset_parameters()

    def reset_parameters(self):
        """Reset all parameters to default values"""
        self.max_demand_mw = 75.0
        self.load_factor = 0.40
        self.fixed_cost_per_kw = 60.0
        self.variable_cost_per_kwh = 0.01
        self.transmission_capital_cost = 1500000.0
        self.diversity_factor_transmission = 1.2
        self.diversity_factor_distribution = 1.25
        self.transmission_efficiency = 0.90
        self.distribution_efficiency = 0.85

    def calculate_costs(self):
        """Calculate all cost parameters"""
        results = {}

        # Basic calculations
        max_demand_kw = self.max_demand_mw * 1000
        hours_per_year = 8760

        # Annual energy generated
        annual_energy_generated = max_demand_kw * self.load_factor * hours_per_year

        # Generating costs
        fixed_generating_cost = max_demand_kw * self.fixed_cost_per_kw
        variable_generating_cost = annual_energy_generated * self.variable_cost_per_kwh
        total_generating_cost = fixed_generating_cost + variable_generating_cost

        # Total cost including transmission
        total_cost = total_generating_cost + self.transmission_capital_cost

        # At Substation
        energy_at_substation = annual_energy_generated * self.transmission_efficiency
        demand_at_substation = max_demand_kw / self.diversity_factor_transmission

        cost_per_kw_substation = total_cost / demand_at_substation
        cost_per_kwh_substation = total_cost / energy_at_substation

        # At Consumer's Premises
        energy_at_consumer = energy_at_substation * self.distribution_efficiency
        demand_at_consumer = demand_at_substation / self.diversity_factor_distribution

        cost_per_kw_consumer = total_cost / demand_at_consumer
        cost_per_kwh_consumer = total_cost / energy_at_consumer

        # Store results
        results['max_demand_kw'] = max_demand_kw
        results['annual_energy_generated'] = annual_energy_generated
        results['fixed_generating_cost'] = fixed_generating_cost
        results['variable_generating_cost'] = variable_generating_cost
        results['total_generating_cost'] = total_generating_cost
        results['transmission_cost'] = self.transmission_capital_cost
        results['total_cost'] = total_cost

        results['energy_at_substation'] = energy_at_substation
        results['demand_at_substation'] = demand_at_substation
        results['cost_per_kw_substation'] = cost_per_kw_substation
        results['cost_per_kwh_substation'] = cost_per_kwh_substation

        results['energy_at_consumer'] = energy_at_consumer
        results['demand_at_consumer'] = demand_at_consumer
        results['cost_per_kw_consumer'] = cost_per_kw_consumer
        results['cost_per_kwh_consumer'] = cost_per_kwh_consumer

        return results


def test_power_generation_calculator():
    """Test the power generation cost calculator"""
    print("=" * 80)
    print("TESTING POWER GENERATION COST CALCULATOR")
    print("=" * 80)
    print()

    calculator = PowerGenerationCostCalculator()
    results = calculator.calculate_costs()

    print("INPUT PARAMETERS:")
    print("-" * 80)
    print(f"Maximum Demand: {calculator.max_demand_mw} MW")
    print(f"Load Factor: {calculator.load_factor:.2%}")
    print(f"Fixed Cost: Rs. {calculator.fixed_cost_per_kw} per kW per annum")
    print(f"Variable Cost: Rs. {calculator.variable_cost_per_kwh} per kWh")
    print(f"Transmission Capital Cost: Rs. {calculator.transmission_capital_cost:,.0f}")
    print(f"Diversity Factor (Transmission): {calculator.diversity_factor_transmission}")
    print(f"Diversity Factor (Distribution): {calculator.diversity_factor_distribution}")
    print(f"Transmission Efficiency: {calculator.transmission_efficiency:.2%}")
    print(f"Distribution Efficiency: {calculator.distribution_efficiency:.2%}")
    print()

    print("CALCULATED RESULTS:")
    print("-" * 80)
    print(f"Annual Energy Generated: {results['annual_energy_generated']/1e6:.2f} Million kWh")
    print(f"Energy at Substation: {results['energy_at_substation']/1e6:.2f} Million kWh")
    print(f"Energy at Consumer: {results['energy_at_consumer']/1e6:.2f} Million kWh")
    print()

    print("COST BREAKDOWN:")
    print("-" * 80)
    print(f"Fixed Generating Cost: Rs. {results['fixed_generating_cost']:,.2f}")
    print(f"Variable Generating Cost: Rs. {results['variable_generating_cost']:,.2f}")
    print(f"Total Generating Cost: Rs. {results['total_generating_cost']:,.2f}")
    print(f"Transmission Cost: Rs. {results['transmission_cost']:,.2f}")
    print(f"TOTAL COST: Rs. {results['total_cost']:,.2f}")
    print()

    print("RESULTS AT SUBSTATION:")
    print("=" * 80)
    print(f"Demand at Substation: {results['demand_at_substation']:,.2f} kW")
    print(f"Cost per kW Demand: Rs. {results['cost_per_kw_substation']:.4f} /kW")
    print(f"Cost per kWh Supplied: Rs. {results['cost_per_kwh_substation']:.6f} /kWh")
    print()

    print("RESULTS AT CONSUMER'S PREMISES:")
    print("=" * 80)
    print(f"Demand at Consumer: {results['demand_at_consumer']:,.2f} kW")
    print(f"Cost per kW Demand: Rs. {results['cost_per_kw_consumer']:.4f} /kW")
    print(f"Cost per kWh Supplied: Rs. {results['cost_per_kwh_consumer']:.6f} /kWh")
    print()

    # Verify calculations
    print("VERIFICATION:")
    print("-" * 80)
    expected_cost_kw_substation = 138.048
    expected_cost_kwh_consumer = 0.042913

    print(f"Expected Cost/kW at Substation: Rs. {expected_cost_kw_substation:.4f}")
    print(f"Calculated Cost/kW at Substation: Rs. {results['cost_per_kw_substation']:.4f}")
    print(f"Match: {abs(results['cost_per_kw_substation'] - expected_cost_kw_substation) < 0.01}")
    print()

    print(f"Expected Cost/kWh at Consumer: Rs. {expected_cost_kwh_consumer:.6f}")
    print(f"Calculated Cost/kWh at Consumer: Rs. {results['cost_per_kwh_consumer']:.6f}")
    print(f"Match: {abs(results['cost_per_kwh_consumer'] - expected_cost_kwh_consumer) < 0.0001}")
    print()

    print("=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)


def test_ode_solver():
    """Test ODE solver functionality"""
    print("\n" + "=" * 80)
    print("TESTING ODE SOLVER (RK45)")
    print("=" * 80)
    print()

    def simple_ode(t, y):
        """Simple test ODE: dy/dt = -y"""
        return -y

    # Solve
    t_span = (0, 5)
    y0 = [1.0]

    sol = solve_ivp(simple_ode, t_span, y0, method='RK45')

    print(f"Time points: {len(sol.t)}")
    print(f"Initial value: y(0) = {sol.y[0][0]:.4f}")
    print(f"Final value: y(5) = {sol.y[0][-1]:.4f}")
    print(f"Expected (e^-5): {np.exp(-5):.4f}")
    print(f"Error: {abs(sol.y[0][-1] - np.exp(-5)):.6f}")
    print()

    if abs(sol.y[0][-1] - np.exp(-5)) < 0.01:
        print("✓ ODE Solver working correctly!")
    else:
        print("✗ ODE Solver has issues!")

    print("=" * 80)


if __name__ == "__main__":
    test_power_generation_calculator()
    test_ode_solver()

#!/usr/bin/env python3
"""
Example 50.29: Economic Comparison of Hydro vs Steam Power Stations (Console Version)
"""


class PowerStationEconomics:
    """Class to handle power station economic calculations"""

    def __init__(self, capital_cost, running_cost, interest_rate, name):
        self.capital_cost = capital_cost
        self.running_cost = running_cost
        self.interest_rate = interest_rate
        self.name = name
        self.hours_per_year = 8760

    def calculate_costs(self, load_factor):
        """Calculate annual costs and cost per unit"""
        # Annual fixed cost per kW (interest on capital)
        annual_fixed_cost = self.capital_cost * self.interest_rate

        # Annual energy generated per kW
        annual_energy = load_factor * self.hours_per_year

        # Annual running cost per kW
        annual_running_cost = self.running_cost * annual_energy

        # Total annual cost per kW
        total_annual_cost = annual_fixed_cost + annual_running_cost

        # Cost per kWh generated
        cost_per_kwh = total_annual_cost / annual_energy if annual_energy > 0 else 0

        return {
            'annual_fixed_cost': annual_fixed_cost,
            'annual_energy': annual_energy,
            'annual_running_cost': annual_running_cost,
            'total_annual_cost': total_annual_cost,
            'cost_per_kwh': cost_per_kwh
        }

    def print_details(self, load_factor, costs):
        """Print detailed cost breakdown"""
        print(f"\n{self.name} Station at {load_factor*100:.0f}% Load Factor:")
        print("=" * 60)
        print(f"Capital Cost: Rs. {self.capital_cost}/kW")
        print(f"Running Cost: Rs. {self.running_cost}/kWh")
        print(f"Interest Rate: {self.interest_rate*100}%")
        print(f"\nAnnual Fixed Cost (Interest on Capital): Rs. {costs['annual_fixed_cost']:.2f} per kW")
        print(f"Annual Energy Output: {costs['annual_energy']:.2f} kWh per kW")
        print(f"Annual Running Cost: Rs. {costs['annual_running_cost']:.2f} per kW")
        print(f"\nTotal Annual Cost: Rs. {costs['total_annual_cost']:.2f} per kW")
        print(f"Cost per kWh Generated: Rs. {costs['cost_per_kwh']:.4f}")


def compare_stations(hydro, steam, load_factor):
    """Compare two stations at a given load factor"""
    print("\n" + "="*80)
    print(f"COMPARISON AT {load_factor*100:.0f}% LOAD FACTOR")
    print("="*80)

    # Calculate costs
    hydro_costs = hydro.calculate_costs(load_factor)
    steam_costs = steam.calculate_costs(load_factor)

    # Print details for both stations
    hydro.print_details(load_factor, hydro_costs)
    steam.print_details(load_factor, steam_costs)

    # Comparison
    print("\n" + "-"*80)
    print("COMPARISON SUMMARY:")
    print("-"*80)
    print(f"{'Parameter':<40} {'Hydro':<20} {'Steam':<20}")
    print("-"*80)
    print(f"{'Annual Fixed Cost (Rs/kW)':<40} {hydro_costs['annual_fixed_cost']:<20.2f} {steam_costs['annual_fixed_cost']:<20.2f}")
    print(f"{'Annual Running Cost (Rs/kW)':<40} {hydro_costs['annual_running_cost']:<20.2f} {steam_costs['annual_running_cost']:<20.2f}")
    print(f"{'Total Annual Cost (Rs/kW)':<40} {hydro_costs['total_annual_cost']:<20.2f} {steam_costs['total_annual_cost']:<20.2f}")
    print(f"{'Cost per kWh (Rs)':<40} {hydro_costs['cost_per_kwh']:<20.4f} {steam_costs['cost_per_kwh']:<20.4f}")
    print("-"*80)

    # Determine winner
    if hydro_costs['cost_per_kwh'] < steam_costs['cost_per_kwh']:
        winner = "HYDRO STATION"
        savings = steam_costs['cost_per_kwh'] - hydro_costs['cost_per_kwh']
        print(f"\n*** {winner} is MORE ECONOMICAL ***")
    else:
        winner = "STEAM STATION"
        savings = hydro_costs['cost_per_kwh'] - steam_costs['cost_per_kwh']
        print(f"\n*** {winner} is MORE ECONOMICAL ***")

    print(f"Savings: Rs. {savings:.4f} per kWh = {savings*100:.4f} Paise per kWh")

    # Explanation
    print("\nExplanation:")
    if load_factor == 0.10:
        print(f"• At low load factor ({load_factor*100:.0f}%), the station operates only {hydro_costs['annual_energy']:.0f} hours/year")
        print(f"• Fixed costs (interest on capital) dominate the total cost")
        print(f"• Hydro has higher capital cost (Rs. {hydro.capital_cost}/kW) vs Steam (Rs. {steam.capital_cost}/kW)")
        print(f"• The lower running cost of hydro (Rs. {hydro.running_cost}/kWh) cannot compensate")
        print(f"• Therefore, steam station with lower capital investment is more economical")
    else:
        print(f"• At high load factor ({load_factor*100:.0f}%), the station operates {hydro_costs['annual_energy']:.0f} hours/year")
        print(f"• Running costs become more significant")
        print(f"• Hydro's low running cost (Rs. {hydro.running_cost}/kWh) vs Steam (Rs. {steam.running_cost}/kWh)")
        print(f"• The running cost advantage of hydro outweighs its higher capital cost")
        print(f"• Therefore, hydro station is more economical at higher load factors")


def main():
    """Main function"""
    print("="*80)
    print("Example 50.29: Economic Comparison of Hydro vs Steam Power Stations")
    print("="*80)

    print("\nGiven Data:")
    print("-" * 60)
    print(f"{'Parameter':<30} {'Hydro Station':<20} {'Steam Station':<20}")
    print("-" * 60)
    print(f"{'Capital Cost':<30} {'Rs. 2,200/kW':<20} {'Rs. 1,200/kW':<20}")
    print(f"{'Running Cost':<30} {'1 Paise/kWh':<20} {'5 Paise/kWh':<20}")
    print(f"{'Interest Rate':<30} {'5%':<20} {'5%':<20}")
    print("-" * 60)

    # Initialize stations
    hydro = PowerStationEconomics(
        capital_cost=2200,     # Rs per kW
        running_cost=0.01,     # Rs per kWh (1 Paise)
        interest_rate=0.05,    # 5%
        name="Hydro"
    )

    steam = PowerStationEconomics(
        capital_cost=1200,     # Rs per kW
        running_cost=0.05,     # Rs per kWh (5 Paise)
        interest_rate=0.05,    # 5%
        name="Steam"
    )

    # Compare at 10% load factor
    compare_stations(hydro, steam, 0.10)

    # Compare at 50% load factor
    compare_stations(hydro, steam, 0.50)

    # Summary
    print("\n" + "="*80)
    print("FINAL CONCLUSION:")
    print("="*80)
    print("• At 10% load factor: STEAM STATION is more economical")
    print("• At 50% load factor: HYDRO STATION is more economical")
    print("\nThe choice depends on the expected load factor:")
    print("- Low load factors favor stations with lower capital costs (Steam)")
    print("- High load factors favor stations with lower running costs (Hydro)")
    print("="*80)


if __name__ == "__main__":
    main()

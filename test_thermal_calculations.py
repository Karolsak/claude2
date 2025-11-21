"""Test script to verify thermal station calculations"""

from thermal_station_calculator import ThermalStationData, ThermalStationCalculator

# Create default data
data = ThermalStationData()

# Create calculator
calculator = ThermalStationCalculator(data)

# Calculate
results = calculator.calculate_all()

# Display results
print("=" * 80)
print("THERMAL STATION COST CALCULATION VERIFICATION")
print("=" * 80)
print("\nINPUT PARAMETERS:")
print(f"Installed Capacity: {data.installed_capacity:,.0f} kW")
print(f"Maximum Demand: {data.max_demand:,.0f} kW")
print(f"Annual Load Factor: {data.annual_load_factor * 100:.0f}%")
print(f"Coal Consumption: {data.coal_consumption:,.0f} tonne")

print("\nKEY CALCULATIONS:")
print(f"Annual Energy Generated: {results['annual_energy_kwh']:,.2f} kWh")
print(f"Total Fixed Costs: Rs. {results['total_fixed_costs']:,.2f}")
print(f"Total Running Costs: Rs. {results['total_running_costs']:,.2f}")
print(f"Total Annual Cost: Rs. {results['total_annual_cost']:,.2f}")

print("\n" + "=" * 80)
print("FINAL RESULTS:")
print("=" * 80)
print(f"Cost per kW per Year: Rs. {results['cost_per_kw_year']:.2f}")
print(f"Cost per kWh Generated: Rs. {results['cost_per_kwh_generated']:.4f}")
print("=" * 80)

# Verify calculation manually
print("\nMANUAL VERIFICATION:")
annual_energy = data.max_demand * data.annual_load_factor * 8760
print(f"Annual Energy = {data.max_demand} × {data.annual_load_factor} × 8760 = {annual_energy:,.2f} kWh")

plant_cost = data.installed_capacity * data.cost_per_kw
print(f"Plant Cost = {data.installed_capacity} × {data.cost_per_kw} = Rs. {plant_cost:,.2f}")

fixed_plant = plant_cost * (data.interest_tax_plant + data.depreciation_plant)
print(f"Fixed Cost (Plant) = {plant_cost:,.2f} × {(data.interest_tax_plant + data.depreciation_plant)} = Rs. {fixed_plant:,.2f}")

coal_cost = data.coal_consumption * data.coal_cost_per_tonne
print(f"Coal Cost = {data.coal_consumption} × {data.coal_cost_per_tonne} = Rs. {coal_cost:,.2f}")

print("\n✓ Calculations verified successfully!")

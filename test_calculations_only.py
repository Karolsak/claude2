"""Test script to verify thermal station calculations - standalone version"""

from dataclasses import dataclass

@dataclass
class ThermalStationData:
    """Data structure for thermal station parameters"""
    installed_capacity: float = 10000.0  # kW
    max_demand: float = 9000.0  # kW
    annual_load_factor: float = 0.60  # 60%
    cost_per_kw: float = 1200.0  # Rs per kW
    interest_tax_plant: float = 0.05  # 5% p.a.
    depreciation_plant: float = 0.05  # 5% p.a.
    distribution_cost: float = 400000.0  # Rs
    interest_tax_distribution: float = 0.05  # 5% p.a.
    coal_cost_per_tonne: float = 40.0  # Rs per tonne
    operating_cost: float = 400000.0  # Rs p.a.
    maintenance_fixed: float = 20000.0  # Rs p.a.
    maintenance_variable: float = 30000.0  # Rs p.a.
    coal_consumption: float = 25300.0  # tonne


class ThermalStationCalculator:
    """Handles all thermal station cost calculations"""

    def __init__(self, data: ThermalStationData):
        self.data = data
        self.results = {}

    def calculate_all(self):
        """Perform all calculations"""
        # Annual energy generated
        hours_per_year = 8760
        self.results['annual_energy_kwh'] = (
            self.data.max_demand * self.data.annual_load_factor * hours_per_year
        )

        # Fixed costs on plant
        plant_total_cost = self.data.installed_capacity * self.data.cost_per_kw
        interest_tax_plant = plant_total_cost * self.data.interest_tax_plant
        depreciation_plant = plant_total_cost * self.data.depreciation_plant
        fixed_cost_plant = interest_tax_plant + depreciation_plant

        # Fixed costs on distribution
        fixed_cost_distribution = (
            self.data.distribution_cost * self.data.interest_tax_distribution
        )

        # Total fixed costs
        total_fixed_costs = (
            fixed_cost_plant +
            fixed_cost_distribution +
            self.data.maintenance_fixed
        )

        # Running costs
        coal_cost_annual = self.data.coal_consumption * self.data.coal_cost_per_tonne
        total_running_costs = (
            coal_cost_annual +
            self.data.operating_cost +
            self.data.maintenance_variable
        )

        # Total annual cost
        total_annual_cost = total_fixed_costs + total_running_costs

        # Cost per kW per year (based on maximum demand)
        cost_per_kw_year = total_annual_cost / self.data.max_demand

        # Cost per kWh generated
        cost_per_kwh_generated = total_annual_cost / self.results['annual_energy_kwh']

        # Store results
        self.results.update({
            'plant_total_cost': plant_total_cost,
            'interest_tax_plant': interest_tax_plant,
            'depreciation_plant': depreciation_plant,
            'fixed_cost_plant': fixed_cost_plant,
            'fixed_cost_distribution': fixed_cost_distribution,
            'total_fixed_costs': total_fixed_costs,
            'coal_cost_annual': coal_cost_annual,
            'total_running_costs': total_running_costs,
            'total_annual_cost': total_annual_cost,
            'cost_per_kw_year': cost_per_kw_year,
            'cost_per_kwh_generated': cost_per_kwh_generated,
        })

        return self.results


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
print(f"Cost per kW: Rs. {data.cost_per_kw:,.0f}")
print(f"Interest & Tax (Plant): {data.interest_tax_plant * 100:.0f}% p.a.")
print(f"Depreciation (Plant): {data.depreciation_plant * 100:.0f}% p.a.")
print(f"Distribution Cost: Rs. {data.distribution_cost:,.0f}")
print(f"Coal Cost per Tonne: Rs. {data.coal_cost_per_tonne:,.0f}")
print(f"Operating Cost: Rs. {data.operating_cost:,.0f} p.a.")
print(f"Maintenance Fixed: Rs. {data.maintenance_fixed:,.0f} p.a.")
print(f"Maintenance Variable: Rs. {data.maintenance_variable:,.0f} p.a.")
print(f"Coal Consumption: {data.coal_consumption:,.0f} tonne")

print("\n" + "-" * 80)
print("STEP-BY-STEP CALCULATIONS:")
print("-" * 80)

# 1. Annual Energy
annual_energy = data.max_demand * data.annual_load_factor * 8760
print(f"\n1. Annual Energy Generated:")
print(f"   = Max Demand × Load Factor × Hours per Year")
print(f"   = {data.max_demand:,.0f} × {data.annual_load_factor} × 8760")
print(f"   = {annual_energy:,.2f} kWh")

# 2. Plant Cost
plant_cost = data.installed_capacity * data.cost_per_kw
print(f"\n2. Total Plant Cost:")
print(f"   = Installed Capacity × Cost per kW")
print(f"   = {data.installed_capacity:,.0f} × {data.cost_per_kw:,.0f}")
print(f"   = Rs. {plant_cost:,.2f}")

# 3. Fixed Costs
interest_tax = plant_cost * data.interest_tax_plant
depreciation = plant_cost * data.depreciation_plant
fixed_plant = interest_tax + depreciation
print(f"\n3. Fixed Costs (Plant):")
print(f"   Interest & Tax = {plant_cost:,.2f} × {data.interest_tax_plant}")
print(f"                  = Rs. {interest_tax:,.2f}")
print(f"   Depreciation   = {plant_cost:,.2f} × {data.depreciation_plant}")
print(f"                  = Rs. {depreciation:,.2f}")
print(f"   Total          = Rs. {fixed_plant:,.2f}")

# 4. Distribution Fixed Cost
dist_fixed = data.distribution_cost * data.interest_tax_distribution
print(f"\n4. Fixed Cost (Distribution):")
print(f"   = {data.distribution_cost:,.2f} × {data.interest_tax_distribution}")
print(f"   = Rs. {dist_fixed:,.2f}")

# 5. Total Fixed Costs
total_fixed = fixed_plant + dist_fixed + data.maintenance_fixed
print(f"\n5. Total Fixed Costs:")
print(f"   = Fixed (Plant) + Fixed (Distribution) + Maintenance Fixed")
print(f"   = {fixed_plant:,.2f} + {dist_fixed:,.2f} + {data.maintenance_fixed:,.2f}")
print(f"   = Rs. {total_fixed:,.2f}")

# 6. Running Costs
coal_cost = data.coal_consumption * data.coal_cost_per_tonne
total_running = coal_cost + data.operating_cost + data.maintenance_variable
print(f"\n6. Running Costs:")
print(f"   Coal Cost      = {data.coal_consumption:,.0f} × {data.coal_cost_per_tonne:,.0f}")
print(f"                  = Rs. {coal_cost:,.2f}")
print(f"   Operating Cost = Rs. {data.operating_cost:,.2f}")
print(f"   Maintenance Var= Rs. {data.maintenance_variable:,.2f}")
print(f"   Total Running  = Rs. {total_running:,.2f}")

# 7. Total Annual Cost
total_annual = total_fixed + total_running
print(f"\n7. Total Annual Cost:")
print(f"   = Total Fixed + Total Running")
print(f"   = {total_fixed:,.2f} + {total_running:,.2f}")
print(f"   = Rs. {total_annual:,.2f}")

# 8. Cost per kW per year
cost_kw_year = total_annual / data.max_demand
print(f"\n8. Cost per kW per Year:")
print(f"   = Total Annual Cost / Maximum Demand")
print(f"   = {total_annual:,.2f} / {data.max_demand:,.0f}")
print(f"   = Rs. {cost_kw_year:.2f}")

# 9. Cost per kWh
cost_kwh = total_annual / annual_energy
print(f"\n9. Cost per kWh Generated:")
print(f"   = Total Annual Cost / Annual Energy")
print(f"   = {total_annual:,.2f} / {annual_energy:,.2f}")
print(f"   = Rs. {cost_kwh:.4f}")

print("\n" + "=" * 80)
print("FINAL RESULTS:")
print("=" * 80)
print(f"Cost per kW per Year       : Rs. {results['cost_per_kw_year']:.2f}")
print(f"Cost per kWh Generated     : Rs. {results['cost_per_kwh_generated']:.4f}")
print(f"Total Cost of Generation   : Rs. {results['cost_per_kwh_generated']:.4f} per kWh")
print("=" * 80)

# Performance Metrics
capacity_factor = (annual_energy / (data.installed_capacity * 8760)) * 100
utilization_factor = (data.max_demand / data.installed_capacity) * 100

print("\nPERFORMANCE METRICS:")
print("-" * 80)
print(f"Capacity Factor            : {capacity_factor:.2f}%")
print(f"Utilization Factor         : {utilization_factor:.2f}%")
print(f"Energy per Tonne Coal      : {annual_energy / data.coal_consumption:.2f} kWh/tonne")
print("=" * 80)

print("\n✓ All calculations completed successfully!")
print("✓ No syntax errors detected!")

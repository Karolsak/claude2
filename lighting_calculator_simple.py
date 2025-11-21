#!/usr/bin/env python3
"""
Factory Lighting Calculator - Simple Pure Python Version
No external dependencies required
"""

import math


def calculate_lamps_with_wattage(area_length, area_width, illumination,
                                 depreciation_factor, coefficient_utilization,
                                 lamp_efficiency, lamp_wattage):
    """Calculate number of lamps with known wattage"""
    area = area_length * area_width
    total_lumens_required = illumination * area

    # Lumens per lamp = Wattage × Efficiency (lm/W)
    lumens_per_lamp = lamp_wattage * lamp_efficiency

    # Effective lumens considering utilization and depreciation
    effective_lumens_per_lamp = lumens_per_lamp * coefficient_utilization * depreciation_factor

    number_of_lamps = total_lumens_required / effective_lumens_per_lamp

    # Calculate total power consumption
    total_power = math.ceil(number_of_lamps) * lamp_wattage / 1000  # kW

    return {
        'area': area,
        'total_lumens_required': total_lumens_required,
        'lumens_per_lamp': lumens_per_lamp,
        'effective_lumens_per_lamp': effective_lumens_per_lamp,
        'number_of_lamps': math.ceil(number_of_lamps),
        'actual_number': number_of_lamps,
        'total_power_kw': total_power
    }


def suggest_lamp_disposition(area_length, area_width, num_lamps):
    """Suggest optimal lamp disposition"""
    ratio = area_length / area_width

    best_rows = 1
    best_cols = num_lamps
    min_diff = float('inf')

    for rows in range(1, num_lamps + 1):
        if num_lamps % rows == 0:
            cols = num_lamps // rows
            actual_ratio = cols / rows
            diff = abs(actual_ratio - ratio)
            if diff < min_diff:
                min_diff = diff
                best_rows = rows
                best_cols = cols

    spacing_length = area_length / best_cols
    spacing_width = area_width / best_rows

    return {
        'rows': best_rows,
        'columns': best_cols,
        'spacing_length': spacing_length,
        'spacing_width': spacing_width,
        'pattern': f"{best_rows} × {best_cols}"
    }


def print_definitions():
    """Print lighting definitions"""
    print("\n" + "="*80)
    print("LIGHTING ENGINEERING DEFINITIONS")
    print("="*80)

    print("\n1. LUX (lx)")
    print("-" * 80)
    print("Definition: Unit of illuminance, measuring luminous flux per unit area.")
    print("Formula: 1 lux = 1 lumen/m²")
    print("\nPhysical Meaning:")
    print("  Lux represents how bright a surface appears when illuminated.")
    print("  It is the amount of light falling on a surface per unit area.")
    print("\nExamples:")
    print("  • Direct sunlight: ~100,000 lux")
    print("  • Office lighting: 320-500 lux")
    print("  • Living room: 50-150 lux")
    print("  • Moonlight: ~0.25 lux")

    print("\n2. LUMINOUS FLUX (Φ)")
    print("-" * 80)
    print("Definition: Total quantity of visible light emitted by a source per unit time.")
    print("Unit: Lumen (lm)")
    print("\nPhysical Meaning:")
    print("  Luminous flux is the total 'amount' of light energy emitted by a source,")
    print("  weighted by the sensitivity of the human eye.")
    print("\nRelationship:")
    print("  Luminous Flux = Luminous Efficacy × Power")
    print("  • LED: 80-150 lm/W")
    print("  • Incandescent: 10-17 lm/W")
    print("  • Fluorescent: 50-100 lm/W")
    print("\nExamples:")
    print("  • 100W incandescent bulb: ~1,600 lumens")
    print("  • 100W LED equivalent: ~1,600 lumens (15-20W actual)")
    print("  • Candle: ~12 lumens")

    print("\n3. CANDLE POWER (Luminous Intensity)")
    print("-" * 80)
    print("Definition: Luminous flux emitted per unit solid angle in a direction.")
    print("Unit: Candela (cd)")
    print("Formula: I = dΦ/dΩ")
    print("\nPhysical Meaning:")
    print("  Candle power measures how 'focused' or 'intense' the light is in a")
    print("  specific direction, independent of distance.")
    print("\nRelationship to Illuminance:")
    print("  E = I/r² (Inverse square law)")
    print("  where E is illuminance (lux), I is intensity (candela), r is distance (m)")
    print("\nExamples:")
    print("  • Standard candle: ~1 candela")
    print("  • Car headlight: 25,000-150,000 cd")
    print("  • LED flashlight: 1,000-10,000 cd")
    print("\nNote: 'Candle power' is historical; modern usage prefers 'luminous intensity.'")


def solve_problem1():
    """Solve Problem 1: Factory Hall 30m × 12m"""
    print("\n" + "="*80)
    print("PROBLEM 1: Factory Hall 30m × 12m - 100 lux")
    print("="*80)

    # Problem parameters
    length = 30  # m
    width = 12  # m
    illumination = 100  # lux
    depreciation_factor = 0.8
    coefficient_utilization = 0.4
    lamp_efficiency = 14  # lm/W
    lamp_wattage = 100  # W (assumed for calculation)

    print("\nGiven:")
    print(f"  • Factory hall dimensions: {length}m × {width}m")
    print(f"  • Required illumination: {illumination} lux")
    print(f"  • Depreciation factor: {depreciation_factor}")
    print(f"  • Coefficient of utilization: {coefficient_utilization}")
    print(f"  • Lamp efficiency: {lamp_efficiency} lm/W")
    print(f"  • Assumed lamp wattage: {lamp_wattage} W")

    result = calculate_lamps_with_wattage(
        length, width, illumination, depreciation_factor,
        coefficient_utilization, lamp_efficiency, lamp_wattage
    )

    disposition = suggest_lamp_disposition(length, width, result['number_of_lamps'])

    print(f"\nStep-by-Step Calculation:")
    print(f"  1. Area = {length}m × {width}m = {result['area']:.2f} m²")
    print(f"  2. Total lumens required = Illumination × Area")
    print(f"                           = {illumination} lux × {result['area']:.2f} m²")
    print(f"                           = {result['total_lumens_required']:.2f} lumens")
    print(f"  3. Lumens per lamp = Wattage × Efficiency")
    print(f"                     = {lamp_wattage} W × {lamp_efficiency} lm/W")
    print(f"                     = {result['lumens_per_lamp']:.2f} lumens")
    print(f"  4. Effective lumens per lamp = Lumens × Cu × Df")
    print(f"                               = {result['lumens_per_lamp']:.2f} × {coefficient_utilization} × {depreciation_factor}")
    print(f"                               = {result['effective_lumens_per_lamp']:.2f} lumens")
    print(f"  5. Number of lamps = Total lumens / Effective lumens per lamp")
    print(f"                     = {result['total_lumens_required']:.2f} / {result['effective_lumens_per_lamp']:.2f}")
    print(f"                     = {result['actual_number']:.2f}")

    print(f"\n{'='*80}")
    print(f"✓ ANSWER:")
    print(f"  • Number of lamps required: {result['number_of_lamps']} lamps")
    print(f"  • Total power consumption: {result['total_power_kw']:.2f} kW")
    print(f"{'='*80}")

    print(f"\n✓ LAMP DISPOSITION:")
    print(f"  • Recommended pattern: {disposition['pattern']} (rows × columns)")
    print(f"  • {disposition['rows']} rows across the width")
    print(f"  • {disposition['columns']} columns along the length")
    print(f"  • Spacing between lamps (length): {disposition['spacing_length']:.2f} m")
    print(f"  • Spacing between lamps (width): {disposition['spacing_width']:.2f} m")

    # Verification
    actual_lux = (result['number_of_lamps'] * result['effective_lumens_per_lamp']) / result['area']
    print(f"\nVerification:")
    print(f"  • Actual illumination: {actual_lux:.2f} lux")
    print(f"  • Design margin: +{actual_lux - illumination:.2f} lux")


def solve_problem2():
    """Solve Problem 2: Workshop 100m × 50m"""
    print("\n\n" + "="*80)
    print("PROBLEM 2: Workshop 100m × 50m - 50 lux")
    print("="*80)

    # Problem parameters
    length = 100  # m
    width = 50  # m
    illumination = 50  # lux
    depreciation_factor = 0.7
    coefficient_utilization = 0.9
    lamp_efficiency = 80  # lm/W
    lamp_wattage = 100  # W

    print("\nGiven:")
    print(f"  • Workshop dimensions: {length}m × {width}m")
    print(f"  • Required illumination intensity: {illumination} lux")
    print(f"  • Coefficient of utilization: {coefficient_utilization}")
    print(f"  • Depreciation factor: {depreciation_factor}")
    print(f"  • Efficiency of lamps: {lamp_efficiency} lm/W")
    print(f"  • Lamp wattage: {lamp_wattage} W")

    result = calculate_lamps_with_wattage(
        length, width, illumination, depreciation_factor,
        coefficient_utilization, lamp_efficiency, lamp_wattage
    )

    disposition = suggest_lamp_disposition(length, width, result['number_of_lamps'])

    print(f"\nStep-by-Step Calculation:")
    print(f"  1. Area = {length}m × {width}m = {result['area']:.2f} m²")
    print(f"  2. Total lumens required = Illumination × Area")
    print(f"                           = {illumination} lux × {result['area']:.2f} m²")
    print(f"                           = {result['total_lumens_required']:.2f} lumens")
    print(f"  3. Lumens per lamp = Wattage × Efficiency")
    print(f"                     = {lamp_wattage} W × {lamp_efficiency} lm/W")
    print(f"                     = {result['lumens_per_lamp']:.2f} lumens")
    print(f"  4. Effective lumens per lamp = Lumens × Cu × Df")
    print(f"                               = {result['lumens_per_lamp']:.2f} × {coefficient_utilization} × {depreciation_factor}")
    print(f"                               = {result['effective_lumens_per_lamp']:.2f} lumens")
    print(f"  5. Number of lamps = Total lumens / Effective lumens per lamp")
    print(f"                     = {result['total_lumens_required']:.2f} / {result['effective_lumens_per_lamp']:.2f}")
    print(f"                     = {result['actual_number']:.2f}")

    print(f"\n{'='*80}")
    print(f"✓ ANSWER:")
    print(f"  • Number of lamps required: {result['number_of_lamps']} lamps")
    print(f"  • Total power consumption: {result['total_power_kw']:.2f} kW")
    print(f"  • Power density: {(result['total_power_kw'] * 1000 / result['area']):.2f} W/m²")
    print(f"{'='*80}")

    print(f"\n✓ SUITABLE LIGHTING SCHEME DESIGN:")
    print(f"  • Recommended pattern: {disposition['pattern']} (rows × columns)")
    print(f"  • {disposition['rows']} rows across the width")
    print(f"  • {disposition['columns']} columns along the length")
    print(f"  • Spacing between lamps (length): {disposition['spacing_length']:.2f} m")
    print(f"  • Spacing between lamps (width): {disposition['spacing_width']:.2f} m")
    print(f"  • Uniform distribution recommended")
    print(f"  • Consider task lighting for specific work areas")

    # Verification
    actual_lux = (result['number_of_lamps'] * result['effective_lumens_per_lamp']) / result['area']
    print(f"\nVerification:")
    print(f"  • Actual illumination: {actual_lux:.2f} lux")
    print(f"  • Design margin: +{actual_lux - illumination:.2f} lux")
    print(f"  • Efficiency rating: Excellent (Cu={coefficient_utilization}, Df={depreciation_factor})")


def explain_formulas():
    """Explain the formulas used"""
    print("\n\n" + "="*80)
    print("LIGHTING CALCULATION FORMULAS")
    print("="*80)

    print("\n1. Number of Lamps Required:")
    print("   N = (E × A) / (Φ × Cu × Df)")
    print("\n   where:")
    print("   N  = Number of lamps")
    print("   E  = Required illumination (lux)")
    print("   A  = Area (m²)")
    print("   Φ  = Luminous flux per lamp (lumens)")
    print("   Cu = Coefficient of utilization")
    print("   Df = Depreciation factor (maintenance factor)")

    print("\n2. Luminous Flux per Lamp:")
    print("   Φ = P × η")
    print("\n   where:")
    print("   P = Lamp power (Watts)")
    print("   η = Lamp efficiency (lm/W)")

    print("\n3. Total Power Consumption:")
    print("   P_total = N × P_lamp")


def main():
    """Main function"""
    print("\n" + "="*80)
    print(" FACTORY LIGHTING CALCULATOR")
    print(" Advanced Electrical Engineering Application")
    print(" Pure Python Implementation")
    print("="*80)

    # Print definitions
    print_definitions()

    # Solve problems
    solve_problem1()
    solve_problem2()

    # Explain formulas
    explain_formulas()

    print("\n\n" + "="*80)
    print("✓ ALL CALCULATIONS COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nFor the full GUI version with multi-physics simulation:")
    print("  python3 factory_lighting_calculator.py")
    print("\nGUI Features:")
    print("  • Interactive Tkinter interface")
    print("  • Real-time sliders for parameter adjustment")
    print("  • Multi-physics RLC circuit simulation")
    print("  • ODE solvers (RK45, Euler methods)")
    print("  • Dynamic visualization with matplotlib")
    print("  • Start/Stop/Reset controls")
    print("  • Auto-scaling window")
    print("\nRequires: tkinter, numpy, scipy, matplotlib")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

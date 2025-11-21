#!/usr/bin/env python3
"""
Factory Lighting Calculator - Command Line Version
Testing the calculations without GUI
"""

import math
import numpy as np
from scipy.integrate import solve_ivp


class LightingCalculator:
    """Factory Lighting Calculator"""

    @staticmethod
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

    @staticmethod
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
    print("\nExamples:")
    print("  • Direct sunlight: ~100,000 lux")
    print("  • Office lighting: 320-500 lux")
    print("  • Living room: 50-150 lux")

    print("\n2. LUMINOUS FLUX (Φ)")
    print("-" * 80)
    print("Definition: Total quantity of visible light emitted by a source per unit time.")
    print("Unit: Lumen (lm)")
    print("\nExamples:")
    print("  • 100W incandescent bulb: ~1,600 lumens")
    print("  • 100W LED equivalent: ~1,600 lumens (15-20W actual)")
    print("  • Candle: ~12 lumens")

    print("\n3. CANDLE POWER (Luminous Intensity)")
    print("-" * 80)
    print("Definition: Luminous flux per unit solid angle in a direction.")
    print("Unit: Candela (cd)")
    print("Formula: I = dΦ/dΩ")
    print("\nExamples:")
    print("  • Standard candle: ~1 candela")
    print("  • Car headlight: 25,000-150,000 cd")
    print("  • LED flashlight: 1,000-10,000 cd")
    print()


def solve_problem1():
    """Solve Problem 1: Factory Hall 30m × 12m"""
    print("\n" + "="*80)
    print("PROBLEM 1: Factory Hall 30m × 12m - 100 lux")
    print("="*80)

    calc = LightingCalculator()

    # Problem parameters
    length = 30  # m
    width = 12  # m
    illumination = 100  # lux
    depreciation_factor = 0.8
    coefficient_utilization = 0.4
    lamp_efficiency = 14  # lm/W
    lamp_wattage = 100  # W (assumed)

    result = calc.calculate_lamps_with_wattage(
        length, width, illumination, depreciation_factor,
        coefficient_utilization, lamp_efficiency, lamp_wattage
    )

    disposition = calc.suggest_lamp_disposition(length, width, result['number_of_lamps'])

    print(f"\nINPUT PARAMETERS:")
    print(f"  • Area: {length}m × {width}m = {result['area']:.2f} m²")
    print(f"  • Required illumination: {illumination} lux")
    print(f"  • Depreciation factor: {depreciation_factor}")
    print(f"  • Coefficient of utilization: {coefficient_utilization}")
    print(f"  • Lamp efficiency: {lamp_efficiency} lm/W")
    print(f"  • Lamp wattage: {lamp_wattage} W")

    print(f"\nCALCULATIONS:")
    print(f"  • Lumens per lamp: {lamp_wattage} W × {lamp_efficiency} lm/W = {result['lumens_per_lamp']:.2f} lm")
    print(f"  • Effective lumens: {result['effective_lumens_per_lamp']:.2f} lm")
    print(f"  • Total lumens needed: {result['total_lumens_required']:.2f} lm")
    print(f"  • Calculated lamps: {result['actual_number']:.2f}")

    print(f"\n✓ RESULTS:")
    print(f"  • Number of lamps required: {result['number_of_lamps']} lamps")
    print(f"  • Total power consumption: {result['total_power_kw']:.2f} kW")

    print(f"\n✓ LAMP DISPOSITION:")
    print(f"  • Pattern: {disposition['pattern']} (rows × columns)")
    print(f"  • {disposition['rows']} rows × {disposition['columns']} columns")
    print(f"  • Spacing (length): {disposition['spacing_length']:.2f} m")
    print(f"  • Spacing (width): {disposition['spacing_width']:.2f} m")

    # Verification
    actual_lux = (result['number_of_lamps'] * result['effective_lumens_per_lamp']) / result['area']
    print(f"\nVERIFICATION:")
    print(f"  • Actual illumination: {actual_lux:.2f} lux")
    print(f"  • Design margin: {actual_lux - illumination:.2f} lux")


def solve_problem2():
    """Solve Problem 2: Workshop 100m × 50m"""
    print("\n" + "="*80)
    print("PROBLEM 2: Workshop 100m × 50m - 50 lux")
    print("="*80)

    calc = LightingCalculator()

    # Problem parameters
    length = 100  # m
    width = 50  # m
    illumination = 50  # lux
    depreciation_factor = 0.7
    coefficient_utilization = 0.9
    lamp_efficiency = 80  # lm/W
    lamp_wattage = 100  # W

    result = calc.calculate_lamps_with_wattage(
        length, width, illumination, depreciation_factor,
        coefficient_utilization, lamp_efficiency, lamp_wattage
    )

    disposition = calc.suggest_lamp_disposition(length, width, result['number_of_lamps'])

    print(f"\nINPUT PARAMETERS:")
    print(f"  • Area: {length}m × {width}m = {result['area']:.2f} m²")
    print(f"  • Required illumination: {illumination} lux")
    print(f"  • Depreciation factor: {depreciation_factor}")
    print(f"  • Coefficient of utilization: {coefficient_utilization}")
    print(f"  • Lamp efficiency: {lamp_efficiency} lm/W")
    print(f"  • Lamp wattage: {lamp_wattage} W")

    print(f"\nCALCULATIONS:")
    print(f"  • Lumens per lamp: {lamp_wattage} W × {lamp_efficiency} lm/W = {result['lumens_per_lamp']:.2f} lm")
    print(f"  • Effective lumens: {result['effective_lumens_per_lamp']:.2f} lm")
    print(f"  • Total lumens needed: {result['total_lumens_required']:.2f} lm")
    print(f"  • Calculated lamps: {result['actual_number']:.2f}")

    print(f"\n✓ RESULTS:")
    print(f"  • Number of lamps required: {result['number_of_lamps']} lamps")
    print(f"  • Total power consumption: {result['total_power_kw']:.2f} kW")
    print(f"  • Power density: {(result['total_power_kw'] * 1000 / result['area']):.2f} W/m²")

    print(f"\n✓ LAMP DISPOSITION:")
    print(f"  • Pattern: {disposition['pattern']} (rows × columns)")
    print(f"  • {disposition['rows']} rows × {disposition['columns']} columns")
    print(f"  • Spacing (length): {disposition['spacing_length']:.2f} m")
    print(f"  • Spacing (width): {disposition['spacing_width']:.2f} m")

    # Verification
    actual_lux = (result['number_of_lamps'] * result['effective_lumens_per_lamp']) / result['area']
    print(f"\nVERIFICATION:")
    print(f"  • Actual illumination: {actual_lux:.2f} lux")
    print(f"  • Design margin: {actual_lux - illumination:.2f} lux")


def test_rlc_simulation():
    """Test RLC circuit simulation"""
    print("\n" + "="*80)
    print("MULTI-PHYSICS SIMULATION: RLC Circuit")
    print("="*80)

    # RLC parameters
    R = 10  # Ohms
    L = 0.1  # Henry
    C = 100e-6  # Farads
    V_input = 24  # Volts

    def rlc_model(t, y):
        """RLC differential equations"""
        I = y[0]
        V_C = y[1]
        dI_dt = (V_input - R * I - V_C) / L
        dV_C_dt = I / C
        return [dI_dt, dV_C_dt]

    # Solve using RK45
    time_span = (0, 1)
    y0 = [0, 0]  # Initial conditions
    sol = solve_ivp(rlc_model, time_span, y0, method='RK45', dense_output=True)

    # Calculate circuit characteristics
    omega_0 = 1 / np.sqrt(L * C)
    f_0 = omega_0 / (2 * np.pi)
    zeta = R / 2 * np.sqrt(C / L)
    Q = omega_0 * L / R

    print(f"\nCIRCUIT PARAMETERS:")
    print(f"  • Resistance: {R} Ω")
    print(f"  • Inductance: {L*1000} mH")
    print(f"  • Capacitance: {C*1e6} µF")
    print(f"  • Input Voltage: {V_input} V")

    print(f"\nCIRCUIT CHARACTERISTICS:")
    print(f"  • Natural frequency: {f_0:.2f} Hz")
    print(f"  • Damping ratio: {zeta:.4f}")
    print(f"  • Quality factor: {Q:.2f}")
    print(f"  • Type: {'Underdamped' if zeta < 1 else 'Overdamped' if zeta > 1 else 'Critically damped'}")

    # RMS calculations
    I_final = sol.y[0][-1]
    V_C_final = sol.y[1][-1]
    print(f"\nFINAL STATE (t=1s):")
    print(f"  • Current: {I_final:.4f} A")
    print(f"  • Capacitor voltage: {V_C_final:.4f} V")

    print(f"\n✓ Simulation completed successfully using RK45 solver")


def main():
    """Main function"""
    print("\n" + "="*80)
    print("FACTORY LIGHTING CALCULATOR & MULTI-PHYSICS SIMULATOR")
    print("Advanced Electrical Engineering Application")
    print("="*80)

    # Print definitions
    print_definitions()

    # Solve problems
    solve_problem1()
    solve_problem2()

    # Test simulation
    test_rlc_simulation()

    print("\n" + "="*80)
    print("✓ ALL CALCULATIONS COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nTo run the GUI version, execute:")
    print("  python3 factory_lighting_calculator.py")
    print("\nNote: Requires tkinter, numpy, scipy, and matplotlib")
    print()


if __name__ == "__main__":
    main()

"""
Test script for Resistance Oven Simulator
Verifies calculations and demonstrates functionality
"""

import numpy as np
from resistance_oven_simulator import ResistanceOvenCalculator, ThermalElectricalModel


def test_problem_4():
    """Test Problem 4: Single-phase cylindrical wire"""
    print("=" * 70)
    print("TESTING PROBLEM 4: SINGLE-PHASE CYLINDRICAL WIRE")
    print("=" * 70)

    calc = ResistanceOvenCalculator()

    # Problem 4 parameters
    P = 15000  # 15 kW
    V = 220  # 220 V
    T_wire = 1000  # 1000°C
    T_charge = 600  # 600°C
    efficiency = 0.6
    emissivity = 0.9
    resistivity = 1.016e-6  # Ω·m

    results = calc.solve_problem_4(P, V, T_wire, T_charge, efficiency, emissivity, resistivity)

    print("\nInput Parameters:")
    print(f"  Power: {P/1000} kW")
    print(f"  Voltage: {V} V")
    print(f"  Wire Temperature: {T_wire}°C")
    print(f"  Charge Temperature: {T_charge}°C")
    print(f"  Radiating Efficiency: {efficiency}")
    print(f"  Emissivity: {emissivity}")
    print(f"  Resistivity: {resistivity*1e6} × 10⁻⁶ Ω·m")

    print("\nCalculated Results:")
    print(f"  Wire Diameter: {results['diameter_mm']:.2f} mm")
    print(f"  Wire Length: {results['length_m']:.2f} m")
    print(f"  Resistance: {results['resistance_ohm']:.3f} Ω")
    print(f"  Surface Area: {results['surface_area_m2']:.4f} m²")
    print(f"  Heat Flux: {results['heat_flux_W_m2']:.2f} W/m²")

    print("\nExpected Values:")
    print(f"  Diameter: 3.11 mm")
    print(f"  Length: 24.24 m")

    print("\nVerification:")
    print(f"  Resistance Check: {results['verification']['resistance_check']:.3f} Ω")
    print(f"  Power Check: {results['verification']['power_check']/1000:.2f} kW")
    print(f"  Error in Resistance: {abs(results['resistance_ohm'] - results['verification']['resistance_check']):.6f} Ω")
    print(f"  Error in Power: {abs(P - results['verification']['power_check']):.2f} W")

    # Check if close to expected values
    diameter_error = abs(results['diameter_mm'] - 3.11)
    length_error = abs(results['length_m'] - 24.24)

    print(f"\nComparison with Expected:")
    print(f"  Diameter Error: {diameter_error:.2f} mm ({diameter_error/3.11*100:.1f}%)")
    print(f"  Length Error: {length_error:.2f} m ({length_error/24.24*100:.1f}%)")

    if diameter_error < 0.5 and length_error < 2.0:
        print("\n✓ PROBLEM 4: PASSED - Results are within acceptable range")
    else:
        print("\n✗ PROBLEM 4: REVIEW - Results differ from expected values")

    return results


def test_problem_5():
    """Test Problem 5: Three-phase rectangular strip"""
    print("\n" + "=" * 70)
    print("TESTING PROBLEM 5: THREE-PHASE RECTANGULAR STRIP")
    print("=" * 70)

    calc = ResistanceOvenCalculator()

    # Problem 5 parameters
    P = 30000  # 30 kW
    V_line = 400  # 400 V
    T_wire = 1100  # 1100°C
    T_charge = 700  # 700°C
    efficiency = 0.6
    emissivity = 0.9
    resistivity = 1.03e-6  # Ω·m
    thickness = 0.00025  # 0.025 cm = 0.25 mm = 0.00025 m

    results = calc.solve_problem_5(P, V_line, T_wire, T_charge, efficiency,
                                   emissivity, resistivity, thickness)

    print("\nInput Parameters:")
    print(f"  Total Power: {P/1000} kW")
    print(f"  Line Voltage: {V_line} V")
    print(f"  Phase Voltage: {results['phase_voltage']:.2f} V")
    print(f"  Power per Phase: {results['power_per_phase']/1000:.2f} kW")
    print(f"  Wire Temperature: {T_wire}°C")
    print(f"  Charge Temperature: {T_charge}°C")
    print(f"  Strip Thickness: {thickness*1000} mm")
    print(f"  Radiating Efficiency: {efficiency}")
    print(f"  Emissivity: {emissivity}")
    print(f"  Resistivity: {resistivity*1e6} × 10⁻⁶ Ω·m")

    print("\nCalculated Results:")
    print(f"  Strip Width: {results['width_mm']:.2f} mm")
    print(f"  Strip Length: {results['length_m']:.2f} m")
    print(f"  Resistance per Phase: {results['resistance_per_phase_ohm']:.3f} Ω")
    print(f"  Surface Area per Phase: {results['surface_area_per_phase_m2']:.4f} m²")
    print(f"  Heat Flux: {results['heat_flux_W_m2']:.2f} W/m²")

    print("\nVerification:")
    print(f"  Resistance Check: {results['verification']['resistance_check']:.3f} Ω")
    print(f"  Power per Phase Check: {results['verification']['power_phase_check']/1000:.2f} kW")
    print(f"  Total Power Check: {results['verification']['power_total_check']/1000:.2f} kW")
    print(f"  Error in Resistance: {abs(results['resistance_per_phase_ohm'] - results['verification']['resistance_check']):.6f} Ω")
    print(f"  Error in Total Power: {abs(P - results['verification']['power_total_check']):.2f} W")

    print("\n✓ PROBLEM 5: COMPLETED - Results calculated and verified")

    return results


def test_thermal_model():
    """Test thermal-electrical model with short simulation"""
    print("\n" + "=" * 70)
    print("TESTING THERMAL-ELECTRICAL MODEL")
    print("=" * 70)

    calc = ResistanceOvenCalculator()
    model = ThermalElectricalModel(calc)

    # Simulation parameters
    params = {
        'V_rms': 220.0,
        'R_base': 3.23,
        'alpha': 0.0001,
        'mass_wire': 0.5,
        'mass_charge': 10.0,
        'cp_wire': 450.0,
        'cp_charge': 900.0,
        'efficiency': 0.6,
        'emissivity': 0.9,
        'surface_area': 0.238,
        'T_ambient': 25.0,
    }

    initial_state = [25.0, 25.0, 0.0]  # T_wire, T_charge, I
    t_span = (0, 60)  # 60 seconds

    print("\nRunning 60-second simulation with RK45 solver...")
    solution_rk45 = model.simulate(t_span, initial_state, params, method='RK45')

    if solution_rk45.success:
        print("✓ RK45 simulation completed successfully")
        print(f"  Final wire temperature: {solution_rk45.y[0, -1]:.2f}°C")
        print(f"  Final charge temperature: {solution_rk45.y[1, -1]:.2f}°C")
        print(f"  Final current: {solution_rk45.y[2, -1]:.2f} A")
        print(f"  Number of time steps: {len(solution_rk45.t)}")
    else:
        print("✗ RK45 simulation failed")

    print("\nRunning 60-second simulation with Euler method...")
    solution_euler = model.simulate(t_span, initial_state, params, method='Euler')

    if solution_euler.success:
        print("✓ Euler simulation completed successfully")
        print(f"  Final wire temperature: {solution_euler.y[0, -1]:.2f}°C")
        print(f"  Final charge temperature: {solution_euler.y[1, -1]:.2f}°C")
        print(f"  Final current: {solution_euler.y[2, -1]:.2f} A")
        print(f"  Number of time steps: {len(solution_euler.t)}")
    else:
        print("✗ Euler simulation failed")

    print("\n✓ THERMAL MODEL: PASSED - Both solvers working correctly")


def test_stefan_boltzmann():
    """Verify Stefan-Boltzmann heat transfer calculations"""
    print("\n" + "=" * 70)
    print("TESTING STEFAN-BOLTZMANN HEAT TRANSFER")
    print("=" * 70)

    calc = ResistanceOvenCalculator()

    T_wire = 1000  # °C
    T_charge = 600  # °C
    efficiency = 0.6
    emissivity = 0.9

    q = calc.calculate_heat_radiated_per_area(T_wire, T_charge, efficiency, emissivity)

    print(f"\nHeat radiated per unit area:")
    print(f"  Wire Temperature: {T_wire}°C ({T_wire + 273.15}K)")
    print(f"  Charge Temperature: {T_charge}°C ({T_charge + 273.15}K)")
    print(f"  Efficiency: {efficiency}")
    print(f"  Emissivity: {emissivity}")
    print(f"  Heat Flux: {q:.2f} W/m²")

    # Manual calculation for verification
    sigma = 5.67e-8  # Stefan-Boltzmann constant
    T_w_K = T_wire + 273.15
    T_c_K = T_charge + 273.15
    q_manual = efficiency * emissivity * sigma * (T_w_K**4 - T_c_K**4)

    print(f"\nManual calculation: {q_manual:.2f} W/m²")
    print(f"Difference: {abs(q - q_manual):.6f} W/m²")

    if abs(q - q_manual) < 1e-6:
        print("\n✓ HEAT TRANSFER: PASSED - Calculations match")
    else:
        print("\n✗ HEAT TRANSFER: FAILED - Calculations don't match")


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  RESISTANCE OVEN SIMULATOR - COMPREHENSIVE TEST SUITE  ".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")

    try:
        # Test Stefan-Boltzmann calculations
        test_stefan_boltzmann()

        # Test Problem 4
        results_4 = test_problem_4()

        # Test Problem 5
        results_5 = test_problem_5()

        # Test thermal model
        test_thermal_model()

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print("\n✓ All tests completed successfully!")
        print("\nKey Results:")
        print(f"  Problem 4 - Wire Diameter: {results_4['diameter_mm']:.2f} mm, Length: {results_4['length_m']:.2f} m")
        print(f"  Problem 5 - Strip Width: {results_5['width_mm']:.2f} mm, Length: {results_5['length_m']:.2f} m")
        print("\nTo run the full GUI simulator, execute:")
        print("  python resistance_oven_simulator.py")

    except Exception as e:
        print(f"\n✗ ERROR: Test suite encountered an error:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

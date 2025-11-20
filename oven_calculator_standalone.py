"""
Standalone Resistance Oven Calculator (No GUI)
Solves Problems 4 and 5 with comprehensive calculations
"""

import numpy as np
from scipy.constants import sigma as stefan_boltzmann_constant
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


class ResistanceOvenCalculator:
    """Core calculation module for resistance oven design"""

    def __init__(self):
        self.sigma = stefan_boltzmann_constant  # Stefan-Boltzmann constant: 5.67e-8 W/(m²·K⁴)

    def calculate_heat_radiated_per_area(self, T_wire, T_charge, emissivity, efficiency):
        """
        Calculate heat radiated per unit surface area
        Q/A = η × ε × σ × (T_wire⁴ - T_charge⁴)
        """
        T_w = T_wire + 273.15  # Convert to Kelvin
        T_c = T_charge + 273.15

        q_per_area = efficiency * emissivity * self.sigma * (T_w**4 - T_c**4)
        return q_per_area

    def solve_problem_4(self, P=15000, V=220, T_wire=1000, T_charge=600,
                       efficiency=0.6, emissivity=0.9, resistivity=1.016e-6):
        """
        Problem 4: Single-phase resistance oven with cylindrical wire
        Returns: diameter (mm), length (m), and detailed results
        """
        # Calculate heat radiated per unit area
        q_per_area = self.calculate_heat_radiated_per_area(T_wire, T_charge, emissivity, efficiency)

        # Required surface area
        A_surface = P / q_per_area

        # Resistance of the heater
        R = V**2 / P

        # For a cylindrical wire: A_surface = π × d × L
        # Resistance: R = ρ × L / A_cross = ρ × L / (π × (d/2)²)
        # R = 4 × ρ × L / (π × d²)
        # L = R × π × d² / (4 × ρ)

        # Substitute into surface area equation:
        # π × d × L = A_surface
        # L = A_surface / (π × d)

        # Equating the two expressions for L:
        # A_surface / (π × d) = R × π × d² / (4 × ρ)
        # A_surface × 4 × ρ = R × π² × d³
        # d³ = 4 × ρ × A_surface / (R × π²)

        d_cubed = (4 * resistivity * A_surface) / (R * np.pi**2)
        d = d_cubed**(1/3)  # diameter in meters
        d_mm = d * 1000  # Convert to mm

        # Calculate length
        L = A_surface / (np.pi * d)

        # Verification
        A_cross = np.pi * (d/2)**2
        R_check = resistivity * L / A_cross
        P_check = V**2 / R_check
        A_surface_check = np.pi * d * L

        results = {
            'diameter_mm': d_mm,
            'length_m': L,
            'resistance_ohm': R,
            'surface_area_m2': A_surface,
            'heat_flux_W_m2': q_per_area,
            'verification': {
                'resistance_check': R_check,
                'power_check': P_check,
                'surface_area_check': A_surface_check
            }
        }

        return results

    def solve_problem_5(self, P=30000, V_line=400, T_wire=1100, T_charge=700,
                       efficiency=0.6, emissivity=0.9, resistivity=1.03e-6,
                       thickness=0.00025):
        """
        Problem 5: Three-phase star-connected oven with rectangular strip
        Returns: width (mm) and detailed results
        """
        # For star connection, phase voltage
        V_phase = V_line / np.sqrt(3)

        # Power per phase
        P_phase = P / 3

        # Calculate heat radiated per unit area
        q_per_area = self.calculate_heat_radiated_per_area(T_wire, T_charge, emissivity, efficiency)

        # Required surface area per phase
        A_surface_phase = P_phase / q_per_area

        # Resistance per phase
        R_phase = V_phase**2 / P_phase

        # For a rectangular strip: A_surface = 2 × w × L (both sides radiate)
        # Resistance: R = ρ × L / A_cross = ρ × L / (w × t)
        # L = R × w × t / ρ

        # Surface area: 2 × w × L = A_surface_phase
        # L = A_surface_phase / (2 × w)

        # Equating the two expressions for L:
        # A_surface_phase / (2 × w) = R_phase × w × t / ρ
        # A_surface_phase × ρ = 2 × R_phase × w² × t
        # w² = A_surface_phase × ρ / (2 × R_phase × t)

        w_squared = (A_surface_phase * resistivity) / (2 * R_phase * thickness)
        w = np.sqrt(w_squared)  # width in meters
        w_mm = w * 1000  # Convert to mm

        # Calculate length
        L = A_surface_phase / (2 * w)

        # Verification
        A_cross = w * thickness
        R_check = resistivity * L / A_cross
        P_phase_check = V_phase**2 / R_check
        P_total_check = 3 * P_phase_check
        A_surface_check = 2 * w * L

        results = {
            'width_mm': w_mm,
            'length_m': L,
            'thickness_mm': thickness * 1000,
            'resistance_per_phase_ohm': R_phase,
            'surface_area_per_phase_m2': A_surface_phase,
            'heat_flux_W_m2': q_per_area,
            'phase_voltage': V_phase,
            'power_per_phase': P_phase,
            'verification': {
                'resistance_check': R_check,
                'power_phase_check': P_phase_check,
                'power_total_check': P_total_check,
                'surface_area_check': A_surface_check
            }
        }

        return results


class ThermalElectricalModel:
    """
    Multi-physics model combining thermal and electrical dynamics
    Models the transient heating behavior of resistance ovens
    """

    def __init__(self, calculator):
        self.calc = calculator
        self.sigma = stefan_boltzmann_constant

    def thermal_electrical_ode(self, t, state, params):
        """
        Coupled thermal-electrical differential equations

        State variables:
        - T_wire: Wire temperature (°C)
        - T_charge: Charge temperature (°C)
        - I: Current (A)
        """
        T_wire, T_charge, I = state

        # Unpack parameters
        V_rms = params['V_rms']
        R_base = params['R_base']
        alpha = params['alpha']
        mass_wire = params['mass_wire']
        mass_charge = params['mass_charge']
        cp_wire = params['cp_wire']
        cp_charge = params['cp_charge']
        efficiency = params['efficiency']
        emissivity = params['emissivity']
        surface_area = params['surface_area']
        T_ambient = params['T_ambient']

        # Temperature-dependent resistance
        R = R_base * (1 + alpha * (T_wire - 20))

        # Electrical power
        P_elec = V_rms**2 / R
        I_new = V_rms / R

        # Heat transfer from wire to charge (radiation)
        T_w_K = T_wire + 273.15
        T_c_K = T_charge + 273.15
        Q_rad = efficiency * emissivity * self.sigma * surface_area * (T_w_K**4 - T_c_K**4)

        # Heat loss from wire to ambient (convection + radiation)
        T_a_K = T_ambient + 273.15
        h_conv = 10  # Convection coefficient (W/m²·K)
        Q_loss_conv = h_conv * surface_area * (T_wire - T_ambient)
        Q_loss_rad_ambient = 0.5 * emissivity * self.sigma * surface_area * (T_w_K**4 - T_a_K**4)

        # Heat loss from charge to ambient
        Q_charge_loss = h_conv * surface_area * 0.5 * (T_charge - T_ambient)

        # Energy balance for wire
        dT_wire_dt = (P_elec - Q_rad - Q_loss_conv - Q_loss_rad_ambient) / (mass_wire * cp_wire)

        # Energy balance for charge
        dT_charge_dt = (Q_rad - Q_charge_loss) / (mass_charge * cp_charge)

        # Current dynamics (simplified first-order lag)
        tau_elec = 0.01  # Electrical time constant (s)
        dI_dt = (I_new - I) / tau_elec

        return [dT_wire_dt, dT_charge_dt, dI_dt]

    def simulate(self, t_span, initial_state, params, method='RK45'):
        """
        Run dynamic simulation using ODE solver
        """
        if method == 'RK45':
            solution = solve_ivp(
                fun=lambda t, y: self.thermal_electrical_ode(t, y, params),
                t_span=t_span,
                y0=initial_state,
                method='RK45',
                dense_output=True,
                max_step=1.0
            )
            return solution

        elif method == 'Euler':
            # Manual Euler integration
            t_start, t_end = t_span
            dt = 0.1  # Time step
            t_points = np.arange(t_start, t_end, dt)
            n_points = len(t_points)

            state = np.zeros((3, n_points))
            state[:, 0] = initial_state

            for i in range(1, n_points):
                derivatives = self.thermal_electrical_ode(t_points[i-1], state[:, i-1], params)
                state[:, i] = state[:, i-1] + np.array(derivatives) * dt

            class EulerSolution:
                def __init__(self, t, y):
                    self.t = t
                    self.y = y
                    self.success = True

            return EulerSolution(t_points, state)


def print_problem_4():
    """Solve and print Problem 4 results"""
    print("=" * 70)
    print("PROBLEM 4: SINGLE-PHASE CYLINDRICAL WIRE")
    print("=" * 70)

    calc = ResistanceOvenCalculator()
    results = calc.solve_problem_4()

    print("\nGIVEN:")
    print("  Power: 15 kW")
    print("  Voltage: 220 V (single-phase)")
    print("  Wire Temperature: 1000°C")
    print("  Charge Temperature: 600°C")
    print("  Radiating Efficiency: 0.6")
    print("  Emissivity: 0.9")
    print("  Resistivity: 1.016 × 10⁻⁶ Ω·m")

    print("\nSOLUTION:")
    print(f"  Wire Diameter: {results['diameter_mm']:.2f} mm")
    print(f"  Wire Length: {results['length_m']:.2f} m")
    print(f"  Resistance: {results['resistance_ohm']:.3f} Ω")
    print(f"  Surface Area: {results['surface_area_m2']:.4f} m²")
    print(f"  Heat Flux: {results['heat_flux_W_m2']:.2f} W/m²")

    print("\nVERIFICATION:")
    print(f"  Resistance Check: {results['verification']['resistance_check']:.3f} Ω")
    print(f"  Power Check: {results['verification']['power_check']/1000:.2f} kW")
    print(f"  Surface Area Check: {results['verification']['surface_area_check']:.4f} m²")

    print("\nEXPECTED:")
    print("  Diameter: 3.11 mm")
    print("  Length: 24.24 m")

    return results


def print_problem_5():
    """Solve and print Problem 5 results"""
    print("\n" + "=" * 70)
    print("PROBLEM 5: THREE-PHASE RECTANGULAR STRIP")
    print("=" * 70)

    calc = ResistanceOvenCalculator()
    results = calc.solve_problem_5()

    print("\nGIVEN:")
    print("  Total Power: 30 kW")
    print("  Line Voltage: 400 V (3-phase star)")
    print("  Wire Temperature: 1100°C")
    print("  Charge Temperature: 700°C")
    print("  Strip Thickness: 0.025 cm (0.25 mm)")
    print("  Radiating Efficiency: 0.6")
    print("  Emissivity: 0.9")
    print("  Resistivity: 1.03 × 10⁻⁶ Ω·m")

    print("\nCALCULATED:")
    print(f"  Phase Voltage: {results['phase_voltage']:.2f} V")
    print(f"  Power per Phase: {results['power_per_phase']/1000:.2f} kW")

    print("\nSOLUTION:")
    print(f"  Strip Width: {results['width_mm']:.2f} mm")
    print(f"  Strip Length: {results['length_m']:.2f} m")
    print(f"  Resistance per Phase: {results['resistance_per_phase_ohm']:.3f} Ω")
    print(f"  Surface Area per Phase: {results['surface_area_per_phase_m2']:.4f} m²")
    print(f"  Heat Flux: {results['heat_flux_W_m2']:.2f} W/m²")

    print("\nVERIFICATION:")
    print(f"  Resistance Check: {results['verification']['resistance_check']:.3f} Ω")
    print(f"  Power per Phase Check: {results['verification']['power_phase_check']/1000:.2f} kW")
    print(f"  Total Power Check: {results['verification']['power_total_check']/1000:.2f} kW")
    print(f"  Surface Area Check: {results['verification']['surface_area_check']:.4f} m²")

    return results


def run_dynamic_simulation():
    """Run and visualize dynamic simulation"""
    print("\n" + "=" * 70)
    print("DYNAMIC THERMAL-ELECTRICAL SIMULATION")
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
    t_span = (0, 300)  # 300 seconds (5 minutes)

    print("\nSimulation Parameters:")
    print(f"  Applied Voltage: {params['V_rms']} V")
    print(f"  Base Resistance: {params['R_base']} Ω")
    print(f"  Wire Mass: {params['mass_wire']} kg")
    print(f"  Charge Mass: {params['mass_charge']} kg")
    print(f"  Simulation Time: {t_span[1]} seconds")
    print(f"  Initial Temperature: {initial_state[0]}°C")

    print("\nRunning RK45 simulation...")
    solution = model.simulate(t_span, initial_state, params, method='RK45')

    if solution.success:
        print("✓ Simulation completed successfully")
        print(f"  Final wire temperature: {solution.y[0, -1]:.2f}°C")
        print(f"  Final charge temperature: {solution.y[1, -1]:.2f}°C")
        print(f"  Final current: {solution.y[2, -1]:.2f} A")

        # Create comprehensive visualization
        fig, axes = plt.subplots(3, 2, figsize=(14, 10))
        fig.suptitle('Resistance Oven Multi-Physics Simulation Results', fontsize=14, fontweight='bold')

        # Temperature evolution
        axes[0, 0].plot(solution.t, solution.y[0], 'r-', label='Wire', linewidth=2)
        axes[0, 0].plot(solution.t, solution.y[1], 'b-', label='Charge', linewidth=2)
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Temperature (°C)')
        axes[0, 0].set_title('Temperature Evolution')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Current evolution
        axes[0, 1].plot(solution.t, solution.y[2], 'g-', linewidth=2)
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Current (A)')
        axes[0, 1].set_title('Current Evolution')
        axes[0, 1].grid(True)

        # Power consumption
        R_values = params['R_base'] * (1 + params['alpha'] * (solution.y[0] - 20))
        P_values = params['V_rms']**2 / R_values / 1000  # kW
        axes[1, 0].plot(solution.t, P_values, 'm-', linewidth=2)
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Power (kW)')
        axes[1, 0].set_title('Power Consumption')
        axes[1, 0].grid(True)

        # Phase space
        axes[1, 1].plot(solution.y[0], solution.y[2], 'b-', linewidth=2)
        axes[1, 1].scatter(solution.y[0, 0], solution.y[2, 0], c='g', s=100, marker='o', label='Start', zorder=5)
        axes[1, 1].scatter(solution.y[0, -1], solution.y[2, -1], c='r', s=100, marker='s', label='End', zorder=5)
        axes[1, 1].set_xlabel('Wire Temperature (°C)')
        axes[1, 1].set_ylabel('Current (A)')
        axes[1, 1].set_title('Phase Space: Temperature vs Current')
        axes[1, 1].legend()
        axes[1, 1].grid(True)

        # Heat transfer analysis
        sigma = stefan_boltzmann_constant
        Q_rad = (params['efficiency'] * params['emissivity'] * sigma * params['surface_area'] *
                ((solution.y[0] + 273.15)**4 - (solution.y[1] + 273.15)**4)) / 1000  # kW

        axes[2, 0].plot(solution.t, Q_rad, 'r-', label='Radiated Heat', linewidth=2)
        axes[2, 0].plot(solution.t, P_values, 'b-', label='Input Power', linewidth=2)
        axes[2, 0].set_xlabel('Time (s)')
        axes[2, 0].set_ylabel('Heat Transfer Rate (kW)')
        axes[2, 0].set_title('Heat Transfer Analysis')
        axes[2, 0].legend()
        axes[2, 0].grid(True)

        # Efficiency analysis
        efficiency = (Q_rad / P_values * 100)
        axes[2, 1].plot(solution.t, efficiency, 'c-', linewidth=2)
        axes[2, 1].axhline(y=60, color='r', linestyle='--', label='Design Efficiency', linewidth=2)
        axes[2, 1].set_xlabel('Time (s)')
        axes[2, 1].set_ylabel('Efficiency (%)')
        axes[2, 1].set_title('System Efficiency')
        axes[2, 1].legend()
        axes[2, 1].grid(True)

        plt.tight_layout()
        plt.savefig('oven_simulation_results.png', dpi=300, bbox_inches='tight')
        print("\n✓ Visualization saved as 'oven_simulation_results.png'")

        return solution
    else:
        print("✗ Simulation failed")
        return None


def main():
    """Main function"""
    print("\n" + "*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  RESISTANCE OVEN CALCULATOR - STANDALONE VERSION  ".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70 + "\n")

    # Solve Problem 4
    results_4 = print_problem_4()

    # Solve Problem 5
    results_5 = print_problem_5()

    # Run dynamic simulation
    solution = run_dynamic_simulation()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✓ All calculations completed successfully!")
    print("\nResults:")
    print(f"  Problem 4 - Diameter: {results_4['diameter_mm']:.2f} mm, Length: {results_4['length_m']:.2f} m")
    print(f"  Problem 5 - Width: {results_5['width_mm']:.2f} mm, Length: {results_5['length_m']:.2f} m")

    if solution:
        print(f"\nSimulation:")
        print(f"  Final wire temperature: {solution.y[0, -1]:.2f}°C")
        print(f"  Final charge temperature: {solution.y[1, -1]:.2f}°C")
        print(f"  Steady-state current: {solution.y[2, -1]:.2f} A")

    print("\n" + "*" * 70)


if __name__ == "__main__":
    main()

"""
Resistance Oven Wire Calculator and Multi-Physics Simulator
Solves heating element design problems with dynamic thermal-electrical simulation
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox
from scipy.integrate import solve_ivp
from scipy.constants import sigma as stefan_boltzmann_constant
import threading
import time


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

        Parameters:
        - V: Voltage (V)
        - R_base: Base resistance at reference temperature (Ω)
        - alpha: Temperature coefficient of resistance (1/°C)
        - mass_wire: Mass of wire (kg)
        - mass_charge: Mass of charge (kg)
        - cp_wire: Specific heat of wire (J/kg·°C)
        - cp_charge: Specific heat of charge (J/kg·°C)
        - efficiency: Radiating efficiency
        - emissivity: Emissivity
        - surface_area: Surface area (m²)
        - T_ambient: Ambient temperature (°C)
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

        Args:
            t_span: Tuple (t_start, t_end)
            initial_state: [T_wire_0, T_charge_0, I_0]
            params: Dictionary of parameters
            method: 'RK45' or 'Euler'
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

            # Create solution object compatible with solve_ivp
            class EulerSolution:
                def __init__(self, t, y):
                    self.t = t
                    self.y = y
                    self.success = True

                def sol(self, t_eval):
                    # Simple linear interpolation
                    return np.array([np.interp(t_eval, self.t, self.y[i]) for i in range(self.y.shape[0])])

            return EulerSolution(t_points, state)


class ResistanceOvenGUI:
    """Main GUI application with Tkinter"""

    def __init__(self, root):
        self.root = root
        self.root.title("Resistance Oven Multi-Physics Simulator")
        self.root.geometry("1400x900")

        # Initialize calculator and model
        self.calculator = ResistanceOvenCalculator()
        self.model = ThermalElectricalModel(self.calculator)

        # Simulation control
        self.is_simulating = False
        self.simulation_thread = None
        self.current_time = 0
        self.time_history = []
        self.temp_wire_history = []
        self.temp_charge_history = []
        self.current_history = []
        self.power_history = []

        # Setup GUI
        self.setup_gui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def setup_gui(self):
        """Setup the main GUI components"""

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Static Calculations
        self.tab_static = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_static, text='Static Design Calculator')
        self.setup_static_tab()

        # Tab 2: Dynamic Simulation
        self.tab_dynamic = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dynamic, text='Dynamic Simulation')
        self.setup_dynamic_tab()

        # Tab 3: Results & Visualization
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text='Results Visualization')
        self.setup_results_tab()

    def setup_static_tab(self):
        """Setup static calculation tab"""

        # Main container with scrollbar
        canvas = tk.Canvas(self.tab_static)
        scrollbar = ttk.Scrollbar(self.tab_static, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Problem selection
        prob_frame = ttk.LabelFrame(scrollable_frame, text="Problem Selection", padding=10)
        prob_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

        self.problem_var = tk.StringVar(value="Problem 4")
        ttk.Radiobutton(prob_frame, text="Problem 4: Single-Phase Cylindrical Wire",
                       variable=self.problem_var, value="Problem 4",
                       command=self.update_input_fields).pack(anchor='w')
        ttk.Radiobutton(prob_frame, text="Problem 5: Three-Phase Rectangular Strip",
                       variable=self.problem_var, value="Problem 5",
                       command=self.update_input_fields).pack(anchor='w')

        # Input parameters
        input_frame = ttk.LabelFrame(scrollable_frame, text="Input Parameters", padding=10)
        input_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

        self.inputs = {}

        # Common parameters
        common_params = [
            ('Power (kW)', 'power', 15.0),
            ('Voltage (V)', 'voltage', 220.0),
            ('Wire Temperature (°C)', 't_wire', 1000.0),
            ('Charge Temperature (°C)', 't_charge', 600.0),
            ('Radiating Efficiency', 'efficiency', 0.6),
            ('Emissivity', 'emissivity', 0.9),
            ('Resistivity (×10⁻⁶ Ω·m)', 'resistivity', 1.016),
        ]

        for i, (label, key, default) in enumerate(common_params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            var = tk.DoubleVar(value=default)
            self.inputs[key] = var
            entry = ttk.Entry(input_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky='ew', pady=2, padx=5)

        # Problem 5 specific
        ttk.Label(input_frame, text="Strip Thickness (mm)").grid(row=len(common_params), column=0, sticky='w', pady=2)
        self.inputs['thickness'] = tk.DoubleVar(value=0.25)
        self.thickness_entry = ttk.Entry(input_frame, textvariable=self.inputs['thickness'], width=15)
        self.thickness_entry.grid(row=len(common_params), column=1, sticky='ew', pady=2, padx=5)

        # Calculate button
        ttk.Button(input_frame, text="Calculate", command=self.calculate_static).grid(
            row=len(common_params)+1, column=0, columnspan=2, pady=10)

        # Results display
        results_frame = ttk.LabelFrame(scrollable_frame, text="Calculation Results", padding=10)
        results_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)

        self.results_text = tk.Text(results_frame, height=30, width=60, wrap='word')
        results_scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)

        self.results_text.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.update_input_fields()

    def setup_dynamic_tab(self):
        """Setup dynamic simulation tab"""

        # Left panel: Controls
        control_frame = ttk.Frame(self.tab_dynamic)
        control_frame.pack(side='left', fill='y', padx=10, pady=10)

        # Simulation parameters
        param_frame = ttk.LabelFrame(control_frame, text="Simulation Parameters", padding=10)
        param_frame.pack(fill='x', pady=5)

        self.sim_params = {}

        sim_inputs = [
            ('Simulation Time (s)', 'sim_time', 300.0),
            ('Applied Voltage (V)', 'v_applied', 220.0),
            ('Base Resistance (Ω)', 'r_base', 3.23),
            ('Temp Coefficient (1/°C)', 'alpha', 0.0001),
            ('Wire Mass (kg)', 'mass_wire', 0.5),
            ('Charge Mass (kg)', 'mass_charge', 10.0),
            ('Wire Sp. Heat (J/kg·°C)', 'cp_wire', 450.0),
            ('Charge Sp. Heat (J/kg·°C)', 'cp_charge', 900.0),
            ('Surface Area (m²)', 'surface_area', 0.238),
            ('Ambient Temp (°C)', 't_ambient', 25.0),
        ]

        for i, (label, key, default) in enumerate(sim_inputs):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            var = tk.DoubleVar(value=default)
            self.sim_params[key] = var
            entry = ttk.Entry(param_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky='ew', pady=2, padx=5)

        # Initial conditions
        ic_frame = ttk.LabelFrame(control_frame, text="Initial Conditions", padding=10)
        ic_frame.pack(fill='x', pady=5)

        ttk.Label(ic_frame, text="Initial Wire Temp (°C)").grid(row=0, column=0, sticky='w', pady=2)
        self.sim_params['t_wire_0'] = tk.DoubleVar(value=25.0)
        ttk.Entry(ic_frame, textvariable=self.sim_params['t_wire_0'], width=15).grid(row=0, column=1, pady=2, padx=5)

        ttk.Label(ic_frame, text="Initial Charge Temp (°C)").grid(row=1, column=0, sticky='w', pady=2)
        self.sim_params['t_charge_0'] = tk.DoubleVar(value=25.0)
        ttk.Entry(ic_frame, textvariable=self.sim_params['t_charge_0'], width=15).grid(row=1, column=1, pady=2, padx=5)

        # ODE Solver selection
        solver_frame = ttk.LabelFrame(control_frame, text="ODE Solver", padding=10)
        solver_frame.pack(fill='x', pady=5)

        self.solver_var = tk.StringVar(value="RK45")
        ttk.Radiobutton(solver_frame, text="RK45 (Runge-Kutta 4-5)",
                       variable=self.solver_var, value="RK45").pack(anchor='w')
        ttk.Radiobutton(solver_frame, text="Euler Method",
                       variable=self.solver_var, value="Euler").pack(anchor='w')

        # Control sliders
        slider_frame = ttk.LabelFrame(control_frame, text="Real-Time Control", padding=10)
        slider_frame.pack(fill='x', pady=5)

        ttk.Label(slider_frame, text="Voltage Adjustment (%)").pack(anchor='w')
        self.voltage_scale = tk.DoubleVar(value=100.0)
        ttk.Scale(slider_frame, from_=0, to=150, variable=self.voltage_scale,
                 orient='horizontal').pack(fill='x')
        ttk.Label(slider_frame, textvariable=self.voltage_scale).pack()

        ttk.Label(slider_frame, text="Efficiency Adjustment (%)").pack(anchor='w')
        self.efficiency_scale = tk.DoubleVar(value=100.0)
        ttk.Scale(slider_frame, from_=0, to=100, variable=self.efficiency_scale,
                 orient='horizontal').pack(fill='x')
        ttk.Label(slider_frame, textvariable=self.efficiency_scale).pack()

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side='left', padx=2, fill='x', expand=True)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.stop_button.pack(side='left', padx=2, fill='x', expand=True)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side='left', padx=2, fill='x', expand=True)

        # Right panel: Real-time plots
        plot_frame = ttk.Frame(self.tab_dynamic)
        plot_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        self.fig_dynamic = Figure(figsize=(10, 8))
        self.ax_temp = self.fig_dynamic.add_subplot(311)
        self.ax_current = self.fig_dynamic.add_subplot(312)
        self.ax_power = self.fig_dynamic.add_subplot(313)

        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_title('Temperature vs Time')
        self.ax_temp.grid(True)
        self.ax_temp.legend(['Wire', 'Charge'])

        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Current vs Time')
        self.ax_current.grid(True)

        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (kW)')
        self.ax_power.set_title('Power vs Time')
        self.ax_power.grid(True)

        self.fig_dynamic.tight_layout()

        self.canvas_dynamic = FigureCanvasTkAgg(self.fig_dynamic, plot_frame)
        self.canvas_dynamic.get_tk_widget().pack(fill='both', expand=True)

    def setup_results_tab(self):
        """Setup results and visualization tab"""

        # Create figure with multiple subplots
        self.fig_results = Figure(figsize=(12, 10))

        # Temperature profile
        self.ax_results_temp = self.fig_results.add_subplot(321)
        self.ax_results_temp.set_title('Temperature Evolution')
        self.ax_results_temp.set_xlabel('Time (s)')
        self.ax_results_temp.set_ylabel('Temperature (°C)')
        self.ax_results_temp.grid(True)

        # Current profile
        self.ax_results_current = self.fig_results.add_subplot(322)
        self.ax_results_current.set_title('Current Evolution')
        self.ax_results_current.set_xlabel('Time (s)')
        self.ax_results_current.set_ylabel('Current (A)')
        self.ax_results_current.grid(True)

        # Power profile
        self.ax_results_power = self.fig_results.add_subplot(323)
        self.ax_results_power.set_title('Power Consumption')
        self.ax_results_power.set_xlabel('Time (s)')
        self.ax_results_power.set_ylabel('Power (kW)')
        self.ax_results_power.grid(True)

        # Phase space (Temperature vs Current)
        self.ax_phase = self.fig_results.add_subplot(324)
        self.ax_phase.set_title('Phase Space: Temperature vs Current')
        self.ax_phase.set_xlabel('Wire Temperature (°C)')
        self.ax_phase.set_ylabel('Current (A)')
        self.ax_phase.grid(True)

        # Heat transfer analysis
        self.ax_heat = self.fig_results.add_subplot(325)
        self.ax_heat.set_title('Heat Transfer Analysis')
        self.ax_heat.set_xlabel('Time (s)')
        self.ax_heat.set_ylabel('Heat Transfer Rate (kW)')
        self.ax_heat.grid(True)

        # Efficiency analysis
        self.ax_efficiency = self.fig_results.add_subplot(326)
        self.ax_efficiency.set_title('System Efficiency')
        self.ax_efficiency.set_xlabel('Time (s)')
        self.ax_efficiency.set_ylabel('Efficiency (%)')
        self.ax_efficiency.grid(True)

        self.fig_results.tight_layout()

        self.canvas_results = FigureCanvasTkAgg(self.fig_results, self.tab_results)
        self.canvas_results.get_tk_widget().pack(fill='both', expand=True)

        # Export button
        export_frame = ttk.Frame(self.tab_results)
        export_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(export_frame, text="Export Data to CSV",
                  command=self.export_data).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Update Visualization",
                  command=self.update_results_visualization).pack(side='left', padx=5)

    def update_input_fields(self):
        """Update input fields based on problem selection"""
        if self.problem_var.get() == "Problem 4":
            self.inputs['power'].set(15.0)
            self.inputs['voltage'].set(220.0)
            self.inputs['t_wire'].set(1000.0)
            self.inputs['t_charge'].set(600.0)
            self.inputs['resistivity'].set(1.016)
            self.thickness_entry.config(state='disabled')
        else:
            self.inputs['power'].set(30.0)
            self.inputs['voltage'].set(400.0)
            self.inputs['t_wire'].set(1100.0)
            self.inputs['t_charge'].set(700.0)
            self.inputs['resistivity'].set(1.03)
            self.thickness_entry.config(state='normal')

    def calculate_static(self):
        """Perform static calculations"""
        try:
            # Get input values
            P = self.inputs['power'].get() * 1000  # Convert to W
            V = self.inputs['voltage'].get()
            T_wire = self.inputs['t_wire'].get()
            T_charge = self.inputs['t_charge'].get()
            efficiency = self.inputs['efficiency'].get()
            emissivity = self.inputs['emissivity'].get()
            resistivity = self.inputs['resistivity'].get() * 1e-6

            self.results_text.delete(1.0, tk.END)

            if self.problem_var.get() == "Problem 4":
                results = self.calculator.solve_problem_4(
                    P, V, T_wire, T_charge, efficiency, emissivity, resistivity
                )

                output = "=" * 60 + "\n"
                output += "PROBLEM 4: SINGLE-PHASE CYLINDRICAL WIRE\n"
                output += "=" * 60 + "\n\n"
                output += "INPUT PARAMETERS:\n"
                output += f"  Power: {P/1000:.2f} kW\n"
                output += f"  Voltage: {V:.2f} V\n"
                output += f"  Wire Temperature: {T_wire:.2f} °C\n"
                output += f"  Charge Temperature: {T_charge:.2f} °C\n"
                output += f"  Radiating Efficiency: {efficiency:.2f}\n"
                output += f"  Emissivity: {emissivity:.2f}\n"
                output += f"  Resistivity: {resistivity*1e6:.3f} × 10⁻⁶ Ω·m\n\n"

                output += "RESULTS:\n"
                output += f"  Wire Diameter: {results['diameter_mm']:.2f} mm\n"
                output += f"  Wire Length: {results['length_m']:.2f} m\n"
                output += f"  Resistance: {results['resistance_ohm']:.3f} Ω\n"
                output += f"  Surface Area: {results['surface_area_m2']:.4f} m²\n"
                output += f"  Heat Flux: {results['heat_flux_W_m2']:.2f} W/m²\n\n"

                output += "VERIFICATION:\n"
                output += f"  Calculated Resistance: {results['verification']['resistance_check']:.3f} Ω\n"
                output += f"  Power Check: {results['verification']['power_check']/1000:.2f} kW\n"
                output += f"  Surface Area Check: {results['verification']['surface_area_check']:.4f} m²\n\n"

                output += "Expected Values: Diameter = 3.11 mm, Length = 24.24 m\n"

            else:  # Problem 5
                thickness = self.inputs['thickness'].get() / 1000  # Convert to m
                results = self.calculator.solve_problem_5(
                    P, V, T_wire, T_charge, efficiency, emissivity, resistivity, thickness
                )

                output = "=" * 60 + "\n"
                output += "PROBLEM 5: THREE-PHASE RECTANGULAR STRIP\n"
                output += "=" * 60 + "\n\n"
                output += "INPUT PARAMETERS:\n"
                output += f"  Total Power: {P/1000:.2f} kW\n"
                output += f"  Line Voltage: {V:.2f} V\n"
                output += f"  Phase Voltage: {results['phase_voltage']:.2f} V\n"
                output += f"  Power per Phase: {results['power_per_phase']/1000:.2f} kW\n"
                output += f"  Wire Temperature: {T_wire:.2f} °C\n"
                output += f"  Charge Temperature: {T_charge:.2f} °C\n"
                output += f"  Strip Thickness: {results['thickness_mm']:.2f} mm\n"
                output += f"  Radiating Efficiency: {efficiency:.2f}\n"
                output += f"  Emissivity: {emissivity:.2f}\n"
                output += f"  Resistivity: {resistivity*1e6:.3f} × 10⁻⁶ Ω·m\n\n"

                output += "RESULTS:\n"
                output += f"  Strip Width: {results['width_mm']:.2f} mm\n"
                output += f"  Strip Length: {results['length_m']:.2f} m\n"
                output += f"  Resistance per Phase: {results['resistance_per_phase_ohm']:.3f} Ω\n"
                output += f"  Surface Area per Phase: {results['surface_area_per_phase_m2']:.4f} m²\n"
                output += f"  Heat Flux: {results['heat_flux_W_m2']:.2f} W/m²\n\n"

                output += "VERIFICATION:\n"
                output += f"  Calculated Resistance: {results['verification']['resistance_check']:.3f} Ω\n"
                output += f"  Power per Phase Check: {results['verification']['power_phase_check']/1000:.2f} kW\n"
                output += f"  Total Power Check: {results['verification']['power_total_check']/1000:.2f} kW\n"
                output += f"  Surface Area Check: {results['verification']['surface_area_check']:.4f} m²\n\n"

            self.results_text.insert(1.0, output)

        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error during calculation:\n{str(e)}")

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.is_simulating:
            return

        self.is_simulating = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        # Reset history
        self.current_time = 0
        self.time_history = []
        self.temp_wire_history = []
        self.temp_charge_history = []
        self.current_history = []
        self.power_history = []

        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
        self.simulation_thread.start()

    def stop_simulation(self):
        """Stop dynamic simulation"""
        self.is_simulating = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()

        # Clear history
        self.current_time = 0
        self.time_history = []
        self.temp_wire_history = []
        self.temp_charge_history = []
        self.current_history = []
        self.power_history = []

        # Clear plots
        self.ax_temp.clear()
        self.ax_current.clear()
        self.ax_power.clear()

        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_title('Temperature vs Time')
        self.ax_temp.grid(True)

        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Current vs Time')
        self.ax_current.grid(True)

        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (kW)')
        self.ax_power.set_title('Power vs Time')
        self.ax_power.grid(True)

        self.canvas_dynamic.draw()

    def run_simulation(self):
        """Run the dynamic simulation"""
        try:
            # Get simulation parameters
            sim_time = self.sim_params['sim_time'].get()

            params = {
                'V_rms': self.sim_params['v_applied'].get(),
                'R_base': self.sim_params['r_base'].get(),
                'alpha': self.sim_params['alpha'].get(),
                'mass_wire': self.sim_params['mass_wire'].get(),
                'mass_charge': self.sim_params['mass_charge'].get(),
                'cp_wire': self.sim_params['cp_wire'].get(),
                'cp_charge': self.sim_params['cp_charge'].get(),
                'efficiency': 0.6,
                'emissivity': 0.9,
                'surface_area': self.sim_params['surface_area'].get(),
                'T_ambient': self.sim_params['t_ambient'].get(),
            }

            initial_state = [
                self.sim_params['t_wire_0'].get(),
                self.sim_params['t_charge_0'].get(),
                0.0  # Initial current
            ]

            solver = self.solver_var.get()

            # Run simulation in steps for real-time update
            dt = 1.0  # Update every second
            t_current = 0
            state_current = initial_state.copy()

            while self.is_simulating and t_current < sim_time:
                # Apply slider adjustments
                voltage_factor = self.voltage_scale.get() / 100.0
                efficiency_factor = self.efficiency_scale.get() / 100.0

                params['V_rms'] = self.sim_params['v_applied'].get() * voltage_factor
                params['efficiency'] = 0.6 * efficiency_factor

                # Solve for next time step
                t_span = (t_current, min(t_current + dt, sim_time))

                solution = self.model.simulate(t_span, state_current, params, method=solver)

                if solution.success:
                    # Get final state
                    state_current = [solution.y[0, -1], solution.y[1, -1], solution.y[2, -1]]
                    t_current = solution.t[-1]

                    # Calculate power
                    R = params['R_base'] * (1 + params['alpha'] * (state_current[0] - 20))
                    P = params['V_rms']**2 / R

                    # Store history
                    self.time_history.append(t_current)
                    self.temp_wire_history.append(state_current[0])
                    self.temp_charge_history.append(state_current[1])
                    self.current_history.append(state_current[2])
                    self.power_history.append(P / 1000)  # kW

                    # Update plots
                    self.root.after(0, self.update_dynamic_plots)

                    time.sleep(0.05)  # Small delay for visualization
                else:
                    break

            self.is_simulating = False
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))

        except Exception as e:
            self.is_simulating = False
            self.root.after(0, lambda: messagebox.showerror("Simulation Error",
                                                            f"Error during simulation:\n{str(e)}"))

    def update_dynamic_plots(self):
        """Update real-time plots"""
        if len(self.time_history) == 0:
            return

        # Temperature plot
        self.ax_temp.clear()
        self.ax_temp.plot(self.time_history, self.temp_wire_history, 'r-', label='Wire', linewidth=2)
        self.ax_temp.plot(self.time_history, self.temp_charge_history, 'b-', label='Charge', linewidth=2)
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_title('Temperature vs Time')
        self.ax_temp.legend()
        self.ax_temp.grid(True)

        # Current plot
        self.ax_current.clear()
        self.ax_current.plot(self.time_history, self.current_history, 'g-', linewidth=2)
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Current vs Time')
        self.ax_current.grid(True)

        # Power plot
        self.ax_power.clear()
        self.ax_power.plot(self.time_history, self.power_history, 'm-', linewidth=2)
        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (kW)')
        self.ax_power.set_title('Power vs Time')
        self.ax_power.grid(True)

        self.fig_dynamic.tight_layout()
        self.canvas_dynamic.draw()

    def update_results_visualization(self):
        """Update comprehensive results visualization"""
        if len(self.time_history) == 0:
            messagebox.showinfo("No Data", "Run a simulation first to generate results.")
            return

        try:
            # Temperature evolution
            self.ax_results_temp.clear()
            self.ax_results_temp.plot(self.time_history, self.temp_wire_history, 'r-', label='Wire', linewidth=2)
            self.ax_results_temp.plot(self.time_history, self.temp_charge_history, 'b-', label='Charge', linewidth=2)
            self.ax_results_temp.set_xlabel('Time (s)')
            self.ax_results_temp.set_ylabel('Temperature (°C)')
            self.ax_results_temp.set_title('Temperature Evolution')
            self.ax_results_temp.legend()
            self.ax_results_temp.grid(True)

            # Current evolution
            self.ax_results_current.clear()
            self.ax_results_current.plot(self.time_history, self.current_history, 'g-', linewidth=2)
            self.ax_results_current.set_xlabel('Time (s)')
            self.ax_results_current.set_ylabel('Current (A)')
            self.ax_results_current.set_title('Current Evolution')
            self.ax_results_current.grid(True)

            # Power consumption
            self.ax_results_power.clear()
            self.ax_results_power.plot(self.time_history, self.power_history, 'm-', linewidth=2)
            self.ax_results_power.set_xlabel('Time (s)')
            self.ax_results_power.set_ylabel('Power (kW)')
            self.ax_results_power.set_title('Power Consumption')
            self.ax_results_power.grid(True)

            # Phase space
            self.ax_phase.clear()
            self.ax_phase.plot(self.temp_wire_history, self.current_history, 'b-', linewidth=2)
            self.ax_phase.scatter(self.temp_wire_history[0], self.current_history[0],
                                 c='g', s=100, marker='o', label='Start', zorder=5)
            self.ax_phase.scatter(self.temp_wire_history[-1], self.current_history[-1],
                                 c='r', s=100, marker='s', label='End', zorder=5)
            self.ax_phase.set_xlabel('Wire Temperature (°C)')
            self.ax_phase.set_ylabel('Current (A)')
            self.ax_phase.set_title('Phase Space: Temperature vs Current')
            self.ax_phase.legend()
            self.ax_phase.grid(True)

            # Heat transfer analysis
            self.ax_heat.clear()

            # Calculate heat transfer rates
            params = {
                'efficiency': 0.6,
                'emissivity': 0.9,
                'surface_area': self.sim_params['surface_area'].get(),
            }

            sigma = stefan_boltzmann_constant
            heat_rad = []

            for i in range(len(self.time_history)):
                T_w_K = self.temp_wire_history[i] + 273.15
                T_c_K = self.temp_charge_history[i] + 273.15
                Q_rad = (params['efficiency'] * params['emissivity'] * sigma *
                        params['surface_area'] * (T_w_K**4 - T_c_K**4)) / 1000  # kW
                heat_rad.append(Q_rad)

            self.ax_heat.plot(self.time_history, heat_rad, 'r-', label='Radiated Heat', linewidth=2)
            self.ax_heat.plot(self.time_history, self.power_history, 'b-', label='Input Power', linewidth=2)
            self.ax_heat.set_xlabel('Time (s)')
            self.ax_heat.set_ylabel('Heat Transfer Rate (kW)')
            self.ax_heat.set_title('Heat Transfer Analysis')
            self.ax_heat.legend()
            self.ax_heat.grid(True)

            # Efficiency analysis
            self.ax_efficiency.clear()
            efficiency = [(heat_rad[i] / self.power_history[i] * 100) if self.power_history[i] > 0 else 0
                         for i in range(len(self.time_history))]

            self.ax_efficiency.plot(self.time_history, efficiency, 'c-', linewidth=2)
            self.ax_efficiency.set_xlabel('Time (s)')
            self.ax_efficiency.set_ylabel('Efficiency (%)')
            self.ax_efficiency.set_title('System Efficiency')
            self.ax_efficiency.grid(True)
            self.ax_efficiency.axhline(y=60, color='r', linestyle='--', label='Design Efficiency')
            self.ax_efficiency.legend()

            self.fig_results.tight_layout()
            self.canvas_results.draw()

        except Exception as e:
            messagebox.showerror("Visualization Error", f"Error updating visualization:\n{str(e)}")

    def export_data(self):
        """Export simulation data to CSV"""
        if len(self.time_history) == 0:
            messagebox.showinfo("No Data", "Run a simulation first to generate data.")
            return

        try:
            import csv
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Time (s)', 'Wire Temperature (°C)', 'Charge Temperature (°C)',
                                   'Current (A)', 'Power (kW)'])

                    for i in range(len(self.time_history)):
                        writer.writerow([
                            self.time_history[i],
                            self.temp_wire_history[i],
                            self.temp_charge_history[i],
                            self.current_history[i],
                            self.power_history[i]
                        ])

                messagebox.showinfo("Export Successful", f"Data exported to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data:\n{str(e)}")

    def on_window_resize(self, event):
        """Handle window resize events for auto-scaling"""
        # Only process resize events from the root window
        if event.widget == self.root:
            try:
                # Redraw canvases to fit new window size
                self.canvas_dynamic.draw_idle()
                self.canvas_results.draw_idle()
            except:
                pass


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ResistanceOvenGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

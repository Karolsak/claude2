"""
Advanced Power Generation Cost and Dynamic Simulation System
A comprehensive electrical engineering tool for power station analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
from scipy.integrate import odeint, solve_ivp
from datetime import datetime


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


class PowerStationDynamicSimulator:
    """Module for dynamic simulation of power station using ODE solvers"""

    def __init__(self):
        self.reset_parameters()
        self.simulation_running = False

    def reset_parameters(self):
        """Reset simulation parameters"""
        # Generator parameters
        self.rated_power = 75.0  # MW
        self.inertia_constant = 5.0  # MJ/MVA
        self.damping_coefficient = 2.0
        self.mechanical_power = 50.0  # MW
        self.electrical_power = 45.0  # MW

        # Control system parameters
        self.governor_gain = 20.0
        self.governor_time_constant = 0.5
        self.exciter_gain = 50.0
        self.exciter_time_constant = 0.2

        # Network parameters
        self.frequency_nominal = 50.0  # Hz
        self.voltage_nominal = 11.0  # kV

        # Simulation parameters
        self.time_span = 10.0  # seconds
        self.time_step = 0.01

    def generator_swing_equation(self, t, y, params):
        """
        Swing equation for generator dynamics
        State variables: [delta, omega, Pm_gov, Vf_exc]
        delta: rotor angle (rad)
        omega: angular frequency deviation (rad/s)
        Pm_gov: mechanical power from governor (MW)
        Vf_exc: field voltage from exciter (pu)
        """
        delta, omega, Pm_gov, Vf_exc = y

        # Extract parameters
        H = params['H']  # Inertia constant
        D = params['D']  # Damping coefficient
        Pm_ref = params['Pm_ref']  # Reference mechanical power
        Pe = params['Pe']  # Electrical power
        Kg = params['Kg']  # Governor gain
        Tg = params['Tg']  # Governor time constant
        Ke = params['Ke']  # Exciter gain
        Te = params['Te']  # Exciter time constant
        omega_s = params['omega_s']  # Synchronous speed

        # Swing equation: d(delta)/dt = omega
        d_delta = omega

        # d(omega)/dt = (Pm - Pe - D*omega) / (2*H)
        d_omega = (Pm_gov - Pe - D * omega) / (2 * H)

        # Governor dynamics: dPm/dt = (Kg*(omega_ref - omega) + Pm_ref - Pm) / Tg
        omega_ref = 0  # Reference is zero deviation
        d_Pm_gov = (Kg * (omega_ref - omega) + Pm_ref - Pm_gov) / Tg

        # Exciter dynamics: dVf/dt = (Ke*(Vref - V) - Vf) / Te
        V_measured = 1.0 + 0.1 * np.sin(omega * t)  # Simplified voltage measurement
        V_ref = 1.0
        d_Vf_exc = (Ke * (V_ref - V_measured) - Vf_exc) / Te

        return [d_delta, d_omega, d_Pm_gov, d_Vf_exc]

    def euler_method(self, f, t_span, y0, params, dt=0.01):
        """Euler method for ODE solution"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        n = len(t)
        y = np.zeros((n, len(y0)))
        y[0] = y0

        for i in range(1, n):
            dydt = f(t[i-1], y[i-1], params)
            y[i] = y[i-1] + dt * np.array(dydt)

        return t, y

    def rk45_solve(self, f, t_span, y0, params):
        """RK45 method using scipy"""
        sol = solve_ivp(
            lambda t, y: f(t, y, params),
            t_span,
            y0,
            method='RK45',
            dense_output=True,
            max_step=0.01
        )

        t = np.linspace(t_span[0], t_span[1], 1000)
        y = sol.sol(t).T

        return t, y

    def simulate(self, method='RK45'):
        """Run simulation with selected method"""
        # Initial conditions
        delta_0 = 0.0  # Initial rotor angle
        omega_0 = 0.0  # Initial frequency deviation
        Pm_gov_0 = self.mechanical_power
        Vf_exc_0 = 1.0

        y0 = [delta_0, omega_0, Pm_gov_0, Vf_exc_0]

        # Parameters
        params = {
            'H': self.inertia_constant,
            'D': self.damping_coefficient,
            'Pm_ref': self.mechanical_power,
            'Pe': self.electrical_power,
            'Kg': self.governor_gain,
            'Tg': self.governor_time_constant,
            'Ke': self.exciter_gain,
            'Te': self.exciter_time_constant,
            'omega_s': 2 * np.pi * self.frequency_nominal
        }

        t_span = (0, self.time_span)

        if method == 'Euler':
            t, y = self.euler_method(
                self.generator_swing_equation,
                t_span,
                y0,
                params,
                dt=self.time_step
            )
        else:  # RK45
            t, y = self.rk45_solve(
                self.generator_swing_equation,
                t_span,
                y0,
                params
            )

        # Extract results
        results = {
            't': t,
            'delta': y[:, 0],
            'omega': y[:, 1],
            'frequency': self.frequency_nominal + y[:, 1] / (2 * np.pi),
            'Pm': y[:, 2],
            'Vf': y[:, 3]
        }

        return results


class AdvancedPowerGenerationGUI:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Power Generation Analysis & Simulation System")
        self.root.geometry("1400x900")

        # Initialize calculators
        self.cost_calculator = PowerGenerationCostCalculator()
        self.simulator = PowerStationDynamicSimulator()

        # Simulation control
        self.is_simulating = False

        # Setup GUI
        self.setup_menu()
        self.setup_main_interface()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def setup_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset All", command=self.reset_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Cost Calculator", command=lambda: self.notebook.select(0))
        tools_menu.add_command(label="Dynamic Simulator", command=lambda: self.notebook.select(1))

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_main_interface(self):
        """Setup main tabbed interface"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Cost Calculator
        self.cost_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cost_tab, text="Power Generation Cost Calculator")
        self.setup_cost_calculator_tab()

        # Tab 2: Dynamic Simulator
        self.simulator_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.simulator_tab, text="Dynamic Power Station Simulator")
        self.setup_simulator_tab()

        # Tab 3: Results Comparison
        self.comparison_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_tab, text="Comprehensive Analysis")
        self.setup_comparison_tab()

    def setup_cost_calculator_tab(self):
        """Setup cost calculator interface"""
        # Left panel - Input parameters
        left_frame = ttk.LabelFrame(self.cost_tab, text="Input Parameters", padding=10)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Configure grid weights
        self.cost_tab.columnconfigure(0, weight=1)
        self.cost_tab.columnconfigure(1, weight=2)
        self.cost_tab.rowconfigure(0, weight=1)

        row = 0

        # Maximum Demand
        ttk.Label(left_frame, text="Maximum Demand (MW):").grid(row=row, column=0, sticky='w', pady=5)
        self.md_var = tk.DoubleVar(value=75.0)
        self.md_scale = ttk.Scale(left_frame, from_=10, to=500, variable=self.md_var, orient='horizontal')
        self.md_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.md_label = ttk.Label(left_frame, text="75.0")
        self.md_label.grid(row=row, column=2, sticky='w')
        self.md_var.trace_add('write', lambda *args: self.update_label(self.md_var, self.md_label))
        row += 1

        # Load Factor
        ttk.Label(left_frame, text="Load Factor:").grid(row=row, column=0, sticky='w', pady=5)
        self.lf_var = tk.DoubleVar(value=0.40)
        self.lf_scale = ttk.Scale(left_frame, from_=0.1, to=1.0, variable=self.lf_var, orient='horizontal')
        self.lf_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.lf_label = ttk.Label(left_frame, text="0.40")
        self.lf_label.grid(row=row, column=2, sticky='w')
        self.lf_var.trace_add('write', lambda *args: self.update_label(self.lf_var, self.lf_label))
        row += 1

        # Fixed Cost per kW
        ttk.Label(left_frame, text="Fixed Cost (Rs/kW/annum):").grid(row=row, column=0, sticky='w', pady=5)
        self.fc_var = tk.DoubleVar(value=60.0)
        self.fc_scale = ttk.Scale(left_frame, from_=10, to=200, variable=self.fc_var, orient='horizontal')
        self.fc_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.fc_label = ttk.Label(left_frame, text="60.0")
        self.fc_label.grid(row=row, column=2, sticky='w')
        self.fc_var.trace_add('write', lambda *args: self.update_label(self.fc_var, self.fc_label))
        row += 1

        # Variable Cost per kWh
        ttk.Label(left_frame, text="Variable Cost (Rs/kWh):").grid(row=row, column=0, sticky='w', pady=5)
        self.vc_var = tk.DoubleVar(value=0.01)
        self.vc_scale = ttk.Scale(left_frame, from_=0.001, to=0.1, variable=self.vc_var, orient='horizontal')
        self.vc_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.vc_label = ttk.Label(left_frame, text="0.01")
        self.vc_label.grid(row=row, column=2, sticky='w')
        self.vc_var.trace_add('write', lambda *args: self.update_label(self.vc_var, self.vc_label, '0.3f'))
        row += 1

        # Transmission Capital Cost
        ttk.Label(left_frame, text="Trans. Capital Cost (Rs M):").grid(row=row, column=0, sticky='w', pady=5)
        self.tc_var = tk.DoubleVar(value=1.5)
        self.tc_scale = ttk.Scale(left_frame, from_=0.1, to=10, variable=self.tc_var, orient='horizontal')
        self.tc_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.tc_label = ttk.Label(left_frame, text="1.5")
        self.tc_label.grid(row=row, column=2, sticky='w')
        self.tc_var.trace_add('write', lambda *args: self.update_label(self.tc_var, self.tc_label))
        row += 1

        # Diversity Factor - Transmission
        ttk.Label(left_frame, text="Diversity Factor (Trans):").grid(row=row, column=0, sticky='w', pady=5)
        self.df1_var = tk.DoubleVar(value=1.2)
        self.df1_scale = ttk.Scale(left_frame, from_=1.0, to=2.0, variable=self.df1_var, orient='horizontal')
        self.df1_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.df1_label = ttk.Label(left_frame, text="1.2")
        self.df1_label.grid(row=row, column=2, sticky='w')
        self.df1_var.trace_add('write', lambda *args: self.update_label(self.df1_var, self.df1_label))
        row += 1

        # Diversity Factor - Distribution
        ttk.Label(left_frame, text="Diversity Factor (Dist):").grid(row=row, column=0, sticky='w', pady=5)
        self.df2_var = tk.DoubleVar(value=1.25)
        self.df2_scale = ttk.Scale(left_frame, from_=1.0, to=2.0, variable=self.df2_var, orient='horizontal')
        self.df2_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.df2_label = ttk.Label(left_frame, text="1.25")
        self.df2_label.grid(row=row, column=2, sticky='w')
        self.df2_var.trace_add('write', lambda *args: self.update_label(self.df2_var, self.df2_label))
        row += 1

        # Transmission Efficiency
        ttk.Label(left_frame, text="Transmission Efficiency:").grid(row=row, column=0, sticky='w', pady=5)
        self.te_var = tk.DoubleVar(value=0.90)
        self.te_scale = ttk.Scale(left_frame, from_=0.5, to=1.0, variable=self.te_var, orient='horizontal')
        self.te_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.te_label = ttk.Label(left_frame, text="0.90")
        self.te_label.grid(row=row, column=2, sticky='w')
        self.te_var.trace_add('write', lambda *args: self.update_label(self.te_var, self.te_label))
        row += 1

        # Distribution Efficiency
        ttk.Label(left_frame, text="Distribution Efficiency:").grid(row=row, column=0, sticky='w', pady=5)
        self.de_var = tk.DoubleVar(value=0.85)
        self.de_scale = ttk.Scale(left_frame, from_=0.5, to=1.0, variable=self.de_var, orient='horizontal')
        self.de_scale.grid(row=row, column=1, sticky='ew', padx=5)
        self.de_label = ttk.Label(left_frame, text="0.85")
        self.de_label.grid(row=row, column=2, sticky='w')
        self.de_var.trace_add('write', lambda *args: self.update_label(self.de_var, self.de_label))
        row += 1

        # Calculate button
        ttk.Button(left_frame, text="Calculate Costs", command=self.calculate_costs).grid(
            row=row, column=0, columnspan=3, pady=20, sticky='ew'
        )

        # Configure left frame columns
        left_frame.columnconfigure(1, weight=1)

        # Right panel - Results
        right_frame = ttk.LabelFrame(self.cost_tab, text="Results", padding=10)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # Results text area
        self.cost_results_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=60,
            height=30,
            font=('Courier', 10)
        )
        self.cost_results_text.pack(fill='both', expand=True)

    def setup_simulator_tab(self):
        """Setup dynamic simulator interface"""
        # Top frame - Control parameters
        top_frame = ttk.LabelFrame(self.simulator_tab, text="Simulation Parameters", padding=10)
        top_frame.pack(fill='x', padx=5, pady=5)

        # Create two columns for parameters
        left_params = ttk.Frame(top_frame)
        left_params.pack(side='left', fill='both', expand=True)

        right_params = ttk.Frame(top_frame)
        right_params.pack(side='left', fill='both', expand=True)

        # Left column parameters
        row = 0
        ttk.Label(left_params, text="Mechanical Power (MW):").grid(row=row, column=0, sticky='w', pady=3)
        self.mech_power_var = tk.DoubleVar(value=50.0)
        ttk.Scale(left_params, from_=10, to=100, variable=self.mech_power_var, orient='horizontal').grid(
            row=row, column=1, sticky='ew', padx=5
        )
        self.mech_power_label = ttk.Label(left_params, text="50.0")
        self.mech_power_label.grid(row=row, column=2)
        self.mech_power_var.trace_add('write', lambda *args: self.update_label(self.mech_power_var, self.mech_power_label))
        row += 1

        ttk.Label(left_params, text="Electrical Power (MW):").grid(row=row, column=0, sticky='w', pady=3)
        self.elec_power_var = tk.DoubleVar(value=45.0)
        ttk.Scale(left_params, from_=10, to=100, variable=self.elec_power_var, orient='horizontal').grid(
            row=row, column=1, sticky='ew', padx=5
        )
        self.elec_power_label = ttk.Label(left_params, text="45.0")
        self.elec_power_label.grid(row=row, column=2)
        self.elec_power_var.trace_add('write', lambda *args: self.update_label(self.elec_power_var, self.elec_power_label))
        row += 1

        ttk.Label(left_params, text="Inertia Constant (H):").grid(row=row, column=0, sticky='w', pady=3)
        self.inertia_var = tk.DoubleVar(value=5.0)
        ttk.Scale(left_params, from_=1, to=10, variable=self.inertia_var, orient='horizontal').grid(
            row=row, column=1, sticky='ew', padx=5
        )
        self.inertia_label = ttk.Label(left_params, text="5.0")
        self.inertia_label.grid(row=row, column=2)
        self.inertia_var.trace_add('write', lambda *args: self.update_label(self.inertia_var, self.inertia_label))
        row += 1

        ttk.Label(left_params, text="Damping Coefficient:").grid(row=row, column=0, sticky='w', pady=3)
        self.damping_var = tk.DoubleVar(value=2.0)
        ttk.Scale(left_params, from_=0.1, to=10, variable=self.damping_var, orient='horizontal').grid(
            row=row, column=1, sticky='ew', padx=5
        )
        self.damping_label = ttk.Label(left_params, text="2.0")
        self.damping_label.grid(row=row, column=2)
        self.damping_var.trace_add('write', lambda *args: self.update_label(self.damping_var, self.damping_label))

        # Right column parameters
        row = 0
        ttk.Label(right_params, text="Governor Gain:").grid(row=row, column=0, sticky='w', pady=3)
        self.gov_gain_var = tk.DoubleVar(value=20.0)
        ttk.Scale(right_params, from_=1, to=50, variable=self.gov_gain_var, orient='horizontal').grid(
            row=row, column=1, sticky='ew', padx=5
        )
        self.gov_gain_label = ttk.Label(right_params, text="20.0")
        self.gov_gain_label.grid(row=row, column=2)
        self.gov_gain_var.trace_add('write', lambda *args: self.update_label(self.gov_gain_var, self.gov_gain_label))
        row += 1

        ttk.Label(right_params, text="Governor Time Constant:").grid(row=row, column=0, sticky='w', pady=3)
        self.gov_time_var = tk.DoubleVar(value=0.5)
        ttk.Scale(right_params, from_=0.1, to=2, variable=self.gov_time_var, orient='horizontal').grid(
            row=row, column=1, sticky='ew', padx=5
        )
        self.gov_time_label = ttk.Label(right_params, text="0.5")
        self.gov_time_label.grid(row=row, column=2)
        self.gov_time_var.trace_add('write', lambda *args: self.update_label(self.gov_time_var, self.gov_time_label))
        row += 1

        ttk.Label(right_params, text="Simulation Time (s):").grid(row=row, column=0, sticky='w', pady=3)
        self.sim_time_var = tk.DoubleVar(value=10.0)
        ttk.Scale(right_params, from_=1, to=30, variable=self.sim_time_var, orient='horizontal').grid(
            row=row, column=1, sticky='ew', padx=5
        )
        self.sim_time_label = ttk.Label(right_params, text="10.0")
        self.sim_time_label.grid(row=row, column=2)
        self.sim_time_var.trace_add('write', lambda *args: self.update_label(self.sim_time_var, self.sim_time_label))
        row += 1

        ttk.Label(right_params, text="ODE Solver:").grid(row=row, column=0, sticky='w', pady=3)
        self.solver_var = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(right_params, textvariable=self.solver_var, values=["RK45", "Euler"], state='readonly')
        solver_combo.grid(row=row, column=1, sticky='ew', padx=5)

        # Configure column weights
        left_params.columnconfigure(1, weight=1)
        right_params.columnconfigure(1, weight=1)

        # Control buttons
        control_frame = ttk.Frame(self.simulator_tab)
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="Start Simulation", command=self.start_simulation).pack(
            side='left', padx=5
        )
        ttk.Button(control_frame, text="Stop", command=self.stop_simulation).pack(
            side='left', padx=5
        )
        ttk.Button(control_frame, text="Reset", command=self.reset_simulation).pack(
            side='left', padx=5
        )

        # Status label
        self.sim_status_var = tk.StringVar(value="Ready")
        ttk.Label(control_frame, textvariable=self.sim_status_var, foreground='blue').pack(
            side='left', padx=20
        )

        # Plots frame
        plots_frame = ttk.Frame(self.simulator_tab)
        plots_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create matplotlib figure
        self.sim_fig = Figure(figsize=(12, 8), dpi=100)
        self.sim_canvas = FigureCanvasTkAgg(self.sim_fig, master=plots_frame)
        self.sim_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Create subplots
        self.ax1 = self.sim_fig.add_subplot(2, 2, 1)
        self.ax2 = self.sim_fig.add_subplot(2, 2, 2)
        self.ax3 = self.sim_fig.add_subplot(2, 2, 3)
        self.ax4 = self.sim_fig.add_subplot(2, 2, 4)

        self.sim_fig.tight_layout()

    def setup_comparison_tab(self):
        """Setup comprehensive analysis tab"""
        # Create frame
        main_frame = ttk.Frame(self.comparison_tab)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Comprehensive Power System Analysis Dashboard",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=10)

        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Summary", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.comprehensive_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Courier', 10)
        )
        self.comprehensive_text.pack(fill='both', expand=True)

        # Generate report button
        ttk.Button(
            main_frame,
            text="Generate Comprehensive Report",
            command=self.generate_comprehensive_report
        ).pack(pady=10)

    def update_label(self, var, label, fmt='1f'):
        """Update label with current slider value"""
        label.config(text=f"{var.get():.{fmt[0]}f}")

    def calculate_costs(self):
        """Calculate power generation costs"""
        # Update calculator parameters
        self.cost_calculator.max_demand_mw = self.md_var.get()
        self.cost_calculator.load_factor = self.lf_var.get()
        self.cost_calculator.fixed_cost_per_kw = self.fc_var.get()
        self.cost_calculator.variable_cost_per_kwh = self.vc_var.get()
        self.cost_calculator.transmission_capital_cost = self.tc_var.get() * 1000000
        self.cost_calculator.diversity_factor_transmission = self.df1_var.get()
        self.cost_calculator.diversity_factor_distribution = self.df2_var.get()
        self.cost_calculator.transmission_efficiency = self.te_var.get()
        self.cost_calculator.distribution_efficiency = self.de_var.get()

        # Calculate
        results = self.cost_calculator.calculate_costs()

        # Display results
        output = "=" * 70 + "\n"
        output += "POWER GENERATION COST ANALYSIS RESULTS\n"
        output += "=" * 70 + "\n\n"

        output += "INPUT PARAMETERS:\n"
        output += "-" * 70 + "\n"
        output += f"Maximum Demand: {results['max_demand_kw']/1000:.2f} MW ({results['max_demand_kw']:.2f} kW)\n"
        output += f"Load Factor: {self.lf_var.get():.2%}\n"
        output += f"Fixed Cost: Rs. {self.fc_var.get():.2f} per kW per annum\n"
        output += f"Variable Cost: Rs. {self.vc_var.get():.4f} per kWh\n"
        output += f"Transmission Capital Cost: Rs. {self.tc_var.get():.2f} Million\n"
        output += f"Diversity Factor (Transmission): {self.df1_var.get():.2f}\n"
        output += f"Diversity Factor (Distribution): {self.df2_var.get():.2f}\n"
        output += f"Transmission Efficiency: {self.te_var.get():.2%}\n"
        output += f"Distribution Efficiency: {self.de_var.get():.2%}\n\n"

        output += "ENERGY CALCULATIONS:\n"
        output += "-" * 70 + "\n"
        output += f"Annual Energy Generated: {results['annual_energy_generated']/1e6:.2f} Million kWh\n"
        output += f"Energy at Substation: {results['energy_at_substation']/1e6:.2f} Million kWh\n"
        output += f"Energy at Consumer's Premises: {results['energy_at_consumer']/1e6:.2f} Million kWh\n\n"

        output += "COST BREAKDOWN:\n"
        output += "-" * 70 + "\n"
        output += f"Fixed Generating Cost: Rs. {results['fixed_generating_cost']:,.2f}\n"
        output += f"Variable Generating Cost: Rs. {results['variable_generating_cost']:,.2f}\n"
        output += f"Total Generating Cost: Rs. {results['total_generating_cost']:,.2f}\n"
        output += f"Transmission Capital Cost: Rs. {results['transmission_cost']:,.2f}\n"
        output += f"TOTAL COST: Rs. {results['total_cost']:,.2f}\n\n"

        output += "RESULTS AT SUBSTATION:\n"
        output += "=" * 70 + "\n"
        output += f"Demand at Substation: {results['demand_at_substation']/1000:.2f} MW ({results['demand_at_substation']:.2f} kW)\n"
        output += f"Cost per kW Demand: Rs. {results['cost_per_kw_substation']:.4f} /kW\n"
        output += f"Cost per kWh Supplied: Rs. {results['cost_per_kwh_substation']:.6f} /kWh\n\n"

        output += "RESULTS AT CONSUMER'S PREMISES:\n"
        output += "=" * 70 + "\n"
        output += f"Demand at Consumer's: {results['demand_at_consumer']/1000:.2f} MW ({results['demand_at_consumer']:.2f} kW)\n"
        output += f"Cost per kW Demand: Rs. {results['cost_per_kw_consumer']:.4f} /kW\n"
        output += f"Cost per kWh Supplied: Rs. {results['cost_per_kwh_consumer']:.6f} /kWh\n\n"

        output += "=" * 70 + "\n"
        output += f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += "=" * 70 + "\n"

        self.cost_results_text.delete('1.0', tk.END)
        self.cost_results_text.insert('1.0', output)

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.is_simulating:
            messagebox.showwarning("Warning", "Simulation already running!")
            return

        self.is_simulating = True
        self.sim_status_var.set("Simulating...")

        # Update simulator parameters
        self.simulator.mechanical_power = self.mech_power_var.get()
        self.simulator.electrical_power = self.elec_power_var.get()
        self.simulator.inertia_constant = self.inertia_var.get()
        self.simulator.damping_coefficient = self.damping_var.get()
        self.simulator.governor_gain = self.gov_gain_var.get()
        self.simulator.governor_time_constant = self.gov_time_var.get()
        self.simulator.time_span = self.sim_time_var.get()

        # Run simulation
        method = self.solver_var.get()
        results = self.simulator.simulate(method=method)

        # Plot results
        self.plot_simulation_results(results)

        self.is_simulating = False
        self.sim_status_var.set(f"Simulation Complete ({method} method)")

    def plot_simulation_results(self, results):
        """Plot simulation results"""
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        t = results['t']

        # Plot 1: Rotor Angle
        self.ax1.plot(t, np.degrees(results['delta']), 'b-', linewidth=2)
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Rotor Angle (degrees)')
        self.ax1.set_title('Rotor Angle vs Time')
        self.ax1.grid(True, alpha=0.3)

        # Plot 2: Frequency
        self.ax2.plot(t, results['frequency'], 'r-', linewidth=2)
        self.ax2.axhline(y=50, color='k', linestyle='--', alpha=0.5, label='Nominal')
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Frequency (Hz)')
        self.ax2.set_title('System Frequency vs Time')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)

        # Plot 3: Mechanical Power
        self.ax3.plot(t, results['Pm'], 'g-', linewidth=2)
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Mechanical Power (MW)')
        self.ax3.set_title('Governor Response (Mechanical Power)')
        self.ax3.grid(True, alpha=0.3)

        # Plot 4: Field Voltage
        self.ax4.plot(t, results['Vf'], 'm-', linewidth=2)
        self.ax4.set_xlabel('Time (s)')
        self.ax4.set_ylabel('Field Voltage (pu)')
        self.ax4.set_title('Exciter Response (Field Voltage)')
        self.ax4.grid(True, alpha=0.3)

        self.sim_fig.tight_layout()
        self.sim_canvas.draw()

    def stop_simulation(self):
        """Stop simulation"""
        self.is_simulating = False
        self.sim_status_var.set("Stopped")

    def reset_simulation(self):
        """Reset simulation"""
        self.is_simulating = False
        self.simulator.reset_parameters()

        # Reset GUI controls
        self.mech_power_var.set(50.0)
        self.elec_power_var.set(45.0)
        self.inertia_var.set(5.0)
        self.damping_var.set(2.0)
        self.gov_gain_var.set(20.0)
        self.gov_time_var.set(0.5)
        self.sim_time_var.set(10.0)
        self.solver_var.set("RK45")

        # Clear plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.sim_canvas.draw()

        self.sim_status_var.set("Reset Complete")

    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        # Calculate costs first
        self.cost_calculator.max_demand_mw = self.md_var.get()
        self.cost_calculator.load_factor = self.lf_var.get()
        cost_results = self.cost_calculator.calculate_costs()

        # Generate report
        report = "=" * 80 + "\n"
        report += "COMPREHENSIVE POWER SYSTEM ANALYSIS REPORT\n"
        report += "=" * 80 + "\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "SECTION 1: ECONOMIC ANALYSIS\n"
        report += "-" * 80 + "\n"
        report += f"Maximum Demand: {cost_results['max_demand_kw']/1000:.2f} MW\n"
        report += f"Load Factor: {self.lf_var.get():.2%}\n"
        report += f"Annual Energy: {cost_results['annual_energy_generated']/1e6:.2f} GWh\n"
        report += f"Total Annual Cost: Rs. {cost_results['total_cost']:,.2f}\n"
        report += f"\nAt Substation:\n"
        report += f"  - Cost per kW: Rs. {cost_results['cost_per_kw_substation']:.2f}\n"
        report += f"  - Cost per kWh: Rs. {cost_results['cost_per_kwh_substation']:.4f}\n"
        report += f"\nAt Consumer's Premises:\n"
        report += f"  - Cost per kW: Rs. {cost_results['cost_per_kw_consumer']:.2f}\n"
        report += f"  - Cost per kWh: Rs. {cost_results['cost_per_kwh_consumer']:.4f}\n\n"

        report += "SECTION 2: SYSTEM EFFICIENCY\n"
        report += "-" * 80 + "\n"
        report += f"Transmission Efficiency: {self.te_var.get():.2%}\n"
        report += f"Distribution Efficiency: {self.de_var.get():.2%}\n"
        report += f"Overall System Efficiency: {self.te_var.get() * self.de_var.get():.2%}\n"
        report += f"Energy Losses: {cost_results['annual_energy_generated'] - cost_results['energy_at_consumer']:.2f} kWh/year\n\n"

        report += "SECTION 3: TECHNICAL PARAMETERS\n"
        report += "-" * 80 + "\n"
        report += f"Generator Inertia Constant: {self.inertia_var.get():.2f} MJ/MVA\n"
        report += f"Damping Coefficient: {self.damping_var.get():.2f}\n"
        report += f"Governor Gain: {self.gov_gain_var.get():.2f}\n"
        report += f"Governor Time Constant: {self.gov_time_var.get():.2f} s\n\n"

        report += "SECTION 4: RECOMMENDATIONS\n"
        report += "-" * 80 + "\n"

        # Generate recommendations based on parameters
        if self.lf_var.get() < 0.5:
            report += "• Low load factor detected. Consider load management strategies.\n"

        if self.te_var.get() < 0.85:
            report += "• Transmission efficiency is below optimal. Consider upgrading infrastructure.\n"

        if self.de_var.get() < 0.80:
            report += "• Distribution losses are high. Review distribution network.\n"

        overall_eff = self.te_var.get() * self.de_var.get()
        if overall_eff < 0.75:
            report += "• Overall system efficiency is low. Comprehensive review recommended.\n"

        report += "\n" + "=" * 80 + "\n"
        report += "END OF REPORT\n"
        report += "=" * 80 + "\n"

        self.comprehensive_text.delete('1.0', tk.END)
        self.comprehensive_text.insert('1.0', report)

    def reset_all(self):
        """Reset all parameters"""
        # Reset cost calculator
        self.md_var.set(75.0)
        self.lf_var.set(0.40)
        self.fc_var.set(60.0)
        self.vc_var.set(0.01)
        self.tc_var.set(1.5)
        self.df1_var.set(1.2)
        self.df2_var.set(1.25)
        self.te_var.set(0.90)
        self.de_var.set(0.85)

        # Reset simulator
        self.reset_simulation()

        messagebox.showinfo("Reset", "All parameters reset to default values")

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Power Generation Analysis & Simulation System
Version 2.0

Features:
• Power Generation Cost Calculator
• Dynamic Power Station Simulator
• ODE Solvers (RK45, Euler)
• Real-time Visualization
• Comprehensive Analysis Tools

Developed for Electrical Engineering Applications
        """
        messagebox.showinfo("About", about_text)

    def on_window_resize(self, event):
        """Handle window resize event for auto-scaling"""
        if hasattr(self, 'sim_fig'):
            self.sim_fig.tight_layout()
            if hasattr(self, 'sim_canvas'):
                self.sim_canvas.draw_idle()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = AdvancedPowerGenerationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

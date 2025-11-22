"""
Advanced Thermal Power Station Analysis Tool
============================================
This application provides comprehensive analysis of thermal power station economics
and dynamic behavior using differential equations and real-time simulation.

Features:
- Cost calculation and analysis (a, b, c constants determination)
- Dynamic load simulation with ODE solvers (RK45, Euler)
- Interactive controls and parameter adjustment
- Real-time visualization with autoscaling
- Practical electrical engineering applications
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
import math

class ThermalStationAnalyzer:
    """Core calculation engine for thermal station analysis"""

    def __init__(self):
        # Default parameters for the example problem
        self.installed_capacity = 60000  # kW (60 MW)
        self.load_factor = 0.40  # 40%
        self.capital_cost = 500000  # Rs. 5 × 10^5
        self.annual_fuel_cost = 90000  # Rs.
        self.interest_depreciation_rate = 0.10  # 10%
        self.annual_org_cost = 50000  # Rs.

        # Calculated constants
        self.a = 0  # Fixed costs
        self.b = 0  # Cost per kW
        self.c = 0  # Cost per kWh
        self.energy_per_annum = 0  # kWh

        self.calculate_constants()

    def calculate_constants(self):
        """Calculate the constants a, b, and c for the cost formula"""
        # Energy produced per annum = Capacity × Load Factor × 8760 hours
        self.energy_per_annum = self.installed_capacity * self.load_factor * 8760

        # a: Fixed annual costs (organization, site interest, etc.)
        self.a = self.annual_org_cost

        # b: Cost per kW of installed capacity (interest & depreciation)
        annual_capital_cost = self.interest_depreciation_rate * self.capital_cost
        self.b = annual_capital_cost / self.installed_capacity

        # c: Cost per kWh of energy produced (fuel, oil, wages, etc.)
        self.c = self.annual_fuel_cost / self.energy_per_annum

        return self.a, self.b, self.c

    def calculate_total_cost(self):
        """Calculate total annual working cost"""
        return self.a + (self.b * self.installed_capacity) + (self.c * self.energy_per_annum)

    def get_cost_breakdown(self):
        """Get detailed cost breakdown"""
        fixed_cost = self.a
        capacity_cost = self.b * self.installed_capacity
        energy_cost = self.c * self.energy_per_annum
        total_cost = fixed_cost + capacity_cost + energy_cost

        return {
            'fixed': fixed_cost,
            'capacity': capacity_cost,
            'energy': energy_cost,
            'total': total_cost
        }


class PowerStationDynamics:
    """Dynamic simulation of power station behavior using differential equations"""

    def __init__(self):
        # System parameters
        self.inertia_constant = 5.0  # Generator inertia (seconds)
        self.damping_coefficient = 0.5  # Damping factor
        self.droop_constant = 0.05  # Speed droop (5%)
        self.time_constant_turbine = 1.0  # Turbine time constant
        self.time_constant_boiler = 10.0  # Boiler time constant

        # State variables
        self.frequency = 50.0  # Hz
        self.power_output = 0.5  # per unit
        self.turbine_power = 0.5  # per unit
        self.boiler_steam = 0.5  # per unit

        # Setpoints
        self.power_reference = 0.5
        self.load_demand = 0.5

    def system_dynamics(self, t, y, u_turbine, load):
        """
        Differential equations describing power station dynamics

        State vector y = [delta_f, P_gen, P_turbine, P_boiler]
        - delta_f: Frequency deviation (Hz)
        - P_gen: Generator power output (pu)
        - P_turbine: Turbine mechanical power (pu)
        - P_boiler: Boiler steam flow (pu)
        """
        delta_f, P_gen, P_turbine, P_boiler = y

        # Swing equation (frequency dynamics)
        # H * d(delta_f)/dt = P_turbine - P_load - D * delta_f
        d_delta_f = (1 / (2 * self.inertia_constant)) * (
            P_turbine - load - self.damping_coefficient * delta_f
        )

        # Generator output follows turbine power with small delay
        d_P_gen = (P_turbine - P_gen) / 0.5

        # Turbine dynamics (first-order lag)
        d_P_turbine = (P_boiler - P_turbine) / self.time_constant_turbine

        # Boiler dynamics (first-order lag with governor control)
        governor_signal = u_turbine - self.droop_constant * delta_f
        d_P_boiler = (governor_signal - P_boiler) / self.time_constant_boiler

        return [d_delta_f, d_P_gen, d_P_turbine, d_P_boiler]

    def euler_step(self, y, t, dt, u_turbine, load):
        """Euler method for ODE integration"""
        dydt = self.system_dynamics(t, y, u_turbine, load)
        y_new = [y[i] + dt * dydt[i] for i in range(len(y))]
        return y_new

    def rk45_step(self, y0, t_span, u_turbine, load):
        """RK45 method using scipy's solve_ivp"""
        sol = solve_ivp(
            lambda t, y: self.system_dynamics(t, y, u_turbine, load),
            t_span,
            y0,
            method='RK45',
            dense_output=True
        )
        return sol


class ThermalStationGUI:
    """Main GUI application for thermal station analysis"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Thermal Power Station Analysis Tool")
        self.root.geometry("1400x900")

        # Initialize analyzers
        self.analyzer = ThermalStationAnalyzer()
        self.dynamics = PowerStationDynamics()

        # Simulation state
        self.simulation_running = False
        self.simulation_time = 0.0
        self.dt = 0.01  # Time step
        self.solver_type = "RK45"  # Default solver

        # Data storage for plotting
        self.time_history = []
        self.frequency_history = []
        self.power_history = []
        self.turbine_history = []
        self.boiler_history = []

        # Initial state
        self.state = [0.0, 0.5, 0.5, 0.5]  # [delta_f, P_gen, P_turbine, P_boiler]

        # Create GUI
        self.create_menu()
        self.create_main_interface()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset All", command=self.reset_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Cost Analysis", command=self.show_cost_analysis)
        analysis_menu.add_command(label="System Info", command=self.show_system_info)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_interface(self):
        """Create main interface with notebook tabs"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Cost Analysis
        self.cost_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cost_tab, text="Cost Analysis")
        self.create_cost_tab()

        # Tab 2: Dynamic Simulation
        self.simulation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.simulation_tab, text="Dynamic Simulation")
        self.create_simulation_tab()

        # Tab 3: Load Profile Analysis
        self.load_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.load_tab, text="Load Profile")
        self.create_load_tab()

    def create_cost_tab(self):
        """Create cost analysis tab"""
        # Left panel: Parameters
        left_frame = ttk.LabelFrame(self.cost_tab, text="Input Parameters", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Parameter inputs
        params = [
            ("Installed Capacity (kW):", "installed_capacity", 60000),
            ("Load Factor (%):", "load_factor", 40),
            ("Capital Cost (Rs.):", "capital_cost", 500000),
            ("Annual Fuel Cost (Rs.):", "annual_fuel_cost", 90000),
            ("Interest & Depreciation (%):", "interest_rate", 10),
            ("Annual Org. Cost (Rs.):", "annual_org_cost", 50000)
        ]

        self.cost_entries = {}
        for i, (label, key, default) in enumerate(params):
            ttk.Label(left_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entry = ttk.Entry(left_frame, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.cost_entries[key] = entry

        # Calculate button
        ttk.Button(left_frame, text="Calculate Constants",
                  command=self.calculate_cost_constants).grid(row=len(params),
                                                              column=0, columnspan=2, pady=10)

        # Right panel: Results
        right_frame = ttk.LabelFrame(self.cost_tab, text="Results & Visualization", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Results text
        self.cost_results_text = tk.Text(right_frame, height=12, width=50, wrap=tk.WORD)
        self.cost_results_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Matplotlib figure for cost breakdown
        self.cost_fig = Figure(figsize=(6, 4), dpi=100)
        self.cost_canvas = FigureCanvasTkAgg(self.cost_fig, right_frame)
        self.cost_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Configure grid weights
        self.cost_tab.columnconfigure(1, weight=1)
        self.cost_tab.rowconfigure(0, weight=1)

        # Initial calculation
        self.calculate_cost_constants()

    def create_simulation_tab(self):
        """Create dynamic simulation tab"""
        # Control panel
        control_frame = ttk.LabelFrame(self.simulation_tab, text="Simulation Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5, columnspan=2)

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=0, column=0, padx=5)
        self.solver_var = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                     values=["RK45", "Euler"], state="readonly", width=10)
        solver_combo.grid(row=0, column=1, padx=5)

        # Control buttons
        ttk.Button(control_frame, text="Start", command=self.start_simulation,
                  style="Success.TButton").grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_simulation,
                  style="Danger.TButton").grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="Reset", command=self.reset_simulation).grid(row=0, column=4, padx=5)

        # Parameter sliders
        slider_frame = ttk.LabelFrame(self.simulation_tab, text="Adjustable Parameters", padding=10)
        slider_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Power reference slider
        ttk.Label(slider_frame, text="Power Reference (pu):").grid(row=0, column=0, sticky="w")
        self.power_ref_var = tk.DoubleVar(value=0.5)
        self.power_ref_slider = ttk.Scale(slider_frame, from_=0.0, to=1.0,
                                         variable=self.power_ref_var, orient=tk.HORIZONTAL)
        self.power_ref_slider.grid(row=0, column=1, sticky="ew", padx=5)
        self.power_ref_label = ttk.Label(slider_frame, text="0.50")
        self.power_ref_label.grid(row=0, column=2)
        self.power_ref_var.trace_add('write', self.update_slider_labels)

        # Load demand slider
        ttk.Label(slider_frame, text="Load Demand (pu):").grid(row=1, column=0, sticky="w")
        self.load_demand_var = tk.DoubleVar(value=0.5)
        self.load_demand_slider = ttk.Scale(slider_frame, from_=0.0, to=1.0,
                                           variable=self.load_demand_var, orient=tk.HORIZONTAL)
        self.load_demand_slider.grid(row=1, column=1, sticky="ew", padx=5)
        self.load_demand_label = ttk.Label(slider_frame, text="0.50")
        self.load_demand_label.grid(row=1, column=2)
        self.load_demand_var.trace_add('write', self.update_slider_labels)

        # Inertia constant slider
        ttk.Label(slider_frame, text="Inertia Constant (s):").grid(row=2, column=0, sticky="w")
        self.inertia_var = tk.DoubleVar(value=5.0)
        self.inertia_slider = ttk.Scale(slider_frame, from_=1.0, to=10.0,
                                       variable=self.inertia_var, orient=tk.HORIZONTAL)
        self.inertia_slider.grid(row=2, column=1, sticky="ew", padx=5)
        self.inertia_label = ttk.Label(slider_frame, text="5.00")
        self.inertia_label.grid(row=2, column=2)
        self.inertia_var.trace_add('write', self.update_slider_labels)

        # Damping coefficient slider
        ttk.Label(slider_frame, text="Damping Coefficient:").grid(row=3, column=0, sticky="w")
        self.damping_var = tk.DoubleVar(value=0.5)
        self.damping_slider = ttk.Scale(slider_frame, from_=0.1, to=2.0,
                                       variable=self.damping_var, orient=tk.HORIZONTAL)
        self.damping_slider.grid(row=3, column=1, sticky="ew", padx=5)
        self.damping_label = ttk.Label(slider_frame, text="0.50")
        self.damping_label.grid(row=3, column=2)
        self.damping_var.trace_add('write', self.update_slider_labels)

        slider_frame.columnconfigure(1, weight=1)

        # Visualization panel
        viz_frame = ttk.LabelFrame(self.simulation_tab, text="Real-Time Visualization", padding=10)
        viz_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        # Create matplotlib figure with subplots
        self.sim_fig = Figure(figsize=(8, 8), dpi=100)
        self.sim_axes = []

        # 4 subplots for different variables
        for i in range(4):
            ax = self.sim_fig.add_subplot(4, 1, i+1)
            self.sim_axes.append(ax)

        self.sim_fig.tight_layout()
        self.sim_canvas = FigureCanvasTkAgg(self.sim_fig, viz_frame)
        self.sim_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Status panel
        status_frame = ttk.LabelFrame(self.simulation_tab, text="System Status", padding=10)
        status_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        self.status_text = tk.Text(status_frame, height=8, width=40)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Configure grid weights
        self.simulation_tab.columnconfigure(1, weight=1)
        self.simulation_tab.rowconfigure(1, weight=1)

    def create_load_tab(self):
        """Create load profile analysis tab"""
        # Controls
        control_frame = ttk.LabelFrame(self.load_tab, text="Load Profile Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(control_frame, text="Profile Type:").grid(row=0, column=0, padx=5)
        self.profile_var = tk.StringVar(value="Daily")
        profile_combo = ttk.Combobox(control_frame, textvariable=self.profile_var,
                                     values=["Daily", "Weekly", "Seasonal"],
                                     state="readonly", width=15)
        profile_combo.grid(row=0, column=1, padx=5)

        ttk.Button(control_frame, text="Generate Profile",
                  command=self.generate_load_profile).grid(row=0, column=2, padx=5)

        # Visualization
        viz_frame = ttk.LabelFrame(self.load_tab, text="Load Profile Visualization", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.load_fig = Figure(figsize=(10, 6), dpi=100)
        self.load_canvas = FigureCanvasTkAgg(self.load_fig, viz_frame)
        self.load_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Generate initial profile
        self.generate_load_profile()

    def update_slider_labels(self, *args):
        """Update slider value labels"""
        self.power_ref_label.config(text=f"{self.power_ref_var.get():.2f}")
        self.load_demand_label.config(text=f"{self.load_demand_var.get():.2f}")
        self.inertia_label.config(text=f"{self.inertia_var.get():.2f}")
        self.damping_label.config(text=f"{self.damping_var.get():.2f}")

        # Update dynamics parameters
        self.dynamics.inertia_constant = self.inertia_var.get()
        self.dynamics.damping_coefficient = self.damping_var.get()

    def calculate_cost_constants(self):
        """Calculate and display cost constants"""
        try:
            # Update analyzer parameters
            self.analyzer.installed_capacity = float(self.cost_entries['installed_capacity'].get())
            self.analyzer.load_factor = float(self.cost_entries['load_factor'].get()) / 100
            self.analyzer.capital_cost = float(self.cost_entries['capital_cost'].get())
            self.analyzer.annual_fuel_cost = float(self.cost_entries['annual_fuel_cost'].get())
            self.analyzer.interest_depreciation_rate = float(self.cost_entries['interest_rate'].get()) / 100
            self.analyzer.annual_org_cost = float(self.cost_entries['annual_org_cost'].get())

            # Calculate constants
            a, b, c = self.analyzer.calculate_constants()
            breakdown = self.analyzer.get_cost_breakdown()

            # Display results
            results_text = f"""
COST FORMULA CONSTANTS:
{'='*50}

The annual working cost formula is:
Cost = a + b×kW + c×kWh

where:

a (Fixed Annual Costs): Rs. {a:,.2f}
  - Organization costs
  - Site interest and maintenance
  - Independent of capacity and generation

b (Cost per kW Installed): Rs. {b:.4f} per kW
  - Interest and depreciation on equipment
  - Proportional to installed capacity
  - Capital cost recovery per kW

c (Cost per kWh Generated): Rs. {c:.6f} per kWh
  - Fuel, oil, and consumables
  - Wages and operating staff
  - Variable costs proportional to generation

{'='*50}
COST BREAKDOWN:
{'='*50}

Energy Produced per Annum: {self.analyzer.energy_per_annum:,.0f} kWh
Annual Load Factor: {self.analyzer.load_factor*100:.1f}%

Fixed Costs (a):           Rs. {breakdown['fixed']:,.2f}
Capacity Costs (b×kW):     Rs. {breakdown['capacity']:,.2f}
Energy Costs (c×kWh):      Rs. {breakdown['energy']:,.2f}
{'='*50}
TOTAL ANNUAL COST:         Rs. {breakdown['total']:,.2f}
{'='*50}

Cost per kW installed:     Rs. {breakdown['total']/self.analyzer.installed_capacity:.2f}
Cost per kWh generated:    Rs. {breakdown['total']/self.analyzer.energy_per_annum:.6f}
"""

            self.cost_results_text.delete(1.0, tk.END)
            self.cost_results_text.insert(1.0, results_text)

            # Update visualization
            self.plot_cost_breakdown(breakdown)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    def plot_cost_breakdown(self, breakdown):
        """Plot cost breakdown pie chart"""
        self.cost_fig.clear()

        ax1 = self.cost_fig.add_subplot(2, 1, 1)
        labels = ['Fixed Costs', 'Capacity Costs', 'Energy Costs']
        sizes = [breakdown['fixed'], breakdown['capacity'], breakdown['energy']]
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        explode = (0.05, 0.05, 0.05)

        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               explode=explode, shadow=True, startangle=90)
        ax1.set_title('Annual Cost Breakdown')

        # Bar chart
        ax2 = self.cost_fig.add_subplot(2, 1, 2)
        categories = ['Fixed\n(a)', 'Capacity\n(b×kW)', 'Energy\n(c×kWh)', 'Total']
        values = [breakdown['fixed'], breakdown['capacity'], breakdown['energy'], breakdown['total']]
        bars = ax2.bar(categories, values, color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])

        ax2.set_ylabel('Cost (Rs.)')
        ax2.set_title('Cost Components')
        ax2.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'Rs. {height:,.0f}',
                    ha='center', va='bottom', fontsize=8)

        self.cost_fig.tight_layout()
        self.cost_canvas.draw()

    def start_simulation(self):
        """Start dynamic simulation"""
        if not self.simulation_running:
            self.simulation_running = True
            self.solver_type = self.solver_var.get()
            self.update_status("Simulation started with {} solver".format(self.solver_type))
            self.run_simulation_step()

    def stop_simulation(self):
        """Stop dynamic simulation"""
        self.simulation_running = False
        self.update_status("Simulation stopped")

    def reset_simulation(self):
        """Reset simulation to initial state"""
        self.stop_simulation()
        self.simulation_time = 0.0
        self.state = [0.0, 0.5, 0.5, 0.5]

        # Clear history
        self.time_history = []
        self.frequency_history = []
        self.power_history = []
        self.turbine_history = []
        self.boiler_history = []

        # Clear plots
        for ax in self.sim_axes:
            ax.clear()
        self.sim_canvas.draw()

        self.update_status("Simulation reset to initial conditions")

    def run_simulation_step(self):
        """Execute one simulation step"""
        if not self.simulation_running:
            return

        # Get current control inputs
        u_turbine = self.power_ref_var.get()
        load = self.load_demand_var.get()

        # Perform integration step
        if self.solver_type == "Euler":
            self.state = self.dynamics.euler_step(
                self.state, self.simulation_time, self.dt, u_turbine, load
            )
        else:  # RK45
            sol = self.dynamics.rk45_step(
                self.state, [self.simulation_time, self.simulation_time + self.dt],
                u_turbine, load
            )
            self.state = sol.y[:, -1].tolist()

        # Update time
        self.simulation_time += self.dt

        # Store history (subsample for plotting)
        if len(self.time_history) == 0 or self.simulation_time - self.time_history[-1] >= 0.1:
            self.time_history.append(self.simulation_time)
            self.frequency_history.append(50.0 + self.state[0])  # Actual frequency
            self.power_history.append(self.state[1])
            self.turbine_history.append(self.state[2])
            self.boiler_history.append(self.state[3])

            # Limit history length
            max_points = 500
            if len(self.time_history) > max_points:
                self.time_history = self.time_history[-max_points:]
                self.frequency_history = self.frequency_history[-max_points:]
                self.power_history = self.power_history[-max_points:]
                self.turbine_history = self.turbine_history[-max_points:]
                self.boiler_history = self.boiler_history[-max_points:]

        # Update plots every 10 steps
        if int(self.simulation_time / self.dt) % 10 == 0:
            self.update_simulation_plots()
            self.update_status_display()

        # Schedule next step
        self.root.after(10, self.run_simulation_step)

    def update_simulation_plots(self):
        """Update real-time simulation plots"""
        if len(self.time_history) < 2:
            return

        # Clear all axes
        for ax in self.sim_axes:
            ax.clear()

        # Plot 1: Frequency deviation
        self.sim_axes[0].plot(self.time_history, self.frequency_history, 'b-', linewidth=1.5)
        self.sim_axes[0].axhline(y=50.0, color='r', linestyle='--', alpha=0.5, label='Nominal')
        self.sim_axes[0].set_ylabel('Frequency (Hz)')
        self.sim_axes[0].set_title('System Frequency')
        self.sim_axes[0].grid(True, alpha=0.3)
        self.sim_axes[0].legend(loc='upper right')

        # Plot 2: Generator power
        self.sim_axes[1].plot(self.time_history, self.power_history, 'g-', linewidth=1.5)
        self.sim_axes[1].set_ylabel('Power (pu)')
        self.sim_axes[1].set_title('Generator Output Power')
        self.sim_axes[1].grid(True, alpha=0.3)
        self.sim_axes[1].set_ylim([0, 1.1])

        # Plot 3: Turbine power
        self.sim_axes[2].plot(self.time_history, self.turbine_history, 'm-', linewidth=1.5)
        self.sim_axes[2].set_ylabel('Power (pu)')
        self.sim_axes[2].set_title('Turbine Mechanical Power')
        self.sim_axes[2].grid(True, alpha=0.3)
        self.sim_axes[2].set_ylim([0, 1.1])

        # Plot 4: Boiler steam flow
        self.sim_axes[3].plot(self.time_history, self.boiler_history, 'c-', linewidth=1.5)
        self.sim_axes[3].set_ylabel('Flow (pu)')
        self.sim_axes[3].set_xlabel('Time (s)')
        self.sim_axes[3].set_title('Boiler Steam Flow')
        self.sim_axes[3].grid(True, alpha=0.3)
        self.sim_axes[3].set_ylim([0, 1.1])

        self.sim_fig.tight_layout()
        self.sim_canvas.draw()

    def update_status_display(self):
        """Update status text display"""
        if len(self.time_history) == 0:
            return

        status = f"""
SYSTEM STATUS
{'='*40}
Simulation Time: {self.simulation_time:.2f} s
Solver Method: {self.solver_type}

CURRENT STATE:
Frequency: {self.frequency_history[-1]:.3f} Hz
Frequency Deviation: {self.state[0]:.4f} Hz
Generator Power: {self.power_history[-1]:.4f} pu
Turbine Power: {self.turbine_history[-1]:.4f} pu
Boiler Steam Flow: {self.boiler_history[-1]:.4f} pu

CONTROL INPUTS:
Power Reference: {self.power_ref_var.get():.3f} pu
Load Demand: {self.load_demand_var.get():.3f} pu

SYSTEM PARAMETERS:
Inertia Constant: {self.inertia_var.get():.2f} s
Damping Coefficient: {self.damping_var.get():.2f}
Droop: {self.dynamics.droop_constant*100:.1f}%
"""
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status)

    def generate_load_profile(self):
        """Generate and plot load profiles"""
        self.load_fig.clear()

        profile_type = self.profile_var.get()

        if profile_type == "Daily":
            # 24-hour daily load profile
            hours = np.arange(0, 24, 0.5)

            # Typical industrial load profile
            base_load = 0.4
            peak_morning = 0.85
            peak_evening = 0.95

            load = []
            for h in hours:
                if 0 <= h < 6:  # Night: low load
                    l = base_load + 0.05 * np.sin(np.pi * h / 6)
                elif 6 <= h < 10:  # Morning ramp
                    l = base_load + (peak_morning - base_load) * (h - 6) / 4
                elif 10 <= h < 16:  # Day: medium-high load
                    l = peak_morning - 0.1 * np.sin(np.pi * (h - 10) / 6)
                elif 16 <= h < 20:  # Evening peak
                    l = peak_morning + (peak_evening - peak_morning) * (h - 16) / 4
                else:  # Night ramp down
                    l = peak_evening - (peak_evening - base_load) * (h - 20) / 4
                load.append(l)

            ax = self.load_fig.add_subplot(111)
            ax.plot(hours, load, 'b-', linewidth=2)
            ax.fill_between(hours, load, alpha=0.3)
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Load (pu)')
            ax.set_title('Daily Load Profile')
            ax.grid(True, alpha=0.3)
            ax.set_xlim([0, 24])
            ax.set_xticks(range(0, 25, 3))

        elif profile_type == "Weekly":
            # 7-day weekly profile
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            avg_load = [0.75, 0.78, 0.80, 0.76, 0.72, 0.50, 0.45]
            peak_load = [0.95, 0.97, 0.98, 0.96, 0.92, 0.70, 0.65]

            x = np.arange(len(days))
            width = 0.35

            ax = self.load_fig.add_subplot(111)
            ax.bar(x - width/2, avg_load, width, label='Average Load', alpha=0.8)
            ax.bar(x + width/2, peak_load, width, label='Peak Load', alpha=0.8)
            ax.set_xlabel('Day of Week')
            ax.set_ylabel('Load (pu)')
            ax.set_title('Weekly Load Profile')
            ax.set_xticks(x)
            ax.set_xticklabels(days)
            ax.legend()
            ax.grid(axis='y', alpha=0.3)

        else:  # Seasonal
            # Monthly seasonal variation
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            # Higher load in summer (cooling) and winter (heating)
            energy_demand = [0.80, 0.75, 0.70, 0.65, 0.70, 0.85,
                           0.95, 0.90, 0.75, 0.70, 0.75, 0.85]

            ax = self.load_fig.add_subplot(111)
            ax.plot(months, energy_demand, 'ro-', linewidth=2, markersize=8)
            ax.fill_between(range(len(months)), energy_demand, alpha=0.3)
            ax.set_xlabel('Month')
            ax.set_ylabel('Average Load Factor')
            ax.set_title('Seasonal Load Variation')
            ax.grid(True, alpha=0.3)
            ax.set_ylim([0, 1.0])

        self.load_fig.tight_layout()
        self.load_canvas.draw()

    def update_status(self, message):
        """Update status message"""
        print(f"[STATUS] {message}")

    def on_window_resize(self, event):
        """Handle window resize events for autoscaling"""
        # Only process resize events for the main window
        if event.widget == self.root:
            # Redraw all canvases to adjust to new size
            try:
                self.cost_canvas.draw()
                self.sim_canvas.draw()
                self.load_canvas.draw()
            except:
                pass  # Ignore errors during initialization

    def show_cost_analysis(self):
        """Show detailed cost analysis"""
        self.notebook.select(self.cost_tab)
        self.calculate_cost_constants()

    def show_system_info(self):
        """Show system information dialog"""
        info = f"""
Thermal Power Station Analysis Tool
Version 1.0

Current System Parameters:
- Installed Capacity: {self.analyzer.installed_capacity/1000:.1f} MW
- Load Factor: {self.analyzer.load_factor*100:.1f}%
- Annual Energy: {self.analyzer.energy_per_annum/1e6:.2f} GWh

Cost Constants:
- a = Rs. {self.analyzer.a:,.2f}
- b = Rs. {self.analyzer.b:.4f} per kW
- c = Rs. {self.analyzer.c:.6f} per kWh

Simulation Settings:
- ODE Solver: {self.solver_type}
- Time Step: {self.dt} s
- Inertia Constant: {self.dynamics.inertia_constant} s
"""
        messagebox.showinfo("System Information", info)

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Thermal Power Station Analysis Tool
Version 1.0

Features:
• Cost analysis with a, b, c constants determination
• Dynamic simulation using differential equations
• Multiple ODE solvers (RK45, Euler)
• Real-time visualization with autoscaling
• Interactive parameter adjustment
• Load profile analysis

Developed for electrical engineering education
and practical power station analysis.

© 2025 Thermal Station Analyzer
"""
        messagebox.showinfo("About", about_text)

    def reset_all(self):
        """Reset all parameters to defaults"""
        response = messagebox.askyesno("Reset All",
                                       "Reset all parameters to default values?")
        if response:
            # Reset cost parameters
            self.cost_entries['installed_capacity'].delete(0, tk.END)
            self.cost_entries['installed_capacity'].insert(0, "60000")
            self.cost_entries['load_factor'].delete(0, tk.END)
            self.cost_entries['load_factor'].insert(0, "40")
            self.cost_entries['capital_cost'].delete(0, tk.END)
            self.cost_entries['capital_cost'].insert(0, "500000")
            self.cost_entries['annual_fuel_cost'].delete(0, tk.END)
            self.cost_entries['annual_fuel_cost'].insert(0, "90000")
            self.cost_entries['interest_rate'].delete(0, tk.END)
            self.cost_entries['interest_rate'].insert(0, "10")
            self.cost_entries['annual_org_cost'].delete(0, tk.END)
            self.cost_entries['annual_org_cost'].insert(0, "50000")

            # Reset simulation
            self.reset_simulation()

            # Reset sliders
            self.power_ref_var.set(0.5)
            self.load_demand_var.set(0.5)
            self.inertia_var.set(5.0)
            self.damping_var.set(0.5)

            # Recalculate
            self.calculate_cost_constants()

            messagebox.showinfo("Reset Complete", "All parameters reset to defaults")


def main():
    """Main application entry point"""
    root = tk.Tk()

    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')

    # Custom button styles
    style.configure("Success.TButton", foreground="green")
    style.configure("Danger.TButton", foreground="red")

    # Create application
    app = ThermalStationGUI(root)

    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()

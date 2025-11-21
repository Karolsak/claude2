"""
Thermal Station Cost Calculator with Advanced Electrical Engineering Simulations
Includes: Cost calculations, Dynamic ODE solvers (RK45, Euler), Real-time visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from dataclasses import dataclass
import time
from threading import Thread
from typing import Callable, List, Tuple


# ==================== Data Classes ====================
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


@dataclass
class ElectricalSystemState:
    """State variables for electrical system simulation"""
    voltage: float = 0.0  # V (RMS)
    current: float = 0.0  # A (RMS)
    frequency: float = 50.0  # Hz
    power: float = 0.0  # W
    rotor_angle: float = 0.0  # radians
    angular_velocity: float = 314.159  # rad/s (2*pi*50)


# ==================== Calculation Engine ====================
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


# ==================== ODE Solvers ====================
class ODESolver:
    """Base class for ODE solvers"""

    @staticmethod
    def euler_step(f: Callable, t: float, y: np.ndarray, h: float) -> np.ndarray:
        """Euler's method - first order"""
        return y + h * f(t, y)

    @staticmethod
    def rk45_step(f: Callable, t: float, y: np.ndarray, h: float) -> np.ndarray:
        """Runge-Kutta 4th/5th order (Dormand-Prince)"""
        # RK4 coefficients
        k1 = f(t, y)
        k2 = f(t + h/2, y + h*k1/2)
        k3 = f(t + h/2, y + h*k2/2)
        k4 = f(t + h, y + h*k3)

        # 4th order estimate
        y_new = y + h * (k1 + 2*k2 + 2*k3 + k4) / 6
        return y_new


# ==================== Electrical System Models ====================
class ElectricalSystemModel:
    """Advanced electrical system models with differential equations"""

    def __init__(self, system_type: str = "generator"):
        self.system_type = system_type
        self.setup_parameters()

    def setup_parameters(self):
        """Setup system parameters based on type"""
        if self.system_type == "generator":
            # Synchronous generator parameters
            self.H = 5.0  # Inertia constant (s)
            self.D = 2.0  # Damping coefficient
            self.Pm = 1.0  # Mechanical power (pu)
            self.V = 1.0  # Terminal voltage (pu)
            self.Xd = 1.5  # d-axis reactance (pu)
            self.omega_s = 2 * np.pi * 50  # Synchronous frequency

        elif self.system_type == "rlc_circuit":
            # RLC circuit parameters
            self.R = 10.0  # Resistance (Ohms)
            self.L = 0.1  # Inductance (H)
            self.C = 100e-6  # Capacitance (F)
            self.V_source = 230.0  # Source voltage (V RMS)

        elif self.system_type == "transformer":
            # Transformer parameters
            self.R1 = 0.5  # Primary resistance
            self.L1 = 0.05  # Primary inductance
            self.R2 = 0.3  # Secondary resistance
            self.L2 = 0.03  # Secondary inductance
            self.M = 0.04  # Mutual inductance

    def generator_swing_equation(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Generator swing equation dynamics
        y[0] = delta (rotor angle)
        y[1] = omega (angular velocity)
        """
        delta, omega = y
        omega_pu = omega / self.omega_s

        # Electrical power (simplified)
        Pe = (self.Pm * self.V / self.Xd) * np.sin(delta)

        # Swing equation
        ddelta_dt = omega - self.omega_s
        domega_dt = (self.omega_s / (2 * self.H)) * (self.Pm - Pe - self.D * (omega_pu - 1.0))

        return np.array([ddelta_dt, domega_dt])

    def rlc_circuit_equation(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        RLC circuit differential equations
        y[0] = i (current)
        y[1] = v_c (capacitor voltage)
        """
        i, v_c = y

        # Input voltage (sinusoidal source)
        v_in = self.V_source * np.sqrt(2) * np.sin(2 * np.pi * 50 * t)

        # Circuit equations
        di_dt = (v_in - self.R * i - v_c) / self.L
        dv_c_dt = i / self.C

        return np.array([di_dt, dv_c_dt])

    def transformer_equation(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Transformer coupled circuit equations
        y[0] = i1 (primary current)
        y[1] = i2 (secondary current)
        """
        i1, i2 = y

        # Input voltage
        v_in = self.V_source * np.sqrt(2) * np.sin(2 * np.pi * 50 * t)

        # Load resistance
        R_load = 50.0

        # Coupled equations
        di1_dt = (v_in - self.R1 * i1 - self.M * (di2 := 0)) / self.L1
        di2_dt = (-self.R2 * i2 - R_load * i2 + self.M * di1_dt) / self.L2

        return np.array([di1_dt, di2_dt])

    def get_ode_function(self) -> Callable:
        """Return the appropriate ODE function"""
        if self.system_type == "generator":
            return self.generator_swing_equation
        elif self.system_type == "rlc_circuit":
            return self.rlc_circuit_equation
        elif self.system_type == "transformer":
            return self.transformer_equation
        else:
            return self.rlc_circuit_equation


# ==================== Simulation Engine ====================
class SimulationEngine:
    """Handles real-time dynamic simulation"""

    def __init__(self):
        self.running = False
        self.solver_method = "rk45"  # or "euler"
        self.model = ElectricalSystemModel("rlc_circuit")
        self.reset_simulation()

    def reset_simulation(self):
        """Reset simulation state"""
        self.t = 0.0
        self.dt = 0.0001  # Time step (100 microseconds)

        if self.model.system_type == "generator":
            self.y = np.array([0.1, 2 * np.pi * 50])  # [delta, omega]
        else:
            self.y = np.array([0.0, 0.0])  # [i, v_c] or [i1, i2]

        self.time_history = []
        self.state_history = []

    def step(self):
        """Perform one simulation step"""
        if not self.running:
            return

        ode_func = self.model.get_ode_function()

        if self.solver_method == "euler":
            self.y = ODESolver.euler_step(ode_func, self.t, self.y, self.dt)
        else:  # rk45
            self.y = ODESolver.rk45_step(ode_func, self.t, self.y, self.dt)

        self.t += self.dt

        # Store history (decimated for efficiency)
        if len(self.time_history) == 0 or self.t - self.time_history[-1] >= 0.001:
            self.time_history.append(self.t)
            self.state_history.append(self.y.copy())

            # Limit history length
            if len(self.time_history) > 5000:
                self.time_history.pop(0)
                self.state_history.pop(0)

    def get_current_rms_values(self) -> dict:
        """Calculate RMS values from current state"""
        if self.model.system_type == "generator":
            delta, omega = self.y
            freq = omega / (2 * np.pi)
            voltage_rms = self.model.V * 230  # Convert pu to V
            current_rms = abs(self.model.Pm / self.model.V) * 100  # Approximate
            power = voltage_rms * current_rms * np.cos(delta)

            return {
                'voltage': voltage_rms,
                'current': current_rms,
                'frequency': freq,
                'power': power,
                'angle': np.degrees(delta)
            }
        else:  # RLC or transformer
            if len(self.y) >= 2:
                current = abs(self.y[0])
                voltage = abs(self.y[1])
                # Convert instantaneous to RMS
                current_rms = current / np.sqrt(2) if current > 0 else 0
                voltage_rms = voltage / np.sqrt(2) if voltage > 0 else 0
                power = voltage_rms * current_rms

                return {
                    'voltage': voltage_rms,
                    'current': current_rms,
                    'frequency': 50.0,
                    'power': power,
                    'angle': 0.0
                }

        return {'voltage': 0, 'current': 0, 'frequency': 50, 'power': 0, 'angle': 0}


# ==================== Main GUI Application ====================
class ThermalStationApp:
    """Main application with Tkinter GUI"""

    def __init__(self, root):
        self.root = root
        self.root.title("Thermal Station Cost Calculator & Electrical System Simulator")
        self.root.geometry("1400x900")

        # Data models
        self.thermal_data = ThermalStationData()
        self.calculator = ThermalStationCalculator(self.thermal_data)
        self.simulation = SimulationEngine()

        # Create menu bar
        self.create_menu_bar()

        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.create_thermal_calculator_tab()
        self.create_simulation_tab()
        self.create_results_tab()

        # Bind resize event for auto-scaling
        self.root.bind('<Configure>', self.on_window_resize)

        # Simulation thread
        self.simulation_thread = None
        self.update_interval = 50  # ms

        # Start periodic update
        self.update_display()

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset All", command=self.reset_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start", command=self.start_simulation)
        sim_menu.add_command(label="Stop", command=self.stop_simulation)
        sim_menu.add_command(label="Reset", command=self.reset_simulation)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_thermal_calculator_tab(self):
        """Create thermal station calculator tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Thermal Station Calculator")

        # Create scrollable frame
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Input parameters section
        input_frame = ttk.LabelFrame(scrollable_frame, text="Input Parameters", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Store slider references
        self.thermal_sliders = {}

        parameters = [
            ("Installed Capacity (kW)", "installed_capacity", 1000, 50000, 10000),
            ("Maximum Demand (kW)", "max_demand", 500, 50000, 9000),
            ("Annual Load Factor (%)", "annual_load_factor", 10, 100, 60),
            ("Cost per kW (Rs)", "cost_per_kw", 500, 5000, 1200),
            ("Interest & Tax Plant (%)", "interest_tax_plant", 1, 20, 5),
            ("Depreciation Plant (%)", "depreciation_plant", 1, 20, 5),
            ("Distribution Cost (Rs)", "distribution_cost", 100000, 1000000, 400000),
            ("Interest & Tax Distribution (%)", "interest_tax_distribution", 1, 20, 5),
            ("Coal Cost per Tonne (Rs)", "coal_cost_per_tonne", 10, 200, 40),
            ("Operating Cost (Rs)", "operating_cost", 100000, 1000000, 400000),
            ("Maintenance Fixed (Rs)", "maintenance_fixed", 5000, 100000, 20000),
            ("Maintenance Variable (Rs)", "maintenance_variable", 5000, 100000, 30000),
            ("Coal Consumption (tonne)", "coal_consumption", 5000, 50000, 25300),
        ]

        for i, (label, attr, min_val, max_val, default) in enumerate(parameters):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)

            slider = tk.Scale(
                input_frame,
                from_=min_val,
                to=max_val,
                orient=tk.HORIZONTAL,
                length=300,
                resolution=(max_val - min_val) / 100
            )
            slider.set(default)
            slider.grid(row=i, column=1, padx=10, pady=2)

            value_label = ttk.Label(input_frame, text=f"{default:.2f}")
            value_label.grid(row=i, column=2, sticky="w", pady=2)

            # Update value label on slider change
            slider.config(command=lambda val, lbl=value_label, s=slider: lbl.config(text=f"{s.get():.2f}"))

            self.thermal_sliders[attr] = slider

        # Calculate button
        calc_button = ttk.Button(
            scrollable_frame,
            text="Calculate Costs",
            command=self.calculate_thermal_costs
        )
        calc_button.grid(row=1, column=0, pady=20)

        # Results display
        results_frame = ttk.LabelFrame(scrollable_frame, text="Calculation Results", padding=10)
        results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.thermal_results_text = scrolledtext.ScrolledText(
            results_frame,
            height=20,
            width=80,
            font=("Courier", 10)
        )
        self.thermal_results_text.pack(fill=tk.BOTH, expand=True)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_simulation_tab(self):
        """Create dynamic simulation tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Dynamic Electrical System Simulation")

        # Control panel
        control_frame = ttk.LabelFrame(frame, text="Simulation Controls", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # System type selection
        ttk.Label(control_frame, text="System Type:").grid(row=0, column=0, padx=5)
        self.system_type_var = tk.StringVar(value="rlc_circuit")
        system_combo = ttk.Combobox(
            control_frame,
            textvariable=self.system_type_var,
            values=["generator", "rlc_circuit", "transformer"],
            state="readonly",
            width=15
        )
        system_combo.grid(row=0, column=1, padx=5)
        system_combo.bind("<<ComboboxSelected>>", self.on_system_type_change)

        # Solver method selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=0, column=2, padx=5)
        self.solver_var = tk.StringVar(value="rk45")
        solver_combo = ttk.Combobox(
            control_frame,
            textvariable=self.solver_var,
            values=["rk45", "euler"],
            state="readonly",
            width=10
        )
        solver_combo.grid(row=0, column=3, padx=5)
        solver_combo.bind("<<ComboboxSelected>>", self.on_solver_change)

        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=0, column=4, columnspan=3, padx=20)

        self.start_btn = ttk.Button(btn_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="⏸ Stop", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(btn_frame, text="⟳ Reset", command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # System parameters adjustment
        params_frame = ttk.LabelFrame(frame, text="System Parameters", padding=10)
        params_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.param_sliders = {}
        self.create_parameter_sliders(params_frame)

        # Real-time display
        display_frame = ttk.LabelFrame(frame, text="Real-Time Measurements (RMS Values)", padding=10)
        display_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.voltage_label = ttk.Label(display_frame, text="Voltage (V RMS): 0.00", font=("Arial", 12))
        self.voltage_label.grid(row=0, column=0, padx=20, pady=5)

        self.current_label = ttk.Label(display_frame, text="Current (A RMS): 0.00", font=("Arial", 12))
        self.current_label.grid(row=0, column=1, padx=20, pady=5)

        self.freq_label = ttk.Label(display_frame, text="Frequency (Hz): 50.00", font=("Arial", 12))
        self.freq_label.grid(row=0, column=2, padx=20, pady=5)

        self.power_label = ttk.Label(display_frame, text="Power (W): 0.00", font=("Arial", 12))
        self.power_label.grid(row=0, column=3, padx=20, pady=5)

        # Visualization
        viz_frame = ttk.LabelFrame(frame, text="Waveform Visualization", padding=5)
        viz_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig.tight_layout()

    def create_parameter_sliders(self, parent):
        """Create parameter adjustment sliders"""
        # Clear existing sliders
        for widget in parent.winfo_children():
            widget.destroy()

        self.param_sliders.clear()

        # Define parameters based on system type
        if self.simulation.model.system_type == "generator":
            params = [
                ("Inertia Constant H (s)", "H", 1.0, 10.0, self.simulation.model.H),
                ("Damping D", "D", 0.5, 5.0, self.simulation.model.D),
                ("Mechanical Power (pu)", "Pm", 0.1, 2.0, self.simulation.model.Pm),
            ]
        elif self.simulation.model.system_type == "rlc_circuit":
            params = [
                ("Resistance (Ω)", "R", 1.0, 100.0, self.simulation.model.R),
                ("Inductance (H)", "L", 0.01, 1.0, self.simulation.model.L),
                ("Capacitance (µF)", "C", 10.0, 1000.0, self.simulation.model.C * 1e6),
                ("Source Voltage (V)", "V_source", 50.0, 500.0, self.simulation.model.V_source),
            ]
        else:  # transformer
            params = [
                ("Primary Resistance (Ω)", "R1", 0.1, 5.0, self.simulation.model.R1),
                ("Secondary Resistance (Ω)", "R2", 0.1, 5.0, self.simulation.model.R2),
                ("Primary Inductance (H)", "L1", 0.01, 0.5, self.simulation.model.L1),
            ]

        for i, (label, attr, min_val, max_val, default) in enumerate(params):
            ttk.Label(parent, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)

            slider = tk.Scale(
                parent,
                from_=min_val,
                to=max_val,
                orient=tk.HORIZONTAL,
                length=200,
                resolution=(max_val - min_val) / 100
            )
            slider.set(default)
            slider.grid(row=i, column=1, padx=5, pady=2)
            slider.config(command=lambda val, a=attr: self.on_parameter_change(a, float(val)))

            value_label = ttk.Label(parent, text=f"{default:.3f}")
            value_label.grid(row=i, column=2, sticky="w", padx=5, pady=2)

            self.param_sliders[attr] = (slider, value_label)

    def create_results_tab(self):
        """Create comprehensive results tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Comprehensive Results & Analysis")

        # Create text area for results
        self.results_text = scrolledtext.ScrolledText(
            frame,
            height=40,
            width=100,
            font=("Courier", 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add initial message
        self.results_text.insert(tk.END, "Calculate thermal costs and run simulation to see results here.\n")

    def calculate_thermal_costs(self):
        """Calculate thermal station costs"""
        # Update data from sliders
        for attr, slider in self.thermal_sliders.items():
            value = slider.get()
            if attr == "annual_load_factor":
                value = value / 100.0  # Convert percentage to decimal
            if attr in ["interest_tax_plant", "depreciation_plant", "interest_tax_distribution"]:
                value = value / 100.0  # Convert percentage to decimal
            setattr(self.thermal_data, attr, value)

        # Create new calculator with updated data
        self.calculator = ThermalStationCalculator(self.thermal_data)
        results = self.calculator.calculate_all()

        # Display results
        output = "=" * 80 + "\n"
        output += "THERMAL STATION COST CALCULATION RESULTS\n"
        output += "=" * 80 + "\n\n"

        output += "INPUT PARAMETERS:\n"
        output += "-" * 80 + "\n"
        output += f"Installed Plant Capacity        : {self.thermal_data.installed_capacity:,.2f} kW\n"
        output += f"Maximum Demand                  : {self.thermal_data.max_demand:,.2f} kW\n"
        output += f"Annual Load Factor              : {self.thermal_data.annual_load_factor * 100:.2f}%\n"
        output += f"Cost of Plant per kW            : Rs. {self.thermal_data.cost_per_kw:,.2f}\n"
        output += f"Interest, Insurance, Tax (Plant): {self.thermal_data.interest_tax_plant * 100:.2f}% p.a.\n"
        output += f"Depreciation (Plant)            : {self.thermal_data.depreciation_plant * 100:.2f}% p.a.\n"
        output += f"Distribution System Cost        : Rs. {self.thermal_data.distribution_cost:,.2f}\n"
        output += f"Coal Cost per Tonne             : Rs. {self.thermal_data.coal_cost_per_tonne:,.2f}\n"
        output += f"Operating Cost                  : Rs. {self.thermal_data.operating_cost:,.2f} p.a.\n"
        output += f"Maintenance Fixed               : Rs. {self.thermal_data.maintenance_fixed:,.2f} p.a.\n"
        output += f"Maintenance Variable            : Rs. {self.thermal_data.maintenance_variable:,.2f} p.a.\n"
        output += f"Coal Consumption                : {self.thermal_data.coal_consumption:,.2f} tonne\n\n"

        output += "CALCULATIONS:\n"
        output += "-" * 80 + "\n"
        output += f"Annual Energy Generated         : {results['annual_energy_kwh']:,.2f} kWh\n\n"

        output += "FIXED COSTS:\n"
        output += f"  Plant Total Cost              : Rs. {results['plant_total_cost']:,.2f}\n"
        output += f"  Interest, Tax on Plant        : Rs. {results['interest_tax_plant']:,.2f}\n"
        output += f"  Depreciation on Plant         : Rs. {results['depreciation_plant']:,.2f}\n"
        output += f"  Fixed Cost (Plant)            : Rs. {results['fixed_cost_plant']:,.2f}\n"
        output += f"  Fixed Cost (Distribution)     : Rs. {results['fixed_cost_distribution']:,.2f}\n"
        output += f"  Maintenance Fixed             : Rs. {self.thermal_data.maintenance_fixed:,.2f}\n"
        output += f"  TOTAL FIXED COSTS             : Rs. {results['total_fixed_costs']:,.2f}\n\n"

        output += "RUNNING COSTS:\n"
        output += f"  Coal Cost (Annual)            : Rs. {results['coal_cost_annual']:,.2f}\n"
        output += f"  Operating Cost                : Rs. {self.thermal_data.operating_cost:,.2f}\n"
        output += f"  Maintenance Variable          : Rs. {self.thermal_data.maintenance_variable:,.2f}\n"
        output += f"  TOTAL RUNNING COSTS           : Rs. {results['total_running_costs']:,.2f}\n\n"

        output += "=" * 80 + "\n"
        output += "FINAL RESULTS:\n"
        output += "=" * 80 + "\n"
        output += f"Total Annual Cost               : Rs. {results['total_annual_cost']:,.2f}\n"
        output += f"Cost per kW per Year            : Rs. {results['cost_per_kw_year']:,.2f}\n"
        output += f"Cost per kWh Generated          : Rs. {results['cost_per_kwh_generated']:.4f}\n"
        output += "=" * 80 + "\n\n"

        # Additional analysis
        output += "PERFORMANCE METRICS:\n"
        output += "-" * 80 + "\n"
        capacity_factor = (results['annual_energy_kwh'] / (self.thermal_data.installed_capacity * 8760)) * 100
        output += f"Capacity Factor                 : {capacity_factor:.2f}%\n"
        output += f"Utilization Factor              : {(self.thermal_data.max_demand / self.thermal_data.installed_capacity) * 100:.2f}%\n"

        coal_rate = results['annual_energy_kwh'] / self.thermal_data.coal_consumption if self.thermal_data.coal_consumption > 0 else 0
        output += f"Energy per Tonne Coal           : {coal_rate:.2f} kWh/tonne\n"

        thermal_efficiency = (results['annual_energy_kwh'] * 3600) / (self.thermal_data.coal_consumption * 25e6) * 100 if self.thermal_data.coal_consumption > 0 else 0
        output += f"Approximate Thermal Efficiency  : {thermal_efficiency:.2f}%\n"
        output += "=" * 80 + "\n"

        # Update display
        self.thermal_results_text.delete(1.0, tk.END)
        self.thermal_results_text.insert(tk.END, output)

        # Also update comprehensive results tab
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)

        messagebox.showinfo("Success", "Thermal station costs calculated successfully!")

    def on_system_type_change(self, event=None):
        """Handle system type change"""
        new_type = self.system_type_var.get()
        self.stop_simulation()
        self.simulation.model = ElectricalSystemModel(new_type)
        self.simulation.reset_simulation()

        # Recreate parameter sliders
        params_frame = None
        for widget in self.notebook.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and "System Parameters" in child.cget("text"):
                        params_frame = child
                        break

        if params_frame:
            self.create_parameter_sliders(params_frame)

    def on_solver_change(self, event=None):
        """Handle solver method change"""
        self.simulation.solver_method = self.solver_var.get()

    def on_parameter_change(self, attr, value):
        """Handle parameter slider change"""
        if attr == "C":
            value = value * 1e-6  # Convert µF to F

        setattr(self.simulation.model, attr, value)

        # Update label
        if attr in self.param_sliders:
            slider, label = self.param_sliders[attr]
            display_value = value * 1e6 if attr == "C" else value
            label.config(text=f"{display_value:.3f}")

    def start_simulation(self):
        """Start the simulation"""
        self.simulation.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # Start simulation thread
        if self.simulation_thread is None or not self.simulation_thread.is_alive():
            self.simulation_thread = Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def reset_simulation(self):
        """Reset the simulation"""
        self.stop_simulation()
        self.simulation.reset_simulation()

        # Clear plots
        self.ax1.clear()
        self.ax2.clear()
        self.canvas.draw()

    def run_simulation(self):
        """Run simulation in background thread"""
        while self.simulation.running:
            # Perform multiple steps per iteration for speed
            for _ in range(100):
                self.simulation.step()
            time.sleep(0.001)  # Small delay

    def update_display(self):
        """Update display periodically"""
        if self.simulation.running or len(self.simulation.time_history) > 0:
            # Update real-time measurements
            rms_values = self.simulation.get_current_rms_values()

            self.voltage_label.config(text=f"Voltage (V RMS): {rms_values['voltage']:.2f}")
            self.current_label.config(text=f"Current (A RMS): {rms_values['current']:.2f}")
            self.freq_label.config(text=f"Frequency (Hz): {rms_values['frequency']:.2f}")
            self.power_label.config(text=f"Power (W): {rms_values['power']:.2f}")

            # Update plots
            if len(self.simulation.time_history) > 10:
                self.update_plots()

        # Schedule next update
        self.root.after(self.update_interval, self.update_display)

    def update_plots(self):
        """Update visualization plots"""
        if len(self.simulation.time_history) < 2:
            return

        time_data = np.array(self.simulation.time_history)
        state_data = np.array(self.simulation.state_history)

        # Clear axes
        self.ax1.clear()
        self.ax2.clear()

        # Plot based on system type
        if self.simulation.model.system_type == "generator":
            self.ax1.plot(time_data, np.degrees(state_data[:, 0]), 'b-', linewidth=1.5)
            self.ax1.set_ylabel('Rotor Angle (degrees)', fontsize=10)
            self.ax1.set_title('Generator Swing Dynamics', fontsize=11)
            self.ax1.grid(True, alpha=0.3)

            self.ax2.plot(time_data, state_data[:, 1] / (2 * np.pi), 'r-', linewidth=1.5)
            self.ax2.set_ylabel('Frequency (Hz)', fontsize=10)
            self.ax2.set_xlabel('Time (s)', fontsize=10)
            self.ax2.grid(True, alpha=0.3)
        else:
            self.ax1.plot(time_data, state_data[:, 0], 'b-', linewidth=1.5)
            self.ax1.set_ylabel('Current (A)', fontsize=10)
            self.ax1.set_title(f'{self.simulation.model.system_type.upper()} Dynamics', fontsize=11)
            self.ax1.grid(True, alpha=0.3)

            self.ax2.plot(time_data, state_data[:, 1], 'r-', linewidth=1.5)
            self.ax2.set_ylabel('Voltage (V)', fontsize=10)
            self.ax2.set_xlabel('Time (s)', fontsize=10)
            self.ax2.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        if event.widget == self.root:
            # Redraw canvas to fit new size
            if hasattr(self, 'canvas'):
                self.fig.tight_layout()
                self.canvas.draw()

    def reset_all(self):
        """Reset all data to defaults"""
        response = messagebox.askyesno("Confirm Reset", "Reset all parameters to default values?")
        if response:
            # Reset thermal data
            self.thermal_data = ThermalStationData()
            for attr, slider in self.thermal_sliders.items():
                value = getattr(self.thermal_data, attr)
                if attr == "annual_load_factor":
                    value *= 100
                if attr in ["interest_tax_plant", "depreciation_plant", "interest_tax_distribution"]:
                    value *= 100
                slider.set(value)

            # Reset simulation
            self.reset_simulation()

            # Clear results
            self.thermal_results_text.delete(1.0, tk.END)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "All parameters reset to default values.\n")

    def show_about(self):
        """Show about dialog"""
        about_text = """Thermal Station Cost Calculator & Electrical System Simulator

Version: 1.0

Features:
• Comprehensive thermal power station cost analysis
• Dynamic electrical system simulation with ODE solvers
• Real-time visualization of system behavior
• RK45 and Euler integration methods
• Multiple system models (Generator, RLC, Transformer)
• Auto-scaling responsive GUI

Developed for electrical engineering education and analysis.
"""
        messagebox.showinfo("About", about_text)


# ==================== Main Entry Point ====================
def main():
    """Main entry point"""
    root = tk.Tk()
    app = ThermalStationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

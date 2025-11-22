"""
Advanced Power Station Economics and Dynamic System Simulator
Combines power station cost analysis with real-time dynamic simulation
for electrical engineering applications.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Tuple
import math


# ==================== Data Classes ====================

@dataclass
class PowerStationData:
    """Data class for power station parameters"""
    max_demand_mw: float = 100.0
    load_factor: float = 0.30
    hydro_annual_kwh: float = 1e8
    hydro_max_mw: float = 40.0
    steam_capital_cost: float = 600.0  # Rs/kW
    hydro_capital_cost: float = 1500.0  # Rs/kW
    steam_interest_depreciation: float = 0.12
    hydro_interest_depreciation: float = 0.10
    steam_operating_cost: float = 0.05  # Rs/kWh (5 paise)
    hydro_operating_cost: float = 0.01  # Rs/kWh (1 paisa)
    hydro_transmission_cost: float = 0.0025  # Rs/kWh (0.25 paise)


@dataclass
class DynamicSystemState:
    """State variables for dynamic power system simulation"""
    delta: float = 0.0  # Rotor angle (radians)
    omega: float = 1.0  # Rotor speed (pu)
    pm: float = 1.0  # Mechanical power (pu)
    pe: float = 1.0  # Electrical power (pu)
    frequency: float = 50.0  # System frequency (Hz)


# ==================== Economics Calculator ====================

class PowerStationEconomics:
    """Calculate power station economics for different schemes"""

    def __init__(self, data: PowerStationData):
        self.data = data
        self.results = {}

    def calculate_annual_energy(self) -> float:
        """Calculate annual energy generated in kWh"""
        max_demand_kw = self.data.max_demand_mw * 1000
        hours_per_year = 8760
        annual_energy = max_demand_kw * self.data.load_factor * hours_per_year
        return annual_energy

    def calculate_scheme_a(self) -> dict:
        """Steam + Hydro combination"""
        annual_energy = self.calculate_annual_energy()
        hydro_energy = self.data.hydro_annual_kwh
        steam_energy = annual_energy - hydro_energy

        # Hydro capacity
        hydro_capacity_kw = self.data.hydro_max_mw * 1000

        # Steam capacity (must handle peak load minus hydro)
        steam_capacity_kw = (self.data.max_demand_mw - self.data.hydro_max_mw) * 1000

        # Capital costs
        steam_capital = steam_capacity_kw * self.data.steam_capital_cost
        hydro_capital = hydro_capacity_kw * self.data.hydro_capital_cost
        total_capital = steam_capital + hydro_capital

        # Annual fixed charges
        steam_fixed = steam_capital * self.data.steam_interest_depreciation
        hydro_fixed = hydro_capital * self.data.hydro_interest_depreciation
        total_fixed = steam_fixed + hydro_fixed

        # Operating costs
        steam_operating = steam_energy * self.data.steam_operating_cost
        hydro_operating = hydro_energy * self.data.hydro_operating_cost
        hydro_transmission = hydro_energy * self.data.hydro_transmission_cost
        total_operating = steam_operating + hydro_operating + hydro_transmission

        # Total annual cost
        total_annual_cost = total_fixed + total_operating

        # Cost per unit
        cost_per_unit = total_annual_cost / annual_energy

        return {
            'scheme': 'Steam + Hydro',
            'steam_capacity_kw': steam_capacity_kw,
            'hydro_capacity_kw': hydro_capacity_kw,
            'total_capacity_kw': steam_capacity_kw + hydro_capacity_kw,
            'steam_energy_kwh': steam_energy,
            'hydro_energy_kwh': hydro_energy,
            'annual_energy_kwh': annual_energy,
            'steam_capital': steam_capital,
            'hydro_capital': hydro_capital,
            'total_capital': total_capital,
            'steam_fixed': steam_fixed,
            'hydro_fixed': hydro_fixed,
            'total_fixed': total_fixed,
            'steam_operating': steam_operating,
            'hydro_operating': hydro_operating,
            'hydro_transmission': hydro_transmission,
            'total_operating': total_operating,
            'total_annual_cost': total_annual_cost,
            'cost_per_unit': cost_per_unit
        }

    def calculate_scheme_b(self) -> dict:
        """Steam only"""
        annual_energy = self.calculate_annual_energy()
        steam_capacity_kw = self.data.max_demand_mw * 1000

        # Capital cost
        steam_capital = steam_capacity_kw * self.data.steam_capital_cost

        # Annual fixed charges
        steam_fixed = steam_capital * self.data.steam_interest_depreciation

        # Operating costs
        steam_operating = annual_energy * self.data.steam_operating_cost

        # Total annual cost
        total_annual_cost = steam_fixed + steam_operating

        # Cost per unit
        cost_per_unit = total_annual_cost / annual_energy

        return {
            'scheme': 'Steam Only',
            'steam_capacity_kw': steam_capacity_kw,
            'annual_energy_kwh': annual_energy,
            'steam_capital': steam_capital,
            'steam_fixed': steam_fixed,
            'steam_operating': steam_operating,
            'total_annual_cost': total_annual_cost,
            'cost_per_unit': cost_per_unit
        }

    def calculate_scheme_c(self) -> dict:
        """Hydro only"""
        annual_energy = self.calculate_annual_energy()
        hydro_capacity_kw = self.data.max_demand_mw * 1000

        # Capital cost
        hydro_capital = hydro_capacity_kw * self.data.hydro_capital_cost

        # Annual fixed charges
        hydro_fixed = hydro_capital * self.data.hydro_interest_depreciation

        # Operating costs
        hydro_operating = annual_energy * self.data.hydro_operating_cost
        hydro_transmission = annual_energy * self.data.hydro_transmission_cost

        # Total annual cost
        total_annual_cost = hydro_fixed + hydro_operating + hydro_transmission

        # Cost per unit
        cost_per_unit = total_annual_cost / annual_energy

        return {
            'scheme': 'Hydro Only',
            'hydro_capacity_kw': hydro_capacity_kw,
            'annual_energy_kwh': annual_energy,
            'hydro_capital': hydro_capital,
            'hydro_fixed': hydro_fixed,
            'hydro_operating': hydro_operating,
            'hydro_transmission': hydro_transmission,
            'total_annual_cost': total_annual_cost,
            'cost_per_unit': cost_per_unit
        }

    def calculate_all_schemes(self) -> dict:
        """Calculate all schemes and return results"""
        self.results = {
            'scheme_a': self.calculate_scheme_a(),
            'scheme_b': self.calculate_scheme_b(),
            'scheme_c': self.calculate_scheme_c()
        }
        return self.results


# ==================== ODE Solvers ====================

class ODESolver:
    """Base class for ODE solvers"""

    @staticmethod
    def euler(f: Callable, t: float, y: np.ndarray, h: float) -> np.ndarray:
        """Euler method for solving ODEs"""
        return y + h * f(t, y)

    @staticmethod
    def rk45(f: Callable, t: float, y: np.ndarray, h: float) -> np.ndarray:
        """Runge-Kutta 4th/5th order method (RK45)"""
        # Standard RK4 implementation (simplified version of RK45)
        k1 = f(t, y)
        k2 = f(t + h/2, y + h*k1/2)
        k3 = f(t + h/2, y + h*k2/2)
        k4 = f(t + h, y + h*k3)
        return y + h * (k1 + 2*k2 + 2*k3 + k4) / 6


# ==================== Dynamic Power System Simulator ====================

class PowerSystemDynamics:
    """
    Dynamic simulation of synchronous generator with swing equation
    Models transient stability and frequency dynamics
    """

    def __init__(self):
        # System parameters (per unit)
        self.M = 10.0  # Inertia constant (seconds)
        self.D = 2.0   # Damping coefficient
        self.Pmax = 2.0  # Maximum power transfer
        self.omega_0 = 2 * np.pi * 50  # Synchronous speed (rad/s)
        self.fault_time = None
        self.fault_duration = 0.0
        self.fault_active = False

    def swing_equation(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Swing equation for synchronous generator
        y[0] = delta (rotor angle in radians)
        y[1] = omega (rotor speed in pu)
        """
        delta, omega = y

        # Electrical power (Pe = Pmax * sin(delta))
        if self.fault_active and self.fault_time is not None:
            if t >= self.fault_time and t < self.fault_time + self.fault_duration:
                Pe = 0  # Fault condition
            else:
                Pe = self.Pmax * np.sin(delta)
        else:
            Pe = self.Pmax * np.sin(delta)

        # Mechanical power (constant)
        Pm = self.Pmax * np.sin(0.5)  # Operating point

        # Swing equation: M * d(omega)/dt = Pm - Pe - D*(omega - 1)
        d_omega = (Pm - Pe - self.D * (omega - 1.0)) / self.M
        d_delta = self.omega_0 * (omega - 1.0)

        return np.array([d_delta, d_omega])

    def update_parameters(self, inertia: float, damping: float, pmax: float):
        """Update system parameters"""
        self.M = inertia
        self.D = damping
        self.Pmax = pmax

    def set_fault(self, fault_time: float, duration: float):
        """Set fault parameters"""
        self.fault_time = fault_time
        self.fault_duration = duration
        self.fault_active = True


# ==================== Main GUI Application ====================

class PowerStationSimulatorGUI:
    """Main application with advanced GUI"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Power Station Dynamic Simulator")
        self.root.geometry("1400x900")

        # Data and simulation objects
        self.ps_data = PowerStationData()
        self.economics = PowerStationEconomics(self.ps_data)
        self.dynamics = PowerSystemDynamics()
        self.solver = ODESolver()

        # Simulation state
        self.simulation_running = False
        self.simulation_thread = None
        self.current_time = 0.0
        self.dt = 0.01  # Time step
        self.state = np.array([0.5, 1.0])  # Initial state [delta, omega]
        self.solver_method = 'rk45'

        # Data storage for plotting
        self.time_data = []
        self.delta_data = []
        self.omega_data = []
        self.power_data = []
        self.max_points = 1000

        # Create GUI
        self.create_menu()
        self.create_widgets()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def create_menu(self):
        """Create main menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Calculate Economics", command=self.show_economics)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start", command=self.start_simulation)
        sim_menu.add_command(label="Stop", command=self.stop_simulation)
        sim_menu.add_command(label="Reset", command=self.reset_simulation)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="System Parameters", command=self.show_parameters)
        settings_menu.add_command(label="Solver Settings", command=self.show_solver_settings)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        """Create main GUI widgets"""
        # Main container with grid layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure root grid weights for auto-scaling
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)

        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Right panel - Visualization
        viz_frame = ttk.LabelFrame(main_frame, text="Real-Time Visualization", padding="10")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)

        # Create control widgets
        self.create_control_panel(control_frame)

        # Create visualization
        self.create_visualization(viz_frame)

    def create_control_panel(self, parent):
        """Create control panel with sliders and buttons"""
        row = 0

        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(button_frame, text="▶ Start", command=self.start_simulation, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation, width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(button_frame, text="⟲ Reset", command=self.reset_simulation, width=12)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # System parameters label
        ttk.Label(parent, text="System Parameters", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        # Inertia constant slider
        ttk.Label(parent, text="Inertia Constant (M):").grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.inertia_var = tk.DoubleVar(value=10.0)
        self.inertia_slider = ttk.Scale(parent, from_=1.0, to=50.0, orient=tk.HORIZONTAL,
                                        variable=self.inertia_var, command=self.update_parameters)
        self.inertia_slider.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.inertia_label = ttk.Label(parent, text=f"{self.inertia_var.get():.2f} s")
        self.inertia_label.grid(row=row, column=1, sticky=tk.E)
        row += 1

        # Damping coefficient slider
        ttk.Label(parent, text="Damping Coefficient (D):").grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.damping_var = tk.DoubleVar(value=2.0)
        self.damping_slider = ttk.Scale(parent, from_=0.1, to=10.0, orient=tk.HORIZONTAL,
                                       variable=self.damping_var, command=self.update_parameters)
        self.damping_slider.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.damping_label = ttk.Label(parent, text=f"{self.damping_var.get():.2f}")
        self.damping_label.grid(row=row, column=1, sticky=tk.E)
        row += 1

        # Maximum power slider
        ttk.Label(parent, text="Max Power Transfer (Pmax):").grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.pmax_var = tk.DoubleVar(value=2.0)
        self.pmax_slider = ttk.Scale(parent, from_=0.5, to=5.0, orient=tk.HORIZONTAL,
                                    variable=self.pmax_var, command=self.update_parameters)
        self.pmax_slider.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.pmax_label = ttk.Label(parent, text=f"{self.pmax_var.get():.2f} pu")
        self.pmax_label.grid(row=row, column=1, sticky=tk.E)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Fault simulation
        ttk.Label(parent, text="Fault Simulation", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        ttk.Label(parent, text="Fault Duration (s):").grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.fault_duration_var = tk.DoubleVar(value=0.1)
        self.fault_slider = ttk.Scale(parent, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                     variable=self.fault_duration_var)
        self.fault_slider.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.fault_label = ttk.Label(parent, text=f"{self.fault_duration_var.get():.3f} s")
        self.fault_label.grid(row=row, column=1, sticky=tk.E)
        row += 1

        self.fault_btn = ttk.Button(parent, text="Apply Fault", command=self.apply_fault)
        self.fault_btn.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Solver selection
        ttk.Label(parent, text="ODE Solver:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.solver_var = tk.StringVar(value='rk45')
        ttk.Radiobutton(parent, text="RK45 (4th/5th Order)", variable=self.solver_var,
                       value='rk45').grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        ttk.Radiobutton(parent, text="Euler (1st Order)", variable=self.solver_var,
                       value='euler').grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1

        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Status display
        ttk.Label(parent, text="Status Information", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        self.status_text = scrolledtext.ScrolledText(parent, height=10, width=30, wrap=tk.WORD)
        self.status_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Economics button
        row += 1
        ttk.Button(parent, text="📊 View Economics Analysis",
                  command=self.show_economics).grid(row=row, column=0, columnspan=2, pady=10)

    def create_visualization(self, parent):
        """Create real-time visualization plots"""
        # Create matplotlib figure with subplots
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')

        # Create subplots
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)

        # Configure subplots
        self.ax1.set_title('Rotor Angle (δ)', fontweight='bold')
        self.ax1.set_ylabel('Angle (rad)')
        self.ax1.grid(True, alpha=0.3)

        self.ax2.set_title('Rotor Speed (ω)', fontweight='bold')
        self.ax2.set_ylabel('Speed (pu)')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Synchronous speed')

        self.ax3.set_title('Electrical Power (Pe)', fontweight='bold')
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Power (pu)')
        self.ax3.grid(True, alpha=0.3)

        # Initialize lines
        self.line1, = self.ax1.plot([], [], 'b-', linewidth=2)
        self.line2, = self.ax2.plot([], [], 'g-', linewidth=2)
        self.line3, = self.ax3.plot([], [], 'r-', linewidth=2)

        self.fig.tight_layout()

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def update_parameters(self, event=None):
        """Update system parameters from sliders"""
        inertia = self.inertia_var.get()
        damping = self.damping_var.get()
        pmax = self.pmax_var.get()

        self.dynamics.update_parameters(inertia, damping, pmax)

        # Update labels
        self.inertia_label.config(text=f"{inertia:.2f} s")
        self.damping_label.config(text=f"{damping:.2f}")
        self.pmax_label.config(text=f"{pmax:.2f} pu")

        self.update_status(f"Parameters updated: M={inertia:.2f}, D={damping:.2f}, Pmax={pmax:.2f}")

    def apply_fault(self):
        """Apply fault to the system"""
        if self.simulation_running:
            duration = self.fault_duration_var.get()
            self.dynamics.set_fault(self.current_time, duration)
            self.update_status(f"Fault applied at t={self.current_time:.2f}s, duration={duration:.3f}s")
            self.fault_label.config(text=f"{duration:.3f} s")

    def start_simulation(self):
        """Start the dynamic simulation"""
        if not self.simulation_running:
            self.simulation_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            # Start simulation thread
            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()

            self.update_status("Simulation started")

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("Simulation stopped")

    def reset_simulation(self):
        """Reset simulation to initial conditions"""
        was_running = self.simulation_running
        self.stop_simulation()

        # Reset state
        self.current_time = 0.0
        self.state = np.array([0.5, 1.0])
        self.time_data.clear()
        self.delta_data.clear()
        self.omega_data.clear()
        self.power_data.clear()
        self.dynamics.fault_active = False

        # Clear plots
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        self.line3.set_data([], [])
        self.canvas.draw()

        self.update_status("Simulation reset to initial conditions")

        if was_running:
            self.root.after(100, self.start_simulation)

    def run_simulation(self):
        """Main simulation loop"""
        while self.simulation_running:
            # Select solver
            solver_method = self.solver_var.get()

            # Solve ODE
            if solver_method == 'rk45':
                self.state = self.solver.rk45(self.dynamics.swing_equation,
                                             self.current_time, self.state, self.dt)
            else:  # euler
                self.state = self.solver.euler(self.dynamics.swing_equation,
                                              self.current_time, self.state, self.dt)

            # Calculate electrical power
            delta = self.state[0]
            Pe = self.dynamics.Pmax * np.sin(delta)

            # Store data
            self.time_data.append(self.current_time)
            self.delta_data.append(delta)
            self.omega_data.append(self.state[1])
            self.power_data.append(Pe)

            # Limit data points
            if len(self.time_data) > self.max_points:
                self.time_data.pop(0)
                self.delta_data.pop(0)
                self.omega_data.pop(0)
                self.power_data.pop(0)

            # Update plots
            self.root.after(0, self.update_plots)

            # Increment time
            self.current_time += self.dt

            # Control simulation speed
            time.sleep(self.dt)

    def update_plots(self):
        """Update visualization plots"""
        if len(self.time_data) > 1:
            # Update data
            self.line1.set_data(self.time_data, self.delta_data)
            self.line2.set_data(self.time_data, self.omega_data)
            self.line3.set_data(self.time_data, self.power_data)

            # Auto-scale axes
            self.ax1.relim()
            self.ax1.autoscale_view()

            self.ax2.relim()
            self.ax2.autoscale_view()

            self.ax3.relim()
            self.ax3.autoscale_view()

            # Redraw canvas
            self.canvas.draw()

    def update_status(self, message: str):
        """Update status text"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)

    def on_window_resize(self, event):
        """Handle window resize event for auto-scaling"""
        if event.widget == self.root:
            try:
                self.fig.tight_layout()
                self.canvas.draw()
            except:
                pass

    def show_economics(self):
        """Show economics analysis window"""
        results = self.economics.calculate_all_schemes()

        # Create new window
        econ_window = tk.Toplevel(self.root)
        econ_window.title("Power Station Economics Analysis")
        econ_window.geometry("900x700")

        # Create notebook for tabs
        notebook = ttk.Notebook(econ_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs for each scheme
        self.create_scheme_tab(notebook, results['scheme_a'], "Scheme A: Steam + Hydro")
        self.create_scheme_tab(notebook, results['scheme_b'], "Scheme B: Steam Only")
        self.create_scheme_tab(notebook, results['scheme_c'], "Scheme C: Hydro Only")

        # Summary tab
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Summary & Comparison")

        # Summary text
        summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD,
                                                 font=('Courier', 10))
        summary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Generate summary
        summary = self.generate_summary(results)
        summary_text.insert(tk.END, summary)
        summary_text.config(state=tk.DISABLED)

    def create_scheme_tab(self, notebook, data: dict, title: str):
        """Create tab for scheme details"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)

        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD,
                                                font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format and display data
        content = f"\n{'='*80}\n"
        content += f"{data['scheme'].center(80)}\n"
        content += f"{'='*80}\n\n"

        # Installed Capacity
        content += "INSTALLED CAPACITY:\n"
        content += "-" * 80 + "\n"
        if 'steam_capacity_kw' in data:
            content += f"  Steam Capacity:        {data['steam_capacity_kw']:>15,.0f} kW\n"
        if 'hydro_capacity_kw' in data:
            content += f"  Hydro Capacity:        {data['hydro_capacity_kw']:>15,.0f} kW\n"
        if 'total_capacity_kw' in data:
            content += f"  Total Capacity:        {data['total_capacity_kw']:>15,.0f} kW\n"
        content += "\n"

        # Annual Energy
        content += "ANNUAL ENERGY GENERATION:\n"
        content += "-" * 80 + "\n"
        if 'steam_energy_kwh' in data:
            content += f"  Steam Energy:          {data['steam_energy_kwh']:>15,.0f} kWh\n"
        if 'hydro_energy_kwh' in data:
            content += f"  Hydro Energy:          {data['hydro_energy_kwh']:>15,.0f} kWh\n"
        content += f"  Total Energy:          {data['annual_energy_kwh']:>15,.0f} kWh\n"
        content += "\n"

        # Capital Costs
        content += "CAPITAL COSTS:\n"
        content += "-" * 80 + "\n"
        if 'steam_capital' in data:
            content += f"  Steam Capital:         Rs. {data['steam_capital']:>15,.2f}\n"
        if 'hydro_capital' in data:
            content += f"  Hydro Capital:         Rs. {data['hydro_capital']:>15,.2f}\n"
        if 'total_capital' in data:
            content += f"  Total Capital:         Rs. {data['total_capital']:>15,.2f}\n"
        content += "\n"

        # Annual Fixed Charges
        content += "ANNUAL FIXED CHARGES (Interest + Depreciation):\n"
        content += "-" * 80 + "\n"
        if 'steam_fixed' in data:
            content += f"  Steam Fixed:           Rs. {data['steam_fixed']:>15,.2f}\n"
        if 'hydro_fixed' in data:
            content += f"  Hydro Fixed:           Rs. {data['hydro_fixed']:>15,.2f}\n"
        if 'total_fixed' in data:
            content += f"  Total Fixed:           Rs. {data['total_fixed']:>15,.2f}\n"
        content += "\n"

        # Operating Costs
        content += "ANNUAL OPERATING COSTS:\n"
        content += "-" * 80 + "\n"
        if 'steam_operating' in data:
            content += f"  Steam Operating:       Rs. {data['steam_operating']:>15,.2f}\n"
        if 'hydro_operating' in data:
            content += f"  Hydro Operating:       Rs. {data['hydro_operating']:>15,.2f}\n"
        if 'hydro_transmission' in data:
            content += f"  Hydro Transmission:    Rs. {data['hydro_transmission']:>15,.2f}\n"
        if 'total_operating' in data:
            content += f"  Total Operating:       Rs. {data['total_operating']:>15,.2f}\n"
        content += "\n"

        # Total Cost
        content += "=" * 80 + "\n"
        content += f"TOTAL ANNUAL COST:     Rs. {data['total_annual_cost']:>15,.2f}\n"
        content += "=" * 80 + "\n\n"

        # Cost per unit
        content += "=" * 80 + "\n"
        content += f"COST PER UNIT:         Rs. {data['cost_per_unit']:>15,.4f} /kWh\n"
        content += "=" * 80 + "\n"

        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

    def generate_summary(self, results: dict) -> str:
        """Generate summary comparison"""
        summary = "\n" + "="*80 + "\n"
        summary += "POWER STATION ECONOMICS - COMPREHENSIVE SUMMARY\n"
        summary += "="*80 + "\n\n"

        summary += "PROBLEM STATEMENT:\n"
        summary += "-" * 80 + "\n"
        summary += f"Maximum Demand:                {self.ps_data.max_demand_mw} MW\n"
        summary += f"Load Factor:                   {self.ps_data.load_factor*100}%\n"
        summary += f"Annual Energy Requirement:     {results['scheme_a']['annual_energy_kwh']:,.0f} kWh\n"
        summary += "\n"

        summary += "SCHEME COMPARISON:\n"
        summary += "="*80 + "\n"
        summary += f"{'Scheme':<30} {'Cost per Unit (Rs/kWh)':<25} {'Total Annual Cost':<25}\n"
        summary += "-" * 80 + "\n"

        schemes = [
            ('Scheme A: Steam + Hydro', results['scheme_a']),
            ('Scheme B: Steam Only', results['scheme_b']),
            ('Scheme C: Hydro Only', results['scheme_c'])
        ]

        min_cost = min(s[1]['cost_per_unit'] for s in schemes)

        for name, data in schemes:
            marker = " ← MOST ECONOMICAL" if data['cost_per_unit'] == min_cost else ""
            summary += f"{name:<30} Rs. {data['cost_per_unit']:<20.4f} Rs. {data['total_annual_cost']:>18,.2f}{marker}\n"

        summary += "="*80 + "\n\n"

        summary += "DETAILED BREAKDOWN:\n"
        summary += "-" * 80 + "\n"

        for name, data in schemes:
            summary += f"\n{name}:\n"
            summary += f"  Cost per unit: Rs. {data['cost_per_unit']:.4f}/kWh\n"
            summary += f"  Total annual cost: Rs. {data['total_annual_cost']:,.2f}\n"

        summary += "\n" + "="*80 + "\n"
        summary += "RECOMMENDATION:\n"
        summary += "-" * 80 + "\n"

        best_scheme = min(schemes, key=lambda x: x[1]['cost_per_unit'])
        summary += f"The most economical scheme is {best_scheme[0]}\n"
        summary += f"with a cost of Rs. {best_scheme[1]['cost_per_unit']:.4f} per kWh.\n"
        summary += "\n"

        # Calculate savings
        for name, data in schemes:
            if data != best_scheme[1]:
                savings = data['cost_per_unit'] - best_scheme[1]['cost_per_unit']
                savings_pct = (savings / data['cost_per_unit']) * 100
                summary += f"Savings vs {name}: Rs. {savings:.4f}/kWh ({savings_pct:.2f}%)\n"

        summary += "="*80 + "\n"

        return summary

    def show_parameters(self):
        """Show system parameters dialog"""
        messagebox.showinfo("System Parameters",
                          f"Current System Parameters:\n\n"
                          f"Inertia Constant (M): {self.dynamics.M:.2f} s\n"
                          f"Damping Coefficient (D): {self.dynamics.D:.2f}\n"
                          f"Max Power Transfer (Pmax): {self.dynamics.Pmax:.2f} pu\n"
                          f"Synchronous Speed: {self.dynamics.omega_0/(2*np.pi):.2f} Hz")

    def show_solver_settings(self):
        """Show solver settings dialog"""
        current_solver = self.solver_var.get()
        messagebox.showinfo("Solver Settings",
                          f"Current ODE Solver: {current_solver.upper()}\n\n"
                          f"Time Step (dt): {self.dt} s\n"
                          f"Max Data Points: {self.max_points}\n\n"
                          f"RK45: 4th/5th order Runge-Kutta (more accurate)\n"
                          f"Euler: 1st order explicit method (faster)")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About",
                          "Advanced Power Station Dynamic Simulator\n\n"
                          "Version 1.0\n\n"
                          "Features:\n"
                          "• Power station economics analysis\n"
                          "• Real-time dynamic simulation\n"
                          "• Swing equation modeling\n"
                          "• Transient stability analysis\n"
                          "• Multiple ODE solvers (RK45, Euler)\n"
                          "• Interactive visualization\n"
                          "• Fault simulation\n\n"
                          "Developed for electrical engineering applications")


# ==================== Main Entry Point ====================

def main():
    """Main entry point"""
    root = tk.Tk()
    app = PowerStationSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

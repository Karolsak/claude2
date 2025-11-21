#!/usr/bin/env python3
"""
Advanced Electrical Engineering Multi-Physics Simulator
Includes: Lighting Design, Electrical Machines, Thermal Analysis, Control Systems
"""

import tkinter as tk
from tkinter import ttk, messagebox, Menu
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.integrate import solve_ivp, odeint
import threading
import time
from dataclasses import dataclass
from typing import Tuple, List
import math

@dataclass
class SimulationParameters:
    """Parameters for electrical system simulation"""
    voltage: float = 400.0  # Voltage (V) RMS
    frequency: float = 50.0  # Frequency (Hz)
    resistance: float = 10.0  # Resistance (Ohm)
    inductance: float = 0.1  # Inductance (H)
    capacitance: float = 100e-6  # Capacitance (F)
    load_torque: float = 10.0  # Load torque (Nm)
    inertia: float = 0.05  # Moment of inertia (kg⋅m²)
    friction: float = 0.01  # Friction coefficient
    thermal_resistance: float = 5.0  # Thermal resistance (K/W)
    thermal_capacitance: float = 100.0  # Thermal capacitance (J/K)
    ambient_temp: float = 25.0  # Ambient temperature (°C)
    magnetic_flux: float = 0.8  # Magnetic flux (Wb)
    pole_pairs: int = 2  # Number of pole pairs

class LightingCalculator:
    """Football pitch lighting calculator"""

    @staticmethod
    def calculate_lamps(pitch_length: float, pitch_width: float,
                       illumination: float, efficiency_factor: float,
                       lamp_power: float, lamp_efficiency: float,
                       num_towers: int) -> dict:
        """
        Calculate lighting requirements for football pitch

        Args:
            pitch_length: Length of pitch (m)
            pitch_width: Width of pitch (m)
            illumination: Required illumination (lm/m²)
            efficiency_factor: Fraction of light reaching pitch
            lamp_power: Power per lamp (W)
            lamp_efficiency: Lamp efficiency (lm/W)
            num_towers: Number of light towers

        Returns:
            Dictionary with calculation results
        """
        pitch_area = pitch_length * pitch_width
        total_lumens_required = pitch_area * illumination
        total_lumens_emitted = total_lumens_required / efficiency_factor
        lumens_per_lamp = lamp_power * lamp_efficiency
        total_lamps = int(np.ceil(total_lumens_emitted / lumens_per_lamp))
        lamps_per_tower = int(np.ceil(total_lamps / num_towers))
        total_power = total_lamps * lamp_power

        return {
            'pitch_area': pitch_area,
            'total_lumens_required': total_lumens_required,
            'total_lumens_emitted': total_lumens_emitted,
            'lumens_per_lamp': lumens_per_lamp,
            'total_lamps': total_lamps,
            'lamps_per_tower': lamps_per_tower,
            'total_power': total_power,
            'power_per_tower': lamps_per_tower * lamp_power
        }

class ElectricalMachineModel:
    """Multi-physics electrical machine model with RLC circuit and thermal dynamics"""

    def __init__(self, params: SimulationParameters):
        self.params = params
        self.time_history = []
        self.state_history = []
        self.current_state = None
        self.running = False

    def rlc_motor_dynamics(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Differential equations for RLC circuit coupled with motor dynamics and thermal model

        State vector y = [i, q, omega, theta, T]
        i: current (A)
        q: charge on capacitor (C)
        omega: angular velocity (rad/s)
        theta: rotor angle (rad)
        T: temperature (°C)
        """
        i, q, omega, theta, T = y
        params = self.params

        # RMS voltage to peak voltage for sinusoidal source
        V_peak = params.voltage * np.sqrt(2)
        V_source = V_peak * np.sin(2 * np.pi * params.frequency * t)

        # Electrical equations (RLC circuit with back-EMF)
        # Back-EMF from motor rotation
        k_e = params.magnetic_flux * params.pole_pairs  # EMF constant
        back_emf = k_e * omega

        # KVL: V_source = L*di/dt + R*i + V_c + back_emf
        # V_c = q/C
        V_c = q / params.capacitance if params.capacitance > 0 else 0
        di_dt = (V_source - params.resistance * i - V_c - back_emf) / params.inductance

        # Capacitor: i = C*dV_c/dt = dq/dt
        dq_dt = i

        # Mechanical equations (motor dynamics)
        # Torque from current
        k_t = params.magnetic_flux * params.pole_pairs  # Torque constant
        T_motor = k_t * i

        # Newton's equation: J*d(omega)/dt = T_motor - T_load - B*omega
        domega_dt = (T_motor - params.load_torque - params.friction * omega) / params.inertia

        # Rotor angle
        dtheta_dt = omega

        # Thermal equation
        # Power dissipation
        P_copper = params.resistance * i**2  # Copper losses
        P_friction = params.friction * omega**2  # Friction losses
        P_total = P_copper + P_friction

        # Thermal dynamics: C_th * dT/dt = P_total - (T - T_ambient)/R_th
        dT_dt = (P_total - (T - params.ambient_temp) / params.thermal_resistance) / params.thermal_capacitance

        return np.array([di_dt, dq_dt, domega_dt, dtheta_dt, dT_dt])

    def simulate_euler(self, t_span: Tuple[float, float], dt: float, y0: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Euler method ODE solver"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(1, len(t)):
            dy = self.rlc_motor_dynamics(t[i-1], y[i-1])
            y[i] = y[i-1] + dy * dt

        return t, y

    def simulate_rk45(self, t_span: Tuple[float, float], y0: np.ndarray, max_step: float = 0.001) -> Tuple[np.ndarray, np.ndarray]:
        """RK45 (Runge-Kutta 4th/5th order) ODE solver"""
        sol = solve_ivp(
            self.rlc_motor_dynamics,
            t_span,
            y0,
            method='RK45',
            max_step=max_step,
            dense_output=True
        )
        return sol.t, sol.y.T

    def calculate_rms_values(self, current: np.ndarray, voltage_source: np.ndarray) -> Tuple[float, float]:
        """Calculate RMS values of current and voltage"""
        i_rms = np.sqrt(np.mean(current**2))
        v_rms = np.sqrt(np.mean(voltage_source**2))
        return i_rms, v_rms

    def calculate_power_factor(self, time: np.ndarray, current: np.ndarray) -> float:
        """Calculate power factor"""
        V_peak = self.params.voltage * np.sqrt(2)
        voltage = V_peak * np.sin(2 * np.pi * self.params.frequency * time)

        # Average power
        P_avg = np.mean(voltage * current)

        # RMS values
        V_rms = self.params.voltage
        I_rms = np.sqrt(np.mean(current**2))

        # Apparent power
        S = V_rms * I_rms

        # Power factor
        pf = P_avg / S if S > 0 else 0
        return pf

    def calculate_magnetic_field(self, current: float) -> float:
        """Calculate magnetic field strength (simplified model)"""
        # B = μ₀ * N * I / l (for solenoid)
        mu_0 = 4 * np.pi * 1e-7  # Permeability of free space
        N = 100  # Number of turns
        l = 0.1  # Effective length (m)
        B = mu_0 * N * current / l
        return B

    def calculate_efficiency(self, current: float, omega: float) -> float:
        """Calculate machine efficiency"""
        # Input power (average)
        P_in = self.params.voltage * abs(current)

        # Output power
        k_t = self.params.magnetic_flux * self.params.pole_pairs
        T_motor = k_t * current
        P_out = T_motor * omega

        # Efficiency
        efficiency = (P_out / P_in * 100) if P_in > 0 else 0
        return max(0, min(100, efficiency))  # Clamp between 0-100%

class ElectricalEngineeringApp:
    """Main application class"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Advanced Electrical Engineering Multi-Physics Simulator")
        self.root.geometry("1400x900")

        # Simulation state
        self.params = SimulationParameters()
        self.model = ElectricalMachineModel(self.params)
        self.simulation_running = False
        self.simulation_thread = None

        # Data storage
        self.time_data = []
        self.current_data = []
        self.voltage_data = []
        self.speed_data = []
        self.temperature_data = []
        self.magnetic_field_data = []

        # Create UI
        self.create_menu()
        self.create_ui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_resize)

    def create_menu(self):
        """Create main menu"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset All", command=self.reset_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Lighting Calculator", command=self.show_lighting_calculator)
        tools_menu.add_command(label="Power Analysis", command=self.show_power_analysis)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_ui(self):
        """Create main user interface"""
        # Main container with two panes
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - Controls
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, width=400)

        # Right panel - Visualization
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame)

        # Create control panels
        self.create_control_panel(left_frame)

        # Create visualization panel
        self.create_visualization_panel(right_frame)

    def create_control_panel(self, parent):
        """Create control panel with input parameters and sliders"""
        # Control buttons frame
        button_frame = ttk.LabelFrame(parent, text="Simulation Control", padding=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        btn_frame = ttk.Frame(button_frame)
        btn_frame.pack()

        self.start_btn = ttk.Button(btn_frame, text="▶ Start", command=self.start_simulation, width=12)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)

        self.stop_btn = ttk.Button(btn_frame, text="⏸ Stop", command=self.stop_simulation, width=12, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)

        self.reset_btn = ttk.Button(btn_frame, text="↻ Reset", command=self.reset_simulation, width=12)
        self.reset_btn.grid(row=0, column=2, padx=5, pady=5)

        # Solver selection
        solver_frame = ttk.Frame(button_frame)
        solver_frame.pack(pady=5)

        ttk.Label(solver_frame, text="ODE Solver:").pack(side=tk.LEFT, padx=5)
        self.solver_var = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(solver_frame, textvariable=self.solver_var,
                                    values=["RK45", "Euler"], state="readonly", width=10)
        solver_combo.pack(side=tk.LEFT, padx=5)

        # Scrollable parameter frame
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Electrical Parameters
        self.create_parameter_section(scrollable_frame, "Electrical Parameters", [
            ("Voltage (V RMS)", 0, 1000, self.params.voltage, 'voltage'),
            ("Frequency (Hz)", 1, 100, self.params.frequency, 'frequency'),
            ("Resistance (Ω)", 0.1, 100, self.params.resistance, 'resistance'),
            ("Inductance (H)", 0.01, 1.0, self.params.inductance, 'inductance'),
            ("Capacitance (μF)", 1, 1000, self.params.capacitance * 1e6, 'capacitance', 1e-6),
        ])

        # Mechanical Parameters
        self.create_parameter_section(scrollable_frame, "Mechanical Parameters", [
            ("Load Torque (Nm)", 0, 50, self.params.load_torque, 'load_torque'),
            ("Inertia (kg⋅m²)", 0.01, 0.5, self.params.inertia, 'inertia'),
            ("Friction Coeff.", 0.001, 0.1, self.params.friction, 'friction'),
        ])

        # Magnetic Parameters
        self.create_parameter_section(scrollable_frame, "Magnetic Parameters", [
            ("Magnetic Flux (Wb)", 0.1, 2.0, self.params.magnetic_flux, 'magnetic_flux'),
            ("Pole Pairs", 1, 8, self.params.pole_pairs, 'pole_pairs'),
        ])

        # Thermal Parameters
        self.create_parameter_section(scrollable_frame, "Thermal Parameters", [
            ("Thermal Res. (K/W)", 1, 20, self.params.thermal_resistance, 'thermal_resistance'),
            ("Thermal Cap. (J/K)", 10, 500, self.params.thermal_capacitance, 'thermal_capacitance'),
            ("Ambient Temp. (°C)", -20, 50, self.params.ambient_temp, 'ambient_temp'),
        ])

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar at bottom
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def create_parameter_section(self, parent, title, parameters):
        """Create a section of parameter sliders"""
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)

        for label, min_val, max_val, default, param_name, *multiplier in parameters:
            mult = multiplier[0] if multiplier else 1.0

            param_frame = ttk.Frame(frame)
            param_frame.pack(fill=tk.X, pady=3)

            ttk.Label(param_frame, text=label, width=20).pack(side=tk.LEFT)

            var = tk.DoubleVar(value=default)

            scale = ttk.Scale(param_frame, from_=min_val, to=max_val,
                            orient=tk.HORIZONTAL, variable=var,
                            command=lambda v, p=param_name, m=mult, va=var: self.update_parameter(p, va.get() * m))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            value_label = ttk.Label(param_frame, text=f"{default:.2f}", width=8)
            value_label.pack(side=tk.LEFT)

            # Update label when slider changes
            var.trace('w', lambda *args, vl=value_label, va=var: vl.config(text=f"{va.get():.2f}"))

    def create_visualization_panel(self, parent):
        """Create visualization panel with plots"""
        # Notebook for multiple tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Electrical Signals
        electrical_frame = ttk.Frame(notebook)
        notebook.add(electrical_frame, text="Electrical Signals")

        self.fig_electrical = Figure(figsize=(10, 8), dpi=100)
        self.ax_current = self.fig_electrical.add_subplot(2, 1, 1)
        self.ax_voltage = self.fig_electrical.add_subplot(2, 1, 2)

        self.ax_current.set_xlabel('Time (s)')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Current vs Time')
        self.ax_current.grid(True, alpha=0.3)

        self.ax_voltage.set_xlabel('Time (s)')
        self.ax_voltage.set_ylabel('Capacitor Voltage (V)')
        self.ax_voltage.set_title('Capacitor Voltage vs Time')
        self.ax_voltage.grid(True, alpha=0.3)

        self.canvas_electrical = FigureCanvasTkAgg(self.fig_electrical, electrical_frame)
        self.canvas_electrical.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tab 2: Mechanical Signals
        mechanical_frame = ttk.Frame(notebook)
        notebook.add(mechanical_frame, text="Mechanical Signals")

        self.fig_mechanical = Figure(figsize=(10, 8), dpi=100)
        self.ax_speed = self.fig_mechanical.add_subplot(2, 1, 1)
        self.ax_torque = self.fig_mechanical.add_subplot(2, 1, 2)

        self.ax_speed.set_xlabel('Time (s)')
        self.ax_speed.set_ylabel('Angular Speed (rad/s)')
        self.ax_speed.set_title('Angular Speed vs Time')
        self.ax_speed.grid(True, alpha=0.3)

        self.ax_torque.set_xlabel('Time (s)')
        self.ax_torque.set_ylabel('Torque (Nm)')
        self.ax_torque.set_title('Motor Torque vs Time')
        self.ax_torque.grid(True, alpha=0.3)

        self.canvas_mechanical = FigureCanvasTkAgg(self.fig_mechanical, mechanical_frame)
        self.canvas_mechanical.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tab 3: Thermal & Magnetic
        thermal_frame = ttk.Frame(notebook)
        notebook.add(thermal_frame, text="Thermal & Magnetic")

        self.fig_thermal = Figure(figsize=(10, 8), dpi=100)
        self.ax_temp = self.fig_thermal.add_subplot(2, 1, 1)
        self.ax_magnetic = self.fig_thermal.add_subplot(2, 1, 2)

        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_title('Temperature vs Time')
        self.ax_temp.grid(True, alpha=0.3)

        self.ax_magnetic.set_xlabel('Time (s)')
        self.ax_magnetic.set_ylabel('Magnetic Field (T)')
        self.ax_magnetic.set_title('Magnetic Field vs Time')
        self.ax_magnetic.grid(True, alpha=0.3)

        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, thermal_frame)
        self.canvas_thermal.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tab 4: Power & Efficiency
        power_frame = ttk.Frame(notebook)
        notebook.add(power_frame, text="Power & Efficiency")

        self.fig_power = Figure(figsize=(10, 8), dpi=100)
        self.ax_power = self.fig_power.add_subplot(2, 1, 1)
        self.ax_efficiency = self.fig_power.add_subplot(2, 1, 2)

        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (W)')
        self.ax_power.set_title('Power Dissipation vs Time')
        self.ax_power.grid(True, alpha=0.3)

        self.ax_efficiency.set_xlabel('Time (s)')
        self.ax_efficiency.set_ylabel('Efficiency (%)')
        self.ax_efficiency.set_title('Machine Efficiency vs Time')
        self.ax_efficiency.grid(True, alpha=0.3)

        self.canvas_power = FigureCanvasTkAgg(self.fig_power, power_frame)
        self.canvas_power.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_parameter(self, param_name: str, value: float):
        """Update simulation parameter"""
        setattr(self.params, param_name, value)
        self.model.params = self.params

    def start_simulation(self):
        """Start the simulation"""
        if not self.simulation_running:
            self.simulation_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Simulation running...")

            # Clear previous data
            self.time_data = []
            self.current_data = []
            self.voltage_data = []
            self.speed_data = []
            self.temperature_data = []
            self.magnetic_field_data = []

            # Start simulation in separate thread
            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Simulation stopped")

    def reset_simulation(self):
        """Reset the simulation"""
        self.stop_simulation()

        # Clear all plots
        for ax in [self.ax_current, self.ax_voltage, self.ax_speed, self.ax_torque,
                   self.ax_temp, self.ax_magnetic, self.ax_power, self.ax_efficiency]:
            ax.clear()
            ax.grid(True, alpha=0.3)

        self.ax_current.set_xlabel('Time (s)')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Current vs Time')

        self.ax_voltage.set_xlabel('Time (s)')
        self.ax_voltage.set_ylabel('Capacitor Voltage (V)')
        self.ax_voltage.set_title('Capacitor Voltage vs Time')

        self.ax_speed.set_xlabel('Time (s)')
        self.ax_speed.set_ylabel('Angular Speed (rad/s)')
        self.ax_speed.set_title('Angular Speed vs Time')

        self.ax_torque.set_xlabel('Time (s)')
        self.ax_torque.set_ylabel('Torque (Nm)')
        self.ax_torque.set_title('Motor Torque vs Time')

        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_title('Temperature vs Time')

        self.ax_magnetic.set_xlabel('Time (s)')
        self.ax_magnetic.set_ylabel('Magnetic Field (T)')
        self.ax_magnetic.set_title('Magnetic Field vs Time')

        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (W)')
        self.ax_power.set_title('Power Dissipation vs Time')

        self.ax_efficiency.set_xlabel('Time (s)')
        self.ax_efficiency.set_ylabel('Efficiency (%)')
        self.ax_efficiency.set_title('Machine Efficiency vs Time')

        self.canvas_electrical.draw()
        self.canvas_mechanical.draw()
        self.canvas_thermal.draw()
        self.canvas_power.draw()

        self.status_label.config(text="Ready")

    def run_simulation(self):
        """Run the simulation (called in separate thread)"""
        # Initial conditions: [i, q, omega, theta, T]
        y0 = np.array([0.0, 0.0, 0.0, 0.0, self.params.ambient_temp])

        # Simulation time
        t_end = 2.0  # 2 seconds

        # Run simulation
        if self.solver_var.get() == "RK45":
            t, y = self.model.simulate_rk45((0, t_end), y0, max_step=0.001)
        else:  # Euler
            t, y = self.model.simulate_euler((0, t_end), 0.0001, y0)

        # Extract state variables
        current = y[:, 0]
        charge = y[:, 1]
        omega = y[:, 2]
        theta = y[:, 3]
        temperature = y[:, 4]

        # Calculate derived quantities
        capacitor_voltage = charge / self.params.capacitance if self.params.capacitance > 0 else charge * 0

        k_t = self.params.magnetic_flux * self.params.pole_pairs
        torque = k_t * current

        magnetic_field = np.array([self.model.calculate_magnetic_field(i) for i in current])

        power_dissipation = self.params.resistance * current**2

        efficiency = np.array([self.model.calculate_efficiency(current[i], omega[i])
                              for i in range(len(current))])

        # Update plots in real-time (simulated)
        chunk_size = max(1, len(t) // 100)  # 100 updates

        for i in range(0, len(t), chunk_size):
            if not self.simulation_running:
                break

            end_idx = min(i + chunk_size, len(t))

            self.time_data = t[:end_idx].tolist()
            self.current_data = current[:end_idx].tolist()
            self.voltage_data = capacitor_voltage[:end_idx].tolist()
            self.speed_data = omega[:end_idx].tolist()
            self.temperature_data = temperature[:end_idx].tolist()
            self.magnetic_field_data = magnetic_field[:end_idx].tolist()

            # Update plots
            self.root.after(0, self.update_plots,
                          t[:end_idx], current[:end_idx], capacitor_voltage[:end_idx],
                          omega[:end_idx], torque[:end_idx], temperature[:end_idx],
                          magnetic_field[:end_idx], power_dissipation[:end_idx],
                          efficiency[:end_idx])

            time.sleep(0.02)  # Slow down for visualization

        if self.simulation_running:
            self.root.after(0, self.simulation_complete)

    def update_plots(self, t, current, voltage, omega, torque, temperature,
                    magnetic_field, power, efficiency):
        """Update all plots"""
        # Electrical plots
        self.ax_current.clear()
        self.ax_current.plot(t, current, 'b-', linewidth=1.5)
        self.ax_current.set_xlabel('Time (s)')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Current vs Time')
        self.ax_current.grid(True, alpha=0.3)

        self.ax_voltage.clear()
        self.ax_voltage.plot(t, voltage, 'r-', linewidth=1.5)
        self.ax_voltage.set_xlabel('Time (s)')
        self.ax_voltage.set_ylabel('Capacitor Voltage (V)')
        self.ax_voltage.set_title('Capacitor Voltage vs Time')
        self.ax_voltage.grid(True, alpha=0.3)

        self.canvas_electrical.draw()

        # Mechanical plots
        self.ax_speed.clear()
        self.ax_speed.plot(t, omega, 'g-', linewidth=1.5)
        self.ax_speed.set_xlabel('Time (s)')
        self.ax_speed.set_ylabel('Angular Speed (rad/s)')
        self.ax_speed.set_title('Angular Speed vs Time')
        self.ax_speed.grid(True, alpha=0.3)

        self.ax_torque.clear()
        self.ax_torque.plot(t, torque, 'm-', linewidth=1.5)
        self.ax_torque.set_xlabel('Time (s)')
        self.ax_torque.set_ylabel('Torque (Nm)')
        self.ax_torque.set_title('Motor Torque vs Time')
        self.ax_torque.grid(True, alpha=0.3)

        self.canvas_mechanical.draw()

        # Thermal & Magnetic plots
        self.ax_temp.clear()
        self.ax_temp.plot(t, temperature, 'r-', linewidth=1.5)
        self.ax_temp.axhline(y=self.params.ambient_temp, color='k', linestyle='--',
                           linewidth=1, alpha=0.5, label='Ambient')
        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_title('Temperature vs Time')
        self.ax_temp.grid(True, alpha=0.3)
        self.ax_temp.legend()

        self.ax_magnetic.clear()
        self.ax_magnetic.plot(t, magnetic_field * 1000, 'c-', linewidth=1.5)  # Convert to mT
        self.ax_magnetic.set_xlabel('Time (s)')
        self.ax_magnetic.set_ylabel('Magnetic Field (mT)')
        self.ax_magnetic.set_title('Magnetic Field vs Time')
        self.ax_magnetic.grid(True, alpha=0.3)

        self.canvas_thermal.draw()

        # Power & Efficiency plots
        self.ax_power.clear()
        self.ax_power.plot(t, power, 'orange', linewidth=1.5)
        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (W)')
        self.ax_power.set_title('Power Dissipation vs Time')
        self.ax_power.grid(True, alpha=0.3)

        self.ax_efficiency.clear()
        self.ax_efficiency.plot(t, efficiency, 'purple', linewidth=1.5)
        self.ax_efficiency.set_xlabel('Time (s)')
        self.ax_efficiency.set_ylabel('Efficiency (%)')
        self.ax_efficiency.set_title('Machine Efficiency vs Time')
        self.ax_efficiency.set_ylim([0, 100])
        self.ax_efficiency.grid(True, alpha=0.3)

        self.canvas_power.draw()

    def simulation_complete(self):
        """Called when simulation completes"""
        self.simulation_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Simulation complete")

        # Calculate and display RMS values
        if len(self.current_data) > 0:
            i_rms = np.sqrt(np.mean(np.array(self.current_data)**2))
            messagebox.showinfo("Simulation Complete",
                              f"Simulation finished successfully!\n\n"
                              f"RMS Current: {i_rms:.3f} A\n"
                              f"Final Temperature: {self.temperature_data[-1]:.2f} °C\n"
                              f"Final Speed: {self.speed_data[-1]:.2f} rad/s")

    def show_lighting_calculator(self):
        """Show football pitch lighting calculator dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Football Pitch Lighting Calculator")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()

        # Input frame
        input_frame = ttk.LabelFrame(dialog, text="Input Parameters", padding=20)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create input fields
        fields = {}
        params = [
            ("Pitch Length (m):", 120.0),
            ("Pitch Width (m):", 60.0),
            ("Required Illumination (lm/m²):", 1000.0),
            ("Light Efficiency Factor:", 0.4),
            ("Lamp Power (W):", 1000.0),
            ("Lamp Efficiency (lm/W):", 30.0),
            ("Number of Towers:", 12),
        ]

        for i, (label, default) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            var = tk.DoubleVar(value=default)
            entry = ttk.Entry(input_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, pady=5, padx=5)
            fields[label] = var

        # Results frame
        results_frame = ttk.LabelFrame(dialog, text="Calculation Results", padding=20)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        results_text = tk.Text(results_frame, height=15, width=60)
        results_text.pack(fill=tk.BOTH, expand=True)

        def calculate():
            try:
                calc = LightingCalculator()
                results = calc.calculate_lamps(
                    fields["Pitch Length (m):"].get(),
                    fields["Pitch Width (m):"].get(),
                    fields["Required Illumination (lm/m²):"].get(),
                    fields["Light Efficiency Factor:"].get(),
                    fields["Lamp Power (W):"].get(),
                    fields["Lamp Efficiency (lm/W):"].get(),
                    int(fields["Number of Towers:"].get())
                )

                results_text.delete(1.0, tk.END)
                results_text.insert(tk.END, "FOOTBALL PITCH LIGHTING CALCULATION\n")
                results_text.insert(tk.END, "=" * 50 + "\n\n")
                results_text.insert(tk.END, f"Pitch Area: {results['pitch_area']:.2f} m²\n\n")
                results_text.insert(tk.END, f"Total Lumens Required on Pitch: {results['total_lumens_required']:,.0f} lm\n")
                results_text.insert(tk.END, f"Total Lumens to be Emitted: {results['total_lumens_emitted']:,.0f} lm\n\n")
                results_text.insert(tk.END, f"Lumens per Lamp: {results['lumens_per_lamp']:,.0f} lm\n")
                results_text.insert(tk.END, f"Total Number of Lamps: {results['total_lamps']} lamps\n\n")
                results_text.insert(tk.END, "=" * 50 + "\n")
                results_text.insert(tk.END, f"LAMPS PER TOWER: {results['lamps_per_tower']} lamps\n")
                results_text.insert(tk.END, "=" * 50 + "\n\n")
                results_text.insert(tk.END, f"Total Power Consumption: {results['total_power']/1000:.2f} kW\n")
                results_text.insert(tk.END, f"Power per Tower: {results['power_per_tower']/1000:.2f} kW\n")

            except Exception as e:
                messagebox.showerror("Error", f"Calculation error: {str(e)}")

        # Calculate button
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Calculate", command=calculate, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)

        # Auto-calculate on open
        calculate()

    def show_power_analysis(self):
        """Show power analysis dialog"""
        if len(self.current_data) == 0:
            messagebox.showwarning("No Data", "Please run a simulation first!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Power Analysis")
        dialog.geometry("500x400")
        dialog.transient(self.root)

        text = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)

        # Calculate statistics
        current_array = np.array(self.current_data)
        time_array = np.array(self.time_data)

        i_rms = np.sqrt(np.mean(current_array**2))
        i_peak = np.max(np.abs(current_array))
        i_avg = np.mean(np.abs(current_array))

        V_peak = self.params.voltage * np.sqrt(2)
        voltage_array = V_peak * np.sin(2 * np.pi * self.params.frequency * time_array)
        v_rms = np.sqrt(np.mean(voltage_array**2))

        # Power calculations
        p_inst = voltage_array * current_array
        p_avg = np.mean(p_inst)
        s_apparent = v_rms * i_rms
        pf = p_avg / s_apparent if s_apparent > 0 else 0
        q_reactive = np.sqrt(s_apparent**2 - p_avg**2) if s_apparent > abs(p_avg) else 0

        # Power losses
        p_copper = self.params.resistance * i_rms**2

        # Display results
        text.insert(tk.END, "POWER ANALYSIS REPORT\n")
        text.insert(tk.END, "=" * 60 + "\n\n")

        text.insert(tk.END, "CURRENT ANALYSIS:\n")
        text.insert(tk.END, f"  RMS Current: {i_rms:.3f} A\n")
        text.insert(tk.END, f"  Peak Current: {i_peak:.3f} A\n")
        text.insert(tk.END, f"  Average Current: {i_avg:.3f} A\n\n")

        text.insert(tk.END, "VOLTAGE ANALYSIS:\n")
        text.insert(tk.END, f"  RMS Voltage: {v_rms:.3f} V\n")
        text.insert(tk.END, f"  Peak Voltage: {V_peak:.3f} V\n\n")

        text.insert(tk.END, "POWER ANALYSIS:\n")
        text.insert(tk.END, f"  Active Power (P): {p_avg:.3f} W\n")
        text.insert(tk.END, f"  Reactive Power (Q): {q_reactive:.3f} VAR\n")
        text.insert(tk.END, f"  Apparent Power (S): {s_apparent:.3f} VA\n")
        text.insert(tk.END, f"  Power Factor: {pf:.3f}\n\n")

        text.insert(tk.END, "LOSSES:\n")
        text.insert(tk.END, f"  Copper Losses: {p_copper:.3f} W\n\n")

        text.insert(tk.END, "THERMAL:\n")
        text.insert(tk.END, f"  Final Temperature: {self.temperature_data[-1]:.2f} °C\n")
        text.insert(tk.END, f"  Temperature Rise: {self.temperature_data[-1] - self.params.ambient_temp:.2f} °C\n")

        text.config(state=tk.DISABLED)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About",
                          "Advanced Electrical Engineering Multi-Physics Simulator\n\n"
                          "Features:\n"
                          "• RLC Circuit Simulation\n"
                          "• Electrical Machine Dynamics\n"
                          "• Thermal Analysis\n"
                          "• Magnetic Field Calculation\n"
                          "• ODE Solvers (RK45, Euler)\n"
                          "• Football Pitch Lighting Calculator\n"
                          "• Real-time Visualization\n\n"
                          "Version 1.0\n"
                          "© 2025 Electrical Engineering Lab")

    def on_resize(self, event):
        """Handle window resize for auto-scaling"""
        # The matplotlib canvases automatically handle resizing
        pass

def main():
    """Main entry point"""
    root = tk.Tk()
    app = ElectricalEngineeringApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

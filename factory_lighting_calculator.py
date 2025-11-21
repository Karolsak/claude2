#!/usr/bin/env python3
"""
Factory Lighting Calculator with Multi-Physics Simulation
Advanced Electrical Engineering Application
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time


class LightingCalculator:
    """
    Factory Lighting Calculator with comprehensive electrical engineering calculations
    """

    @staticmethod
    def calculate_lamps(area_length, area_width, illumination, depreciation_factor,
                       coefficient_utilization, lamp_efficiency):
        """
        Calculate number of lamps required for factory lighting

        Formula: N = (E × A) / (η × Cu × Df)
        where:
        - E = Required illumination (lux)
        - A = Area (m²)
        - η = Luminous efficacy (lm/W)
        - Cu = Coefficient of utilization
        - Df = Depreciation factor
        """
        area = area_length * area_width
        total_lumens_required = illumination * area
        lumens_per_lamp = lamp_efficiency  # This represents lamp output in lumens

        # Effective lumens considering utilization and depreciation
        effective_lumens_per_lamp = lumens_per_lamp * coefficient_utilization * depreciation_factor

        # For the first problem, lamp_efficiency is in lm/W, we need to assume lamp wattage
        # For the second problem, we know the wattage

        number_of_lamps = total_lumens_required / effective_lumens_per_lamp

        return {
            'area': area,
            'total_lumens_required': total_lumens_required,
            'effective_lumens_per_lamp': effective_lumens_per_lamp,
            'number_of_lamps': math.ceil(number_of_lamps),
            'actual_number': number_of_lamps
        }

    @staticmethod
    def calculate_lamps_with_wattage(area_length, area_width, illumination,
                                     depreciation_factor, coefficient_utilization,
                                     lamp_efficiency, lamp_wattage):
        """
        Calculate number of lamps with known wattage
        """
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
        """
        Suggest optimal lamp disposition in a rectangular pattern
        """
        # Try to create a rectangular grid
        ratio = area_length / area_width

        # Find best factorization
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

        # Calculate spacing
        spacing_length = area_length / best_cols
        spacing_width = area_width / best_rows

        return {
            'rows': best_rows,
            'columns': best_cols,
            'spacing_length': spacing_length,
            'spacing_width': spacing_width,
            'pattern': f"{best_rows} × {best_cols}"
        }


class MultiPhysicsSimulator:
    """
    Multi-Physics Electrical Engineering Simulator
    Simulates RLC circuits, power systems, and lighting dynamics
    """

    def __init__(self):
        self.time_span = (0, 10)
        self.time_points = np.linspace(0, 10, 1000)
        self.running = False
        self.current_results = None

    def rlc_circuit_model(self, t, y, R, L, C, V_input):
        """
        RLC Circuit Differential Equations
        dy/dt = f(t, y)
        y[0] = current (I)
        y[1] = voltage across capacitor (V_C)
        """
        I = y[0]
        V_C = y[1]

        # Kirchhoff's voltage law: V_input = V_R + V_L + V_C
        # V_input = R*I + L*(dI/dt) + V_C
        # dI/dt = (V_input - R*I - V_C) / L
        dI_dt = (V_input - R * I - V_C) / L

        # Current through capacitor: I = C * (dV_C/dt)
        # dV_C/dt = I / C
        dV_C_dt = I / C

        return [dI_dt, dV_C_dt]

    def lighting_thermal_model(self, t, y, P_input, R_th, C_th, T_ambient):
        """
        Lighting Thermal Model
        Models temperature rise in lighting fixtures
        y[0] = Temperature (T)
        """
        T = y[0]

        # Heat balance: C_th * dT/dt = P_input - (T - T_ambient) / R_th
        dT_dt = (P_input - (T - T_ambient) / R_th) / C_th

        return [dT_dt]

    def power_system_model(self, t, y, P_load, V_nom, f_nom, H, D):
        """
        Simplified Power System Dynamics
        y[0] = frequency deviation (Δf)
        y[1] = power angle (δ)
        """
        delta_f = y[0]
        delta = y[1]

        # Swing equation for frequency dynamics
        # 2H * d(Δf)/dt = P_m - P_e - D * Δf
        # Simplified: P_m = P_load + damping

        d_delta_f_dt = (P_load - D * delta_f) / (2 * H)
        d_delta_dt = 2 * math.pi * f_nom * delta_f

        return [d_delta_f_dt, d_delta_dt]

    def solve_rlc_rk45(self, R, L, C, V_input, I0=0, V_C0=0):
        """
        Solve RLC circuit using RK45 method
        """
        y0 = [I0, V_C0]

        sol = solve_ivp(
            lambda t, y: self.rlc_circuit_model(t, y, R, L, C, V_input),
            self.time_span,
            y0,
            method='RK45',
            t_eval=self.time_points,
            dense_output=True
        )

        return sol

    def solve_rlc_euler(self, R, L, C, V_input, I0=0, V_C0=0, dt=0.01):
        """
        Solve RLC circuit using Euler method
        """
        t = np.arange(self.time_span[0], self.time_span[1], dt)
        n = len(t)

        I = np.zeros(n)
        V_C = np.zeros(n)

        I[0] = I0
        V_C[0] = V_C0

        for i in range(1, n):
            derivatives = self.rlc_circuit_model(t[i-1], [I[i-1], V_C[i-1]], R, L, C, V_input)
            I[i] = I[i-1] + derivatives[0] * dt
            V_C[i] = V_C[i-1] + derivatives[1] * dt

        return t, I, V_C

    def calculate_rms_values(self, current, voltage):
        """
        Calculate RMS values for AC signals
        """
        I_rms = np.sqrt(np.mean(current**2))
        V_rms = np.sqrt(np.mean(voltage**2))

        return I_rms, V_rms

    def calculate_power_metrics(self, voltage, current, t):
        """
        Calculate power metrics: active, reactive, apparent power
        """
        # Instantaneous power
        p_inst = voltage * current

        # Active power (average)
        P = np.mean(p_inst)

        # RMS values
        V_rms, I_rms = self.calculate_rms_values(voltage, current)

        # Apparent power
        S = V_rms * I_rms

        # Reactive power
        Q = np.sqrt(max(0, S**2 - P**2))

        # Power factor
        pf = P / S if S > 0 else 0

        return {
            'active_power': P,
            'reactive_power': Q,
            'apparent_power': S,
            'power_factor': pf,
            'V_rms': V_rms,
            'I_rms': I_rms
        }


class FactoryLightingApp:
    """
    Main Application Class with Tkinter GUI
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Factory Lighting Calculator & Multi-Physics Simulator")
        self.root.geometry("1400x900")

        # Initialize calculator and simulator
        self.calculator = LightingCalculator()
        self.simulator = MultiPhysicsSimulator()

        # Simulation control
        self.simulation_running = False
        self.simulation_thread = None

        # Create main menu
        self.create_menu()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create tabs
        self.create_lighting_tab()
        self.create_simulation_tab()
        self.create_definitions_tab()

        # Bind resize event for auto-scaling
        self.root.bind('<Configure>', self.on_window_resize)

    def create_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Calculation", command=self.reset_lighting_calc)
        file_menu.add_command(label="Reset Simulation", command=self.reset_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Definitions", command=lambda: self.notebook.select(2))

    def create_lighting_tab(self):
        """Create lighting calculator tab"""
        lighting_frame = ttk.Frame(self.notebook)
        self.notebook.add(lighting_frame, text="Lighting Calculator")

        # Create scrollable frame
        canvas = tk.Canvas(lighting_frame)
        scrollbar = ttk.Scrollbar(lighting_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Problem 1
        problem1_frame = ttk.LabelFrame(scrollable_frame, text="Problem 1: Factory Hall 30m × 12m", padding=10)
        problem1_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        # Input fields for Problem 1
        ttk.Label(problem1_frame, text="Length (m):").grid(row=0, column=0, sticky='w', pady=2)
        self.p1_length = ttk.Entry(problem1_frame, width=15)
        self.p1_length.insert(0, "30")
        self.p1_length.grid(row=0, column=1, pady=2)

        ttk.Label(problem1_frame, text="Width (m):").grid(row=1, column=0, sticky='w', pady=2)
        self.p1_width = ttk.Entry(problem1_frame, width=15)
        self.p1_width.insert(0, "12")
        self.p1_width.grid(row=1, column=1, pady=2)

        ttk.Label(problem1_frame, text="Illumination (lux):").grid(row=2, column=0, sticky='w', pady=2)
        self.p1_illumination = ttk.Entry(problem1_frame, width=15)
        self.p1_illumination.insert(0, "100")
        self.p1_illumination.grid(row=2, column=1, pady=2)

        ttk.Label(problem1_frame, text="Depreciation Factor:").grid(row=3, column=0, sticky='w', pady=2)
        self.p1_depreciation = ttk.Scale(problem1_frame, from_=0.1, to=1.0, orient='horizontal', length=150)
        self.p1_depreciation.set(0.8)
        self.p1_depreciation.grid(row=3, column=1, pady=2)
        self.p1_dep_label = ttk.Label(problem1_frame, text="0.80")
        self.p1_dep_label.grid(row=3, column=2, pady=2)
        self.p1_depreciation.config(command=lambda v: self.p1_dep_label.config(text=f"{float(v):.2f}"))

        ttk.Label(problem1_frame, text="Coefficient of Utilization:").grid(row=4, column=0, sticky='w', pady=2)
        self.p1_utilization = ttk.Scale(problem1_frame, from_=0.1, to=1.0, orient='horizontal', length=150)
        self.p1_utilization.set(0.4)
        self.p1_utilization.grid(row=4, column=1, pady=2)
        self.p1_util_label = ttk.Label(problem1_frame, text="0.40")
        self.p1_util_label.grid(row=4, column=2, pady=2)
        self.p1_utilization.config(command=lambda v: self.p1_util_label.config(text=f"{float(v):.2f}"))

        ttk.Label(problem1_frame, text="Lamp Efficiency (lm/W):").grid(row=5, column=0, sticky='w', pady=2)
        self.p1_efficiency = ttk.Entry(problem1_frame, width=15)
        self.p1_efficiency.insert(0, "14")
        self.p1_efficiency.grid(row=5, column=1, pady=2)

        ttk.Label(problem1_frame, text="Lamp Wattage (W):").grid(row=6, column=0, sticky='w', pady=2)
        self.p1_wattage = ttk.Entry(problem1_frame, width=15)
        self.p1_wattage.insert(0, "100")
        self.p1_wattage.grid(row=6, column=1, pady=2)

        ttk.Button(problem1_frame, text="Calculate", command=self.calculate_problem1).grid(row=7, column=0, columnspan=3, pady=10)

        # Results for Problem 1
        self.p1_results = scrolledtext.ScrolledText(problem1_frame, width=70, height=10, wrap=tk.WORD)
        self.p1_results.grid(row=8, column=0, columnspan=3, pady=5)

        # Problem 2
        problem2_frame = ttk.LabelFrame(scrollable_frame, text="Problem 2: Workshop 100m × 50m", padding=10)
        problem2_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        # Input fields for Problem 2
        ttk.Label(problem2_frame, text="Length (m):").grid(row=0, column=0, sticky='w', pady=2)
        self.p2_length = ttk.Entry(problem2_frame, width=15)
        self.p2_length.insert(0, "100")
        self.p2_length.grid(row=0, column=1, pady=2)

        ttk.Label(problem2_frame, text="Width (m):").grid(row=1, column=0, sticky='w', pady=2)
        self.p2_width = ttk.Entry(problem2_frame, width=15)
        self.p2_width.insert(0, "50")
        self.p2_width.grid(row=1, column=1, pady=2)

        ttk.Label(problem2_frame, text="Illumination (lux):").grid(row=2, column=0, sticky='w', pady=2)
        self.p2_illumination = ttk.Entry(problem2_frame, width=15)
        self.p2_illumination.insert(0, "50")
        self.p2_illumination.grid(row=2, column=1, pady=2)

        ttk.Label(problem2_frame, text="Depreciation Factor:").grid(row=3, column=0, sticky='w', pady=2)
        self.p2_depreciation = ttk.Scale(problem2_frame, from_=0.1, to=1.0, orient='horizontal', length=150)
        self.p2_depreciation.set(0.7)
        self.p2_depreciation.grid(row=3, column=1, pady=2)
        self.p2_dep_label = ttk.Label(problem2_frame, text="0.70")
        self.p2_dep_label.grid(row=3, column=2, pady=2)
        self.p2_depreciation.config(command=lambda v: self.p2_dep_label.config(text=f"{float(v):.2f}"))

        ttk.Label(problem2_frame, text="Coefficient of Utilization:").grid(row=4, column=0, sticky='w', pady=2)
        self.p2_utilization = ttk.Scale(problem2_frame, from_=0.1, to=1.0, orient='horizontal', length=150)
        self.p2_utilization.set(0.9)
        self.p2_utilization.grid(row=4, column=1, pady=2)
        self.p2_util_label = ttk.Label(problem2_frame, text="0.90")
        self.p2_util_label.grid(row=4, column=2, pady=2)
        self.p2_utilization.config(command=lambda v: self.p2_util_label.config(text=f"{float(v):.2f}"))

        ttk.Label(problem2_frame, text="Lamp Efficiency (lm/W):").grid(row=5, column=0, sticky='w', pady=2)
        self.p2_efficiency = ttk.Entry(problem2_frame, width=15)
        self.p2_efficiency.insert(0, "80")
        self.p2_efficiency.grid(row=5, column=1, pady=2)

        ttk.Label(problem2_frame, text="Lamp Wattage (W):").grid(row=6, column=0, sticky='w', pady=2)
        self.p2_wattage = ttk.Entry(problem2_frame, width=15)
        self.p2_wattage.insert(0, "100")
        self.p2_wattage.grid(row=6, column=1, pady=2)

        ttk.Button(problem2_frame, text="Calculate", command=self.calculate_problem2).grid(row=7, column=0, columnspan=3, pady=10)

        # Results for Problem 2
        self.p2_results = scrolledtext.ScrolledText(problem2_frame, width=70, height=10, wrap=tk.WORD)
        self.p2_results.grid(row=8, column=0, columnspan=3, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_simulation_tab(self):
        """Create multi-physics simulation tab"""
        sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(sim_frame, text="Multi-Physics Simulation")

        # Control panel
        control_frame = ttk.LabelFrame(sim_frame, text="Simulation Controls", padding=10)
        control_frame.pack(side='left', fill='y', padx=5, pady=5)

        # RLC Circuit Parameters
        ttk.Label(control_frame, text="RLC Circuit Parameters", font=('Arial', 10, 'bold')).pack(pady=5)

        ttk.Label(control_frame, text="Resistance (Ω):").pack()
        self.sim_R = ttk.Scale(control_frame, from_=1, to=100, orient='horizontal', length=200)
        self.sim_R.set(10)
        self.sim_R.pack()
        self.sim_R_label = ttk.Label(control_frame, text="10.0 Ω")
        self.sim_R_label.pack()
        self.sim_R.config(command=lambda v: self.sim_R_label.config(text=f"{float(v):.1f} Ω"))

        ttk.Label(control_frame, text="Inductance (mH):").pack()
        self.sim_L = ttk.Scale(control_frame, from_=1, to=1000, orient='horizontal', length=200)
        self.sim_L.set(100)
        self.sim_L.pack()
        self.sim_L_label = ttk.Label(control_frame, text="100.0 mH")
        self.sim_L_label.pack()
        self.sim_L.config(command=lambda v: self.sim_L_label.config(text=f"{float(v):.1f} mH"))

        ttk.Label(control_frame, text="Capacitance (µF):").pack()
        self.sim_C = ttk.Scale(control_frame, from_=1, to=1000, orient='horizontal', length=200)
        self.sim_C.set(100)
        self.sim_C.pack()
        self.sim_C_label = ttk.Label(control_frame, text="100.0 µF")
        self.sim_C_label.pack()
        self.sim_C.config(command=lambda v: self.sim_C_label.config(text=f"{float(v):.1f} µF"))

        ttk.Label(control_frame, text="Input Voltage (V):").pack()
        self.sim_V = ttk.Scale(control_frame, from_=1, to=240, orient='horizontal', length=200)
        self.sim_V.set(24)
        self.sim_V.pack()
        self.sim_V_label = ttk.Label(control_frame, text="24.0 V")
        self.sim_V_label.pack()
        self.sim_V.config(command=lambda v: self.sim_V_label.config(text=f"{float(v):.1f} V"))

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:", font=('Arial', 10, 'bold')).pack()
        self.solver_var = tk.StringVar(value="RK45")
        ttk.Radiobutton(control_frame, text="RK45 (Runge-Kutta)", variable=self.solver_var, value="RK45").pack()
        ttk.Radiobutton(control_frame, text="Euler Method", variable=self.solver_var, value="Euler").pack()

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_simulation, width=10)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_simulation, width=10, state='disabled')
        self.stop_button.pack(pady=5)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_simulation, width=10)
        self.reset_button.pack(pady=5)

        # Status
        self.status_label = ttk.Label(control_frame, text="Status: Ready", foreground="green")
        self.status_label.pack(pady=10)

        # Visualization panel
        viz_frame = ttk.Frame(sim_frame)
        viz_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Results text
        results_frame = ttk.LabelFrame(viz_frame, text="Simulation Results", padding=5)
        results_frame.pack(fill='x', pady=5)

        self.sim_results = scrolledtext.ScrolledText(results_frame, width=80, height=6, wrap=tk.WORD)
        self.sim_results.pack(fill='x')

    def create_definitions_tab(self):
        """Create definitions tab"""
        def_frame = ttk.Frame(self.notebook)
        self.notebook.add(def_frame, text="Definitions & Theory")

        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(def_frame, wrap=tk.WORD, font=('Arial', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)

        # Add definitions
        definitions = """
LIGHTING ENGINEERING DEFINITIONS

1. LUX (lx)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Definition: Lux is the SI unit of illuminance, measuring the amount of luminous flux
incident on a surface per unit area.

Formula: 1 lux = 1 lumen/m²

Physical Meaning: It represents how bright a surface appears when illuminated.
One lux is equal to one lumen per square meter.

Examples:
• Direct sunlight: ~100,000 lux
• Office lighting: 320-500 lux
• Living room: 50-150 lux
• Moonlight: ~0.25 lux

Application: Used in lighting design to specify required illumination levels for
different tasks and spaces according to standards (IES, CIE).


2. LUMINOUS FLUX (Φ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Definition: Luminous flux is the measure of the total quantity of visible light
emitted by a source per unit time.

Unit: Lumen (lm)

Physical Meaning: It represents the total "amount" of light energy emitted by a
source, weighted by the sensitivity of the human eye.

Formula: Φ = ∫∫ I(θ,φ) dΩ
where I is luminous intensity and dΩ is the solid angle element.

Relationship:
• Luminous Flux = Luminous Efficacy × Power
• For LED: 80-150 lm/W
• For Incandescent: 10-17 lm/W
• For Fluorescent: 50-100 lm/W

Examples:
• 100W incandescent bulb: ~1,600 lumens
• 100W LED equivalent: ~1,600 lumens (but only 15-20W)
• Candle: ~12 lumens


3. CANDLE POWER (Luminous Intensity)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Definition: Candle power, now called luminous intensity, is the luminous flux
emitted per unit solid angle in a particular direction.

Unit: Candela (cd)

Physical Meaning: It measures how "focused" or "intense" the light is in a specific
direction, independent of distance.

Formula: I = dΦ/dΩ
where dΦ is luminous flux and dΩ is solid angle (steradians).

Relationship to Illuminance:
E = I/r²  (Inverse square law)
where E is illuminance (lux), I is intensity (candela), and r is distance (meters).

Examples:
• Standard candle: ~1 candela
• Car headlight: 25,000-150,000 cd
• LED flashlight: 1,000-10,000 cd

Note: The term "candle power" is historical; modern usage prefers "luminous intensity."


LIGHTING CALCULATION FORMULAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Number of Lamps Required:
   N = (E × A) / (Φ × Cu × Df)

   where:
   N  = Number of lamps
   E  = Required illumination (lux)
   A  = Area (m²)
   Φ  = Luminous flux per lamp (lumens)
   Cu = Coefficient of utilization
   Df = Depreciation factor (maintenance factor)

2. Coefficient of Utilization (Cu):
   Ratio of luminous flux received on the working plane to the total flux
   emitted by lamps. Depends on:
   • Room index
   • Reflectance of surfaces
   • Luminaire type

   Typical values: 0.3-0.7

3. Depreciation Factor (Df):
   Accounts for:
   • Lamp aging (reduction in output)
   • Dirt accumulation on fixtures
   • Room surface deterioration

   Typical values: 0.6-0.8

4. Room Index (K):
   K = (L × W) / [H × (L + W)]

   where:
   L = Room length
   W = Room width
   H = Mounting height above working plane


ELECTRICAL ENGINEERING CONCEPTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RLC Circuit Dynamics:
• Second-order differential equation
• Natural frequency: ω₀ = 1/√(LC)
• Damping ratio: ζ = R/(2)√(C/L)
• Quality factor: Q = ω₀L/R = 1/(ω₀RC)

Power Calculations:
• Active Power (P): Real power consumed (Watts)
• Reactive Power (Q): Power stored/returned (VAR)
• Apparent Power (S): Vector sum (VA)
• Power Factor: PF = P/S = cos(φ)

RMS Values:
• V_RMS = V_peak/√2 for sinusoidal waveforms
• I_RMS = I_peak/√2
• Used in all AC power calculations

Thermal Modeling:
• Heat dissipation in lighting fixtures
• Temperature rise affects efficiency
• Thermal resistance and capacitance analogous to electrical R and C
"""

        text_widget.insert('1.0', definitions)
        text_widget.config(state='disabled')  # Make read-only

    def calculate_problem1(self):
        """Calculate Problem 1"""
        try:
            length = float(self.p1_length.get())
            width = float(self.p1_width.get())
            illumination = float(self.p1_illumination.get())
            depreciation = self.p1_depreciation.get()
            utilization = self.p1_utilization.get()
            efficiency = float(self.p1_efficiency.get())
            wattage = float(self.p1_wattage.get())

            result = self.calculator.calculate_lamps_with_wattage(
                length, width, illumination, depreciation, utilization, efficiency, wattage
            )

            disposition = self.calculator.suggest_lamp_disposition(
                length, width, result['number_of_lamps']
            )

            output = f"""
PROBLEM 1 SOLUTION: Factory Hall {length}m × {width}m
{'='*70}

INPUT PARAMETERS:
  • Area dimensions: {length} m × {width} m
  • Total area: {result['area']:.2f} m²
  • Required illumination: {illumination} lux
  • Depreciation factor: {depreciation:.2f}
  • Coefficient of utilization: {utilization:.2f}
  • Lamp efficiency: {efficiency} lm/W
  • Lamp wattage: {wattage} W

CALCULATIONS:
  • Lumens per lamp: {wattage} W × {efficiency} lm/W = {result['lumens_per_lamp']:.2f} lumens
  • Effective lumens per lamp: {result['effective_lumens_per_lamp']:.2f} lumens
    (considering utilization and depreciation)
  • Total lumens required: {illumination} lux × {result['area']:.2f} m² = {result['total_lumens_required']:.2f} lumens
  • Number of lamps (calculated): {result['actual_number']:.2f}

RESULTS:
  ✓ Number of lamps required: {result['number_of_lamps']} lamps
  ✓ Total power consumption: {result['total_power_kw']:.2f} kW

RECOMMENDED LAMP DISPOSITION:
  • Pattern: {disposition['pattern']} (rows × columns)
  • {disposition['rows']} rows across width
  • {disposition['columns']} columns along length
  • Spacing between lamps (length): {disposition['spacing_length']:.2f} m
  • Spacing between lamps (width): {disposition['spacing_width']:.2f} m

VERIFICATION:
  • Actual illumination: {(result['number_of_lamps'] * result['effective_lumens_per_lamp'] / result['area']):.2f} lux
  • Design margin: {((result['number_of_lamps'] * result['effective_lumens_per_lamp'] / result['area']) - illumination):.2f} lux
"""

            self.p1_results.delete('1.0', tk.END)
            self.p1_results.insert('1.0', output)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Please enter valid numerical values.\n{str(e)}")

    def calculate_problem2(self):
        """Calculate Problem 2"""
        try:
            length = float(self.p2_length.get())
            width = float(self.p2_width.get())
            illumination = float(self.p2_illumination.get())
            depreciation = self.p2_depreciation.get()
            utilization = self.p2_utilization.get()
            efficiency = float(self.p2_efficiency.get())
            wattage = float(self.p2_wattage.get())

            result = self.calculator.calculate_lamps_with_wattage(
                length, width, illumination, depreciation, utilization, efficiency, wattage
            )

            disposition = self.calculator.suggest_lamp_disposition(
                length, width, result['number_of_lamps']
            )

            output = f"""
PROBLEM 2 SOLUTION: Workshop {length}m × {width}m
{'='*70}

INPUT PARAMETERS:
  • Area dimensions: {length} m × {width} m
  • Total area: {result['area']:.2f} m²
  • Required illumination: {illumination} lux
  • Depreciation factor: {depreciation:.2f}
  • Coefficient of utilization: {utilization:.2f}
  • Lamp efficiency: {efficiency} lm/W
  • Lamp wattage: {wattage} W

CALCULATIONS:
  • Lumens per lamp: {wattage} W × {efficiency} lm/W = {result['lumens_per_lamp']:.2f} lumens
  • Effective lumens per lamp: {result['effective_lumens_per_lamp']:.2f} lumens
    (considering utilization and depreciation)
  • Total lumens required: {illumination} lux × {result['area']:.2f} m² = {result['total_lumens_required']:.2f} lumens
  • Number of lamps (calculated): {result['actual_number']:.2f}

RESULTS:
  ✓ Number of lamps required: {result['number_of_lamps']} lamps
  ✓ Total power consumption: {result['total_power_kw']:.2f} kW
  ✓ Power density: {(result['total_power_kw'] * 1000 / result['area']):.2f} W/m²

RECOMMENDED LAMP DISPOSITION:
  • Pattern: {disposition['pattern']} (rows × columns)
  • {disposition['rows']} rows across width
  • {disposition['columns']} columns along length
  • Spacing between lamps (length): {disposition['spacing_length']:.2f} m
  • Spacing between lamps (width): {disposition['spacing_width']:.2f} m

LIGHTING SCHEME DESIGN:
  • Uniform distribution recommended
  • Consider task lighting for specific work areas
  • Ensure minimum spacing requirements for overlap

VERIFICATION:
  • Actual illumination: {(result['number_of_lamps'] * result['effective_lumens_per_lamp'] / result['area']):.2f} lux
  • Design margin: {((result['number_of_lamps'] * result['effective_lumens_per_lamp'] / result['area']) - illumination):.2f} lux
  • Efficiency rating: Excellent (Cu={utilization:.2f}, Df={depreciation:.2f})
"""

            self.p2_results.delete('1.0', tk.END)
            self.p2_results.insert('1.0', output)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Please enter valid numerical values.\n{str(e)}")

    def start_simulation(self):
        """Start the multi-physics simulation"""
        if not self.simulation_running:
            self.simulation_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text="Status: Running...", foreground="blue")

            # Run simulation in separate thread
            self.simulation_thread = threading.Thread(target=self.run_simulation)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Status: Stopped", foreground="orange")

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        self.fig.clear()
        self.canvas.draw()
        self.sim_results.delete('1.0', tk.END)
        self.status_label.config(text="Status: Ready", foreground="green")

    def run_simulation(self):
        """Run the RLC circuit simulation"""
        try:
            # Get parameters
            R = self.sim_R.get()  # Ohms
            L = self.sim_L.get() / 1000  # Convert mH to H
            C = self.sim_C.get() / 1e6  # Convert µF to F
            V_input = self.sim_V.get()  # Volts

            solver = self.solver_var.get()

            # Solve based on selected method
            if solver == "RK45":
                sol = self.simulator.solve_rlc_rk45(R, L, C, V_input)
                t = sol.t
                I = sol.y[0]
                V_C = sol.y[1]
            else:  # Euler
                t, I, V_C = self.simulator.solve_rlc_euler(R, L, C, V_input)

            # Calculate additional metrics
            V_R = R * I
            V_L = V_input - V_R - V_C

            # Calculate RMS values
            I_rms, V_C_rms = self.simulator.calculate_rms_values(I, V_C)

            # Calculate power metrics
            power_metrics = self.simulator.calculate_power_metrics(V_C, I, t)

            # Update plots
            self.fig.clear()

            # Create subplots
            ax1 = self.fig.add_subplot(3, 2, 1)
            ax2 = self.fig.add_subplot(3, 2, 2)
            ax3 = self.fig.add_subplot(3, 2, 3)
            ax4 = self.fig.add_subplot(3, 2, 4)
            ax5 = self.fig.add_subplot(3, 2, 5)
            ax6 = self.fig.add_subplot(3, 2, 6)

            # Plot 1: Current vs Time
            ax1.plot(t, I, 'b-', linewidth=2)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Current (A)')
            ax1.set_title(f'Current vs Time (RMS: {I_rms:.3f} A)')
            ax1.grid(True, alpha=0.3)

            # Plot 2: Capacitor Voltage vs Time
            ax2.plot(t, V_C, 'r-', linewidth=2)
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Voltage (V)')
            ax2.set_title(f'Capacitor Voltage (RMS: {V_C_rms:.3f} V)')
            ax2.grid(True, alpha=0.3)

            # Plot 3: All Voltages
            ax3.plot(t, V_R, 'g-', label='V_R', linewidth=1.5)
            ax3.plot(t, V_L, 'm-', label='V_L', linewidth=1.5)
            ax3.plot(t, V_C, 'r-', label='V_C', linewidth=1.5)
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Voltage (V)')
            ax3.set_title('Voltage Distribution')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

            # Plot 4: Power
            P_inst = V_C * I
            ax4.plot(t, P_inst, 'k-', linewidth=2)
            ax4.axhline(y=power_metrics['active_power'], color='r', linestyle='--',
                       label=f"Avg: {power_metrics['active_power']:.2f} W")
            ax4.set_xlabel('Time (s)')
            ax4.set_ylabel('Power (W)')
            ax4.set_title('Instantaneous Power')
            ax4.legend()
            ax4.grid(True, alpha=0.3)

            # Plot 5: Phase plot (Current vs Voltage)
            ax5.plot(V_C, I, 'b-', linewidth=1.5)
            ax5.set_xlabel('Capacitor Voltage (V)')
            ax5.set_ylabel('Current (A)')
            ax5.set_title('Phase Portrait')
            ax5.grid(True, alpha=0.3)

            # Plot 6: Energy
            E_L = 0.5 * L * I**2
            E_C = 0.5 * C * V_C**2
            E_total = E_L + E_C
            ax6.plot(t, E_L, 'b-', label='Inductor', linewidth=1.5)
            ax6.plot(t, E_C, 'r-', label='Capacitor', linewidth=1.5)
            ax6.plot(t, E_total, 'k--', label='Total', linewidth=2)
            ax6.set_xlabel('Time (s)')
            ax6.set_ylabel('Energy (J)')
            ax6.set_title('Energy Storage')
            ax6.legend()
            ax6.grid(True, alpha=0.3)

            self.fig.tight_layout()
            self.canvas.draw()

            # Calculate circuit characteristics
            omega_0 = 1 / np.sqrt(L * C)  # Natural frequency (rad/s)
            f_0 = omega_0 / (2 * np.pi)  # Natural frequency (Hz)
            zeta = R / 2 * np.sqrt(C / L)  # Damping ratio
            Q = omega_0 * L / R  # Quality factor

            # Update results
            results_text = f"""
SIMULATION RESULTS ({solver} Solver)
{'='*80}

CIRCUIT PARAMETERS:
  • Resistance (R): {R:.2f} Ω
  • Inductance (L): {L*1000:.2f} mH
  • Capacitance (C): {C*1e6:.2f} µF
  • Input Voltage: {V_input:.2f} V

CIRCUIT CHARACTERISTICS:
  • Natural Frequency (f₀): {f_0:.2f} Hz (ω₀ = {omega_0:.2f} rad/s)
  • Damping Ratio (ζ): {zeta:.4f}
  • Quality Factor (Q): {Q:.2f}
  • Circuit Type: {"Underdamped" if zeta < 1 else "Overdamped" if zeta > 1 else "Critically Damped"}

RMS VALUES:
  • Current (I_RMS): {I_rms:.4f} A
  • Capacitor Voltage (V_C_RMS): {V_C_rms:.4f} V

POWER ANALYSIS:
  • Active Power (P): {power_metrics['active_power']:.4f} W
  • Reactive Power (Q): {power_metrics['reactive_power']:.4f} VAR
  • Apparent Power (S): {power_metrics['apparent_power']:.4f} VA
  • Power Factor: {power_metrics['power_factor']:.4f}

IMPEDANCE:
  • Inductive Reactance (X_L): {omega_0 * L:.4f} Ω
  • Capacitive Reactance (X_C): {1/(omega_0 * C):.4f} Ω
  • Total Impedance (Z): {np.sqrt(R**2 + (omega_0*L - 1/(omega_0*C))**2):.4f} Ω
"""

            self.sim_results.delete('1.0', tk.END)
            self.sim_results.insert('1.0', results_text)

            self.status_label.config(text="Status: Complete", foreground="green")

        except Exception as e:
            self.status_label.config(text=f"Status: Error - {str(e)}", foreground="red")
            messagebox.showerror("Simulation Error", str(e))
        finally:
            self.simulation_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')

    def reset_lighting_calc(self):
        """Reset lighting calculations"""
        self.p1_results.delete('1.0', tk.END)
        self.p2_results.delete('1.0', tk.END)

    def show_about(self):
        """Show about dialog"""
        about_text = """
Factory Lighting Calculator & Multi-Physics Simulator
Version 1.0

Advanced Electrical Engineering Application

Features:
• Factory lighting calculations with lumen method
• Multi-physics RLC circuit simulation
• Real-time ODE solvers (RK45, Euler)
• Dynamic visualization
• Auto-scaling interface

Developed for electrical engineering education and practical applications.
"""
        messagebox.showinfo("About", about_text)

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        if event.widget == self.root:
            # Auto-scale matplotlib canvas
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().update_idletasks()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = FactoryLightingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

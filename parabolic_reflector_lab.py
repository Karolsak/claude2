"""
Parabolic Reflector Multi-Physics Simulation Lab
Advanced calculator for optical and electrical engineering applications
Example 49.15: Parabolic Reflector Analysis with Dynamic Simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import odeint, solve_ivp
import math
from datetime import datetime


class ParabolicReflectorLab:
    """
    Comprehensive Parabolic Reflector and Multi-Physics Simulation Laboratory
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Parabolic Reflector Multi-Physics Simulation Lab")
        self.root.geometry("1400x900")

        # Simulation state
        self.is_running = False
        self.simulation_time = 0
        self.time_data = []
        self.simulation_data = {
            'intensity': [],
            'voltage': [],
            'current': [],
            'temperature': [],
            'power': []
        }

        # Default parameters for Example 49.15
        self.params = {
            'source_diameter': 2.5,  # cm
            'source_luminance': 1000,  # cd/cm²
            'focal_length': 10,  # cm
            'reflector_diameter': 40,  # cm
            'reflectance': 0.8,
            'source_offset': 0,  # cm (displacement from focus)
            'voltage_rms': 220,  # V
            'current_rms': 10,  # A
            'resistance': 22,  # Ω
            'inductance': 0.1,  # H
            'capacitance': 100e-6,  # F
            'thermal_mass': 500,  # J/K
            'ambient_temp': 25,  # °C
            'heat_transfer_coeff': 10  # W/K
        }

        # Simulation method
        self.ode_method = tk.StringVar(value="RK45")

        # Setup UI
        self.setup_ui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

        # Initial calculation
        self.calculate()

    def setup_ui(self):
        """Setup the user interface"""
        # Create main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - Controls
        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=1)

        # Right panel - Visualization
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=3)

        self.setup_control_panel(left_frame)
        self.setup_visualization_panel(right_frame)

    def setup_control_panel(self, parent):
        """Setup control panel with input parameters"""
        # Title
        title_label = ttk.Label(parent, text="Control Panel",
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Optical Parameters Section
        optical_frame = ttk.LabelFrame(scrollable_frame, text="Optical Parameters",
                                       padding=10)
        optical_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        self.sliders = {}

        optical_params = [
            ('source_diameter', 'Source Diameter (cm)', 0.5, 10, 0.1),
            ('source_luminance', 'Source Luminance (cd/cm²)', 100, 5000, 100),
            ('focal_length', 'Focal Length (cm)', 5, 50, 1),
            ('reflector_diameter', 'Reflector Diameter (cm)', 10, 100, 1),
            ('reflectance', 'Reflectance', 0.1, 1.0, 0.05),
            ('source_offset', 'Source Offset (cm)', -10, 10, 0.1)
        ]

        for param, label, min_val, max_val, resolution in optical_params:
            self.create_slider(optical_frame, param, label, min_val, max_val, resolution)

        # Electrical Parameters Section
        electrical_frame = ttk.LabelFrame(scrollable_frame, text="Electrical Parameters",
                                         padding=10)
        electrical_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        electrical_params = [
            ('voltage_rms', 'Voltage RMS (V)', 0, 500, 10),
            ('current_rms', 'Current RMS (A)', 0, 50, 1),
            ('resistance', 'Resistance (Ω)', 1, 100, 1),
            ('inductance', 'Inductance (H)', 0.01, 1, 0.01),
            ('capacitance', 'Capacitance (μF)', 1, 1000, 10)
        ]

        for param, label, min_val, max_val, resolution in electrical_params:
            if param == 'capacitance':
                # Convert to μF for display
                self.create_slider(electrical_frame, param, label, min_val, max_val,
                                 resolution, scale_factor=1e6)
            else:
                self.create_slider(electrical_frame, param, label, min_val, max_val,
                                 resolution)

        # Thermal Parameters Section
        thermal_frame = ttk.LabelFrame(scrollable_frame, text="Thermal Parameters",
                                      padding=10)
        thermal_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        thermal_params = [
            ('thermal_mass', 'Thermal Mass (J/K)', 100, 2000, 50),
            ('ambient_temp', 'Ambient Temp (°C)', 0, 50, 1),
            ('heat_transfer_coeff', 'Heat Transfer (W/K)', 1, 50, 1)
        ]

        for param, label, min_val, max_val, resolution in thermal_params:
            self.create_slider(thermal_frame, param, label, min_val, max_val, resolution)

        # ODE Method Selection
        method_frame = ttk.LabelFrame(scrollable_frame, text="Simulation Method",
                                     padding=10)
        method_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        ttk.Radiobutton(method_frame, text="Runge-Kutta 4/5 (RK45)",
                       variable=self.ode_method, value="RK45").pack(anchor=tk.W)
        ttk.Radiobutton(method_frame, text="Euler Method",
                       variable=self.ode_method, value="Euler").pack(anchor=tk.W)
        ttk.Radiobutton(method_frame, text="Radau (Stiff)",
                       variable=self.ode_method, value="Radau").pack(anchor=tk.W)

        # Control Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.BOTH, padx=5, pady=10)

        self.start_btn = ttk.Button(button_frame, text="Start Simulation",
                                    command=self.start_simulation)
        self.start_btn.pack(fill=tk.X, pady=2)

        self.stop_btn = ttk.Button(button_frame, text="Stop Simulation",
                                   command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)

        ttk.Button(button_frame, text="Reset",
                  command=self.reset_simulation).pack(fill=tk.X, pady=2)

        ttk.Button(button_frame, text="Calculate",
                  command=self.calculate).pack(fill=tk.X, pady=2)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_slider(self, parent, param_name, label, min_val, max_val,
                     resolution, scale_factor=1):
        """Create a labeled slider with value display"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)

        # Label
        ttk.Label(frame, text=label, width=25, anchor=tk.W).pack(side=tk.LEFT)

        # Value display
        value_var = tk.StringVar()
        current_val = self.params[param_name]
        if scale_factor != 1:
            current_val = current_val * scale_factor
        value_var.set(f"{current_val:.2f}")

        value_label = ttk.Label(frame, textvariable=value_var, width=8,
                               anchor=tk.E, relief=tk.SUNKEN)
        value_label.pack(side=tk.RIGHT, padx=5)

        # Slider
        slider = ttk.Scale(frame, from_=min_val, to=max_val,
                          orient=tk.HORIZONTAL,
                          command=lambda v: self.on_slider_change(param_name, v,
                                                                  value_var, scale_factor))
        slider.set(current_val)
        slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        self.sliders[param_name] = (slider, value_var, scale_factor)

    def on_slider_change(self, param_name, value, value_var, scale_factor):
        """Handle slider value changes"""
        val = float(value)
        value_var.set(f"{val:.2f}")

        # Update parameter (apply scale factor for storage)
        self.params[param_name] = val / scale_factor

        # Recalculate if not running simulation
        if not self.is_running:
            self.calculate()

    def setup_visualization_panel(self, parent):
        """Setup visualization panel with plots"""
        # Notebook for multiple tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Optical Analysis
        self.optical_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.optical_tab, text="Optical Analysis")

        # Tab 2: Electrical Simulation
        self.electrical_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.electrical_tab, text="Electrical Simulation")

        # Tab 3: Multi-Physics
        self.multiphysics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.multiphysics_tab, text="Multi-Physics")

        # Tab 4: Results
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Results & Analysis")

        self.setup_optical_tab()
        self.setup_electrical_tab()
        self.setup_multiphysics_tab()
        self.setup_results_tab()

    def setup_optical_tab(self):
        """Setup optical analysis visualizations"""
        # Create matplotlib figure
        self.optical_fig = Figure(figsize=(10, 8), dpi=100)

        # Create subplots
        gs = self.optical_fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        self.ax_reflector = self.optical_fig.add_subplot(gs[0:2, 0])
        self.ax_intensity = self.optical_fig.add_subplot(gs[0, 1])
        self.ax_beam = self.optical_fig.add_subplot(gs[1, 1])
        self.ax_offset = self.optical_fig.add_subplot(gs[2, :])

        # Create canvas
        self.optical_canvas = FigureCanvasTkAgg(self.optical_fig, self.optical_tab)
        self.optical_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_electrical_tab(self):
        """Setup electrical simulation visualizations"""
        self.electrical_fig = Figure(figsize=(10, 8), dpi=100)

        gs = self.electrical_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        self.ax_voltage = self.electrical_fig.add_subplot(gs[0, 0])
        self.ax_current = self.electrical_fig.add_subplot(gs[0, 1])
        self.ax_power = self.electrical_fig.add_subplot(gs[1, 0])
        self.ax_impedance = self.electrical_fig.add_subplot(gs[1, 1])

        self.electrical_canvas = FigureCanvasTkAgg(self.electrical_fig,
                                                   self.electrical_tab)
        self.electrical_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_multiphysics_tab(self):
        """Setup multi-physics simulation visualizations"""
        self.multiphysics_fig = Figure(figsize=(10, 8), dpi=100)

        gs = self.multiphysics_fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        self.ax_temp = self.multiphysics_fig.add_subplot(gs[0, 0])
        self.ax_thermal_power = self.multiphysics_fig.add_subplot(gs[0, 1])
        self.ax_efficiency = self.multiphysics_fig.add_subplot(gs[1, 0])
        self.ax_phase = self.multiphysics_fig.add_subplot(gs[1, 1])
        self.ax_combined = self.multiphysics_fig.add_subplot(gs[2, :])

        self.multiphysics_canvas = FigureCanvasTkAgg(self.multiphysics_fig,
                                                     self.multiphysics_tab)
        self.multiphysics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_results_tab(self):
        """Setup results and analysis display"""
        # Text widget for results
        text_frame = ttk.Frame(self.results_tab)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)

        self.results_text = tk.Text(text_frame, wrap=tk.NONE,
                                    yscrollcommand=v_scrollbar.set,
                                    xscrollcommand=h_scrollbar.set,
                                    font=('Courier', 10))

        v_scrollbar.config(command=self.results_text.yview)
        h_scrollbar.config(command=self.results_text.xview)

        # Grid layout
        self.results_text.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

    def calculate_optical_properties(self):
        """Calculate optical properties based on Example 49.15"""
        # Extract parameters
        d_source = self.params['source_diameter']  # cm
        L = self.params['source_luminance']  # cd/cm²
        f = self.params['focal_length']  # cm
        D = self.params['reflector_diameter']  # cm
        rho = self.params['reflectance']
        offset = self.params['source_offset']  # cm

        # Source area
        A_source = np.pi * (d_source / 2) ** 2  # cm²

        # Total luminous intensity of source (assuming Lambertian)
        I_source = L * A_source  # cd

        # Solid angle subtended by reflector at focus
        # For paraboloid: Ω = π * (D/(2f))² for small angles
        # More accurate: Ω = 2π * (1 - f/sqrt(f² + (D/2)²))
        R = D / 2  # reflector radius
        solid_angle = 2 * np.pi * (1 - f / np.sqrt(f**2 + R**2))

        # Fraction of light captured
        # For Lambertian source, luminous intensity varies as cos(θ)
        # Integration over solid angle gives captured flux
        captured_fraction = solid_angle / (2 * np.pi)  # Approximation for small angles

        # Axial intensity (light focused along axis)
        # I_axial = ρ * I_source * captured_fraction
        I_axial = rho * I_source * captured_fraction  # cd

        # More accurate calculation for axial intensity
        # Using the formula: I = ρ * L * A_source * (D/(4*f))²
        I_axial_accurate = rho * L * A_source * (D / (4 * f)) ** 2

        # Beam spread (divergence angle)
        # For source at focus, beam is collimated (parallel)
        # Beam spread ≈ source_diameter / focal_length (in radians)
        beam_spread_rad = d_source / f  # radians
        beam_spread_deg = np.degrees(beam_spread_rad)

        # Effective focal ratio (f-number)
        f_number = f / D

        # Calculate intensity distribution
        # When source is offset from focus
        if abs(offset) > 0.01:
            # Source not at focus - beam diverges/converges
            effective_f = f + offset
            beam_spread_rad_offset = d_source / effective_f
            beam_spread_deg_offset = np.degrees(beam_spread_rad_offset)
            I_axial_offset = rho * L * A_source * (D / (4 * effective_f)) ** 2
        else:
            beam_spread_deg_offset = beam_spread_deg
            I_axial_offset = I_axial_accurate

        results = {
            'source_area': A_source,
            'source_intensity': I_source,
            'solid_angle': solid_angle,
            'captured_fraction': captured_fraction,
            'axial_intensity': I_axial_accurate,
            'axial_intensity_offset': I_axial_offset,
            'beam_spread_deg': beam_spread_deg,
            'beam_spread_deg_offset': beam_spread_deg_offset,
            'beam_spread_rad': beam_spread_rad,
            'f_number': f_number
        }

        return results

    def calculate_electrical_properties(self):
        """Calculate electrical circuit properties"""
        V_rms = self.params['voltage_rms']
        I_rms = self.params['current_rms']
        R = self.params['resistance']
        L = self.params['inductance']
        C = self.params['capacitance']

        # Assuming 50 Hz AC frequency
        f = 50  # Hz
        omega = 2 * np.pi * f

        # Impedances
        X_L = omega * L  # Inductive reactance
        X_C = 1 / (omega * C)  # Capacitive reactance
        X = X_L - X_C  # Net reactance
        Z = np.sqrt(R**2 + X**2)  # Total impedance

        # Power calculations
        P_real = V_rms * I_rms * (R / Z)  # Real power (W)
        P_reactive = V_rms * I_rms * (X / Z)  # Reactive power (VAR)
        P_apparent = V_rms * I_rms  # Apparent power (VA)
        power_factor = R / Z

        # Phase angle
        phi = np.arctan2(X, R)  # radians
        phi_deg = np.degrees(phi)

        # Current through components (RMS)
        I_R = V_rms / R if R > 0 else 0
        I_L = V_rms / X_L if X_L > 0 else 0
        I_C = V_rms / abs(X_C) if X_C != 0 else 0

        results = {
            'impedance': Z,
            'inductive_reactance': X_L,
            'capacitive_reactance': X_C,
            'net_reactance': X,
            'real_power': P_real,
            'reactive_power': P_reactive,
            'apparent_power': P_apparent,
            'power_factor': power_factor,
            'phase_angle_deg': phi_deg,
            'current_R': I_R,
            'current_L': I_L,
            'current_C': I_C
        }

        return results

    def calculate_thermal_properties(self, electrical_results):
        """Calculate thermal properties"""
        P_dissipated = electrical_results['real_power']
        C_thermal = self.params['thermal_mass']
        h = self.params['heat_transfer_coeff']
        T_ambient = self.params['ambient_temp']

        # Steady-state temperature rise
        # P = h * ΔT
        delta_T_ss = P_dissipated / h if h > 0 else 0
        T_steady_state = T_ambient + delta_T_ss

        # Thermal time constant
        tau = C_thermal / h if h > 0 else 0

        # Thermal resistance
        R_thermal = 1 / h if h > 0 else 0

        results = {
            'power_dissipated': P_dissipated,
            'steady_state_temp': T_steady_state,
            'temp_rise': delta_T_ss,
            'thermal_time_constant': tau,
            'thermal_resistance': R_thermal
        }

        return results

    def calculate(self):
        """Perform all calculations and update displays"""
        # Calculate optical properties
        optical_results = self.calculate_optical_properties()

        # Calculate electrical properties
        electrical_results = self.calculate_electrical_properties()

        # Calculate thermal properties
        thermal_results = self.calculate_thermal_properties(electrical_results)

        # Update visualizations
        self.plot_optical_analysis(optical_results)
        self.plot_electrical_analysis(electrical_results)
        self.plot_multiphysics_analysis(optical_results, electrical_results,
                                       thermal_results)
        self.display_results(optical_results, electrical_results, thermal_results)

    def plot_optical_analysis(self, results):
        """Plot optical analysis"""
        # Clear previous plots
        self.ax_reflector.clear()
        self.ax_intensity.clear()
        self.ax_beam.clear()
        self.ax_offset.clear()

        # Plot 1: Parabolic reflector geometry
        f = self.params['focal_length']
        D = self.params['reflector_diameter']
        d_source = self.params['source_diameter']
        offset = self.params['source_offset']

        # Parabola equation: x² = 4*f*y
        y = np.linspace(0, D/2, 100)
        x_parabola = np.sqrt(4 * f * y)

        self.ax_reflector.plot(x_parabola, y, 'b-', linewidth=2, label='Reflector')
        self.ax_reflector.plot(-x_parabola, y, 'b-', linewidth=2)

        # Draw source at focus
        source_y = f + offset
        circle = plt.Circle((0, source_y), d_source/2, color='yellow',
                           edgecolor='orange', linewidth=2, label='Source')
        self.ax_reflector.add_patch(circle)

        # Draw focal point
        self.ax_reflector.plot(0, f, 'r*', markersize=15, label='Focus')

        # Draw sample rays
        n_rays = 5
        ray_angles = np.linspace(-D/2, D/2, n_rays)
        for ray_y in ray_angles:
            if abs(ray_y) <= D/2:
                ray_x = np.sqrt(4 * f * abs(ray_y)) if ray_y != 0 else 0
                # Ray from source to reflector
                self.ax_reflector.plot([0, ray_x], [source_y, abs(ray_y)],
                                      'r--', alpha=0.3, linewidth=0.5)
                # Reflected ray (parallel to axis if source at focus)
                if abs(offset) < 0.01:
                    self.ax_reflector.plot([ray_x, ray_x], [abs(ray_y), D],
                                          'g--', alpha=0.3, linewidth=0.5)
                else:
                    # Diverging/converging beam
                    slope = (abs(ray_y) - source_y) / (ray_x - 0) if ray_x != 0 else 0
                    reflected_slope = -slope
                    x_end = ray_x + (D - abs(ray_y)) / reflected_slope if reflected_slope != 0 else ray_x
                    self.ax_reflector.plot([ray_x, x_end], [abs(ray_y), D],
                                          'g--', alpha=0.3, linewidth=0.5)

        self.ax_reflector.set_xlabel('Radial Distance (cm)')
        self.ax_reflector.set_ylabel('Axial Distance (cm)')
        self.ax_reflector.set_title('Parabolic Reflector Geometry')
        self.ax_reflector.legend()
        self.ax_reflector.grid(True, alpha=0.3)
        self.ax_reflector.axis('equal')

        # Plot 2: Intensity distribution
        angles = np.linspace(-30, 30, 100)
        angles_rad = np.radians(angles)

        # Gaussian-like intensity distribution
        sigma = results['beam_spread_deg_offset'] / 2.355  # FWHM to sigma
        intensity_dist = results['axial_intensity_offset'] * np.exp(
            -(angles**2) / (2 * sigma**2))

        self.ax_intensity.plot(angles, intensity_dist, 'b-', linewidth=2)
        self.ax_intensity.fill_between(angles, intensity_dist, alpha=0.3)
        self.ax_intensity.axvline(0, color='r', linestyle='--', alpha=0.5)
        self.ax_intensity.set_xlabel('Angle (degrees)')
        self.ax_intensity.set_ylabel('Intensity (cd)')
        self.ax_intensity.set_title('Angular Intensity Distribution')
        self.ax_intensity.grid(True, alpha=0.3)

        # Plot 3: Beam spread visualization
        beam_spread = results['beam_spread_deg_offset']
        distance = np.linspace(0, 100, 50)
        beam_radius = distance * np.tan(np.radians(beam_spread / 2))

        self.ax_beam.plot(distance, beam_radius, 'b-', linewidth=2, label='Upper')
        self.ax_beam.plot(distance, -beam_radius, 'b-', linewidth=2, label='Lower')
        self.ax_beam.fill_between(distance, beam_radius, -beam_radius, alpha=0.3)
        self.ax_beam.set_xlabel('Distance from Reflector (cm)')
        self.ax_beam.set_ylabel('Beam Radius (cm)')
        self.ax_beam.set_title(f'Beam Spread: {beam_spread:.2f}°')
        self.ax_beam.grid(True, alpha=0.3)

        # Plot 4: Effect of source offset
        offsets = np.linspace(-10, 10, 50)
        intensities = []
        beam_spreads = []

        for off in offsets:
            effective_f = f + off
            if effective_f > 0:
                I = self.params['reflectance'] * self.params['source_luminance'] * \
                    np.pi * (self.params['source_diameter']/2)**2 * \
                    (D / (4 * effective_f)) ** 2
                bs = np.degrees(self.params['source_diameter'] / effective_f)
            else:
                I = 0
                bs = 0
            intensities.append(I)
            beam_spreads.append(bs)

        ax_offset2 = self.ax_offset.twinx()

        line1 = self.ax_offset.plot(offsets, intensities, 'b-', linewidth=2,
                                     label='Axial Intensity')
        self.ax_offset.axvline(offset, color='r', linestyle='--', alpha=0.5,
                              label='Current Position')

        line2 = ax_offset2.plot(offsets, beam_spreads, 'g-', linewidth=2,
                                label='Beam Spread')

        self.ax_offset.set_xlabel('Source Offset from Focus (cm)')
        self.ax_offset.set_ylabel('Axial Intensity (cd)', color='b')
        ax_offset2.set_ylabel('Beam Spread (degrees)', color='g')
        self.ax_offset.set_title('Effect of Source Displacement')
        self.ax_offset.tick_params(axis='y', labelcolor='b')
        ax_offset2.tick_params(axis='y', labelcolor='g')

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        self.ax_offset.legend(lines, labels, loc='upper left')
        self.ax_offset.grid(True, alpha=0.3)

        self.optical_canvas.draw()

    def plot_electrical_analysis(self, results):
        """Plot electrical analysis"""
        self.ax_voltage.clear()
        self.ax_current.clear()
        self.ax_power.clear()
        self.ax_impedance.clear()

        # Time-domain waveforms
        t = np.linspace(0, 0.04, 1000)  # 2 cycles at 50 Hz
        f = 50
        omega = 2 * np.pi * f

        V_rms = self.params['voltage_rms']
        I_rms = self.params['current_rms']
        phi = np.radians(results['phase_angle_deg'])

        # Voltage and current waveforms
        v_t = V_rms * np.sqrt(2) * np.sin(omega * t)
        i_t = I_rms * np.sqrt(2) * np.sin(omega * t - phi)

        # Plot 1: Voltage waveform
        self.ax_voltage.plot(t * 1000, v_t, 'b-', linewidth=2, label='Voltage')
        self.ax_voltage.axhline(V_rms, color='r', linestyle='--', alpha=0.5,
                               label=f'RMS = {V_rms:.1f} V')
        self.ax_voltage.axhline(-V_rms, color='r', linestyle='--', alpha=0.5)
        self.ax_voltage.set_xlabel('Time (ms)')
        self.ax_voltage.set_ylabel('Voltage (V)')
        self.ax_voltage.set_title('Voltage Waveform')
        self.ax_voltage.legend()
        self.ax_voltage.grid(True, alpha=0.3)

        # Plot 2: Current waveform
        self.ax_current.plot(t * 1000, i_t, 'g-', linewidth=2, label='Current')
        self.ax_current.axhline(I_rms, color='r', linestyle='--', alpha=0.5,
                               label=f'RMS = {I_rms:.1f} A')
        self.ax_current.axhline(-I_rms, color='r', linestyle='--', alpha=0.5)
        self.ax_current.set_xlabel('Time (ms)')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Current Waveform')
        self.ax_current.legend()
        self.ax_current.grid(True, alpha=0.3)

        # Plot 3: Power
        p_t = v_t * i_t
        p_avg = results['real_power']

        self.ax_power.plot(t * 1000, p_t, 'r-', linewidth=2, label='Instantaneous')
        self.ax_power.axhline(p_avg, color='b', linestyle='--', linewidth=2,
                             label=f'Average = {p_avg:.1f} W')
        self.ax_power.fill_between(t * 1000, 0, p_t, alpha=0.3)
        self.ax_power.set_xlabel('Time (ms)')
        self.ax_power.set_ylabel('Power (W)')
        self.ax_power.set_title('Instantaneous Power')
        self.ax_power.legend()
        self.ax_power.grid(True, alpha=0.3)

        # Plot 4: Impedance diagram (phasor)
        self.ax_impedance.clear()

        # Draw impedance triangle
        R = self.params['resistance']
        X = results['net_reactance']
        Z = results['impedance']

        # Resistance (real axis)
        self.ax_impedance.arrow(0, 0, R, 0, head_width=Z*0.05, head_length=Z*0.05,
                               fc='blue', ec='blue', linewidth=2, label='R')

        # Reactance (imaginary axis)
        self.ax_impedance.arrow(R, 0, 0, X, head_width=Z*0.05, head_length=abs(X)*0.05,
                               fc='green', ec='green', linewidth=2, label='X')

        # Impedance
        self.ax_impedance.arrow(0, 0, R, X, head_width=Z*0.05, head_length=Z*0.05,
                               fc='red', ec='red', linewidth=2, label='Z',
                               linestyle='--')

        # Annotations
        self.ax_impedance.text(R/2, -Z*0.1, f'R = {R:.1f} Ω', ha='center')
        self.ax_impedance.text(R+Z*0.1, X/2, f'X = {X:.1f} Ω', ha='left')
        self.ax_impedance.text(R/2, X/2, f'Z = {Z:.1f} Ω', ha='center', color='red')
        self.ax_impedance.text(R*0.3, 0, f'φ = {results["phase_angle_deg"]:.1f}°',
                              ha='center')

        # Arc for phase angle
        if abs(results['phase_angle_deg']) > 1:
            arc_angle = np.linspace(0, np.radians(results['phase_angle_deg']), 50)
            arc_r = Z * 0.15
            self.ax_impedance.plot(arc_r * np.cos(arc_angle),
                                  arc_r * np.sin(arc_angle), 'k-', linewidth=1)

        self.ax_impedance.set_xlabel('Real (Ω)')
        self.ax_impedance.set_ylabel('Imaginary (Ω)')
        self.ax_impedance.set_title('Impedance Phasor Diagram')
        self.ax_impedance.grid(True, alpha=0.3)
        self.ax_impedance.axis('equal')
        self.ax_impedance.legend()

        # Adjust limits
        margin = 1.2
        max_val = max(abs(R), abs(X), Z) * margin
        self.ax_impedance.set_xlim(-max_val*0.1, max_val)
        self.ax_impedance.set_ylim(-max_val*0.6, max_val*0.6)

        self.electrical_canvas.draw()

    def plot_multiphysics_analysis(self, optical_results, electrical_results,
                                   thermal_results):
        """Plot multi-physics analysis"""
        self.ax_temp.clear()
        self.ax_thermal_power.clear()
        self.ax_efficiency.clear()
        self.ax_phase.clear()
        self.ax_combined.clear()

        # Plot 1: Temperature vs Time
        if len(self.time_data) > 0:
            self.ax_temp.plot(self.time_data, self.simulation_data['temperature'],
                             'r-', linewidth=2)
            self.ax_temp.axhline(thermal_results['steady_state_temp'],
                                color='b', linestyle='--',
                                label=f"Steady State: {thermal_results['steady_state_temp']:.1f}°C")
            self.ax_temp.set_xlabel('Time (s)')
            self.ax_temp.set_ylabel('Temperature (°C)')
            self.ax_temp.set_title('Temperature Response')
            self.ax_temp.legend()
            self.ax_temp.grid(True, alpha=0.3)
        else:
            # Show steady-state analysis
            time_sim = np.linspace(0, 5 * thermal_results['thermal_time_constant'], 100)
            T_ambient = self.params['ambient_temp']
            T_ss = thermal_results['steady_state_temp']
            tau = thermal_results['thermal_time_constant']

            T_t = T_ambient + (T_ss - T_ambient) * (1 - np.exp(-time_sim / tau))

            self.ax_temp.plot(time_sim, T_t, 'r-', linewidth=2)
            self.ax_temp.axhline(T_ss, color='b', linestyle='--',
                                label=f'Steady State: {T_ss:.1f}°C')
            self.ax_temp.axhline(T_ambient, color='g', linestyle='--',
                                label=f'Ambient: {T_ambient:.1f}°C')
            self.ax_temp.set_xlabel('Time (s)')
            self.ax_temp.set_ylabel('Temperature (°C)')
            self.ax_temp.set_title('Thermal Response (Theoretical)')
            self.ax_temp.legend()
            self.ax_temp.grid(True, alpha=0.3)

        # Plot 2: Power flow diagram
        P_input = electrical_results['apparent_power']
        P_real = electrical_results['real_power']
        P_reactive = abs(electrical_results['reactive_power'])

        categories = ['Apparent', 'Real', 'Reactive']
        powers = [P_input, P_real, P_reactive]
        colors = ['blue', 'green', 'orange']

        bars = self.ax_thermal_power.bar(categories, powers, color=colors, alpha=0.7)
        self.ax_thermal_power.set_ylabel('Power (W or VA/VAR)')
        self.ax_thermal_power.set_title('Power Analysis')
        self.ax_thermal_power.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, power in zip(bars, powers):
            height = bar.get_height()
            self.ax_thermal_power.text(bar.get_x() + bar.get_width()/2., height,
                                      f'{power:.1f}',
                                      ha='center', va='bottom')

        # Plot 3: System efficiency
        optical_eff = optical_results['captured_fraction'] * self.params['reflectance']
        electrical_eff = electrical_results['power_factor']
        thermal_eff = min(1.0, thermal_results['power_dissipated'] /
                         (electrical_results['real_power'] + 1e-10))
        overall_eff = optical_eff * electrical_eff * thermal_eff

        efficiencies = [optical_eff, electrical_eff, thermal_eff, overall_eff]
        eff_labels = ['Optical', 'Electrical\n(PF)', 'Thermal', 'Overall']
        colors_eff = ['yellow', 'cyan', 'red', 'purple']

        bars = self.ax_efficiency.bar(eff_labels, efficiencies, color=colors_eff,
                                      alpha=0.7)
        self.ax_efficiency.set_ylabel('Efficiency')
        self.ax_efficiency.set_title('System Efficiencies')
        self.ax_efficiency.set_ylim(0, 1)
        self.ax_efficiency.grid(True, alpha=0.3, axis='y')

        for bar, eff in zip(bars, efficiencies):
            height = bar.get_height()
            self.ax_efficiency.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{eff*100:.1f}%',
                                   ha='center', va='bottom')

        # Plot 4: Phase space plot (if simulation running)
        if len(self.time_data) > 10:
            self.ax_phase.plot(self.simulation_data['voltage'],
                              self.simulation_data['current'],
                              'b-', linewidth=1, alpha=0.7)
            self.ax_phase.set_xlabel('Voltage (V)')
            self.ax_phase.set_ylabel('Current (A)')
            self.ax_phase.set_title('V-I Phase Space')
            self.ax_phase.grid(True, alpha=0.3)
        else:
            # Show theoretical phase relationship
            t = np.linspace(0, 0.02, 200)
            V_rms = self.params['voltage_rms']
            I_rms = self.params['current_rms']
            phi = np.radians(electrical_results['phase_angle_deg'])

            v = V_rms * np.sqrt(2) * np.sin(2 * np.pi * 50 * t)
            i = I_rms * np.sqrt(2) * np.sin(2 * np.pi * 50 * t - phi)

            self.ax_phase.plot(v, i, 'b-', linewidth=2)
            self.ax_phase.set_xlabel('Voltage (V)')
            self.ax_phase.set_ylabel('Current (A)')
            self.ax_phase.set_title('V-I Lissajous Pattern')
            self.ax_phase.grid(True, alpha=0.3)

        # Plot 5: Combined multi-physics time series
        if len(self.time_data) > 0:
            # Normalize data for comparison
            norm_temp = np.array(self.simulation_data['temperature']) / \
                       (max(self.simulation_data['temperature']) + 1e-10)
            norm_power = np.array(self.simulation_data['power']) / \
                        (max(self.simulation_data['power']) + 1e-10)
            norm_intensity = np.array(self.simulation_data['intensity']) / \
                           (max(self.simulation_data['intensity']) + 1e-10)

            self.ax_combined.plot(self.time_data, norm_temp, 'r-',
                                 label='Temperature', linewidth=2)
            self.ax_combined.plot(self.time_data, norm_power, 'b-',
                                 label='Power', linewidth=2)
            self.ax_combined.plot(self.time_data, norm_intensity, 'y-',
                                 label='Optical Intensity', linewidth=2)

            self.ax_combined.set_xlabel('Time (s)')
            self.ax_combined.set_ylabel('Normalized Value')
            self.ax_combined.set_title('Multi-Physics Coupling')
            self.ax_combined.legend()
            self.ax_combined.grid(True, alpha=0.3)
        else:
            self.ax_combined.text(0.5, 0.5, 'Start simulation to see real-time data',
                                 ha='center', va='center',
                                 transform=self.ax_combined.transAxes,
                                 fontsize=12)
            self.ax_combined.set_title('Multi-Physics Time Evolution')

        self.multiphysics_canvas.draw()

    def display_results(self, optical_results, electrical_results, thermal_results):
        """Display numerical results"""
        self.results_text.delete('1.0', tk.END)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""
{'='*80}
PARABOLIC REFLECTOR MULTI-PHYSICS SIMULATION RESULTS
{'='*80}
Generated: {timestamp}
Simulation Method: {self.ode_method.get()}

{'='*80}
OPTICAL ANALYSIS (Example 49.15)
{'='*80}

Input Parameters:
  Source Diameter:        {self.params['source_diameter']:.2f} cm
  Source Luminance:       {self.params['source_luminance']:.1f} cd/cm²
  Focal Length:           {self.params['focal_length']:.2f} cm
  Reflector Diameter:     {self.params['reflector_diameter']:.2f} cm
  Reflectance:            {self.params['reflectance']:.3f}
  Source Offset:          {self.params['source_offset']:.2f} cm

Calculated Results:
  Source Area:            {optical_results['source_area']:.3f} cm²
  Source Intensity:       {optical_results['source_intensity']:.1f} cd
  Solid Angle:            {optical_results['solid_angle']:.3f} sr
  Captured Fraction:      {optical_results['captured_fraction']*100:.2f}%

  AXIAL INTENSITY:        {optical_results['axial_intensity']:.2f} cd
  (with offset)           {optical_results['axial_intensity_offset']:.2f} cd

  BEAM SPREAD:            {optical_results['beam_spread_deg']:.3f}° ({optical_results['beam_spread_rad']:.4f} rad)
  (with offset)           {optical_results['beam_spread_deg_offset']:.3f}°

  F-number (f/#):         {optical_results['f_number']:.3f}

Physical Interpretation:
  - The parabolic reflector collimates {optical_results['captured_fraction']*100:.1f}% of the source light
  - With {self.params['reflectance']*100:.0f}% reflectance, effective collection is {optical_results['captured_fraction']*self.params['reflectance']*100:.1f}%
  - Beam divergence is {optical_results['beam_spread_deg']:.2f}° (nearly collimated)
  - Moving source from focus {'increases' if self.params['source_offset'] > 0 else 'decreases' if self.params['source_offset'] < 0 else 'does not change'} beam spread

{'='*80}
ELECTRICAL ANALYSIS
{'='*80}

Circuit Parameters:
  Voltage (RMS):          {self.params['voltage_rms']:.1f} V
  Current (RMS):          {self.params['current_rms']:.2f} A
  Resistance:             {self.params['resistance']:.2f} Ω
  Inductance:             {self.params['inductance']:.3f} H
  Capacitance:            {self.params['capacitance']*1e6:.1f} μF

Impedance Analysis:
  Inductive Reactance:    {electrical_results['inductive_reactance']:.3f} Ω
  Capacitive Reactance:   {electrical_results['capacitive_reactance']:.3f} Ω
  Net Reactance:          {electrical_results['net_reactance']:.3f} Ω
  Total Impedance:        {electrical_results['impedance']:.3f} Ω

Power Analysis:
  Real Power:             {electrical_results['real_power']:.2f} W
  Reactive Power:         {electrical_results['reactive_power']:.2f} VAR
  Apparent Power:         {electrical_results['apparent_power']:.2f} VA
  Power Factor:           {electrical_results['power_factor']:.4f} {'(lagging)' if electrical_results['net_reactance'] > 0 else '(leading)' if electrical_results['net_reactance'] < 0 else '(unity)'}
  Phase Angle:            {electrical_results['phase_angle_deg']:.2f}°

Component Currents (RMS):
  Through Resistor:       {electrical_results['current_R']:.3f} A
  Through Inductor:       {electrical_results['current_L']:.3f} A
  Through Capacitor:      {electrical_results['current_C']:.3f} A

{'='*80}
THERMAL ANALYSIS
{'='*80}

Thermal Parameters:
  Thermal Mass:           {self.params['thermal_mass']:.1f} J/K
  Heat Transfer Coeff:    {self.params['heat_transfer_coeff']:.2f} W/K
  Ambient Temperature:    {self.params['ambient_temp']:.1f} °C

Thermal Results:
  Power Dissipated:       {thermal_results['power_dissipated']:.2f} W
  Thermal Resistance:     {thermal_results['thermal_resistance']:.4f} K/W
  Thermal Time Constant:  {thermal_results['thermal_time_constant']:.2f} s

  Temperature Rise:       {thermal_results['temp_rise']:.2f} °C
  STEADY STATE TEMP:      {thermal_results['steady_state_temp']:.2f} °C

{'='*80}
MULTI-PHYSICS SUMMARY
{'='*80}

System Efficiencies:
  Optical Efficiency:     {optical_results['captured_fraction'] * self.params['reflectance']:.2%}
  Electrical Efficiency:  {electrical_results['power_factor']:.2%} (Power Factor)
  Thermal Efficiency:     {min(1.0, thermal_results['power_dissipated'] / (electrical_results['real_power'] + 1e-10)):.2%}

Energy Flow:
  Electrical Input:       {electrical_results['apparent_power']:.2f} VA
  Real Power:             {electrical_results['real_power']:.2f} W
  Heat Dissipated:        {thermal_results['power_dissipated']:.2f} W
  Optical Output:         {optical_results['axial_intensity']:.2f} cd

Recommendations:
  1. {'Source is at optimal position (focus)' if abs(self.params['source_offset']) < 0.1 else 'Adjust source position to focus for optimal collimation'}
  2. {'Power factor is good (>{0.9})'.format('') if electrical_results['power_factor'] > 0.9 else 'Consider power factor correction (current PF: {:.2f})'.format(electrical_results['power_factor'])}
  3. {'Operating temperature is safe' if thermal_results['steady_state_temp'] < 80 else 'WARNING: High operating temperature - improve cooling'}
  4. {'Reflector efficiency is good' if self.params['reflectance'] > 0.7 else 'Consider higher reflectance coating'}

{'='*80}
SIMULATION STATUS
{'='*80}
  Time Steps Completed:   {len(self.time_data)}
  Simulation Time:        {self.simulation_time:.3f} s
  Status:                 {'RUNNING' if self.is_running else 'STOPPED'}

{'='*80}
"""

        self.results_text.insert('1.0', report)

    def start_simulation(self):
        """Start real-time dynamic simulation"""
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.run_simulation_step()

    def stop_simulation(self):
        """Stop simulation"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def reset_simulation(self):
        """Reset simulation data"""
        self.stop_simulation()
        self.simulation_time = 0
        self.time_data = []
        for key in self.simulation_data:
            self.simulation_data[key] = []
        self.calculate()

    def run_simulation_step(self):
        """Run one step of dynamic simulation"""
        if not self.is_running:
            return

        dt = 0.05  # Time step (50 ms)

        # Get current results
        optical_results = self.calculate_optical_properties()
        electrical_results = self.calculate_electrical_properties()
        thermal_results = self.calculate_thermal_properties(electrical_results)

        # Add noise/variation to simulate dynamics
        noise_factor = 0.02  # 2% noise
        intensity_variation = optical_results['axial_intensity_offset'] * \
                            (1 + noise_factor * np.random.randn())

        # Calculate instantaneous values (sinusoidal)
        omega = 2 * np.pi * 50  # 50 Hz
        v_inst = self.params['voltage_rms'] * np.sqrt(2) * \
                np.sin(omega * self.simulation_time)
        i_inst = self.params['current_rms'] * np.sqrt(2) * \
                np.sin(omega * self.simulation_time -
                       np.radians(electrical_results['phase_angle_deg']))
        p_inst = v_inst * i_inst

        # Temperature dynamics (first-order thermal system)
        if len(self.simulation_data['temperature']) == 0:
            T_current = self.params['ambient_temp']
        else:
            T_current = self.simulation_data['temperature'][-1]

        T_ambient = self.params['ambient_temp']
        tau = thermal_results['thermal_time_constant']
        T_ss = thermal_results['steady_state_temp']

        # ODE: dT/dt = (T_ss - T) / tau
        if self.ode_method.get() == "Euler":
            # Euler method
            dT_dt = (T_ss - T_current) / tau
            T_new = T_current + dT_dt * dt
        else:
            # Exponential solution (exact for first-order system)
            T_new = T_ss + (T_current - T_ss) * np.exp(-dt / tau)

        # Store data
        self.time_data.append(self.simulation_time)
        self.simulation_data['intensity'].append(intensity_variation)
        self.simulation_data['voltage'].append(v_inst)
        self.simulation_data['current'].append(i_inst)
        self.simulation_data['temperature'].append(T_new)
        self.simulation_data['power'].append(p_inst)

        # Limit data points to last 1000
        if len(self.time_data) > 1000:
            self.time_data.pop(0)
            for key in self.simulation_data:
                self.simulation_data[key].pop(0)

        # Increment time
        self.simulation_time += dt

        # Update plots every 10 steps (for performance)
        if len(self.time_data) % 10 == 0:
            optical_results = self.calculate_optical_properties()
            electrical_results = self.calculate_electrical_properties()
            thermal_results = self.calculate_thermal_properties(electrical_results)

            self.plot_multiphysics_analysis(optical_results, electrical_results,
                                           thermal_results)
            self.display_results(optical_results, electrical_results, thermal_results)

        # Schedule next step
        if self.is_running:
            self.root.after(50, self.run_simulation_step)  # 50 ms delay (20 Hz update)

    def on_window_resize(self, event):
        """Handle window resize event for auto-scaling"""
        # Only handle resize of main window
        if event.widget == self.root:
            # Figures will automatically rescale due to pack(fill=BOTH, expand=True)
            pass


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ParabolicReflectorLab(root)
    root.mainloop()


if __name__ == "__main__":
    main()

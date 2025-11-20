# Resistance Oven Multi-Physics Simulator

A comprehensive Python application for designing and simulating resistance ovens with advanced thermal-electrical modeling.

## 🎯 Features

### 1. **Static Design Calculator**
- Solves Problem 4: Single-phase cylindrical wire heating elements
- Solves Problem 5: Three-phase star-connected rectangular strip elements
- Calculates wire/strip dimensions (diameter, width, length)
- Uses Stefan-Boltzmann law for radiative heat transfer
- Comprehensive verification of all calculations

### 2. **Dynamic Multi-Physics Simulation**
- **Coupled thermal-electrical modeling** with differential equations
- **Real-time ODE solvers**: RK45 (Runge-Kutta 4-5) and Euler method
- **Interactive control sliders** for voltage and efficiency adjustment
- **Temperature-dependent resistance** modeling
- **Heat transfer mechanisms**: Radiation, convection, and conduction
- **Start/Stop/Reset controls** for simulation management

### 3. **Advanced Visualization**
- **Real-time plotting** during simulation
- **6 comprehensive plots**:
  - Temperature evolution (wire and charge)
  - Current evolution
  - Power consumption
  - Phase space diagram (Temperature vs Current)
  - Heat transfer analysis
  - System efficiency
- **Auto-scaling** when window is resized
- **Export to CSV** functionality

### 4. **Multi-Physics Models**

#### Electrical Model:
```
V_rms = Applied voltage (RMS value)
R(T) = R_base × (1 + α × (T - T_ref))
I = V_rms / R(T)
P = V_rms² / R(T)
```

#### Thermal Model:
```
dT_wire/dt = (P_elec - Q_rad - Q_loss) / (m_wire × c_p_wire)
dT_charge/dt = (Q_rad - Q_charge_loss) / (m_charge × c_p_charge)
```

#### Heat Transfer:
```
Q_rad = η × ε × σ × A × (T_wire⁴ - T_charge⁴)
Q_conv = h × A × (T - T_ambient)
```

Where:
- η = Radiating efficiency
- ε = Emissivity
- σ = Stefan-Boltzmann constant (5.67×10⁻⁸ W/(m²·K⁴))
- h = Convection coefficient

## 📋 Problems Solved

### Problem 4: Single-Phase Cylindrical Wire
**Given:**
- Power: 15 kW
- Voltage: 220 V (single-phase)
- Wire temperature: 1000°C
- Charge temperature: 600°C
- Radiating efficiency: 0.6
- Emissivity: 0.9
- Resistivity: 1.016×10⁻⁶ Ω·m

**Find:** Wire diameter and length

**Expected Results:** Diameter = 3.11 mm, Length = 24.24 m

### Problem 5: Three-Phase Rectangular Strip
**Given:**
- Power: 30 kW (total)
- Voltage: 400 V (line-to-line, 3-phase star)
- Wire temperature: 1100°C
- Charge temperature: 700°C
- Strip thickness: 0.025 cm
- Radiating efficiency: 0.6
- Emissivity: 0.9
- Resistivity: 1.03×10⁻⁶ Ω·m

**Find:** Strip width

## 🚀 Installation

### Requirements:
```bash
pip install numpy scipy matplotlib tkinter
```

Note: `tkinter` usually comes pre-installed with Python.

### Files:
1. `resistance_oven_simulator.py` - Main GUI application
2. `test_oven_simulator.py` - Test suite
3. `README_OVEN_SIMULATOR.md` - This documentation

## 💻 Usage

### Running the GUI Simulator:
```bash
python resistance_oven_simulator.py
```

### Running Tests:
```bash
python test_oven_simulator.py
```

## 📖 User Guide

### Tab 1: Static Design Calculator

1. **Select Problem Type**:
   - Problem 4: Single-phase cylindrical wire
   - Problem 5: Three-phase rectangular strip

2. **Enter Parameters**:
   - Power (kW)
   - Voltage (V)
   - Wire temperature (°C)
   - Charge temperature (°C)
   - Radiating efficiency
   - Emissivity
   - Resistivity (×10⁻⁶ Ω·m)
   - Strip thickness (mm) - for Problem 5 only

3. **Click Calculate**:
   - Results appear in the right panel
   - Includes dimensions, resistance, heat flux
   - Verification calculations shown

### Tab 2: Dynamic Simulation

1. **Set Simulation Parameters**:
   - Simulation time (s)
   - Applied voltage (V)
   - Base resistance (Ω)
   - Temperature coefficient
   - Material properties (mass, specific heat)
   - Surface area (m²)
   - Ambient temperature (°C)

2. **Set Initial Conditions**:
   - Initial wire temperature (°C)
   - Initial charge temperature (°C)

3. **Choose ODE Solver**:
   - RK45: More accurate, adaptive step size
   - Euler: Simpler, fixed step size

4. **Use Control Sliders**:
   - Voltage adjustment: 0-150% of nominal
   - Efficiency adjustment: 0-100%

5. **Control Simulation**:
   - **Start**: Begin simulation
   - **Stop**: Pause simulation
   - **Reset**: Clear all data and plots

6. **Watch Real-Time Plots**:
   - Temperature evolution
   - Current variation
   - Power consumption

### Tab 3: Results Visualization

1. **Run a simulation** in Tab 2

2. **Click "Update Visualization"** to generate:
   - Temperature evolution plot
   - Current evolution plot
   - Power consumption plot
   - Phase space diagram
   - Heat transfer analysis
   - System efficiency plot

3. **Export Data**:
   - Click "Export Data to CSV"
   - Choose location and filename
   - Data includes: Time, Temperatures, Current, Power

## 🔬 Technical Details

### Mathematical Models

#### 1. Wire Diameter Calculation (Problem 4):

For a cylindrical wire:
- Surface area: A = π × d × L
- Resistance: R = ρ × L / (π × (d/2)²)

Heat balance:
```
P = Q_rad = η × ε × σ × A × (T_wire⁴ - T_charge⁴)
```

Solving simultaneously:
```
d³ = (4 × ρ × A) / (R × π²)
d = ∛[(4 × ρ × P) / (R × π² × q)]
```

#### 2. Strip Width Calculation (Problem 5):

For a rectangular strip:
- Surface area: A = 2 × w × L (both sides)
- Resistance: R = ρ × L / (w × t)

For star connection:
- V_phase = V_line / √3
- P_phase = P_total / 3

Solving:
```
w² = (A × ρ) / (2 × R × t)
w = √[(A × ρ) / (2 × R × t)]
```

#### 3. Dynamic Thermal-Electrical Model:

Differential equations:
```python
dT_wire/dt = (P_elec - Q_rad - Q_loss_conv - Q_loss_rad) / (m_wire × c_p_wire)
dT_charge/dt = (Q_rad - Q_charge_loss) / (m_charge × c_p_charge)
dI/dt = (I_target - I) / τ_elec
```

Where:
- P_elec = V² / R(T)
- R(T) = R_base × (1 + α × ΔT)
- Q_rad = η × ε × σ × A × (T_w⁴ - T_c⁴)

### ODE Solvers

#### RK45 (Runge-Kutta 4-5):
- **Advantages**:
  - High accuracy (5th order)
  - Adaptive step size
  - Error control
- **Use when**: Accuracy is critical

#### Euler Method:
- **Advantages**:
  - Simple implementation
  - Fast for stiff problems
  - Fixed time step
- **Use when**: Speed is more important than precision

## 📊 Output Examples

### Static Calculation Output:
```
PROBLEM 4: SINGLE-PHASE CYLINDRICAL WIRE
=========================================

INPUT PARAMETERS:
  Power: 15.00 kW
  Voltage: 220.00 V
  Wire Temperature: 1000.00 °C
  Charge Temperature: 600.00 °C

RESULTS:
  Wire Diameter: 3.11 mm
  Wire Length: 24.24 m
  Resistance: 3.227 Ω
  Surface Area: 0.2377 m²
  Heat Flux: 63104.52 W/m²

VERIFICATION:
  Calculated Resistance: 3.227 Ω
  Power Check: 15.00 kW
```

### Dynamic Simulation Features:
- Temperature rises from ambient to steady-state
- Current stabilizes based on temperature-dependent resistance
- Power consumption varies with operating conditions
- Real-time response to control adjustments

## 🎓 Educational Value

This simulator is ideal for:
- **Electrical Engineering students** studying heating systems
- **Thermal analysis** of resistance ovens
- **Understanding multi-physics coupling** (thermal + electrical)
- **Learning numerical methods** (ODE solvers)
- **Control systems** education (real-time adjustments)
- **Design optimization** of heating elements

## 🔧 Advanced Features

### Window Auto-Scaling:
- All plots automatically resize with window
- Maintains aspect ratios
- Responsive layout

### Real-Time Simulation:
- Updates every 0.05 seconds
- Smooth animation
- Interactive controls during simulation

### Data Export:
- CSV format for easy analysis
- Compatible with Excel, MATLAB, Python
- Includes all time-series data

## 🐛 Troubleshooting

### Common Issues:

1. **ImportError: No module named 'tkinter'**
   ```bash
   # On Ubuntu/Debian:
   sudo apt-get install python3-tk

   # On Fedora:
   sudo dnf install python3-tkinter
   ```

2. **Simulation runs too fast/slow**
   - Adjust simulation time in parameters
   - Change solver (RK45 vs Euler)
   - Modify time step in code if needed

3. **Plots not updating**
   - Click "Update Visualization" in Results tab
   - Ensure simulation has run
   - Check for console errors

## 📝 License

This educational software is provided as-is for learning purposes.

## 👨‍💻 Author

Created for electrical engineering education and research.

## 🔗 References

1. Stefan-Boltzmann Law: Q = η × ε × σ × A × (T₁⁴ - T₂⁴)
2. Joule Heating: P = I²R = V²/R
3. Heat Transfer Fundamentals
4. Numerical Methods for ODEs

## 📧 Support

For issues or questions, please refer to the test suite for examples and verification.

---

**Version**: 1.0
**Last Updated**: 2025-11-20
**Python Version**: 3.7+

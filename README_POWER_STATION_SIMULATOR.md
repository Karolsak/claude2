# Advanced Power Station Dynamic Simulator

## Overview

This comprehensive Python application combines power station economics analysis with real-time dynamic system simulation for electrical engineering applications. It features an advanced Tkinter GUI with interactive controls, multiple ODE solvers, and real-time visualization.

## Problem Statement

A power station with the following specifications:
- **Maximum Demand**: 100 MW
- **Load Factor**: 30%
- **Annual Energy Requirement**: 262,800,000 kWh

Three supply schemes are analyzed:
1. **Scheme A**: Steam + Hydro combination (Hydro: 10⁸ kWh/year, 40 MW max)
2. **Scheme B**: Steam only (100 MW capacity)
3. **Scheme C**: Hydro only (100 MW capacity)

### Cost Parameters

| Parameter | Steam | Hydro |
|-----------|-------|-------|
| Capital Cost (Rs/kW) | 600 | 1500 |
| Interest & Depreciation | 12% | 10% |
| Operating Cost (Rs/kWh) | 0.05 | 0.01 |
| Transmission Cost (Rs/kWh) | - | 0.0025 |

## Solution Summary

### Economic Analysis Results

**Scheme A (Steam + Hydro):**
- Steam Capacity: 60,000 kW
- Hydro Capacity: 40,000 kW
- Total Annual Cost: Rs. 15,960,000
- **Cost per Unit: Rs. 0.0607/kWh**

**Scheme B (Steam Only):**
- Steam Capacity: 100,000 kW
- Total Annual Cost: Rs. 20,340,000
- **Cost per Unit: Rs. 0.0774/kWh**

**Scheme C (Hydro Only):**
- Hydro Capacity: 100,000 kW
- Total Annual Cost: Rs. 18,282,000
- **Cost per Unit: Rs. 0.0696/kWh**

### Recommendation

**Scheme A (Steam + Hydro)** is the most economical with **Rs. 0.0607 per kWh**, offering:
- 21.6% savings vs Scheme B
- 12.8% savings vs Scheme C

## Features

### 1. User Interface (Tkinter GUI)

#### Main Menu
- **File Menu**: Economics analysis, exit
- **Simulation Menu**: Start, stop, reset controls
- **Settings Menu**: System parameters, solver configuration
- **Help Menu**: About and documentation

#### Input Parameters
- Maximum demand configuration
- Load factor adjustment
- Capital and operating costs
- System constants

#### Control Panel
- **Interactive Sliders**:
  - Inertia Constant (M): 1-50 seconds
  - Damping Coefficient (D): 0.1-10
  - Maximum Power Transfer (Pmax): 0.5-5 pu
  - Fault Duration: 0-1 second

### 2. Calculation Modules

#### Mathematical Modeling

**Swing Equation** (Synchronous Generator Dynamics):
```
M · dω/dt = Pm - Pe - D·(ω - 1)
dδ/dt = ω₀·(ω - 1)
```

Where:
- `M` = Inertia constant (seconds)
- `ω` = Rotor speed (per unit)
- `δ` = Rotor angle (radians)
- `Pm` = Mechanical power (per unit)
- `Pe` = Electrical power = Pmax·sin(δ)
- `D` = Damping coefficient
- `ω₀` = Synchronous speed (2π·50 rad/s)

#### Dynamic Simulation

**ODE Solvers Implemented**:

1. **RK45 (Runge-Kutta 4th/5th Order)**
   - Higher accuracy
   - Better for stiff equations
   - Adaptive time stepping
   - Formula:
   ```
   k₁ = f(t, y)
   k₂ = f(t + h/2, y + h·k₁/2)
   k₃ = f(t + h/2, y + h·k₂/2)
   k₄ = f(t + h, y + h·k₃)
   y_{n+1} = y_n + h·(k₁ + 2k₂ + 2k₃ + k₄)/6
   ```

2. **Euler Method (1st Order)**
   - Faster computation
   - Simpler implementation
   - Formula: `y_{n+1} = y_n + h·f(t, y)`

### 3. Results Visualization

#### Real-Time Plots
- **Rotor Angle (δ)**: Shows oscillations and stability
- **Rotor Speed (ω)**: Frequency deviation from synchronous speed
- **Electrical Power (Pe)**: Power transfer dynamics

#### Features
- Auto-scaling axes
- Continuous data streaming
- 1000-point rolling window
- Grid lines and reference markers

#### Control Buttons
- **▶ Start**: Begin simulation
- **⏸ Stop**: Pause simulation
- **⟲ Reset**: Reset to initial conditions

### 4. Auto-Scaling

The application automatically adjusts to window size changes:
- Dynamic plot resizing
- Responsive layout
- Maintains aspect ratios
- Real-time canvas updates

## Practical Electrical Engineering Applications

### 1. Transient Stability Analysis
- Study generator response to disturbances
- Analyze critical clearing times
- Evaluate system stability margins

### 2. Fault Simulation
- Three-phase fault analysis
- Clearing time effects
- Post-fault recovery dynamics

### 3. Parameter Sensitivity
- Inertia constant effects
- Damping coefficient impact
- Power transfer capability

### 4. Load Frequency Control
- Speed governor response
- Frequency regulation
- AGC system design

### 5. Power System Planning
- Economic comparison of schemes
- Cost optimization
- Capacity planning

## Installation

### Requirements
```bash
pip install numpy matplotlib
```

### System Requirements
- Python 3.6 or higher
- Tkinter (usually included with Python)
- NumPy for numerical computations
- Matplotlib for plotting

## Usage

### Running the Application
```bash
python3 power_station_dynamic_simulator.py
```

### Quick Start Guide

1. **Launch Application**
   ```bash
   python3 power_station_dynamic_simulator.py
   ```

2. **View Economics Analysis**
   - Click "File" → "Calculate Economics"
   - Review all three schemes
   - Compare costs in Summary tab

3. **Start Dynamic Simulation**
   - Click "▶ Start" button
   - Observe real-time plots
   - Adjust parameters with sliders

4. **Apply Fault**
   - Set fault duration (slider)
   - Click "Apply Fault" during simulation
   - Observe transient response

5. **Change Solver**
   - Select RK45 or Euler
   - Compare accuracy and performance

### Advanced Usage

#### Custom Parameter Studies

1. **Stability Margin Analysis**:
   - Increase Pmax gradually
   - Observe critical instability point
   - Note angle oscillations

2. **Inertia Effect Study**:
   - Vary M from low to high
   - Apply same fault
   - Compare recovery times

3. **Damping Impact**:
   - Test with D = 0 (no damping)
   - Add damping incrementally
   - Observe oscillation decay

## Technical Details

### State Variables
- `δ` (delta): Rotor angle in radians
- `ω` (omega): Rotor speed in per unit (1.0 = synchronous)

### System Parameters
- **Default Inertia (M)**: 10 seconds
- **Default Damping (D)**: 2.0
- **Default Pmax**: 2.0 pu
- **Time Step (dt)**: 0.01 seconds
- **Base Frequency**: 50 Hz

### Performance
- Real-time simulation at 1:1 time ratio
- 100 fps update rate
- 1000-point data buffer
- Multi-threaded execution

## Code Structure

```
power_station_dynamic_simulator.py
│
├── Data Classes
│   ├── PowerStationData: Economic parameters
│   └── DynamicSystemState: System state variables
│
├── Economics Calculator
│   └── PowerStationEconomics: Cost analysis for all schemes
│
├── ODE Solvers
│   ├── euler(): 1st order explicit method
│   └── rk45(): 4th/5th order Runge-Kutta
│
├── Dynamic System
│   └── PowerSystemDynamics: Swing equation implementation
│
└── GUI Application
    ├── Main window with menu
    ├── Control panel with sliders
    ├── Real-time visualization
    └── Economics display
```

## Example Use Cases

### Case 1: Economic Planning
A utility company needs to decide between three power generation schemes. Using this tool:
1. Input actual cost data
2. Review detailed breakdown
3. Compare total costs
4. Make informed decision

### Case 2: Stability Study
An engineer needs to verify generator stability:
1. Set system parameters (M, D, Pmax)
2. Apply various fault durations
3. Observe if system remains stable
4. Determine critical clearing time

### Case 3: Teaching Tool
For electrical engineering education:
1. Demonstrate swing equation dynamics
2. Show effects of parameter changes
3. Visualize transient stability
4. Interactive learning experience

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'matplotlib'**
   ```bash
   pip install matplotlib
   ```

2. **tkinter not found**
   - On Ubuntu/Debian: `sudo apt-get install python3-tk`
   - On macOS: Included with Python
   - On Windows: Included with Python

3. **Simulation runs too fast/slow**
   - Adjust `dt` in code (default: 0.01)
   - Change `time.sleep(self.dt)` in `run_simulation()`

4. **Plots not updating**
   - Check if simulation is running
   - Verify canvas refresh rate
   - Ensure threading is working

## Mathematical Background

### Swing Equation Derivation

The swing equation describes the rotor dynamics of a synchronous machine:

```
J · d²δ/dt² = Pm - Pe - D·dδ/dt
```

Converting to per unit with `M = J·ω₀/(2·S)`:

```
M · dω/dt = Pm - Pe - D·(ω - 1)
dδ/dt = ω₀·(ω - 1)
```

This second-order equation represents energy balance between mechanical input and electrical output.

### Power Transfer Equation

For a lossless transmission line:

```
Pe = Pmax · sin(δ)
```

Where:
- `Pmax = (V₁·V₂)/(X)` (maximum power transfer)
- `δ` = load angle between sending and receiving ends

## Future Enhancements

Potential additions:
- Multi-machine simulation
- IEEE standard test systems
- Governor and exciter models
- Advanced fault types
- Data export functionality
- Parameter optimization
- Sensitivity analysis tools

## References

1. Power System Stability and Control - Kundur
2. Power System Dynamics - Machowski
3. Modern Power System Analysis - Kothari & Nagrath

## License

This educational software is provided as-is for learning and research purposes.

## Author

Developed for electrical engineering applications and power system analysis.

## Version History

**v1.0** (2025-11-22)
- Initial release
- Economic analysis for three schemes
- Dynamic simulation with swing equation
- RK45 and Euler ODE solvers
- Real-time visualization
- Interactive parameter control
- Auto-scaling interface
- Fault simulation capability

---

**Note**: This simulator uses simplified models for educational purposes. For actual power system analysis, use specialized software like PSS/E, PowerWorld, or PSCAD.

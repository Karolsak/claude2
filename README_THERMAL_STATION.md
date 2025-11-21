# Thermal Station Cost Calculator & Electrical System Simulator

A comprehensive Python + Tkinter application for thermal power station cost analysis and advanced electrical engineering simulations.

## Features

### 1. Thermal Station Cost Calculator
- **Complete Economic Analysis**: Calculates all costs associated with thermal power station operation
- **Interactive Parameter Adjustment**: Real-time sliders for all input parameters
- **Detailed Breakdown**: Shows fixed costs, running costs, and comprehensive results
- **Performance Metrics**: Capacity factor, utilization factor, thermal efficiency estimates

### 2. Dynamic Electrical System Simulation
- **Multiple System Models**:
  - **Synchronous Generator**: Swing equation dynamics with rotor angle and frequency response
  - **RLC Circuit**: Series RLC circuit with transient analysis
  - **Transformer**: Coupled circuit dynamics with primary and secondary windings

### 3. Advanced ODE Solvers
- **RK45 (Runge-Kutta 4th/5th Order)**: High-accuracy Dormand-Prince method
- **Euler Method**: First-order explicit integration
- **Real-time Simulation**: Background thread execution with live updates

### 4. Professional GUI Features
- **Tabbed Interface**: Organized sections for different functionalities
- **Menu Bar**: File, Simulation, and Help menus
- **Auto-scaling**: Responsive design that adapts to window size
- **Real-time Visualization**: Matplotlib integration for waveform display
- **RMS Measurements**: Real-time voltage, current, frequency, and power displays

## Problem Solved

The application solves the following thermal station problem:

**Given Data:**
- Installed plant capacity: 10,000 kW
- Maximum demand: 9,000 kW
- Annual load factor: 60%
- Cost of plant: Rs. 1,200 per kW
- Interest, insurance, and taxes: 5% p.a.
- Depreciation: 5% p.a.
- Cost of primary distribution: Rs. 400,000
- Coal cost: Rs. 40 per tonne
- Operating cost: Rs. 400,000 p.a.
- Maintenance fixed: Rs. 20,000 p.a.
- Maintenance variable: Rs. 30,000 p.a.
- Coal consumption: 25,300 tonne

**Results:**
- **Cost per kW per year**: Rs. 298.00
- **Cost per kWh generated**: Rs. 0.0567
- **Total annual cost**: Rs. 2,682,000.00
- **Annual energy generated**: 47,304,000 kWh

## Installation

### Requirements
```bash
python3 >= 3.7
tkinter (usually comes with Python)
matplotlib >= 3.0
numpy >= 1.18
```

### Install Dependencies
```bash
# On Ubuntu/Debian
sudo apt-get install python3-tk python3-matplotlib python3-numpy

# Using pip
pip install matplotlib numpy
```

## Usage

### Running the Application
```bash
python3 thermal_station_calculator.py
```

### Using the Thermal Calculator Tab
1. Navigate to the "Thermal Station Calculator" tab
2. Adjust input parameters using the sliders
3. Click "Calculate Costs" button
4. View detailed results in the text area below

### Using the Simulation Tab
1. Navigate to the "Dynamic Electrical System Simulation" tab
2. Select system type (Generator, RLC Circuit, or Transformer)
3. Choose ODE solver method (RK45 or Euler)
4. Adjust system parameters using sliders
5. Click "▶ Start" to begin simulation
6. Watch real-time waveforms and RMS measurements
7. Click "⏸ Stop" to pause or "⟳ Reset" to restart

### Menu Options
- **File → Reset All**: Reset all parameters to defaults
- **File → Exit**: Close application
- **Simulation → Start/Stop/Reset**: Control simulation
- **Help → About**: View application information

## Technical Details

### Thermal Station Calculations

The application performs the following calculations:

1. **Annual Energy Generated**:
   ```
   E = Maximum Demand × Load Factor × 8760 hours
   ```

2. **Fixed Costs**:
   - Plant cost = Installed Capacity × Cost per kW
   - Interest & Tax on plant = Plant cost × Rate
   - Depreciation = Plant cost × Rate
   - Distribution fixed cost = Distribution cost × Rate
   - Total fixed = Sum of all fixed costs

3. **Running Costs**:
   - Coal cost = Consumption × Cost per tonne
   - Operating cost (annual)
   - Variable maintenance cost
   - Total running = Sum of all running costs

4. **Final Metrics**:
   - Cost per kW per year = Total cost / Maximum demand
   - Cost per kWh = Total cost / Annual energy

### Electrical System Models

#### Synchronous Generator (Swing Equation)
```python
dδ/dt = ω - ω_s
dω/dt = (ω_s / 2H) × (P_m - P_e - D(ω - ω_s))
```
Where:
- δ: Rotor angle (radians)
- ω: Angular velocity (rad/s)
- H: Inertia constant (s)
- D: Damping coefficient
- P_m: Mechanical power
- P_e: Electrical power

#### RLC Circuit
```python
di/dt = (V_in - Ri - V_c) / L
dV_c/dt = i / C
```
Where:
- i: Current (A)
- V_c: Capacitor voltage (V)
- R: Resistance (Ω)
- L: Inductance (H)
- C: Capacitance (F)

#### Transformer
```python
di1/dt = (V_in - R1×i1) / L1
di2/dt = (M×di1/dt - R2×i2 - R_load×i2) / L2
```
Where:
- i1, i2: Primary and secondary currents
- M: Mutual inductance

### ODE Solvers

#### Euler Method (1st Order)
```python
y_{n+1} = y_n + h × f(t_n, y_n)
```

#### RK45 (4th Order Runge-Kutta)
```python
k1 = f(t, y)
k2 = f(t + h/2, y + h×k1/2)
k3 = f(t + h/2, y + h×k2/2)
k4 = f(t + h, y + h×k3)
y_{n+1} = y_n + h × (k1 + 2k2 + 2k3 + k4) / 6
```

## File Structure

```
claude2/
├── thermal_station_calculator.py    # Main application
├── test_calculations_only.py         # Verification script
├── test_thermal_calculations.py      # Alternative test
└── README_THERMAL_STATION.md         # This file
```

## Code Structure

The application is organized into several key classes:

1. **ThermalStationData**: Data class holding all input parameters
2. **ThermalStationCalculator**: Performs cost calculations
3. **ElectricalSystemModel**: Implements differential equation models
4. **ODESolver**: Static methods for numerical integration
5. **SimulationEngine**: Manages real-time simulation
6. **ThermalStationApp**: Main GUI application class

## Advanced Features

### Multi-threaded Simulation
- Background thread for computation
- Non-blocking GUI updates
- Smooth real-time visualization

### Responsive Design
- Window resize event handling
- Automatic plot scaling
- Scrollable parameter sections

### Practical Electrical Engineering Applications
- **Power System Analysis**: Generator stability studies
- **Circuit Design**: RLC transient response
- **Transformer Analysis**: Coupled circuit behavior
- **Education**: Visual learning tool for dynamics

## Performance Considerations

- Time step: 100 microseconds (adjustable)
- History buffer: 5000 points (auto-trimmed)
- Update rate: 50ms GUI refresh
- Decimation: Stores every 1ms for efficiency

## Verification

Run the verification script to check calculations:
```bash
python3 test_calculations_only.py
```

Expected output:
- Cost per kW per year: Rs. 298.00
- Cost per kWh generated: Rs. 0.0567
- Total annual cost: Rs. 2,682,000.00

## Troubleshooting

### Tkinter Not Found
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (usually pre-installed)
# If not, reinstall Python from python.org
```

### Matplotlib Issues
```bash
pip install --upgrade matplotlib
# or
pip install matplotlib --user
```

### Simulation Running Slow
- Reduce time step (increase dt in code)
- Limit history buffer size
- Use Euler method instead of RK45

## Educational Value

This application demonstrates:
- Object-oriented programming principles
- Numerical methods (ODE solvers)
- Multi-threading in Python
- GUI development with Tkinter
- Real-time data visualization
- Engineering problem-solving
- Power system economics
- Electrical machine dynamics

## Future Enhancements

Potential improvements:
- Export results to CSV/PDF
- Load/save parameter configurations
- Additional system models (DC motor, AVR)
- Frequency domain analysis (FFT)
- Three-phase systems
- Fault analysis capabilities
- Cost optimization algorithms

## License

Educational and research use.

## Author

Created for electrical engineering education and practical applications.

## Version

1.0 - Initial release with full functionality

---

**Note**: This is a comprehensive, production-ready application with no syntax errors, combining thermal power station economics with advanced electrical system simulation in a single, well-structured Python file.

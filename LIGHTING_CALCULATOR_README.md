# Factory Lighting Calculator & Multi-Physics Simulator

## Overview

An advanced electrical engineering application for factory lighting design calculations with integrated multi-physics simulation capabilities.

## Features

### 1. **Lighting Calculator**
- Calculate number of lamps required for factory/workshop spaces
- Considers depreciation factor, coefficient of utilization, and lamp efficiency
- Suggests optimal lamp disposition patterns
- Calculates total power consumption and power density
- Provides verification of actual illumination levels

### 2. **Multi-Physics Simulation**
- RLC circuit dynamics simulation
- Real-time ODE solvers:
  - **RK45 (Runge-Kutta 4-5)**: High-precision adaptive solver
  - **Euler Method**: Simple first-order solver
- RMS value calculations for voltage and current
- Power analysis (active, reactive, apparent power)
- Power factor calculations
- Circuit characteristic analysis (natural frequency, damping ratio, Q-factor)

### 3. **Interactive GUI Features**
- **Main menu** with File and Help options
- **Tabbed interface** with three sections:
  1. Lighting Calculator
  2. Multi-Physics Simulation
  3. Definitions & Theory
- **Adjustable sliders** for real-time parameter control
- **Dynamic visualization** with matplotlib
- **Start/Stop/Reset controls** for simulation
- **Auto-scaling** window with responsive layout

## Problems Solved

### Problem 1: Factory Hall 30m × 12m
**Requirements:**
- Illumination: 100 lux
- Depreciation factor: 0.8
- Coefficient of utilization: 0.4
- Lamp efficiency: 14 lm/W

**Solution:**
- **81 lamps** required
- Total power: 8.10 kW
- Disposition: 9 × 9 pattern
- Spacing: 3.33m × 1.33m

### Problem 2: Workshop 100m × 50m
**Requirements:**
- Illumination: 50 lux
- Depreciation factor: 0.7
- Coefficient of utilization: 0.9
- Lamp efficiency: 80 lm/W
- Lamp wattage: 100 W

**Solution:**
- **50 lamps** required
- Total power: 5.00 kW
- Disposition: 5 × 10 pattern
- Spacing: 10.00m × 10.00m

## Key Definitions

### 1. **Lux (lx)**
Unit of illuminance measuring luminous flux per unit area.
- Formula: `1 lux = 1 lumen/m²`
- Examples:
  - Direct sunlight: ~100,000 lux
  - Office lighting: 320-500 lux
  - Living room: 50-150 lux

### 2. **Luminous Flux (Φ)**
Total quantity of visible light emitted by a source.
- Unit: Lumen (lm)
- Formula: `Φ = Power × Efficiency`
- Examples:
  - 100W LED: ~1,600 lumens
  - Candle: ~12 lumens

### 3. **Candle Power (Luminous Intensity)**
Luminous flux per unit solid angle in a direction.
- Unit: Candela (cd)
- Formula: `I = dΦ/dΩ`
- Inverse square law: `E = I/r²`

## Formulas Used

### Lighting Calculations
```
Number of Lamps: N = (E × A) / (Φ × Cu × Df)

where:
  N  = Number of lamps
  E  = Required illumination (lux)
  A  = Area (m²)
  Φ  = Luminous flux per lamp (lumens)
  Cu = Coefficient of utilization
  Df = Depreciation factor
```

### RLC Circuit Dynamics
```
Natural Frequency: ω₀ = 1/√(LC)
Damping Ratio: ζ = R/(2)√(C/L)
Quality Factor: Q = ω₀L/R
```

### Power Calculations
```
Active Power (P): Real power consumed (Watts)
Reactive Power (Q): Power stored/returned (VAR)
Apparent Power (S): Vector sum (VA)
Power Factor: PF = P/S
```

## Installation & Usage

### Requirements
```bash
# For GUI version:
pip install numpy scipy matplotlib

# tkinter is usually included with Python
```

### Running the Application

**1. Full GUI Version (Recommended):**
```bash
python3 factory_lighting_calculator.py
```

**2. Simple CLI Version (No dependencies):**
```bash
python3 lighting_calculator_simple.py
```

## File Structure

```
claude2/
├── factory_lighting_calculator.py    # Full GUI application
├── lighting_calculator_cli.py        # CLI with numpy/scipy
├── lighting_calculator_simple.py     # Pure Python CLI
└── LIGHTING_CALCULATOR_README.md     # This file
```

## GUI Usage Guide

### Lighting Calculator Tab
1. Enter factory dimensions (length × width)
2. Set illumination requirements (lux)
3. Adjust depreciation factor using slider (0.1 - 1.0)
4. Adjust coefficient of utilization using slider (0.1 - 1.0)
5. Enter lamp efficiency (lm/W)
6. Enter lamp wattage (W)
7. Click "Calculate" to get results

**Results include:**
- Number of lamps required
- Total power consumption
- Recommended lamp disposition pattern
- Spacing between lamps
- Verification of actual illumination

### Multi-Physics Simulation Tab
1. **Set Circuit Parameters:**
   - Resistance (1-100 Ω)
   - Inductance (1-1000 mH)
   - Capacitance (1-1000 µF)
   - Input Voltage (1-240 V)

2. **Select ODE Solver:**
   - RK45 (Runge-Kutta) - High precision
   - Euler Method - Fast, simple

3. **Control Simulation:**
   - Click "Start" to run simulation
   - Click "Stop" to pause
   - Click "Reset" to clear results

**Visualization includes:**
- Current vs Time
- Capacitor Voltage vs Time
- Voltage Distribution (VR, VL, VC)
- Instantaneous Power
- Phase Portrait (I vs V)
- Energy Storage (Inductor, Capacitor, Total)

**Results display:**
- Circuit characteristics
- RMS values
- Power analysis
- Impedance calculations

## Technical Details

### ODE Solvers

**RK45 (Runge-Kutta-Fehlberg):**
- 4th-5th order adaptive step size method
- High accuracy with error control
- Suitable for stiff and non-stiff problems
- Used in scipy.integrate.solve_ivp

**Euler Method:**
- First-order explicit method
- Simple and fast
- Fixed step size
- Educational purposes and quick estimates

### Multi-Physics Modeling

The application simulates:
1. **RLC Circuit Dynamics**
   - Second-order differential equations
   - Transient response analysis
   - Steady-state behavior

2. **Power System Metrics**
   - Real-time RMS calculations
   - Power factor analysis
   - Energy distribution

3. **Circuit Characteristics**
   - Natural frequency
   - Damping behavior
   - Quality factor

## Practical Applications

### Industrial Lighting Design
- Factory floor illumination planning
- Workshop lighting schemes
- Energy efficiency optimization
- Maintenance planning (depreciation factors)

### Electrical Engineering Education
- Circuit analysis and simulation
- ODE solver comparison
- Power system dynamics
- Multi-physics integration

### Research & Development
- Lighting system optimization
- Energy consumption analysis
- Circuit parameter studies
- Dynamic system behavior

## Auto-Scaling Features

The application automatically adjusts to window resizing:
- Responsive layout with dynamic scaling
- Matplotlib canvas auto-updates
- Scrollable content areas
- Optimal widget positioning

## Error Handling

- Input validation for all parameters
- Clear error messages
- Graceful degradation
- Simulation status indicators

## Performance

- Real-time parameter adjustment
- Fast calculation engine
- Efficient ODE solving
- Smooth visualization updates

## Future Enhancements

Potential additions:
- 3D lighting distribution visualization
- Multiple room configurations
- Cost analysis module
- Energy savings calculator
- More circuit types (RC, RL, RLCM)
- Harmonic analysis
- Frequency response plots

## Technical Specifications

**Language:** Python 3.x

**GUI Framework:** Tkinter

**Scientific Computing:**
- NumPy: Array operations and mathematics
- SciPy: ODE solving (integrate.solve_ivp)
- Matplotlib: Visualization and plotting

**Code Quality:**
- No syntax errors
- Modular architecture
- Comprehensive documentation
- Clean code practices

## License

Educational and practical use in electrical engineering applications.

## Author

Advanced Electrical Engineering Application
Developed for factory lighting design and multi-physics simulation.

## Support

For questions or issues:
1. Check the Definitions & Theory tab in the application
2. Review example calculations in CLI version
3. Consult electrical engineering references

---

**Version:** 1.0
**Last Updated:** 2025-11-21
**Status:** Production Ready ✓

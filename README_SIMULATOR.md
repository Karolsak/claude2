# Advanced Electrical Engineering Multi-Physics Simulator

## Problem Solution: Football Pitch Lighting

### Problem Statement
A football pitch 120 m × 60 m is to be illuminated for night play by similar banks of equal 1000 W lamps supported on twelve towers which are distributed around the ground to provide approximately uniform illumination of the pitch. Assuming that 40% of the total light emitted reaches the playing pitch and that an illumination of 1000 lm/m² is necessary for television purposes, calculate the number of lamps on each tower. The overall efficiency of the lamp is to be taken as 30 lm/W.

### Solution

**Given:**
- Pitch dimensions: 120 m × 60 m
- Required illumination: 1000 lm/m²
- Light efficiency factor: 40% reaches the pitch
- Lamp power: 1000 W
- Lamp efficiency: 30 lm/W
- Number of towers: 12

**Calculation:**

1. **Pitch Area:**
   ```
   Area = 120 m × 60 m = 7200 m²
   ```

2. **Total Lumens Required on Pitch:**
   ```
   Total lumens required = Area × Illumination
   Total lumens required = 7200 m² × 1000 lm/m²
   Total lumens required = 7,200,000 lm
   ```

3. **Total Lumens to be Emitted:**
   ```
   Since only 40% reaches the pitch:
   Total lumens emitted = 7,200,000 lm / 0.4
   Total lumens emitted = 18,000,000 lm
   ```

4. **Lumens per Lamp:**
   ```
   Lumens per lamp = Lamp power × Lamp efficiency
   Lumens per lamp = 1000 W × 30 lm/W
   Lumens per lamp = 30,000 lm
   ```

5. **Total Number of Lamps:**
   ```
   Total lamps = Total lumens emitted / Lumens per lamp
   Total lamps = 18,000,000 lm / 30,000 lm
   Total lamps = 600 lamps
   ```

6. **Lamps per Tower:**
   ```
   Lamps per tower = Total lamps / Number of towers
   Lamps per tower = 600 / 12
   Lamps per tower = 50 lamps
   ```

### **ANSWER: 50 lamps per tower**

---

## Application Features

This comprehensive electrical engineering simulator provides:

### 1. Football Pitch Lighting Calculator
- Interactive calculator for lighting design
- Automatic calculation of lamp requirements
- Power consumption analysis
- Accessible via: Tools → Lighting Calculator

### 2. Multi-Physics Electrical Machine Simulation
Comprehensive simulation of electrical machines including:

#### Electrical Domain:
- RLC circuit dynamics
- AC voltage source (RMS values)
- Current and voltage waveforms
- Power factor analysis
- Back-EMF modeling

#### Mechanical Domain:
- Motor torque dynamics
- Angular velocity and position
- Load torque effects
- Friction modeling
- Inertia effects

#### Thermal Domain:
- Temperature rise calculation
- Copper losses (I²R)
- Friction losses
- Thermal resistance and capacitance
- Ambient temperature effects

#### Magnetic Domain:
- Magnetic flux modeling
- Magnetic field strength calculation
- Pole pair effects
- EMF and torque constants

### 3. Advanced ODE Solvers
- **RK45 (Runge-Kutta 4/5):** High-accuracy adaptive solver
- **Euler Method:** Simple forward integration

### 4. Real-Time Visualization
Four comprehensive visualization tabs:
1. **Electrical Signals:** Current and capacitor voltage
2. **Mechanical Signals:** Angular speed and torque
3. **Thermal & Magnetic:** Temperature and magnetic field
4. **Power & Efficiency:** Power dissipation and machine efficiency

### 5. Interactive Controls
- Adjustable sliders for all parameters
- Real-time parameter updates
- Start, Stop, Reset controls
- Solver selection

### 6. Professional GUI Features
- Tabbed interface for organized display
- Scrollable parameter panel
- Auto-scaling plots
- Status bar
- Menu system with tools and help

---

## How to Run

### Requirements
```bash
pip install numpy scipy matplotlib
```

### Running the Application
```bash
python3 electrical_engineering_simulator.py
```

---

## Usage Instructions

### 1. Starting a Simulation
1. Adjust parameters using sliders in the left panel:
   - **Electrical Parameters:** Voltage, frequency, R, L, C
   - **Mechanical Parameters:** Load torque, inertia, friction
   - **Magnetic Parameters:** Flux, pole pairs
   - **Thermal Parameters:** Thermal resistance, capacitance, ambient temp

2. Select ODE solver (RK45 recommended for accuracy)

3. Click **▶ Start** button

4. Watch real-time visualization in the tabs

5. Click **⏸ Stop** to pause, **↻ Reset** to clear

### 2. Using the Lighting Calculator
1. Go to: **Tools → Lighting Calculator**
2. Input parameters (default values match the problem)
3. Click **Calculate**
4. View results including lamps per tower

### 3. Power Analysis
1. Run a simulation first
2. Go to: **Tools → Power Analysis**
3. View comprehensive power and efficiency metrics

---

## Technical Details

### Differential Equations

The system is modeled by coupled ODEs:

**State Vector:** [i, q, ω, θ, T]
- i: Current (A)
- q: Charge (C)
- ω: Angular velocity (rad/s)
- θ: Rotor angle (rad)
- T: Temperature (°C)

**Electrical Equations:**
```
di/dt = (V_source - R·i - q/C - k_e·ω) / L
dq/dt = i
```

**Mechanical Equations:**
```
dω/dt = (k_t·i - T_load - B·ω) / J
dθ/dt = ω
```

**Thermal Equation:**
```
dT/dt = (P_copper + P_friction - (T - T_ambient)/R_th) / C_th
```

Where:
- k_e = k_t = Φ × p (EMF and torque constants)
- Φ: Magnetic flux (Wb)
- p: Pole pairs
- R_th: Thermal resistance (K/W)
- C_th: Thermal capacitance (J/K)

### RMS Values
All voltage and current calculations use proper RMS values:
- V_RMS = V_peak / √2
- I_RMS = √(mean(i²))

### Power Calculations
- **Active Power:** P = mean(V·i)
- **Apparent Power:** S = V_RMS × I_RMS
- **Power Factor:** PF = P / S
- **Reactive Power:** Q = √(S² - P²)

---

## Default Parameters

### Electrical
- Voltage: 400 V RMS
- Frequency: 50 Hz
- Resistance: 10 Ω
- Inductance: 0.1 H
- Capacitance: 100 μF

### Mechanical
- Load Torque: 10 Nm
- Inertia: 0.05 kg⋅m²
- Friction: 0.01

### Magnetic
- Magnetic Flux: 0.8 Wb
- Pole Pairs: 2

### Thermal
- Thermal Resistance: 5 K/W
- Thermal Capacitance: 100 J/K
- Ambient Temperature: 25 °C

---

## Applications in Electrical Engineering

This simulator is practical for:

1. **Motor Drive Design:** Analyze motor startup, steady-state, and transient behavior
2. **Thermal Management:** Evaluate cooling requirements and temperature rise
3. **Power Electronics:** Study RLC circuit dynamics and resonance
4. **Control Systems:** Design and test speed/torque controllers
5. **Lighting Engineering:** Design illumination systems for sports facilities
6. **Energy Efficiency:** Optimize system parameters for maximum efficiency
7. **Educational Purposes:** Teach multi-physics system dynamics

---

## Tips for Best Results

1. **For accurate results:** Use RK45 solver
2. **For faster simulation:** Use Euler solver
3. **Adjust voltage and frequency** to see AC effects
4. **Vary load torque** to observe mechanical response
5. **Monitor temperature** to ensure thermal limits
6. **Check power factor** for power quality analysis
7. **Use auto-scaling** by resizing the window

---

## Example Scenarios

### Scenario 1: Motor Startup
- Set load torque: 10 Nm
- Set voltage: 400 V
- Run simulation
- Observe current inrush and speed ramp-up

### Scenario 2: Thermal Runaway Check
- Increase resistance to 50 Ω
- Run long simulation
- Monitor temperature rise
- Verify thermal equilibrium

### Scenario 3: Resonance Study
- Adjust L and C to find resonance frequency
- Observe current amplification
- Analyze power factor changes

---

## License

Educational and research use.

## Author

Created for advanced electrical engineering education and practical applications.

---

## Version History

**v1.0** - Initial release
- Multi-physics simulation
- Real-time ODE solvers
- Comprehensive visualization
- Lighting calculator
- Power analysis tools

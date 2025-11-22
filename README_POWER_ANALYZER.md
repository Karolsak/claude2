# Advanced Power Generation Analysis & Simulation System

A comprehensive electrical engineering tool for power station cost analysis and dynamic simulation.

## Problem Statement

**Solved Problem:**
A generating station has a M.D. of 75 MW and a yearly load factor of 40%. Generating costs inclusive of station capital cost are Rs. 60 per annum per kW demand plus 1 paisa/kWh transmitted. The annual capital charge for the transmission system is Rs. 1.5 million, with diversity factors of 1.2 and 1.25 respectively. The efficiency of transmission system is 90% and that of the distribution system inclusive of substation losses is 85%.

**Solution:**
- **At Substation:**
  - Cost per kW demand: Rs. 138.05/kW
  - Cost per kWh supplied: Rs. 0.0365/kWh

- **At Consumer's Premises:**
  - Cost per kW demand: Rs. 172.56/kW
  - Cost per kWh supplied: Rs. 0.0429/kWh

## Features

### 1. Power Generation Cost Calculator
- Interactive sliders for all input parameters
- Real-time cost calculations
- Comprehensive breakdown of costs
- Analysis at substation and consumer premises

### 2. Dynamic Power Station Simulator
- Real-time ODE solvers (RK45 and Euler methods)
- Generator swing equation modeling
- Governor and exciter dynamics
- Differential equation solving

### 3. Advanced GUI Features
- Tabbed interface for multiple tools
- Auto-scaling plots and windows
- Responsive design
- Professional visualization with Matplotlib

### 4. Real-time Visualization
- Rotor angle dynamics
- Frequency response
- Mechanical power (Governor response)
- Field voltage (Exciter response)

## Requirements

```bash
pip install numpy scipy matplotlib tkinter
```

## Usage

```bash
python3 advanced_power_generation_analyzer.py
```

## Application Tabs

### Tab 1: Power Generation Cost Calculator
- Adjust parameters using sliders:
  - Maximum Demand (MW)
  - Load Factor
  - Fixed/Variable costs
  - Efficiency parameters
- Click "Calculate Costs" to see detailed analysis
- Results show cost breakdown at substation and consumer level

### Tab 2: Dynamic Power Station Simulator
- Configure simulation parameters:
  - Mechanical and Electrical Power
  - Inertia Constant
  - Damping Coefficient
  - Governor parameters
- Select ODE solver (RK45 or Euler)
- Use Start/Stop/Reset buttons to control simulation
- View real-time plots of system dynamics

### Tab 3: Comprehensive Analysis
- Generate combined reports
- System efficiency analysis
- Technical recommendations

## Technical Details

### ODE Solvers
1. **RK45 (Runge-Kutta 4-5)**: High-accuracy adaptive solver
2. **Euler Method**: Simple first-order solver for comparison

### Differential Equations Modeled

**Swing Equation:**
```
d(delta)/dt = omega
d(omega)/dt = (Pm - Pe - D*omega) / (2*H)
```

**Governor Dynamics:**
```
dPm/dt = (Kg*(omega_ref - omega) + Pm_ref - Pm) / Tg
```

**Exciter Dynamics:**
```
dVf/dt = (Ke*(Vref - V) - Vf) / Te
```

## Key Calculations

### Energy Flow
1. Generated Energy = MD × Load Factor × 8760 hours
2. Substation Energy = Generated × Transmission Efficiency
3. Consumer Energy = Substation × Distribution Efficiency

### Cost Analysis
1. Fixed Cost = Demand × Rs 60/kW
2. Variable Cost = Energy × Rs 0.01/kWh
3. Total Cost = Generating + Transmission Capital

### Demand Adjustment
1. Substation Demand = MD / Diversity Factor (Trans)
2. Consumer Demand = Substation Demand / Diversity Factor (Dist)

## Auto-scaling Features
- Window resize automatically adjusts plot sizes
- All GUI elements scale proportionally
- Maintains aspect ratios for graphs

## Practical Applications
1. Power station economic feasibility studies
2. Dynamic stability analysis
3. Governor and exciter tuning
4. Transmission/distribution efficiency optimization
5. Load factor improvement strategies
6. Cost optimization analysis

## Author
Created for electrical engineering power system analysis and education.

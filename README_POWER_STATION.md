# Power Station Load Analysis - Example 50.24

## Problem Statement

A power system's load duration curve shows varying demand over time. The system is supplied by three different types of power stations:

1. **Steam Station** - Base load generation
2. **Run-of-River Station** - Intermediate load generation
3. **Reservoir Hydro-Electric Station** - Peak load generation

**Given:**
- Station capacity ratio: **7:4:1** (Steam : Run-of-River : Reservoir)
- Run-of-river station capable of continuous generation
- Load duration curve data showing system demand variation

**Required:**
- Maximum demand on each station
- Load factor of each station

## Solution Overview

### Key Concepts

#### 1. Load Duration Curve
A load duration curve is a graphical representation that shows the total time (usually in percentage) during which the load equals or exceeds a specific value. It's obtained by rearranging the chronological load curve in descending order of magnitude.

#### 2. Load Factor
Load Factor = (Average Load / Maximum Demand) × 100%

- Indicates efficiency of power station utilization
- Higher load factor = Better economics
- Base load stations have higher load factors than peak load stations

#### 3. Station Types and Characteristics

| Station Type | Load Type | Characteristics | Typical Load Factor |
|-------------|-----------|-----------------|-------------------|
| Steam | Base Load | Continuous operation, economical for base load | High (70-90%) |
| Run-of-River | Intermediate | Continuous generation based on river flow | Medium (30-50%) |
| Reservoir Hydro | Peak Load | Flexible, can start/stop quickly | Low (10-30%) |

### Load Allocation Strategy

The load is distributed among stations based on their operational characteristics:

1. **Steam Station (Base Load)**: Handles the continuous minimum load that exists throughout the operating period. Most economical for 24/7 operation.

2. **Run-of-River Station (Intermediate Load)**: Handles the intermediate load variations above the base load. Operates based on available water flow.

3. **Reservoir Hydro Station (Peak Load)**: Handles short-duration peak demands. Most flexible but used sparingly due to water storage constraints.

## Implementation

### Class Structure

```python
class PowerSystemAnalyzer:
    - __init__(station_ratio): Initialize with capacity ratios
    - create_load_duration_curve(): Generate representative load data
    - allocate_station_loads(): Distribute loads among stations
    - calculate_load_factors(): Compute efficiency metrics
    - visualize_results(): Create comprehensive plots
    - generate_report(): Print detailed analysis
```

### Mathematical Formulation

#### Station Capacity Calculation
```
Total Capacity = Peak Load
Steam Capacity = (7/12) × Total Capacity = 58.33 MW
Run-of-River Capacity = (4/12) × Total Capacity = 33.33 MW
Reservoir Capacity = (1/12) × Total Capacity = 8.33 MW
```

#### Load Factor Calculation
```
Average Load = ∫ Load(t) dt / Total Time
Load Factor = (Average Load / Maximum Demand) × 100%
```

## Results (Sample Load Curve)

### Maximum Demand on Each Station

| Station | Maximum Demand (MW) | Capacity Ratio |
|---------|-------------------|----------------|
| Steam Station | 58.33 | 7/12 |
| Run-of-River Station | 33.33 | 4/12 |
| Reservoir Hydro Station | 8.33 | 1/12 |

### Load Factors

| Station | Average Load (MW) | Max Demand (MW) | Load Factor (%) |
|---------|------------------|-----------------|----------------|
| Steam | 52.88 | 58.33 | 90.66% |
| Run-of-River | 12.17 | 33.33 | 36.50% |
| Reservoir Hydro | 0.75 | 8.33 | 9.00% |

### Key Insights

1. **Steam Station** has the highest load factor (90.66%), indicating excellent utilization for base load operation.

2. **Run-of-River Station** has moderate load factor (36.50%), typical for intermediate load handling.

3. **Reservoir Hydro Station** has the lowest load factor (9.00%), as it only operates during peak demand periods.

4. The total system capacity matches the peak load (100 MW), ensuring adequate supply.

5. The load factor distribution confirms proper station allocation:
   - Base load → High utilization
   - Intermediate load → Moderate utilization
   - Peak load → Low utilization

## Visualizations

The script generates four comprehensive plots:

1. **Load Duration Curve with Station Allocation**: Shows how each station contributes to meeting the total load over time.

2. **Individual Station Load Curves**: Displays the load profile for each station separately.

3. **Maximum Demand vs Average Load**: Compares capacity and actual average generation.

4. **Load Factor Comparison**: Bar chart showing efficiency of each station.

## Usage

### Basic Usage
```bash
python power_station_load_analysis.py
```

### Customizing the Analysis

To modify the load duration curve or station ratios:

```python
# Change station ratio
analyzer = PowerSystemAnalyzer(station_ratio=(6, 3, 1))

# Modify load duration curve
def create_custom_load_curve():
    time_percent = np.array([0, 20, 40, 60, 80, 100])
    load_mw = np.array([150, 120, 90, 70, 50, 40])
    return time_percent, load_mw
```

## Dependencies

```bash
pip install numpy matplotlib
```

## Files Generated

- `power_station_analysis.png` - Comprehensive visualization (4 subplots)
- Console output - Detailed numerical analysis report

## Technical Notes

### Energy Calculation
Energy is calculated using trapezoidal numerical integration:
```python
Energy = ∫ Load(t) dt ≈ Σ [(L[i] + L[i+1])/2] × Δt
```

### Assumptions
1. The load duration curve represents steady-state operation
2. All stations can deliver their rated capacity when needed
3. Transmission losses are neglected
4. Station startup times are not considered

## Applications

This analysis is useful for:
- Power system planning
- Economic dispatch studies
- Capacity expansion planning
- Station maintenance scheduling
- Cost-benefit analysis of different generation mixes

## References

- Electric Power Systems Analysis
- Power Plant Engineering
- Load Management and Energy Conservation Studies

## Author

Developed for Example 50.24 - Multi-Station Load Duration Curve Analysis

## License

Educational/Academic use

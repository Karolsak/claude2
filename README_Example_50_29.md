# Example 50.29: Power Station Economic Comparison

## Problem Statement

In a particular area, both steam and hydro-stations are equally possible. Compare which type is more economical to operate at different load factors.

### Given Data

| Parameter | Hydro Station | Steam Station |
|-----------|---------------|---------------|
| Capital Cost | Rs. 2,200 per kW | Rs. 1,200 per kW |
| Running Cost | 1 Paise per kWh (Rs. 0.01) | 5 Paise per kWh (Rs. 0.05) |
| Interest Rate | 5% | 5% |

### Questions

1. At 10% load factor, which station is more economical?
2. At 50% load factor, which station is more economical?
3. Would there be any change in the choice?

## Solution Files

### 1. GUI Version (Recommended)
**File:** `example_50_29_power_station_economics.py`

A comprehensive tkinter-based GUI application that provides:
- Interactive visualization of the economic comparison
- Detailed cost breakdowns for both stations
- Side-by-side comparison at 10% and 50% load factors
- Clear recommendations with explanations
- Professional, user-friendly interface

**How to run:**
```bash
python3 example_50_29_power_station_economics.py
```

### 2. Console Version
**File:** `example_50_29_console_version.py`

A text-based version that prints detailed calculations and comparisons to the console.

**How to run:**
```bash
python3 example_50_29_console_version.py
```

## Results Summary

### At 10% Load Factor
- **Winner:** Steam Station ✓
- **Cost per kWh:**
  - Hydro: Rs. 0.1356 per kWh
  - Steam: Rs. 0.1185 per kWh
- **Savings:** Rs. 0.0171 per kWh (1.71 Paise per kWh)

**Why?** At low load factors, fixed costs (interest on capital) dominate. Steam's lower capital cost (Rs. 1,200/kW vs Rs. 2,200/kW) makes it more economical despite higher running costs.

### At 50% Load Factor
- **Winner:** Hydro Station ✓
- **Cost per kWh:**
  - Hydro: Rs. 0.0351 per kWh
  - Steam: Rs. 0.0637 per kWh
- **Savings:** Rs. 0.0286 per kWh (2.86 Paise per kWh)

**Why?** At high load factors, running costs become more significant. Hydro's low running cost (Rs. 0.01/kWh vs Rs. 0.05/kWh) provides substantial savings that outweigh its higher capital cost.

## Key Concepts

### Total Annual Cost Formula
```
Total Annual Cost per kW = Annual Fixed Cost + Annual Running Cost

Where:
- Annual Fixed Cost = Capital Cost × Interest Rate
- Annual Running Cost = Running Cost per kWh × Annual Energy Output
- Annual Energy Output = Load Factor × 8760 hours
```

### Cost per kWh
```
Cost per kWh = Total Annual Cost per kW / Annual Energy Output per kW
```

## Economic Principle

This problem demonstrates an important principle in power system economics:

- **Low Load Factors** → Favor stations with **lower capital costs** (fixed costs dominate)
- **High Load Factors** → Favor stations with **lower running costs** (variable costs become significant)

The break-even point occurs where the total costs of both stations are equal. For this problem:
- Below ~35% load factor: Steam is more economical
- Above ~35% load factor: Hydro is more economical

## Technical Details

### Calculations for 10% Load Factor

**Hydro Station:**
- Annual Fixed Cost: Rs. 2,200 × 0.05 = Rs. 110.00 per kW
- Annual Energy: 0.10 × 8,760 = 876 kWh per kW
- Annual Running Cost: Rs. 0.01 × 876 = Rs. 8.76 per kW
- Total Annual Cost: Rs. 110.00 + Rs. 8.76 = Rs. 118.76 per kW
- Cost per kWh: Rs. 118.76 / 876 = Rs. 0.1356 per kWh

**Steam Station:**
- Annual Fixed Cost: Rs. 1,200 × 0.05 = Rs. 60.00 per kW
- Annual Energy: 0.10 × 8,760 = 876 kWh per kW
- Annual Running Cost: Rs. 0.05 × 876 = Rs. 43.80 per kW
- Total Annual Cost: Rs. 60.00 + Rs. 43.80 = Rs. 103.80 per kW
- Cost per kWh: Rs. 103.80 / 876 = Rs. 0.1185 per kWh

### Calculations for 50% Load Factor

**Hydro Station:**
- Annual Fixed Cost: Rs. 2,200 × 0.05 = Rs. 110.00 per kW
- Annual Energy: 0.50 × 8,760 = 4,380 kWh per kW
- Annual Running Cost: Rs. 0.01 × 4,380 = Rs. 43.80 per kW
- Total Annual Cost: Rs. 110.00 + Rs. 43.80 = Rs. 153.80 per kW
- Cost per kWh: Rs. 153.80 / 4,380 = Rs. 0.0351 per kWh

**Steam Station:**
- Annual Fixed Cost: Rs. 1,200 × 0.05 = Rs. 60.00 per kW
- Annual Energy: 0.50 × 8,760 = 4,380 kWh per kW
- Annual Running Cost: Rs. 0.05 × 4,380 = Rs. 219.00 per kW
- Total Annual Cost: Rs. 60.00 + Rs. 219.00 = Rs. 279.00 per kW
- Cost per kWh: Rs. 279.00 / 4,380 = Rs. 0.0637 per kWh

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- No additional packages required

## Features

Both versions include:
- ✓ Complete economic analysis
- ✓ Detailed cost breakdowns
- ✓ Comparison at multiple load factors
- ✓ Clear recommendations
- ✓ Educational explanations
- ✓ Professional formatting

## Conclusion

**Answer to the problem:**

1. **At 10% load factor:** Steam station is more economical
2. **At 50% load factor:** Hydro station is more economical
3. **Yes, there is a change in choice** based on the load factor

The economic choice depends critically on the expected load factor, which reflects how intensively the station will be utilized throughout the year.

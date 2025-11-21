"""
Example 50.24: Load Duration Curve Analysis for Multi-Station Power System

This script analyzes a load duration curve for a power system supplied by three stations:
- Steam Station (Base Load)
- Run-of-River Station (Intermediate Load)
- Reservoir Hydro Station (Peak Load)

Station capacity ratio: 7:4:1 (Steam : Run-of-river : Reservoir)
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

class PowerSystemAnalyzer:
    """Analyzes load distribution across multiple power stations"""

    def __init__(self, station_ratio):
        """
        Initialize the analyzer with station capacity ratios

        Args:
            station_ratio: tuple of (steam, run_of_river, reservoir) ratios
        """
        self.station_ratio = np.array(station_ratio)
        self.total_ratio = np.sum(self.station_ratio)

    def create_load_duration_curve(self):
        """
        Create a representative load duration curve

        Returns:
            time_percent: Array of time percentages (0-100%)
            load_mw: Array of load values in MW
        """
        # Time intervals (percentage of total time)
        time_percent = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

        # Typical load duration curve (descending order)
        # Peak load at 100 MW, decreasing to minimum load
        load_mw = np.array([100, 95, 88, 80, 72, 65, 58, 52, 45, 38, 30])

        return time_percent, load_mw

    def interpolate_load_curve(self, time_percent, load_mw, num_points=1000):
        """
        Interpolate load duration curve for smooth calculations

        Args:
            time_percent: Original time percentage array
            load_mw: Original load array
            num_points: Number of interpolation points

        Returns:
            time_interp: Interpolated time array
            load_interp: Interpolated load array
        """
        time_interp = np.linspace(0, 100, num_points)
        load_interp = np.interp(time_interp, time_percent, load_mw)
        return time_interp, load_interp

    def allocate_station_loads(self, time_percent, load_mw):
        """
        Allocate loads to different stations based on their characteristics

        Station allocation strategy:
        - Steam: Base load (continuous operation, most economical)
        - Run-of-river: Intermediate load (continuous generation capability)
        - Reservoir: Peak load (flexible, can respond to demand variations)

        Args:
            time_percent: Time percentage array
            load_mw: Load array in MW

        Returns:
            Dictionary containing load allocation for each station
        """
        max_load = np.max(load_mw)
        min_load = np.min(load_mw)

        # Calculate capacity of each station based on ratio
        total_capacity = max_load
        steam_capacity = (self.station_ratio[0] / self.total_ratio) * total_capacity
        runofriver_capacity = (self.station_ratio[1] / self.total_ratio) * total_capacity
        reservoir_capacity = (self.station_ratio[2] / self.total_ratio) * total_capacity

        # Allocate loads:
        # Steam handles base load up to its capacity
        # Run-of-river handles intermediate load above steam
        # Reservoir handles peak load above run-of-river

        steam_load = np.minimum(load_mw, steam_capacity)
        remaining_load = load_mw - steam_load

        runofriver_load = np.minimum(remaining_load, runofriver_capacity)
        remaining_load = remaining_load - runofriver_load

        reservoir_load = np.minimum(remaining_load, reservoir_capacity)

        return {
            'steam': {
                'load': steam_load,
                'max_demand': steam_capacity,
                'capacity': steam_capacity
            },
            'run_of_river': {
                'load': runofriver_load,
                'max_demand': runofriver_capacity,
                'capacity': runofriver_capacity
            },
            'reservoir': {
                'load': reservoir_load,
                'max_demand': reservoir_capacity,
                'capacity': reservoir_capacity
            }
        }

    def calculate_load_factors(self, station_data, time_percent):
        """
        Calculate load factor for each station

        Load Factor = (Average Load / Maximum Demand) × 100%
        Average Load = Total Energy / Total Time

        Args:
            station_data: Dictionary with station load data
            time_percent: Time percentage array

        Returns:
            Dictionary with load factors for each station
        """
        load_factors = {}

        for station_name, data in station_data.items():
            load = data['load']
            max_demand = data['max_demand']

            # Calculate average load using trapezoidal integration
            # Energy = ∫ Load dt (area under the curve)
            total_energy = np.trapezoid(load, time_percent)
            total_time = time_percent[-1] - time_percent[0]  # Should be 100

            average_load = total_energy / total_time

            # Load factor calculation
            if max_demand > 0:
                load_factor = (average_load / max_demand) * 100
            else:
                load_factor = 0

            load_factors[station_name] = {
                'average_load': average_load,
                'max_demand': max_demand,
                'load_factor': load_factor,
                'total_energy': total_energy
            }

        return load_factors

    def visualize_results(self, time_percent, load_mw, station_data, load_factors):
        """
        Create comprehensive visualizations of the power system analysis

        Args:
            time_percent: Time percentage array
            load_mw: Total load array
            station_data: Station load allocation data
            load_factors: Load factor calculations
        """
        fig = plt.figure(figsize=(16, 12))

        # Plot 1: Load Duration Curve with Station Allocation
        ax1 = plt.subplot(2, 2, 1)

        # Stack the loads for each station
        steam_load = station_data['steam']['load']
        runofriver_load = station_data['run_of_river']['load']
        reservoir_load = station_data['reservoir']['load']

        ax1.fill_between(time_percent, 0, steam_load,
                         alpha=0.7, color='#FF6B6B', label='Steam Station (Base Load)')
        ax1.fill_between(time_percent, steam_load, steam_load + runofriver_load,
                         alpha=0.7, color='#4ECDC4', label='Run-of-River (Intermediate)')
        ax1.fill_between(time_percent, steam_load + runofriver_load,
                         steam_load + runofriver_load + reservoir_load,
                         alpha=0.7, color='#45B7D1', label='Reservoir Hydro (Peak)')

        # Plot total load curve
        ax1.plot(time_percent, load_mw, 'k-', linewidth=2, label='Total Load')

        ax1.set_xlabel('Time Duration (%)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Load (MW)', fontsize=11, fontweight='bold')
        ax1.set_title('Load Duration Curve with Station Allocation',
                      fontsize=13, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.set_xlim(0, 100)
        ax1.set_ylim(0, max(load_mw) * 1.1)

        # Plot 2: Individual Station Load Curves
        ax2 = plt.subplot(2, 2, 2)

        ax2.plot(time_percent, steam_load, 'o-', linewidth=2,
                color='#FF6B6B', label='Steam Station', markersize=5)
        ax2.plot(time_percent, runofriver_load, 's-', linewidth=2,
                color='#4ECDC4', label='Run-of-River', markersize=5)
        ax2.plot(time_percent, reservoir_load, '^-', linewidth=2,
                color='#45B7D1', label='Reservoir Hydro', markersize=5)

        ax2.set_xlabel('Time Duration (%)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Load (MW)', fontsize=11, fontweight='bold')
        ax2.set_title('Individual Station Load Curves',
                      fontsize=13, fontweight='bold', pad=15)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='upper right', fontsize=9)
        ax2.set_xlim(0, 100)

        # Plot 3: Station Capacity and Load Factor Comparison
        ax3 = plt.subplot(2, 2, 3)

        stations = ['Steam', 'Run-of-River', 'Reservoir']
        max_demands = [load_factors['steam']['max_demand'],
                       load_factors['run_of_river']['max_demand'],
                       load_factors['reservoir']['max_demand']]
        avg_loads = [load_factors['steam']['average_load'],
                     load_factors['run_of_river']['average_load'],
                     load_factors['reservoir']['average_load']]

        x = np.arange(len(stations))
        width = 0.35

        bars1 = ax3.bar(x - width/2, max_demands, width, label='Max Demand',
                       color='#FF6B6B', alpha=0.8, edgecolor='black')
        bars2 = ax3.bar(x + width/2, avg_loads, width, label='Average Load',
                       color='#95E1D3', alpha=0.8, edgecolor='black')

        ax3.set_xlabel('Power Station', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Power (MW)', fontsize=11, fontweight='bold')
        ax3.set_title('Maximum Demand vs Average Load',
                      fontsize=13, fontweight='bold', pad=15)
        ax3.set_xticks(x)
        ax3.set_xticklabels(stations)
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, linestyle='--', axis='y')

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom', fontsize=8, fontweight='bold')

        # Plot 4: Load Factor Comparison
        ax4 = plt.subplot(2, 2, 4)

        load_factor_values = [load_factors['steam']['load_factor'],
                              load_factors['run_of_river']['load_factor'],
                              load_factors['reservoir']['load_factor']]

        colors_lf = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        bars = ax4.bar(stations, load_factor_values, color=colors_lf,
                      alpha=0.8, edgecolor='black', linewidth=1.5)

        ax4.set_xlabel('Power Station', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Load Factor (%)', fontsize=11, fontweight='bold')
        ax4.set_title('Load Factor Comparison',
                      fontsize=13, fontweight='bold', pad=15)
        ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax4.set_ylim(0, 100)

        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, load_factor_values)):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Add reference line for ideal load factor
        ax4.axhline(y=100, color='green', linestyle='--',
                   linewidth=1, alpha=0.5, label='Ideal (100%)')
        ax4.legend(fontsize=8)

        plt.tight_layout()
        return fig

    def generate_report(self, station_data, load_factors, time_percent, load_mw):
        """
        Generate a detailed text report of the analysis

        Args:
            station_data: Station load allocation data
            load_factors: Load factor calculations
            time_percent: Time percentage array
            load_mw: Total load array
        """
        print("=" * 80)
        print("POWER SYSTEM LOAD ANALYSIS REPORT".center(80))
        print("Example 50.24: Multi-Station Load Duration Curve Analysis".center(80))
        print("=" * 80)
        print()

        print("SYSTEM CONFIGURATION:")
        print("-" * 80)
        print(f"Station Capacity Ratio (Steam : Run-of-River : Reservoir) = {self.station_ratio[0]}:{self.station_ratio[1]}:{self.station_ratio[2]}")
        print(f"Peak Load on System: {np.max(load_mw):.2f} MW")
        print(f"Minimum Load on System: {np.min(load_mw):.2f} MW")
        print()

        print("STATION-WISE ANALYSIS:")
        print("=" * 80)

        station_names = {
            'steam': 'STEAM STATION (Base Load)',
            'run_of_river': 'RUN-OF-RIVER STATION (Intermediate Load)',
            'reservoir': 'RESERVOIR HYDRO STATION (Peak Load)'
        }

        for key, name in station_names.items():
            print(f"\n{name}")
            print("-" * 80)

            max_demand = load_factors[key]['max_demand']
            avg_load = load_factors[key]['average_load']
            load_factor = load_factors[key]['load_factor']
            total_energy = load_factors[key]['total_energy']

            print(f"Maximum Demand:        {max_demand:.2f} MW")
            print(f"Average Load:          {avg_load:.2f} MW")
            print(f"Load Factor:           {load_factor:.2f}%")
            print(f"Energy Generated:      {total_energy:.2f} MWh (normalized)")
            print(f"Capacity Utilization:  {(avg_load/max_demand*100) if max_demand > 0 else 0:.2f}%")

        print("\n" + "=" * 80)
        print("SUMMARY OF RESULTS:")
        print("-" * 80)

        # Summary table
        print(f"\n{'Station':<25} {'Max Demand (MW)':<20} {'Load Factor (%)':<20}")
        print("-" * 80)
        for key, name in [('steam', 'Steam Station'),
                          ('run_of_river', 'Run-of-River Station'),
                          ('reservoir', 'Reservoir Hydro Station')]:
            max_d = load_factors[key]['max_demand']
            lf = load_factors[key]['load_factor']
            print(f"{name:<25} {max_d:<20.2f} {lf:<20.2f}")

        print("\n" + "=" * 80)
        print("KEY OBSERVATIONS:")
        print("-" * 80)

        # Find station with highest and lowest load factors
        lf_values = {k: v['load_factor'] for k, v in load_factors.items()}
        highest_lf = max(lf_values, key=lf_values.get)
        lowest_lf = min(lf_values, key=lf_values.get)

        print(f"1. Steam station handles base load continuously with highest utilization")
        print(f"2. Reservoir hydro station handles peak loads with flexible operation")
        print(f"3. Highest load factor: {highest_lf.replace('_', '-').title()} ({lf_values[highest_lf]:.2f}%)")
        print(f"4. Lowest load factor: {lowest_lf.replace('_', '-').title()} ({lf_values[lowest_lf]:.2f}%)")
        print(f"5. Total system capacity: {sum(v['max_demand'] for v in load_factors.values()):.2f} MW")

        print("\n" + "=" * 80)
        print("INTERPRETATION:")
        print("-" * 80)
        print("• Load Factor indicates how efficiently each station is utilized")
        print("• Higher load factor = Better capacity utilization and economics")
        print("• Steam (base load) typically has highest load factor")
        print("• Peak load stations have lower load factors due to intermittent operation")
        print("• Optimal mix ensures reliable supply with economic operation")
        print("=" * 80)


def main():
    """Main execution function"""

    # Initialize analyzer with station ratio 7:4:1
    analyzer = PowerSystemAnalyzer(station_ratio=(7, 4, 1))

    # Create load duration curve
    time_percent, load_mw = analyzer.create_load_duration_curve()

    # Allocate loads to different stations
    station_data = analyzer.allocate_station_loads(time_percent, load_mw)

    # Calculate load factors
    load_factors = analyzer.calculate_load_factors(station_data, time_percent)

    # Generate text report
    analyzer.generate_report(station_data, load_factors, time_percent, load_mw)

    # Create visualizations
    fig = analyzer.visualize_results(time_percent, load_mw, station_data, load_factors)

    # Save the figure
    plt.savefig('/home/user/claude2/power_station_analysis.png',
                dpi=300, bbox_inches='tight')
    print("\n✓ Visualization saved as 'power_station_analysis.png'")
    plt.close()


if __name__ == "__main__":
    main()

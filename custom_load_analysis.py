"""
Custom Power Station Load Analysis
Allows users to define their own load duration curves and analyze different scenarios
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
import matplotlib.pyplot as plt
from power_station_load_analysis import PowerSystemAnalyzer


def scenario_1_standard():
    """Standard load curve from Example 50.24"""
    print("\n" + "="*80)
    print("SCENARIO 1: Standard Load Duration Curve")
    print("="*80)

    analyzer = PowerSystemAnalyzer(station_ratio=(7, 4, 1))
    time_percent, load_mw = analyzer.create_load_duration_curve()

    station_data = analyzer.allocate_station_loads(time_percent, load_mw)
    load_factors = analyzer.calculate_load_factors(station_data, time_percent)

    analyzer.generate_report(station_data, load_factors, time_percent, load_mw)

    fig = analyzer.visualize_results(time_percent, load_mw, station_data, load_factors)
    plt.savefig('/home/user/claude2/scenario_1_standard.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: scenario_1_standard.png")
    plt.close()


def scenario_2_high_peak():
    """High peak load scenario with sharper load variations"""
    print("\n" + "="*80)
    print("SCENARIO 2: High Peak Load with Sharp Variations")
    print("="*80)

    analyzer = PowerSystemAnalyzer(station_ratio=(7, 4, 1))

    # Custom load curve with higher peaks
    time_percent = np.array([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    load_mw = np.array([120, 115, 105, 90, 78, 68, 60, 55, 50, 45, 40, 35])

    station_data = analyzer.allocate_station_loads(time_percent, load_mw)
    load_factors = analyzer.calculate_load_factors(station_data, time_percent)

    analyzer.generate_report(station_data, load_factors, time_percent, load_mw)

    fig = analyzer.visualize_results(time_percent, load_mw, station_data, load_factors)
    plt.savefig('/home/user/claude2/scenario_2_high_peak.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: scenario_2_high_peak.png")
    plt.close()


def scenario_3_flat_load():
    """Relatively flat load profile with less variation"""
    print("\n" + "="*80)
    print("SCENARIO 3: Flat Load Profile (Industrial Load)")
    print("="*80)

    analyzer = PowerSystemAnalyzer(station_ratio=(7, 4, 1))

    # Flatter load curve - typical for industrial systems
    time_percent = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    load_mw = np.array([85, 83, 81, 78, 76, 74, 72, 70, 68, 66, 64])

    station_data = analyzer.allocate_station_loads(time_percent, load_mw)
    load_factors = analyzer.calculate_load_factors(station_data, time_percent)

    analyzer.generate_report(station_data, load_factors, time_percent, load_mw)

    fig = analyzer.visualize_results(time_percent, load_mw, station_data, load_factors)
    plt.savefig('/home/user/claude2/scenario_3_flat_load.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: scenario_3_flat_load.png")
    plt.close()


def scenario_4_different_ratio():
    """Same load curve but different station capacity ratio"""
    print("\n" + "="*80)
    print("SCENARIO 4: Different Station Capacity Ratio (5:3:2)")
    print("="*80)

    # Different ratio: More balanced between stations
    analyzer = PowerSystemAnalyzer(station_ratio=(5, 3, 2))

    time_percent = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    load_mw = np.array([100, 95, 88, 80, 72, 65, 58, 52, 45, 38, 30])

    station_data = analyzer.allocate_station_loads(time_percent, load_mw)
    load_factors = analyzer.calculate_load_factors(station_data, time_percent)

    analyzer.generate_report(station_data, load_factors, time_percent, load_mw)

    fig = analyzer.visualize_results(time_percent, load_mw, station_data, load_factors)
    plt.savefig('/home/user/claude2/scenario_4_different_ratio.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: scenario_4_different_ratio.png")
    plt.close()


def scenario_5_renewable_heavy():
    """Scenario with higher renewable capacity (more hydro)"""
    print("\n" + "="*80)
    print("SCENARIO 5: Renewable-Heavy Mix (4:3:3)")
    print("="*80)

    # More balanced mix with higher renewable content
    analyzer = PowerSystemAnalyzer(station_ratio=(4, 3, 3))

    time_percent = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    load_mw = np.array([100, 94, 86, 78, 70, 63, 57, 51, 46, 41, 36])

    station_data = analyzer.allocate_station_loads(time_percent, load_mw)
    load_factors = analyzer.calculate_load_factors(station_data, time_percent)

    analyzer.generate_report(station_data, load_factors, time_percent, load_mw)

    fig = analyzer.visualize_results(time_percent, load_mw, station_data, load_factors)
    plt.savefig('/home/user/claude2/scenario_5_renewable_heavy.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: scenario_5_renewable_heavy.png")
    plt.close()


def compare_all_scenarios():
    """Create a comparison visualization of all scenarios"""
    print("\n" + "="*80)
    print("GENERATING COMPARISON CHART")
    print("="*80)

    scenarios = {
        'Standard (7:4:1)': {
            'ratio': (7, 4, 1),
            'time': np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
            'load': np.array([100, 95, 88, 80, 72, 65, 58, 52, 45, 38, 30])
        },
        'High Peak (7:4:1)': {
            'ratio': (7, 4, 1),
            'time': np.array([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
            'load': np.array([120, 115, 105, 90, 78, 68, 60, 55, 50, 45, 40, 35])
        },
        'Flat Load (7:4:1)': {
            'ratio': (7, 4, 1),
            'time': np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
            'load': np.array([85, 83, 81, 78, 76, 74, 72, 70, 68, 66, 64])
        },
        'Balanced (5:3:2)': {
            'ratio': (5, 3, 2),
            'time': np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
            'load': np.array([100, 95, 88, 80, 72, 65, 58, 52, 45, 38, 30])
        },
        'Renewable (4:3:3)': {
            'ratio': (4, 3, 3),
            'time': np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
            'load': np.array([100, 94, 86, 78, 70, 63, 57, 51, 46, 41, 36])
        }
    }

    # Calculate load factors for all scenarios
    results = {}
    for name, params in scenarios.items():
        analyzer = PowerSystemAnalyzer(station_ratio=params['ratio'])
        station_data = analyzer.allocate_station_loads(params['time'], params['load'])
        load_factors = analyzer.calculate_load_factors(station_data, params['time'])
        results[name] = load_factors

    # Create comparison plots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Load Factor Comparison
    ax1 = axes[0, 0]
    x = np.arange(len(scenarios))
    width = 0.25

    steam_lf = [results[s]['steam']['load_factor'] for s in scenarios.keys()]
    river_lf = [results[s]['run_of_river']['load_factor'] for s in scenarios.keys()]
    hydro_lf = [results[s]['reservoir']['load_factor'] for s in scenarios.keys()]

    ax1.bar(x - width, steam_lf, width, label='Steam', color='#FF6B6B', alpha=0.8)
    ax1.bar(x, river_lf, width, label='Run-of-River', color='#4ECDC4', alpha=0.8)
    ax1.bar(x + width, hydro_lf, width, label='Reservoir', color='#45B7D1', alpha=0.8)

    ax1.set_xlabel('Scenario', fontweight='bold')
    ax1.set_ylabel('Load Factor (%)', fontweight='bold')
    ax1.set_title('Load Factor Comparison Across Scenarios', fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios.keys(), rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Maximum Demand Comparison
    ax2 = axes[0, 1]
    steam_md = [results[s]['steam']['max_demand'] for s in scenarios.keys()]
    river_md = [results[s]['run_of_river']['max_demand'] for s in scenarios.keys()]
    hydro_md = [results[s]['reservoir']['max_demand'] for s in scenarios.keys()]

    ax2.bar(x - width, steam_md, width, label='Steam', color='#FF6B6B', alpha=0.8)
    ax2.bar(x, river_md, width, label='Run-of-River', color='#4ECDC4', alpha=0.8)
    ax2.bar(x + width, hydro_md, width, label='Reservoir', color='#45B7D1', alpha=0.8)

    ax2.set_xlabel('Scenario', fontweight='bold')
    ax2.set_ylabel('Maximum Demand (MW)', fontweight='bold')
    ax2.set_title('Maximum Demand Comparison', fontweight='bold', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios.keys(), rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Load Duration Curves
    ax3 = axes[1, 0]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F38181', '#AA96DA']
    for (name, params), color in zip(scenarios.items(), colors):
        ax3.plot(params['time'], params['load'], 'o-', label=name,
                color=color, linewidth=2, markersize=4)

    ax3.set_xlabel('Time Duration (%)', fontweight='bold')
    ax3.set_ylabel('Load (MW)', fontweight='bold')
    ax3.set_title('Load Duration Curves - All Scenarios', fontweight='bold', pad=15)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Plot 4: Average Load Comparison
    ax4 = axes[1, 1]
    steam_avg = [results[s]['steam']['average_load'] for s in scenarios.keys()]
    river_avg = [results[s]['run_of_river']['average_load'] for s in scenarios.keys()]
    hydro_avg = [results[s]['reservoir']['average_load'] for s in scenarios.keys()]

    ax4.bar(x - width, steam_avg, width, label='Steam', color='#FF6B6B', alpha=0.8)
    ax4.bar(x, river_avg, width, label='Run-of-River', color='#4ECDC4', alpha=0.8)
    ax4.bar(x + width, hydro_avg, width, label='Reservoir', color='#45B7D1', alpha=0.8)

    ax4.set_xlabel('Scenario', fontweight='bold')
    ax4.set_ylabel('Average Load (MW)', fontweight='bold')
    ax4.set_title('Average Load Comparison', fontweight='bold', pad=15)
    ax4.set_xticks(x)
    ax4.set_xticklabels(scenarios.keys(), rotation=45, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('/home/user/claude2/scenario_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: scenario_comparison.png")
    plt.close()

    # Print summary table
    print("\n" + "="*100)
    print("SCENARIO COMPARISON SUMMARY")
    print("="*100)
    print(f"{'Scenario':<20} {'Steam LF':<12} {'River LF':<12} {'Hydro LF':<12} {'Total Cap':<12}")
    print("-"*100)
    for name in scenarios.keys():
        s_lf = results[name]['steam']['load_factor']
        r_lf = results[name]['run_of_river']['load_factor']
        h_lf = results[name]['reservoir']['load_factor']
        total = sum(results[name][st]['max_demand'] for st in ['steam', 'run_of_river', 'reservoir'])
        print(f"{name:<20} {s_lf:>10.2f}% {r_lf:>10.2f}% {h_lf:>10.2f}% {total:>10.2f} MW")
    print("="*100)


def main():
    """Run all scenarios"""
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + "COMPREHENSIVE POWER STATION LOAD ANALYSIS".center(78) + "#")
    print("#" + "Multiple Scenarios and Comparisons".center(78) + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    # Run all scenarios
    scenario_1_standard()
    scenario_2_high_peak()
    scenario_3_flat_load()
    scenario_4_different_ratio()
    scenario_5_renewable_heavy()

    # Generate comparison
    compare_all_scenarios()

    print("\n" + "="*80)
    print("ALL SCENARIOS COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nGenerated Files:")
    print("  1. scenario_1_standard.png")
    print("  2. scenario_2_high_peak.png")
    print("  3. scenario_3_flat_load.png")
    print("  4. scenario_4_different_ratio.png")
    print("  5. scenario_5_renewable_heavy.png")
    print("  6. scenario_comparison.png")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

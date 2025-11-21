#!/usr/bin/env python3
"""
Example 50.29: Economic Comparison of Hydro vs Steam Power Stations
This program compares the economics of hydro and steam power stations
at different load factors considering capital costs, running costs, and interest rates.
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Dict, Tuple


class PowerStationEconomics:
    """Class to handle power station economic calculations"""

    def __init__(self, capital_cost: float, running_cost: float, interest_rate: float, name: str):
        """
        Initialize power station parameters

        Args:
            capital_cost: Capital cost in Rs per kW
            running_cost: Running cost in Rs per kWh
            interest_rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
            name: Name of the station type
        """
        self.capital_cost = capital_cost
        self.running_cost = running_cost
        self.interest_rate = interest_rate
        self.name = name
        self.hours_per_year = 8760

    def calculate_costs(self, load_factor: float) -> Dict[str, float]:
        """
        Calculate annual costs and cost per unit

        Args:
            load_factor: Load factor as decimal (e.g., 0.1 for 10%)

        Returns:
            Dictionary containing all cost calculations
        """
        # Annual fixed cost per kW (interest on capital)
        annual_fixed_cost = self.capital_cost * self.interest_rate

        # Annual energy generated per kW
        annual_energy = load_factor * self.hours_per_year

        # Annual running cost per kW
        annual_running_cost = self.running_cost * annual_energy

        # Total annual cost per kW
        total_annual_cost = annual_fixed_cost + annual_running_cost

        # Cost per kWh generated
        if annual_energy > 0:
            cost_per_kwh = total_annual_cost / annual_energy
        else:
            cost_per_kwh = 0

        return {
            'annual_fixed_cost': annual_fixed_cost,
            'annual_energy': annual_energy,
            'annual_running_cost': annual_running_cost,
            'total_annual_cost': total_annual_cost,
            'cost_per_kwh': cost_per_kwh
        }


class PowerStationComparisonGUI:
    """GUI for power station economic comparison"""

    def __init__(self, root):
        self.root = root
        self.root.title("Power Station Economic Comparison - Example 50.29")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')

        # Initialize power stations
        self.hydro = PowerStationEconomics(
            capital_cost=2200,  # Rs per kW
            running_cost=0.01,   # Rs per kWh (1 Paise)
            interest_rate=0.05,  # 5%
            name="Hydro"
        )

        self.steam = PowerStationEconomics(
            capital_cost=1200,  # Rs per kW
            running_cost=0.05,   # Rs per kWh (5 Paise)
            interest_rate=0.05,  # 5%
            name="Steam"
        )

        self.create_widgets()
        self.calculate_and_display()

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        title_label = ttk.Label(
            main_frame,
            text="Economic Comparison: Hydro vs Steam Power Stations",
            font=title_font
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Problem statement
        problem_frame = ttk.LabelFrame(main_frame, text="Problem Statement", padding="10")
        problem_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        problem_frame.columnconfigure(0, weight=1)

        problem_text = (
            "Compare hydro and steam power stations to determine which is more economical\n"
            "at load factors of 10% and 50%, considering capital costs, running costs, and interest."
        )
        ttk.Label(problem_frame, text=problem_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)

        # Input parameters
        input_frame = ttk.LabelFrame(main_frame, text="Given Parameters", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Create table for input parameters
        headers = ["Parameter", "Hydro Station", "Steam Station"]
        for col, header in enumerate(headers):
            label = ttk.Label(input_frame, text=header, font=('Helvetica', 10, 'bold'))
            label.grid(row=0, column=col, padx=10, pady=5, sticky=tk.W)

        input_data = [
            ("Capital Cost", "Rs. 2,200 per kW", "Rs. 1,200 per kW"),
            ("Running Cost", "1 Paise per kWh (Rs. 0.01)", "5 Paise per kWh (Rs. 0.05)"),
            ("Interest Rate", "5%", "5%")
        ]

        for row, (param, hydro_val, steam_val) in enumerate(input_data, start=1):
            ttk.Label(input_frame, text=param).grid(row=row, column=0, padx=10, pady=3, sticky=tk.W)
            ttk.Label(input_frame, text=hydro_val).grid(row=row, column=1, padx=10, pady=3, sticky=tk.W)
            ttk.Label(input_frame, text=steam_val).grid(row=row, column=2, padx=10, pady=3, sticky=tk.W)

        # Results frame
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        self.results_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Calculate button
        calc_button = ttk.Button(
            main_frame,
            text="Recalculate",
            command=self.calculate_and_display
        )
        calc_button.grid(row=4, column=0, pady=(0, 10))

    def calculate_and_display(self):
        """Calculate costs and display results"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Calculate for both load factors
        load_factors = [0.10, 0.50]

        for idx, lf in enumerate(load_factors):
            self.display_comparison(lf, idx)

    def display_comparison(self, load_factor: float, row_offset: int):
        """
        Display comparison for a specific load factor

        Args:
            load_factor: Load factor as decimal
            row_offset: Row offset for grid placement
        """
        # Create frame for this load factor
        lf_frame = ttk.LabelFrame(
            self.results_frame,
            text=f"Analysis at {load_factor*100:.0f}% Load Factor",
            padding="15"
        )
        lf_frame.grid(row=row_offset, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        lf_frame.columnconfigure(1, weight=1)
        lf_frame.columnconfigure(2, weight=1)

        # Calculate costs for both stations
        hydro_costs = self.hydro.calculate_costs(load_factor)
        steam_costs = self.steam.calculate_costs(load_factor)

        # Display detailed calculations
        row = 0

        # Header
        ttk.Label(
            lf_frame,
            text="Cost Component",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)

        ttk.Label(
            lf_frame,
            text="Hydro Station",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(
            lf_frame,
            text="Steam Station",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=2, padx=10, pady=5, sticky=tk.W)

        row += 1

        # Separator
        ttk.Separator(lf_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )
        row += 1

        # Annual Fixed Cost
        ttk.Label(lf_frame, text="Annual Fixed Cost (per kW):").grid(
            row=row, column=0, padx=10, pady=3, sticky=tk.W
        )
        ttk.Label(lf_frame, text=f"Rs. {hydro_costs['annual_fixed_cost']:.2f}").grid(
            row=row, column=1, padx=10, pady=3, sticky=tk.W
        )
        ttk.Label(lf_frame, text=f"Rs. {steam_costs['annual_fixed_cost']:.2f}").grid(
            row=row, column=2, padx=10, pady=3, sticky=tk.W
        )
        row += 1

        # Annual Energy
        ttk.Label(lf_frame, text="Annual Energy Output (per kW):").grid(
            row=row, column=0, padx=10, pady=3, sticky=tk.W
        )
        ttk.Label(lf_frame, text=f"{hydro_costs['annual_energy']:.2f} kWh").grid(
            row=row, column=1, padx=10, pady=3, sticky=tk.W
        )
        ttk.Label(lf_frame, text=f"{steam_costs['annual_energy']:.2f} kWh").grid(
            row=row, column=2, padx=10, pady=3, sticky=tk.W
        )
        row += 1

        # Annual Running Cost
        ttk.Label(lf_frame, text="Annual Running Cost (per kW):").grid(
            row=row, column=0, padx=10, pady=3, sticky=tk.W
        )
        ttk.Label(lf_frame, text=f"Rs. {hydro_costs['annual_running_cost']:.2f}").grid(
            row=row, column=1, padx=10, pady=3, sticky=tk.W
        )
        ttk.Label(lf_frame, text=f"Rs. {steam_costs['annual_running_cost']:.2f}").grid(
            row=row, column=2, padx=10, pady=3, sticky=tk.W
        )
        row += 1

        # Separator
        ttk.Separator(lf_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
        )
        row += 1

        # Total Annual Cost
        ttk.Label(
            lf_frame,
            text="Total Annual Cost (per kW):",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=0, padx=10, pady=3, sticky=tk.W)

        ttk.Label(
            lf_frame,
            text=f"Rs. {hydro_costs['total_annual_cost']:.2f}",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=1, padx=10, pady=3, sticky=tk.W)

        ttk.Label(
            lf_frame,
            text=f"Rs. {steam_costs['total_annual_cost']:.2f}",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=2, padx=10, pady=3, sticky=tk.W)
        row += 1

        # Cost per kWh
        ttk.Label(
            lf_frame,
            text="Cost per kWh Generated:",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=0, padx=10, pady=3, sticky=tk.W)

        ttk.Label(
            lf_frame,
            text=f"Rs. {hydro_costs['cost_per_kwh']:.4f}",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=1, padx=10, pady=3, sticky=tk.W)

        ttk.Label(
            lf_frame,
            text=f"Rs. {steam_costs['cost_per_kwh']:.4f}",
            font=('Helvetica', 9, 'bold')
        ).grid(row=row, column=2, padx=10, pady=3, sticky=tk.W)
        row += 1

        # Separator
        ttk.Separator(lf_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )
        row += 1

        # Recommendation
        if hydro_costs['cost_per_kwh'] < steam_costs['cost_per_kwh']:
            winner = "Hydro Station"
            savings = steam_costs['cost_per_kwh'] - hydro_costs['cost_per_kwh']
            color = '#006400'  # Dark green
        else:
            winner = "Steam Station"
            savings = hydro_costs['cost_per_kwh'] - steam_costs['cost_per_kwh']
            color = '#8B0000'  # Dark red

        recommendation_text = (
            f"Recommendation: {winner} is more economical\n"
            f"Savings: Rs. {savings:.4f} per kWh (Rs. {savings*100:.2f} Paise per kWh)"
        )

        recommendation_label = ttk.Label(
            lf_frame,
            text=recommendation_text,
            font=('Helvetica', 10, 'bold'),
            foreground=color,
            justify=tk.CENTER
        )
        recommendation_label.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1

        # Detailed explanation
        explanation = self.generate_explanation(load_factor, hydro_costs, steam_costs)
        explanation_label = ttk.Label(
            lf_frame,
            text=explanation,
            justify=tk.LEFT,
            wraplength=900
        )
        explanation_label.grid(row=row, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)

    def generate_explanation(self, load_factor: float, hydro_costs: Dict, steam_costs: Dict) -> str:
        """Generate detailed explanation of the results"""
        explanation = f"\nExplanation:\n"
        explanation += f"At {load_factor*100:.0f}% load factor:\n"
        explanation += f"• Hydro station has higher capital cost (Rs. 2,200/kW) but lower running cost (Rs. 0.01/kWh)\n"
        explanation += f"• Steam station has lower capital cost (Rs. 1,200/kW) but higher running cost (Rs. 0.05/kWh)\n"

        if load_factor == 0.10:
            explanation += (
                f"• At low load factor (10%), the station runs only {hydro_costs['annual_energy']:.0f} hours equivalent per year\n"
                f"• The high capital cost of hydro (Rs. {hydro_costs['annual_fixed_cost']:.2f} fixed cost) "
                f"dominates over its low running cost\n"
                f"• Steam station's lower capital investment makes it more economical despite higher running costs"
            )
        else:
            explanation += (
                f"• At high load factor (50%), the station runs {hydro_costs['annual_energy']:.0f} hours equivalent per year\n"
                f"• The running costs become more significant over the year\n"
                f"• Hydro's low running cost (Rs. 0.01/kWh vs Rs. 0.05/kWh) now provides substantial savings\n"
                f"• The higher capital cost is amortized over more energy production, making hydro more economical"
            )

        return explanation


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = PowerStationComparisonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

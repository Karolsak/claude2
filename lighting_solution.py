#!/usr/bin/env python3
"""
Football Pitch Lighting Calculation Solution
Problem: Calculate the number of lamps per tower for a football pitch
"""

def calculate_lighting_solution():
    """
    Solve the football pitch lighting problem
    """
    print("="*70)
    print("FOOTBALL PITCH LIGHTING CALCULATION")
    print("="*70)
    print()

    # Given data
    print("GIVEN DATA:")
    print("-" * 70)
    pitch_length = 120  # meters
    pitch_width = 60    # meters
    required_illumination = 1000  # lm/m²
    efficiency_factor = 0.4  # 40% reaches the pitch
    lamp_power = 1000  # W
    lamp_efficiency = 30  # lm/W
    num_towers = 12

    print(f"Pitch dimensions: {pitch_length} m × {pitch_width} m")
    print(f"Required illumination: {required_illumination} lm/m²")
    print(f"Efficiency factor: {efficiency_factor*100}% reaches the pitch")
    print(f"Lamp power: {lamp_power} W")
    print(f"Lamp efficiency: {lamp_efficiency} lm/W")
    print(f"Number of towers: {num_towers}")
    print()

    # Step-by-step calculation
    print("STEP-BY-STEP CALCULATION:")
    print("-" * 70)

    # Step 1: Calculate pitch area
    pitch_area = pitch_length * pitch_width
    print(f"Step 1: Pitch Area")
    print(f"        Area = {pitch_length} m × {pitch_width} m = {pitch_area} m²")
    print()

    # Step 2: Total lumens required on pitch
    total_lumens_required = pitch_area * required_illumination
    print(f"Step 2: Total Lumens Required on Pitch")
    print(f"        Total lumens = Area × Illumination")
    print(f"        Total lumens = {pitch_area} m² × {required_illumination} lm/m²")
    print(f"        Total lumens = {total_lumens_required:,} lm")
    print()

    # Step 3: Total lumens to be emitted
    total_lumens_emitted = total_lumens_required / efficiency_factor
    print(f"Step 3: Total Lumens to be Emitted")
    print(f"        (Since only {efficiency_factor*100}% reaches the pitch)")
    print(f"        Total emitted = {total_lumens_required:,} lm / {efficiency_factor}")
    print(f"        Total emitted = {total_lumens_emitted:,.0f} lm")
    print()

    # Step 4: Lumens per lamp
    lumens_per_lamp = lamp_power * lamp_efficiency
    print(f"Step 4: Lumens per Lamp")
    print(f"        Lumens/lamp = Power × Efficiency")
    print(f"        Lumens/lamp = {lamp_power} W × {lamp_efficiency} lm/W")
    print(f"        Lumens/lamp = {lumens_per_lamp:,} lm")
    print()

    # Step 5: Total number of lamps
    total_lamps = int(total_lumens_emitted / lumens_per_lamp)
    print(f"Step 5: Total Number of Lamps")
    print(f"        Total lamps = Total emitted / Lumens per lamp")
    print(f"        Total lamps = {total_lumens_emitted:,.0f} lm / {lumens_per_lamp:,} lm")
    print(f"        Total lamps = {total_lamps} lamps")
    print()

    # Step 6: Lamps per tower
    lamps_per_tower = total_lamps // num_towers
    print(f"Step 6: Lamps per Tower")
    print(f"        Lamps/tower = Total lamps / Number of towers")
    print(f"        Lamps/tower = {total_lamps} / {num_towers}")
    print(f"        Lamps/tower = {lamps_per_tower} lamps")
    print()

    # Final answer
    print("="*70)
    print(f"ANSWER: {lamps_per_tower} LAMPS PER TOWER")
    print("="*70)
    print()

    # Additional information
    print("ADDITIONAL INFORMATION:")
    print("-" * 70)
    total_power = total_lamps * lamp_power
    power_per_tower = lamps_per_tower * lamp_power

    print(f"Total power consumption: {total_power:,} W = {total_power/1000:.2f} kW")
    print(f"Power per tower: {power_per_tower:,} W = {power_per_tower/1000:.2f} kW")
    print(f"Total luminous flux: {total_lumens_emitted:,.0f} lm")
    print(f"Luminous flux per tower: {total_lumens_emitted/num_towers:,.0f} lm")
    print()

    # Return results as dictionary
    return {
        'pitch_area': pitch_area,
        'total_lumens_required': total_lumens_required,
        'total_lumens_emitted': total_lumens_emitted,
        'lumens_per_lamp': lumens_per_lamp,
        'total_lamps': total_lamps,
        'lamps_per_tower': lamps_per_tower,
        'total_power': total_power,
        'power_per_tower': power_per_tower
    }

def main():
    """Main function"""
    results = calculate_lighting_solution()

    # Verification
    print("VERIFICATION:")
    print("-" * 70)
    print(f"Lumens reaching pitch: {results['lamps_per_tower']} × {results['lumens_per_lamp']:,} × 12 × 0.4")
    lumens_on_pitch = results['lamps_per_tower'] * results['lumens_per_lamp'] * 12 * 0.4
    print(f"                      = {lumens_on_pitch:,.0f} lm")
    print(f"Illumination achieved: {lumens_on_pitch / results['pitch_area']:.1f} lm/m²")
    print()

    if abs(lumens_on_pitch / results['pitch_area'] - 1000) < 1:
        print("✓ VERIFICATION SUCCESSFUL - Required illumination achieved!")
    else:
        print("✗ Verification failed - Check calculations")
    print("="*70)

if __name__ == "__main__":
    main()

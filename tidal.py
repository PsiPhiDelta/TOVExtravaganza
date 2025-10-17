#!/usr/bin/env python3
"""
Object-Oriented Tidal Deformability Calculator
Computes tidal Love numbers and deformability for neutron stars
"""
from src.eos import EOS
from src.tov_solver import TOVSolver
from src.tidal_calculator import TidalCalculator
from src.output_handlers import TidalWriter


###############################################################################
# USER SETTINGS
###############################################################################
FILENAME = "./inputCode/hsdd2.csv"  # EOS file in TOV code units
RMAX = 100.0                        # Maximum radius for TOV (km)
DR = 0.0005                         # Radial step (km)
NUM_STARS = 100                     # Number of stars to compute
RTOL = 1e-10                        # ODE relative tolerance
ATOL = 1e-12                        # ODE absolute tolerance


def main():
    """Main execution function."""
    
    print("="*70)
    print("  Tidal Deformability Calculator - Object-Oriented Version")
    print("="*70)
    
    # Load EOS
    print(f"Loading EOS from: {FILENAME}")
    eos = EOS.from_file(FILENAME)
    print(f"  Loaded {eos.n_points} points with columns: {eos.colnames}")
    
    # Create solvers
    tov_solver = TOVSolver(eos, r_max=RMAX, dr=DR, rtol=RTOL, atol=ATOL)
    tidal_calc = TidalCalculator(tov_solver)
    
    # Compute tidal deformability sequence
    print(f"\nComputing tidal deformability for {NUM_STARS} stars...")
    results = tidal_calc.compute_sequence(NUM_STARS)
    
    # Print sample results
    valid = [r for r in results if r['M_solar'] > 0.5]
    print(f"\nValid solutions (M > 0.5 Msun): {len(valid)}/{len(results)}")
    
    if valid:
        max_mass_result = max(valid, key=lambda r: r['M_solar'])
        print(f"Maximum mass: {max_mass_result['M_solar']:.4f} Msun, "
              f"Lambda={max_mass_result['Lambda']:.2f}")
    
    # Interpolate at 1.4 Msun
    result_14 = TidalWriter.interpolate_at_mass(results, 1.4)
    if result_14:
        print("\n" + "="*70)
        print(f"  At M = 1.4 Msun:")
        print(f"    Radius R = {result_14['R']:.2f} km")
        print(f"    Lambda = {result_14['Lambda']:.2f}")
        print(f"    k2 = {result_14['k2']:.4f}")
        print("="*70)
    
    # Write output
    import os
    base_name = os.path.splitext(os.path.basename(FILENAME))[0]
    writer = TidalWriter()
    csv_path, pdf_path = writer.write_results(results, base_name)
    
    print(f"\nWrote {len(results)} results to: {csv_path}")
    print(f"Saved plots to: {pdf_path}")
    print("\nDone!")


if __name__ == "__main__":
    main()


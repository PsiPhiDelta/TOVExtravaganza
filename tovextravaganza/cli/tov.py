#!/usr/bin/env python3
import os
import csv
import argparse
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from pathlib import Path
import time

# --------------------------------------------------------------------
# 1) TOTALLY UNNECESSARY PHYSICAL CONSTANTS (for your amusement only)
# --------------------------------------------------------------------
# Even though we used to brag about how to convert from MeV^-4 to code units,
# now we assume your input is ALREADY in TOV "code units" (dimensionless).
# So we do not actually need these constants in this script,
# but let's keep them anyway, like an old friend we can't let go of.
#
# c0   = 299792458         # speed of light, m/s
# G    = 6.67408e-11       # gravitational constant, m^3 / (kg s^2)
# qe   = 1.6021766208e-19  # elementary charge in coulombs
# hbar = 1.054571817e-34   # reduced Planck constant, J*s
#
#
# But seriously, we're not using them here, because you told us
# your file is *already* in those sweet dimensionless code units.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Now we use the fancy object-oriented modules!
from ..core.eos import EOS
from ..core.tov_solver import TOVSolver
from ..core.tidal_calculator import TidalCalculator
from ..core.output_handlers import MassRadiusWriter, TidalWriter

# Use this constant to convert from code units to solar masses:
Msun_in_code = 1.4766  # 1 Msun = 1.4766 (G=c=1) length units

###############################################################################
# DEFAULT SETTINGS (can be overridden via CLI args)
###############################################################################
DEFAULT_RMAX = 100.0                       # Maximum radius for TOV
DEFAULT_DR = 0.001                        # Radial step
DEFAULT_NUM_STARS = 200                    # Number of central pressures to sample
DEFAULT_OUTPUT = "export/stars"           # Output folder
DEFAULT_RTOL = 1e-12                       # ODE relative tolerance
DEFAULT_ATOL = 1e-14                       # ODE absolute tolerance

# Keep old names for backward compatibility with radial.py (use test.csv as default)
FILENAME = "./inputCode/test.csv"
RMAX = DEFAULT_RMAX
DR = DEFAULT_DR
NUM_STARS = DEFAULT_NUM_STARS

###############################################################################
# BACKWARD COMPATIBILITY FUNCTIONS
# These let radial.py still work with the old function calls
###############################################################################
def read_eos_csv_multi(filename):
    """
    Read EOS from CSV:
      - skip comment lines (#) and empty lines
      - if the first non-comment row is textual, treat as header
      - store columns in data_dict = {colname: np.array([...])}
      - assume first column is "p", second is "e" if no explicit header
      - sort by ascending p
    Returns: data_dict, colnames
    """
    raw_data = []
    header = None

    with open(filename, "r") as fin:
        reader = csv.reader(fin)
        for row in reader:
            if (not row) or row[0].startswith("#"):
                continue
            # check if we have a header yet
            if header is None:
                # try parsing first 2 columns as float
                try:
                    float(row[0]), float(row[1])
                    # no exception => numeric => no header
                    raw_data.append(row)
                except ValueError:
                    # not numeric => treat as header
                    header = row
            else:
                raw_data.append(row)

    # if no header found, create a default
    if header is None:
        ncols = len(raw_data[0])
        header = []
        header.append("p")
        header.append("e")
        for i in range(2, ncols):
            header.append(f"col{i}")

    # parse data into float arrays
    columns = [[] for _ in header]
    for row in raw_data:
        if len(row) < 2:
            continue
        valid = True
        vals = []
        for i in range(len(header)):
            try:
                vals.append(float(row[i]))
            except (IndexError, ValueError):
                valid = False
                break
        if valid:
            for i in range(len(header)):
                columns[i].append(vals[i])

    data_dict = {}
    for h, colvals in zip(header, columns):
        data_dict[h] = np.array(colvals, dtype=float)

    # Sort by ascending p
    if "p" not in data_dict:
        raise ValueError("No 'p' column found! (First column must be named 'p' or given by default.)")

    sort_idx = np.argsort(data_dict["p"])
    for k in data_dict.keys():
        data_dict[k] = data_dict[k][sort_idx]

    return data_dict, header


class EOSMulti:
    """
    Backward compatibility wrapper for radial.py
    This wraps the EOS class for compatibility
    """
    def __init__(self, data_dict, colnames):
        self.data_dict = data_dict
        self.colnames = colnames
        self.p_table = data_dict["p"]
        self.n = len(self.p_table)
        if self.n < 2:
            raise ValueError("Need at least 2 data points for interpolation.")
        self.ilast = 0  # bracket index for speed
        
        # Create the real EOS object
        self._eos = EOS(data_dict, colnames)

    def get_value(self, colname, p):
        return self._eos.get_value(colname, p)

    def get_e_of_p(self, p):
        return self._eos.get_energy_density(p)
    
    def interp(self, colname, p):
        """For radial.py compatibility"""
        return self._eos.get_value(colname, p)


def solve_tov(central_p, eos_multi, r_max=RMAX, dr=DR):
    """Legacy function for backward compatibility"""
    solver = TOVSolver(eos_multi._eos, r_max, dr)
    star = solver.solve(central_p)
    return star.radius, star.mass_code


def solve_tov_rad(central_p, eos_multi, r_max=RMAX, dr=DR):
    """Legacy function for backward compatibility with radial.py"""
    solver = TOVSolver(eos_multi._eos, r_max, dr)
    star, r_vals, M_vals, p_vals = solver.solve(central_p, return_profile=True)
    
    # Return in the old format that radial.py expects
    return r_vals, M_vals, p_vals, star.radius, star.mass_code


###############################################################################
# BATCH PROCESSING FUNCTIONS FOR PARALLEL EXECUTION
###############################################################################
def process_single_file(file_args):
    """
    Process a single EOS file (designed for parallel execution).
    
    Parameters:
    -----------
    file_args : tuple
        (input_file, args_dict) where args_dict contains all processing parameters
        
    Returns:
    --------
    dict with status, filename, and results or error message
    """
    input_file, args_dict = file_args
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    try:
        # Read the EOS
        eos = EOS.from_file(input_file)
        
        # Create solver
        solver = TOVSolver(
            eos,
            r_max=args_dict['rmax'],
            dr=args_dict['dr'],
            rtol=args_dict['rtol'],
            atol=args_dict['atol']
        )
        
        # Create tidal calculator
        tidal_calc = TidalCalculator(solver)
        
        # Get pressure range
        p_range = eos.get_pressure_range()
        p_min = max(p_range[0], 1e-15)
        p_max = p_range[1]
        central_pressures = np.logspace(
            np.log10(p_min),
            np.log10(p_max),
            args_dict['num_stars']
        )
        
        # Solve for each pressure
        tidal_results = []
        for p_c in central_pressures:
            try:
                result = tidal_calc.compute(p_c)
                result['p_c'] = p_c
                
                # Add central column values from EOS
                central_values = eos.get_all_values_at_pressure(p_c)
                for key, val in central_values.items():
                    result[f'central_{key}'] = val
                
                tidal_results.append(result)
            except Exception:
                pass  # Skip failed solutions quietly in batch mode
        
        # Check if we got ANY results
        if not tidal_results:
            return {
                'status': 'error',
                'filename': base_name,
                'error': 'No valid solutions found (all stars failed)'
            }
        
        # Write results (with error handling)
        try:
            out_folder = args_dict['output']
            os.makedirs(out_folder, exist_ok=True)  # exist_ok prevents race condition
            
            writer = TidalWriter(output_folder=out_folder)
            csv_path, pdf_path = writer.write_results(
                tidal_results,
                base_name,
                show_plot=False,  # Never show plots in batch mode
                save_png=args_dict.get('save_png', False)
            )
        except Exception as e:
            return {
                'status': 'error',
                'filename': base_name,
                'error': f'Failed to write output: {str(e)}'
            }
        
        # Get stats
        valid_results = [r for r in tidal_results if r['M_solar'] > 0.01]
        max_mass = 0.0
        if valid_results:
            max_result = max(valid_results, key=lambda r: r['M_solar'])
            max_mass = max_result['M_solar']
        
        return {
            'status': 'success',
            'filename': base_name,
            'num_solutions': len(valid_results),
            'max_mass': max_mass,
            'csv_path': csv_path,
            'pdf_path': pdf_path
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'filename': base_name,
            'error': str(e)
        }


def process_batch(args):
    """
    Process all EOS files in a directory in parallel.
    
    Parameters:
    -----------
    args : argparse.Namespace
        Command-line arguments
    """
    input_dir = Path(args.batch)
    
    # Find all CSV files in the directory
    csv_files = list(input_dir.glob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in directory: {input_dir}")
        return
    
    print(f"\n{'='*70}")
    print(f"BATCH PROCESSING MODE - oh boy oh boy!")
    print(f"{'='*70}")
    print(f"Found {len(csv_files)} CSV files in {input_dir}")
    print(f"Processing with {args.workers} parallel workers")
    print(f"Output directory: {args.output}")
    print(f"Stars per file: {args.num_stars}")
    print(f"{'='*70}\n")
    
    # Prepare arguments for each file
    args_dict = {
        'output': args.output,
        'num_stars': args.num_stars,
        'rmax': args.rmax,
        'dr': args.dr,
        'rtol': getattr(args, 'rtol', DEFAULT_RTOL),
        'atol': getattr(args, 'atol', DEFAULT_ATOL),
        'save_png': args.save_png
    }
    
    file_args_list = [(str(f), args_dict) for f in csv_files]
    
    # Process files in parallel
    start_time = time.time()
    
    if args.workers == 1:
        # Sequential processing
        results = [process_single_file(fa) for fa in file_args_list]
    else:
        # Parallel processing
        with Pool(processes=args.workers) as pool:
            results = pool.map(process_single_file, file_args_list)
    
    elapsed = time.time() - start_time
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"BATCH PROCESSING COMPLETE!")
    print(f"{'='*70}")
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    
    print(f"\nProcessed {len(results)} files in {elapsed:.2f} seconds")
    print(f"  ✓ Successful: {len(successful)}")
    print(f"  ✗ Failed: {len(failed)}")
    
    if successful:
        print(f"\n{'='*70}")
        print("SUCCESSFUL FILES:")
        print(f"{'='*70}")
        for r in successful:
            print(f"  {r['filename']:20s} => {r['num_solutions']:4d} solutions, "
                  f"Max M = {r['max_mass']:.4f} Msun")
    
    if failed:
        print(f"\n{'='*70}")
        print("FAILED FILES:")
        print(f"{'='*70}")
        for r in failed:
            print(f"  {r['filename']:20s} => Error: {r['error']}")
    
    print(f"\n{'='*70}")
    print(f"All results saved to: {args.output}")
    print(f"{'='*70}\n")


###############################################################################
# 4) MAIN => for each star solution, store 1 line: (p_c, R, M, e(pc), col2(pc), ...)
###############################################################################
def main(args=None):
    """
    Main function - using fancy OO modules
    but keeping all the comedic style you know and love!
    Now with CLI arguments for extra flexibility!
    """
    # Parse command-line arguments if provided
    if args is None:
        import sys
        # Create custom help formatter to add our message before usage
        class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
            def format_help(self):
                help_text = super().format_help()
                # Add our message at the very top
                custom_header = """More arguments needed, did you mean?

"""
                return custom_header + help_text
        
        parser = argparse.ArgumentParser(
            description="""
===================================================================
SIMPLE VERSION (Most certainly you want this one!):
===================================================================

Just add the name of your EOS file at the end, like this:

  Via pip:
    tovx inputCode/test.csv
    tovx inputCode/hsdd2.csv
    tovx inputCode/csc.csv

  From source:
    python -m tovextravaganza.tov inputCode/test.csv
    python -m tovextravaganza.tov inputCode/hsdd2.csv

That's it! It'll compute 200 stellar configurations (with tidal deformability!)
and save everything to export/stars/ folder. Oh boy oh boy, so simple!

Solve the Tolman-Oppenheimer-Volkoff equations for neutron stars.
Even though we used to brag about physical constants, your input is
ALREADY in TOV "code units" (dimensionless). Oh boy oh boy!
""",
            formatter_class=CustomHelpFormatter,
            epilog="""
===================================================================
But if you are GACHI and want the ADVANCED stuff, here you go:
===================================================================

More stars for better resolution:
  tovx inputCode/hsdd2.csv -n 1000
  python -m tovextravaganza.tov inputCode/hsdd2.csv -n 1000

High precision (finer steps, like a fancy scientist):
  tovx inputCode/hsdd2.csv --dr 0.0005
  python -m tovextravaganza.tov inputCode/hsdd2.csv --dr 0.0005

Quiet mode (no spam, just the goods):
  tovx inputCode/hsdd2.csv -q

Custom output folder (be organized, be proud):
  tovx inputCode/test.csv -o export/my_awesome_results

FULL GACHI MODE (all the bells and whistles):
  tovx inputCode/hsdd2.csv -n 2000 --dr 0.0001 -q -o export/ultra

===================================================================
NEW! BATCH PROCESSING MODE (process multiple files in parallel!):
===================================================================

Process all CSV files in a folder using all CPU cores:
  tovx --batch inputCode/
  python -m tovextravaganza.tov --batch inputCode/

Process with specific number of workers:
  tovx --batch inputCode/ --workers 4
  
Batch mode with custom output and settings:
  tovx --batch inputCode/ -o export/batch_results -n 500 --workers 8

Oh boy oh boy, this will process all EOS files in parallel!
Perfect for when you have many EOS files to analyze!

===================================================================
Output: Mass-radius sequences WITH tidal deformability (Lambda, k2)!
        CSV + beautiful PDF plots in export/stars/ folder!
===================================================================
            """
        )
        parser.add_argument('input', nargs='?',
                          help='Input EOS file (e.g., inputCode/hsdd2.csv)')
        parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                          help=f'Output folder (default: {DEFAULT_OUTPUT})')
        parser.add_argument('-n', '--num-stars', type=int, default=DEFAULT_NUM_STARS,
                          help=f'Number of stars to compute (default: {DEFAULT_NUM_STARS})')
        parser.add_argument('--rmax', type=float, default=DEFAULT_RMAX,
                          help=f'Maximum radius (default: {DEFAULT_RMAX})')
        parser.add_argument('--dr', type=float, default=DEFAULT_DR,
                          help=f'Radial step size (default: {DEFAULT_DR})')
        parser.add_argument('-q', '--quiet', action='store_true',
                          help='Suppress per-star output')
        parser.add_argument('--no-show', action='store_true',
                          help='Do not display plot (still saves to file)')
        parser.add_argument('--no-plot', action='store_true',
                          help='Skip plotting entirely')
        parser.add_argument('--save-png', action='store_true',
                          help='Also save PNG versions of plots (for README/web, default: PDF only)')
        
        # Batch processing options
        parser.add_argument('-b', '--batch', type=str,
                          help='Batch mode: process all CSV files in the specified directory in parallel')
        parser.add_argument('-w', '--workers', type=int, default=cpu_count(),
                          help=f'Number of parallel workers for batch mode (default: {cpu_count()} = CPU count)')
        
        args = parser.parse_args()
        
        # Check if batch mode is requested
        if args.batch:
            # Batch mode: process all files in directory
            process_batch(args)
            return
        
        # If no input file provided, print help and exit
        if args.input is None:
            parser.print_help()
            sys.exit(0)
    
    # Read the multi-column EOS using our fancy new EOS class
    eos = EOS.from_file(args.input)
    
    print(f"Loaded EOS from {args.input}")
    print(f"  {eos.n_points} data points")
    print(f"  Columns: {', '.join(eos.colnames)}")
    
    # Create our solver object with high accuracy for good tidal deformability results!
    rtol = getattr(args, 'rtol', DEFAULT_RTOL)
    atol = getattr(args, 'atol', DEFAULT_ATOL)
    solver = TOVSolver(eos, r_max=args.rmax, dr=args.dr, rtol=rtol, atol=atol)
    
    # Also create tidal calculator for Lambda and k2!
    tidal_calc = TidalCalculator(solver)

    # Prepare an output folder
    out_folder = args.output
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # We'll create a single CSV with 1 line per star:
    # p_c, R, M, Lambda, k2, e(pc), plus other columns col2(pc)...
    base_name = os.path.splitext(os.path.basename(args.input))[0]
    
    # Generate the sequence of stars using our fancy solver
    print(f"\nSolving TOV + Tidal Deformability for {args.num_stars} central pressures...")
    
    # Get pressure range
    p_range = eos.get_pressure_range()
    p_min = max(p_range[0], 1e-15)
    p_max = p_range[1]
    central_pressures = np.logspace(np.log10(p_min), np.log10(p_max), args.num_stars)
    
    # Solve for each pressure - including tidal deformability!
    tidal_results = []
    for p_c in central_pressures:
        try:
            result = tidal_calc.compute(p_c)
            # Add p_c to the result dictionary
            result['p_c'] = p_c
            
            # Add central column values from EOS
            central_values = eos.get_all_values_at_pressure(p_c)
            for key, val in central_values.items():
                result[f'central_{key}'] = val
            
            tidal_results.append(result)
            if not args.quiet:
                M = result['M_solar']
                R = result['R']
                Lambda = result['Lambda']
                k2 = result['k2']
                print(f"p_c={p_c:.3e} => M={M:.4f} Msun, R={R:.2f} km, Lambda={Lambda:.2f}, k2={k2:.4f}")
        except Exception as e:
            if not args.quiet:
                print(f"Failed at p_c={p_c:.3e}: {e}")
    
    # Use our fancy tidal writer (has all the data: M, R, Lambda, k2)
    writer = TidalWriter(output_folder=out_folder)
    show_plot = not args.no_show and not args.no_plot
    csv_path, pdf_path = writer.write_results(tidal_results, base_name, show_plot=show_plot, save_png=args.save_png)
    
    if args.save_png:
        print("\n✓ Also saved PNG versions for README/web display")
    
    # Print some stats
    valid_results = [r for r in tidal_results if r['M_solar'] > 0.01]
    if valid_results:
        max_result = max(valid_results, key=lambda r: r['M_solar'])
        print(f"\nValid solutions: {len(valid_results)}/{len(tidal_results)}")
        print(f"Maximum mass: {max_result['M_solar']:.4f} Msun at R={max_result['R']:.2f} km")
        
        # Find star near 1.4 solar masses and print its tidal deformability!
        near_14 = min(valid_results, key=lambda r: abs(r['M_solar'] - 1.4))
        print(f"Near 1.4 Msun: M={near_14['M_solar']:.4f} Msun, R={near_14['R']:.2f} km")
        print(f"              Lambda={near_14['Lambda']:.2f}, k2={near_14['k2']:.4f}")

    print(f"\nWrote {len(tidal_results)} stars to: {csv_path}")
    if not args.no_plot:
        print(f"Saved M-R plot to: {pdf_path}")
    print("\nDone!\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import os
import sys

###############################################################################
# OH BOY OH BOY, WE HAVE OUR PHYSICAL CONSTANTS IN SI
###############################################################################
c0   = 299792458         # Speed of light in m/s
G    = 6.67408e-11       # Gravitational constant, m^3 / (kg*s^2)
qe   = 1.6021766208e-19  # Elementary charge in coulombs
hbar = 1.054571817e-34   # Reduced Planck constant in J*s

###############################################################################
# WE COMPUTE SOME DERIVED EXPRESSIONS, ACCORDING TO YOUR LIST:
# oh boy oh boy, let's do this carefully
###############################################################################

# 1) hbarcMeVfm = hbar * c0 / qe / (1.0e6 * 1.0e-15) ~ 197.327
hbarcMeVfm = hbar * c0 / qe / (1.0e6 * 1.0e-15)

# 2) cMeVfm3km2 = G * qe / (c0**4) * 1.0e57 ~ 1.32379*10^-6
cMeVfm3km2 = G * qe / (c0**4) * 1.0e57

# 3) cMeVfm3dynecm2 = 1.6021766208e33
cMeVfm3dynecm2 = 1.6021766208e33

# 4) cMeVfm3gcm3 = 1.7826619069e12
cMeVfm3gcm3 = 1.7826619069e12

###############################################################################
# OH BOY OH BOY, NOW THE FACTORS:
# (1) cMeVfm3km2/(hbarcMeVfm^3) => for MeV^-4 => code units => ~1.722898e-13
# (2) cMeVfm3km2               => for MeV*fm^-3 => code units => ~1.323790e-06
# (3) 'TODO' => fm^-4 => code
# (4) For CGS, we do separate:
#     pFactor = cMeVfm3km2/cMeVfm3dynecm2  ~8.262445e-40
#     eFactor = cMeVfm3km2/cMeVfm3gcm3    ~7.425915e-19
###############################################################################

factor_MeVneg4 = cMeVfm3km2 / (hbarcMeVfm**3)   # MeV^-4 => ~1.722898e-13
factor_MeVfm3  = 1.323790e-06                  # MeV*fm^-3 => ~1.323790e-06
factor_fmneg4  = 1.323790e-06*(hbarcMeVfm)  # fm^-4 => 'TODO'
pFactor_CGS    = cMeVfm3km2 / cMeVfm3dynecm2    # ~8.262445e-40
eFactor_CGS    = cMeVfm3km2 / cMeVfm3gcm3       # ~7.425915e-19


###############################################################################
# OH BOY OH BOY, NOW WE MAKE IT OBJECT ORIENTED!
###############################################################################

class EOSConverter:
    """
    oh boy oh boy! This class converts EOS data to TOV code units
    while keeping all the comedic style you know and love!
    """
    
    def __init__(self):
        """Initialize with our beautiful factors. oh boy oh boy!"""
        self.factor_MeVneg4 = factor_MeVneg4
        self.factor_MeVfm3 = factor_MeVfm3
        self.factor_fmneg4 = factor_fmneg4
        self.pFactor_CGS = pFactor_CGS
        self.eFactor_CGS = eFactor_CGS
    
    def print_factors(self):
        """
        Print numeric approximate factors for each system => TOV code units.
        oh boy oh boy, let's do it!
        """
        print("\n** Checking our derived factor expressions => TOV code units **\n")
        print(f"(1) MeV^-4 => factor ~ {self.factor_MeVneg4:.6e} ( ~1.722898e-13 )")
        print(f"(2) MeV*fm^-3 => factor ~ {self.factor_MeVfm3:.6e} ( ~1.323790e-06 )")
        print(f"(3) fm^-4 => 'TODO' => factor ~ {self.factor_fmneg4:.6e} ( placeholder )")

        print("\n(4) CGS => separate p,e factors => code units:")
        print(f"    p(dyn/cm^2) => pFactor= {self.pFactor_CGS:.6e} (~8.262445e-40)")
        print(f"    e(erg/cm^3) => eFactor= {self.eFactor_CGS:.6e} (~7.425915e-19)")
        print("\nOh boy oh boy, hopefully that clarifies the raw numeric factors!\n")
    
    def get_factors_for_system(self, choice):
        """
        Get pFactor and eFactor based on user choice (0..4).
        oh boy oh boy, returns (pFactor, eFactor, description)
        """
        if choice == "0":
            return 1.0, 1.0, "Already code => factor=1"
        elif choice == "1":
            return self.factor_MeVneg4, self.factor_MeVneg4, "MeV^-4 => code"
        elif choice == "2":
            return self.factor_MeVfm3, self.factor_MeVfm3, "MeV*fm^-3 => code"
        elif choice == "3":
            return self.factor_fmneg4, self.factor_fmneg4, "fm^-4 => code"
        elif choice == "4":
            return self.pFactor_CGS, self.eFactor_CGS, "CGS => separate p/e => code"
        else:
            return None, None, "Invalid choice, oh boy oh boy, no luck!"
    
    def read_csv_file(self, input_path, has_header):
        """
        Read CSV file and return (lines, header_cols, data_start_index, num_cols).
        oh boy oh boy, this handles the header detection!
        """
        with open(input_path, "r") as fin:
            lines = fin.readlines()
        
        if not lines:
            print(f"Oh boy oh boy, file is empty! Bailing out.")
            return None, None, None, None
        
        header_cols = None
        data_start_index = 0
        
        if has_header:
            # The first non-empty, non-comment line is presumably the header
            for i, line in enumerate(lines):
                line_strip = line.strip()
                if line_strip and not line_strip.startswith("#"):
                    header_cols = [col.strip() for col in line_strip.split(",")]
                    data_start_index = i + 1
                    break
        
        # Determine number of columns
        num_cols = 0
        if header_cols is not None:
            num_cols = len(header_cols)
        else:
            # Guess from first data line
            for i in range(data_start_index, len(lines)):
                row = lines[i].strip()
                if row and not row.startswith("#"):
                    num_cols = len(row.split(","))
                    break
        
        return lines, header_cols, data_start_index, num_cols
    
    def convert_and_write(self, input_path, output_path, pcol, ecol, pFactor, eFactor, 
                         system_desc, header_cols=None, data_start_index=0):
        """
        Convert the EOS file and write to output.
        oh boy oh boy, this does the actual work!
        """
        with open(input_path, "r") as fin:
            lines = fin.readlines()
        
        # Figure out num_cols
        num_cols = 0
        if header_cols is not None:
            num_cols = len(header_cols)
        else:
            for i in range(data_start_index, len(lines)):
                row = lines[i].strip()
                if row and not row.startswith("#"):
                    num_cols = len(row.split(","))
                    break
        
        if pcol < 0 or ecol < 0 or pcol >= num_cols or ecol >= num_cols:
            print("Oh boy oh boy, your chosen columns exceed the CSV's actual columns!")
            return 0
        
        # We'll create a "reorder" list of column indices:
        # pcol => 0, ecol => 1, then the rest
        reorder_indices = [pcol, ecol] + [i for i in range(num_cols) if i not in (pcol, ecol)]
        
        count = 0
        with open(output_path, "w") as fout:
            # Write a commented-out introduction line
            fout.write("# p(code_units), e(code_units) => first two columns, plus original columns afterward\n")
            fout.write(f"# system={system_desc}, pFactor={pFactor:e}, eFactor={eFactor:e}\n")
            
            # If we have a header, rename pcol/ecol and reorder
            if header_cols is not None:
                header_cols_copy = header_cols[:]
                header_cols_copy[pcol] = f"{header_cols_copy[pcol]} (code_units)"
                header_cols_copy[ecol] = f"{header_cols_copy[ecol]} (code_units)"
                reordered_header = [header_cols_copy[i] for i in reorder_indices]
                fout.write("# " + ",".join(reordered_header) + "\n")
            
            # Process data lines
            for i in range(data_start_index, len(lines)):
                line = lines[i].strip()
                if not line or line.startswith("#"):
                    continue
                
                cols = [x.strip() for x in line.split(",")]
                
                if len(cols) <= max(pcol, ecol):
                    continue
                
                try:
                    p_in = float(cols[pcol])
                    e_in = float(cols[ecol])
                except ValueError:
                    continue
                
                # Convert
                p_out = p_in * pFactor
                e_out = e_in * eFactor
                
                # Put them back
                cols[pcol] = f"{p_out:.6e}"
                cols[ecol] = f"{e_out:.6e}"
                
                # Now reorder them so pcol, ecol appear first
                reordered = [cols[idx] for idx in reorder_indices]
                fout.write(",".join(reordered) + "\n")
                count += 1
        
        return count


def main():
    """
    This script:
      - Reads from folder inputRaw/
      - Asks user for CSV filename (must exist in inputRaw/) OR accepts CLI args
      - prints your 4 factor expressions with approximate numeric values
      - asks user to choose 0..4 for input system
      - if CGS => we do separate factor for p,e
      - multiplies (p,e) by those => final TOV code units
      - reorders columns so p(code_units) is #1, e(code_units) is #2,
        then all other columns follow
      - writes the new CSV to folder inputCode/, with default name:
          "<original_filename>.csv"
      - comedic style included. oh boy oh boy!
    
    CLI Usage:
      python converter.py <input_file> <pcol> <ecol> <system> [output_file]
      where:
        input_file: filename in inputRaw/ (just the name, not full path)
        pcol: pressure column (1-based)
        ecol: energy column (1-based)  
        system: 0-4 (0=code, 1=MeV^-4, 2=MeV*fm^-3, 3=fm^-4, 4=CGS)
        output_file: optional output path (default: inputCode/<input_file>)
    """
    print("===== TOV CODE-UNITS: THE BIG 4 FACTORS EDITION! =====")
    
    # Create our converter object, oh boy oh boy!
    converter = EOSConverter()
    
    # Check if we have CLI arguments
    if len(sys.argv) >= 5:
        # CLI mode
        infile = sys.argv[1]
        pcol = int(sys.argv[2]) - 1  # Convert to 0-based
        ecol = int(sys.argv[3]) - 1  # Convert to 0-based
        choice = sys.argv[4]
        
        input_path = os.path.join("inputRaw", infile)
        
        if not os.path.isfile(input_path):
            print(f"Oh boy oh boy, cannot find '{infile}' in folder 'inputRaw'! Bailing out.")
            return
        
        # Default output path
        if len(sys.argv) >= 6:
            out_file = sys.argv[5]
        else:
            out_file = os.path.join("inputCode", infile)
        
        # Assume header exists (read it)
        has_header = True
        lines, header_cols, data_start_index, num_cols = converter.read_csv_file(input_path, has_header)
        if lines is None:
            return
        
        print(f"\n** CLI Mode **")
        print(f"Input: {infile}")
        print(f"Pressure column: {pcol+1} (1-based)")
        print(f"Energy column: {ecol+1} (1-based)")
        print(f"System choice: {choice}")
        print(f"Output: {out_file}")
        
    else:
        # Interactive mode
        converter.print_factors()
        
        # Prompt user for the input file, which must exist in 'inputRaw'
        infile = input("Enter CSV filename (from folder 'inputRaw'): ").strip()
        input_path = os.path.join("inputRaw", infile)
        
        if not os.path.isfile(input_path):
            print(f"Oh boy oh boy, cannot find '{infile}' in folder 'inputRaw'! Bailing out.")
            return
        
        # Ask user if the file has a header line (column names)
        has_header = input("\nDoes your CSV have a header line with column names? (y/n)? ").strip().lower()
        has_header = has_header.startswith("y")
        
        # Read the file
        lines, header_cols, data_start_index, num_cols = converter.read_csv_file(input_path, has_header)
        if lines is None:
            return
        
        if header_cols is not None:
            print("\nOh boy oh boy, here are your column names (1-based) => be careful!")
            for idx, colname in enumerate(header_cols, start=1):
                print(f"  {idx}) {colname}")
            print("Remember to pick your pressure and energy columns using these 1-based indices.\n")
        else:
            print("\nNo header line found (or user said 'no'). We'll just do raw columns.\n")
        
        # Next, ask for columns in comedic style
        print("** Next up: we need to know which columns hold pressure and energy density. **")
        print("But oh boy oh boy, heads up: we are using *1-based* indexing here!")
        print("If your pressure is in the first column, type '1'. If it's in the second column,")
        print("type '2', etc. Because apparently, 0-based indexing wasn't confusing enough.\n")
        
        try:
            pcol_str = input("Which column is pressure? (1-based)? ").strip()
            pcol = int(pcol_str) - 1
            ecol_str = input("Which column is energy density? (1-based)? ").strip()
            ecol = int(ecol_str) - 1
        except ValueError:
            print("Columns must be integers. oh boy oh boy!")
            return
        
        print("\nWe have 5 options for input system => final TOV code units:")
        print("  0) Already code units => factor=1")
        print("  1) MeV^-4 => cMeVfm3km2/(hbarc^3) ~ 1.722898e-13")
        print("  2) MeV*fm^-3 => cMeVfm3km2 ~ 1.323790e-06")
        print("  3) fm^-4 => 'TODO' => ( I am lazy )")
        print("  4) CGS => separate pFactor/eFactor => ~8.262445e-40 & ~7.425915e-19")
        
        choice = input("Which system (0..4)? ").strip()
        
        # Build the default output filename => "input_<original_name>.csv"
        out_default_name = f"{infile}"
        out_default_path = os.path.join("inputCode", out_default_name)
        
        out_file = input(f"Output file? (default: {out_default_path}): ").strip()
        if out_file == "":
            out_file = out_default_path
    
    # Common code for both modes
    pFactor, eFactor, system_desc = converter.get_factors_for_system(choice)
    if pFactor is None:
        print("Invalid choice, oh boy oh boy, no luck!")
        return
    
    print(f"\nReading '{infile}' from 'inputRaw/' => pcol={pcol+1}, ecol={ecol+1}, system={system_desc}")
    print(f"Applying pFactor= {pFactor:e}, eFactor= {eFactor:e} => final code units.")
    print("** Will reorder columns so that p and e appear as the FIRST TWO columns in the output! **\n")
    print(f"Writing new CSV => '{out_file}', oh boy oh boy!\n")
    
    # Read file again if in CLI mode (to get header info)
    if len(sys.argv) >= 5:
        lines, header_cols, data_start_index, num_cols = converter.read_csv_file(input_path, True)
    
    # Do the conversion!
    count = converter.convert_and_write(input_path, out_file, pcol, ecol, pFactor, eFactor,
                                       system_desc, header_cols, data_start_index)
    
    if count == 0:
        print("WARNING: no lines converted. oh boy oh boy, check your columns!\n")
    else:
        print(f"Done! Wrote {count} lines in code units to '{out_file}'.")
        print("Your p(code_units) is now the first column, e(code_units) is second,")
        print("and the rest follow. oh boy oh boy!\n")


if __name__ == "__main__":
    main()

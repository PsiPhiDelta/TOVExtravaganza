#!/usr/bin/env python3

import os

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
factor_fmneg4  = 9.999999e-11                  # fm^-4 => 'TODO'
pFactor_CGS    = cMeVfm3km2 / cMeVfm3dynecm2    # ~8.262445e-40
eFactor_CGS    = cMeVfm3km2 / cMeVfm3gcm3       # ~7.425915e-19

###############################################################################
# PRINT FOR THE USER
###############################################################################

def print_factors():
    """
    Print numeric approximate factors for each system => TOV code units.
    oh boy oh boy, let's do it!
    """
    print("\n** Checking our derived factor expressions => TOV code units **\n")
    print(f"(1) MeV^-4 => factor ~ {factor_MeVneg4:.6e} ( ~1.722898e-13 )")
    print(f"(2) MeV*fm^-3 => factor ~ {factor_MeVfm3:.6e} ( ~1.323790e-06 )")
    print(f"(3) fm^-4 => 'TODO' => factor ~ {factor_fmneg4:.6e} ( placeholder )")

    print("\n(4) CGS => separate p,e factors => code units:")
    print(f"    p(dyn/cm^2) => pFactor= {pFactor_CGS:.6e} (~8.262445e-40)")
    print(f"    e(erg/cm^3) => eFactor= {eFactor_CGS:.6e} (~7.425915e-19)")
    print("\nOh boy oh boy, hopefully that clarifies the raw numeric factors!\n")


def main():
    """
    This script:
      - Reads from folder inputRaw/
      - Asks user for CSV filename (must exist in inputRaw/)
      - prints your 4 factor expressions with approximate numeric values
      - asks user to choose 0..4 for input system
      - if CGS => we do separate factor for p,e
      - multiplies (p,e) by those => final TOV code units
      - reorders columns so p(code_units) is #1, e(code_units) is #2,
        then all other columns follow
      - writes the new CSV to folder inputCode/, with default name:
          "<original_filename>.csv"
      - comedic style included. oh boy oh boy!
    """
    print("===== TOV CODE-UNITS: THE BIG 4 FACTORS EDITION! =====")
    print_factors()

    # Prompt user for the input file, which must exist in 'inputRaw'
    infile = input("Enter CSV filename (from folder 'inputRaw'): ").strip()
    input_path = os.path.join("inputRaw", infile)

    if not os.path.isfile(input_path):
        print(f"Oh boy oh boy, cannot find '{infile}' in folder 'inputRaw'! Bailing out.")
        return

    # Ask user if the file has a header line (column names)
    has_header = input("\nDoes your CSV have a header line with column names? (y/n)? ").strip().lower()
    if has_header.startswith("y"):
        has_header = True
    else:
        has_header = False

    # We'll store header columns if needed
    header_cols = None

    # Read lines up front
    with open(input_path, "r") as fin:
        lines = fin.readlines()

    # If the file is empty, bail
    if not lines:
        print(f"Oh boy oh boy, '{infile}' is empty! Bailing out.")
        return

    data_start_index = 0
    if has_header:
        # The first non-empty, non-comment line is presumably the header
        for i, line in enumerate(lines):
            line_strip = line.strip()
            if line_strip and not line_strip.startswith("#"):
                header_cols = [col.strip() for col in line_strip.split(",")]
                data_start_index = i + 1
                break

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

    pFactor, eFactor = None, None
    system_desc = ""

    if choice == "0":
        pFactor = 1.0
        eFactor = 1.0
        system_desc = "Already code => factor=1"
    elif choice == "1":
        pFactor = factor_MeVneg4
        eFactor = factor_MeVneg4
        system_desc = "MeV^-4 => code"
    elif choice == "2":
        pFactor = factor_MeVfm3
        eFactor = factor_MeVfm3
        system_desc = "MeV*fm^-3 => code"
    elif choice == "3":
        pFactor = factor_fmneg4
        eFactor = factor_fmneg4
        system_desc = "fm^-4 => code"
    elif choice == "4":
        pFactor = pFactor_CGS
        eFactor = eFactor_CGS
        system_desc = "CGS => separate p/e => code"
    else:
        print("Invalid choice, oh boy oh boy, no luck!")
        return

    # Build the default output filename => "input_<original_name>.csv"
    out_default_name = f"{infile}"
    out_default_path = os.path.join("inputCode", out_default_name)

    out_file = input(f"Output file? (default: {out_default_path}): ").strip()
    if out_file == "":
        out_file = out_default_path

    print(f"\nReading '{infile}' from 'inputRaw/' => pcol={pcol+1}, ecol={ecol+1}, system={system_desc}")
    print(f"Applying pFactor= {pFactor:e}, eFactor= {eFactor:e} => final code units.")
    print("** Will reorder columns so that p and e appear as the FIRST TWO columns in the output! **\n")
    print(f"Writing new CSV => '{out_file}', oh boy oh boy!\n")

    # We'll create a "reorder" list of column indices:
    # pcol => 0, ecol => 1, then the rest
    num_cols = 0
    if header_cols is not None:
        num_cols = len(header_cols)
    else:
        # If no header, let's guess from the first data line that isn't comment
        for i in range(data_start_index, len(lines)):
            row = lines[i].strip()
            if row and not row.startswith("#"):
                num_cols = len(row.split(","))
                break

    if pcol < 0 or ecol < 0 or pcol >= num_cols or ecol >= num_cols:
        print("Oh boy oh boy, your chosen columns exceed the CSV's actual columns!")
        return

    reorder_indices = [pcol, ecol] + [i for i in range(num_cols) if i not in (pcol, ecol)]

    count = 0
    with open(out_file, "w") as fout:
        # Write a commented-out introduction line
        fout.write("# p(code_units), e(code_units) => first two columns, plus original columns afterward\n")
        fout.write(f"# system={system_desc}, pFactor={pFactor:e}, eFactor={eFactor:e}\n")

        # If we have a header, rename pcol/ecol and reorder
        if header_cols is not None:
            header_cols[pcol] = f"{header_cols[pcol]} (code_units)"
            header_cols[ecol] = f"{header_cols[ecol]} (code_units)"

            reordered_header = [header_cols[i] for i in reorder_indices]
            fout.write("# " + ",".join(reordered_header) + "\n")

        # Process data lines
        for i in range(data_start_index, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith("#"):
                # Skip empty/comment lines
                continue

            cols = [x.strip() for x in line.split(",")]

            # If row has fewer columns than needed, skip
            if len(cols) <= max(pcol, ecol):
                continue

            try:
                p_in = float(cols[pcol])
                e_in = float(cols[ecol])
            except ValueError:
                # Possibly can't convert to float
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

    if count == 0:
        print("WARNING: no lines converted. oh boy oh boy, check your columns!\n")
    else:
        print(f"Done! Wrote {count} lines in code units to '{out_file}'.")
        print("Your p(code_units) is now the first column, e(code_units) is second,")
        print("and the rest follow. oh boy oh boy!\n")


if __name__ == "__main__":
    main()

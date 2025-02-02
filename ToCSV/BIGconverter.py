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

# 2) cMeVfm3km2 = G * qe / (c0**4) * 1.0e57 ~ 1.32379e-06
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


def convert_file(
    infile_path,
    has_header,
    pcol,
    ecol,
    pFactor,
    eFactor,
    system_desc,
    out_file
):
    """
    Convert a single CSV file (infile_path) into code units and write to out_file.
    """
    # Read lines up front
    with open(infile_path, "r") as fin:
        lines = fin.readlines()

    if not lines:
        print(f"Oh boy oh boy, '{infile_path}' is empty! Skipping.")
        return 0

    # We'll store header columns if needed
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
        # If no header, let's guess from the first data line that isn't comment
        for i in range(data_start_index, len(lines)):
            row = lines[i].strip()
            if row and not row.startswith("#"):
                num_cols = len(row.split(","))
                break

    # Check pcol/ecol
    if pcol < 0 or ecol < 0 or pcol >= num_cols or ecol >= num_cols:
        print(f"** WARNING: For file '{infile_path}', chosen pcol/ecol exceed #cols. Skipping! **")
        return 0

    # We'll create a "reorder" list of column indices: pcol => 0, ecol => 1, then the rest
    reorder_indices = [pcol, ecol] + [i for i in range(num_cols) if i not in (pcol, ecol)]

    # Make sure output folder(s) exist
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    count = 0
    with open(out_file, "w") as fout:
        # Write a commented-out introduction line
        fout.write("# p(code_units), e(code_units) => first two columns, plus original columns afterward\n")
        fout.write(f"# system={system_desc}, pFactor={pFactor:e}, eFactor={eFactor:e}\n")

        # If we have a header, rename pcol/ecol and reorder
        if header_cols is not None:
            # We'll do an inline rename so the user sees something like "pressure (code_units)"
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

    return count


def main():
    """
    This script:
      - Asks user for folder containing CSV files (all will be processed).
      - Asks for presence of header line
      - prints your 4 factor expressions with approximate numeric values
      - asks user to choose 0..4 for input system
      - if CGS => we do separate factor for p,e
      - multiplies (p,e) by those => final TOV code units
      - reorders columns so p(code_units) is #1, e(code_units) is #2,
        then all other columns follow
      - writes each new CSV to folder 'outputCSCtocode/', with same base filename.
      - comedic style included. oh boy oh boy!
    """
    print("===== TOV CODE-UNITS: THE BIG 4 FACTORS EDITION! =====")
    print_factors()

    # Prompt user for folder containing CSV files
    folder_in = input("Enter the folder containing your CSV files: ").strip()
    if not os.path.isdir(folder_in):
        print(f"Oh boy oh boy, '{folder_in}' is not a valid directory! Bailing out.")
        return

    # Ask user if the file(s) have a header line (column names)
    has_header_input = input("\nDo these CSVs have a header line with column names? (y/n)? ").strip().lower()
    has_header = has_header_input.startswith("y")

    print("\nOh boy oh boy, let's define which columns hold pressure and energy density.")
    print("Heads up: we are using *1-based* indexing here!\n")
    try:
        pcol_str = input("Which column is pressure? (1-based)? ").strip()
        pcol = int(pcol_str) - 1
        ecol_str = input("Which column is energy density? (1-based)? ").strip()
        ecol = int(ecol_str) - 1
    except ValueError:
        print("Columns must be integers. oh boy oh boy!")
        return

    # Let user choose the system => code units
    print("\nWe have 5 options for input system => final TOV code units:")
    print("  0) Already code units => factor=1")
    print("  1) MeV^-4 => cMeVfm3km2/(hbarc^3) ~ 1.722898e-13")
    print("  2) MeV*fm^-3 => cMeVfm3km2 ~ 1.323790e-06")
    print("  3) fm^-4 => 'TODO' => ( I am lazy )")
    print("  4) CGS => separate pFactor/eFactor => ~8.262445e-40 & ~7.425915e-19")

    choice = input("Which system (0..4)? ").strip()

    pFactor_out, eFactor_out = None, None
    system_desc = ""

    if choice == "0":
        pFactor_out = 1.0
        eFactor_out = 1.0
        system_desc = "Already code => factor=1"
    elif choice == "1":
        pFactor_out = factor_MeVneg4
        eFactor_out = factor_MeVneg4
        system_desc = "MeV^-4 => code"
    elif choice == "2":
        pFactor_out = factor_MeVfm3
        eFactor_out = factor_MeVfm3
        system_desc = "MeV*fm^-3 => code"
    elif choice == "3":
        pFactor_out = factor_fmneg4
        eFactor_out = factor_fmneg4
        system_desc = "fm^-4 => code"
    elif choice == "4":
        pFactor_out = pFactor_CGS
        eFactor_out = eFactor_CGS
        system_desc = "CGS => separate p/e => code"
    else:
        print("Invalid choice, oh boy oh boy, no luck!")
        return

    print(f"\nYour choice => {system_desc}, pFactor= {pFactor_out:e}, eFactor= {eFactor_out:e}")
    print("** We will reorder columns so that p and e appear as the FIRST TWO columns in each output. **")

    # Create output folder if needed
    out_folder = "outputCSCtocode"
    os.makedirs(out_folder, exist_ok=True)

    # Now loop over every file in 'folder_in' that ends with .csv
    files = sorted(
        f for f in os.listdir(folder_in)
        if f.lower().endswith(".csv") and os.path.isfile(os.path.join(folder_in, f))
    )

    if not files:
        print(f"No CSV files found in '{folder_in}'. Bailing out.")
        return

    total_files = 0
    total_lines = 0

    for csv_file in files:
        infile_path = os.path.join(folder_in, csv_file)
        outfile_path = os.path.join(out_folder, csv_file)

        print(f"\n===== Processing file: {csv_file} =====")
        print(f"Reading '{infile_path}' => pcol={pcol+1}, ecol={ecol+1}, system={system_desc}")

        count = convert_file(
            infile_path = infile_path,
            has_header  = has_header,
            pcol        = pcol,
            ecol        = ecol,
            pFactor     = pFactor_out,
            eFactor     = eFactor_out,
            system_desc = system_desc,
            out_file    = outfile_path
        )

        if count == 0:
            print(f"WARNING: no lines converted in '{csv_file}'. oh boy oh boy, check your columns!")
        else:
            print(f"Done! Wrote {count} lines in code units to '{outfile_path}'.")
            total_files += 1
            total_lines += count

    print(f"\nFinished processing. We converted {total_lines} lines across {total_files} files.")
    print("Your p(code_units) is now the first column, e(code_units) is second, the rest follow. Oh boy oh boy!\n")


if __name__ == "__main__":
    main()

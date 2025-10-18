#!/usr/bin/env python3
"""
🌟 TOV EXTRAVAGANZA WIZARD 🌟
Oh boy oh boy! The ultimate interactive wrapper for all your neutron star needs!

This script will guide you through:
  1. Converting EOS to code units (if needed)
  2. Computing Mass-Radius curves + Tidal properties
  3. Generating internal structure profiles
  
Just sit back, answer some questions, and watch the magic happen!
"""

import os
import sys
import subprocess

###############################################################################
# OH BOY OH BOY, LET'S START THE SHOW!
###############################################################################

def print_banner():
    """Print a beautiful banner because why not?"""
    print("\n" + "="*70)
    print("  🌟  W E L C O M E   T O   T O V   E X T R A V A G A N Z A  🌟")
    print("="*70)
    print("\n  Your one-stop shop for neutron star calculations!")
    print("  Oh boy oh boy, let's do some SCIENCE!\n")
    print("="*70 + "\n")


def list_eos_files(folder):
    """List all CSV files in a folder. Oh boy oh boy, choices!"""
    if not os.path.exists(folder):
        return []
    
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    return sorted(files)


def ask_yes_no(question, default='y'):
    """Ask a yes/no question. Oh boy oh boy, decisions!"""
    choices = 'Y/n' if default.lower() == 'y' else 'y/N'
    while True:
        response = input(f"{question} [{choices}]: ").strip().lower()
        if response == '':
            response = default.lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("  Please answer 'y' or 'n'. Oh boy oh boy, try again!")


def choose_from_list(items, prompt="Choose an item"):
    """Let user pick from a list. Oh boy oh boy, so many options!"""
    if not items:
        return None
    
    print(f"\n{prompt}:")
    for i, item in enumerate(items, 1):
        print(f"  {i}) {item}")
    
    while True:
        try:
            choice = input(f"\nEnter number (1-{len(items)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            else:
                print(f"  Oh boy oh boy, pick a number between 1 and {len(items)}!")
        except ValueError:
            print("  That's not a number! Oh boy oh boy, try again!")


def run_command(cmd_list, description):
    """Run a command and show output. Oh boy oh boy, running things!"""
    print(f"\n{'─'*70}")
    print(f"🚀 {description}")
    print(f"{'─'*70}\n")
    
    cmd_str = ' '.join(cmd_list)
    print(f"Running: {cmd_str}\n")
    
    result = subprocess.run(cmd_list, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n⚠️  Oh boy oh boy, something went wrong! Return code: {result.returncode}")
        return False
    else:
        print(f"\n✓ Done!")
        return True


def main():
    """The main wizard. Oh boy oh boy, here we go!"""
    
    print_banner()
    
    # Step 1: Check if we need to convert EOS
    print("STEP 1: Equation of State Setup")
    print("─" * 70)
    
    raw_files = list_eos_files('inputRaw')
    code_files = list_eos_files('inputCode')
    
    if code_files:
        print("\nI found these EOS files already in code units:")
        for f in code_files:
            print(f"  ✓ {f}")
        
        if ask_yes_no("\nDo you want to use one of these?", default='y'):
            eos_file = choose_from_list(code_files, "Which EOS file do you want to use?")
            if eos_file:
                eos_path = os.path.join('inputCode', eos_file)
            else:
                print("\nOh boy oh boy, no file selected! Exiting.")
                return
        else:
            # User wants to convert a new EOS
            if raw_files:
                print("\nOkay! Let's convert a raw EOS file.")
                print("Oh boy oh boy, we'll run the converter for you!")
                
                if ask_yes_no("Use converter in CLI mode (faster) or interactive mode?", default='y'):
                    # CLI mode would require more input, just run interactive
                    print("\nRunning interactive converter...")
                else:
                    print("\nRunning interactive converter...")
                
                run_command(['python', 'converter.py'], "EOS Converter")
                
                # Ask user what the output file was
                code_files = list_eos_files('inputCode')
                eos_file = choose_from_list(code_files, "Which converted file do you want to use?")
                if eos_file:
                    eos_path = os.path.join('inputCode', eos_file)
                else:
                    print("\nOh boy oh boy, no file found! Exiting.")
                    return
            else:
                print("\nOh boy oh boy! No EOS files found in inputRaw/ or inputCode/!")
                print()
                print("💡 First time? Get example files with:")
                print("   tovx-demo")
                print()
                print("Or add your own EOS file to inputRaw/ folder.")
                return
    elif raw_files:
        print("\nNo converted EOS files found, but I found raw files:")
        for f in raw_files:
            print(f"  • {f}")
        
        print("\nOh boy oh boy! Let's convert one to code units first!")
        run_command(['python', '-m', 'tovextravaganza.converter'], "EOS Converter")
        
        code_files = list_eos_files('inputCode')
        eos_file = choose_from_list(code_files, "Which converted file do you want to use?")
        if eos_file:
            eos_path = os.path.join('inputCode', eos_file)
        else:
            print("\nOh boy oh boy, no file found! Exiting.")
            return
    else:
        print("\nOh boy oh boy! No EOS files found anywhere!")
        print()
        print("💡 First time? Get example files with:")
        print("   tovx-demo")
        print()
        print("Or add your own EOS file to inputRaw/ or inputCode/ folder.")
        return
    
    print(f"\n✓ Using EOS file: {eos_path}")
    
    # Step 2: Compute Mass-Radius + Tidal
    print("\n\nSTEP 2: Mass-Radius & Tidal Deformability")
    print("─" * 70)
    
    if ask_yes_no("Compute M-R curve and tidal properties?", default='y'):
        print("\nHow many stars do you want to compute?")
        print("  (More stars = smoother curve, but slower)")
        print("  Default is 200. Oh boy oh boy!")
        
        num_stars = input("\nNumber of stars [200]: ").strip()
        num_stars = num_stars if num_stars else "200"
        
        cmd = ['python', '-m', 'tovextravaganza.tov', eos_path, '-n', num_stars, '--no-show']
        
        if run_command(cmd, f"Computing {num_stars} neutron stars"):
            print("\n✓ Results saved to export/stars/")
    
    # Step 3: Radial Profiles
    print("\n\nSTEP 3: Internal Structure Profiles")
    print("─" * 70)
    
    if ask_yes_no("Generate radial profiles (M(r), p(r))?", default='y'):
        print("\nHow do you want to select stars?")
        print("  1) Automatic: Generate N profiles across pressure range")
        print("  2) By Mass: Generate profiles for specific masses (e.g., 1.4 M☉)")
        print("  3) By Radius: Generate profiles for specific radii (e.g., 12 km)")
        
        choice = input("\nChoice [1]: ").strip()
        choice = choice if choice else "1"
        
        cmd = ['python', '-m', 'tovextravaganza.radial', eos_path]
        
        if choice == "1":
            num_profiles = input("\nHow many profiles? [10]: ").strip()
            num_profiles = num_profiles if num_profiles else "10"
            cmd.extend(['-n', num_profiles])
            description = f"Generating {num_profiles} radial profiles"
        
        elif choice == "2":
            masses_str = input("\nEnter masses in M☉ (comma-separated, e.g., 1.4,2.0): ").strip()
            if masses_str:
                masses = [m.strip() for m in masses_str.split(',')]
                for m in masses:
                    cmd.extend(['-M', m])
                description = f"Generating profiles for masses: {masses_str} M☉"
            else:
                print("  No masses provided, using default...")
                cmd.extend(['-n', '10'])
                description = "Generating 10 radial profiles (default)"
        
        elif choice == "3":
            radii_str = input("\nEnter radii in km (comma-separated, e.g., 12,13): ").strip()
            if radii_str:
                radii = [r.strip() for r in radii_str.split(',')]
                for r in radii:
                    cmd.extend(['-R', r])
                description = f"Generating profiles for radii: {radii_str} km"
            else:
                print("  No radii provided, using default...")
                cmd.extend(['-n', '10'])
                description = "Generating 10 radial profiles (default)"
        else:
            print("  Invalid choice. Oh boy oh boy, using default...")
            cmd.extend(['-n', '10'])
            description = "Generating 10 radial profiles (default)"
        
        if run_command(cmd, description):
            print("\n✓ Results saved to export/radial_profiles/")
    
    # All done!
    print("\n\n" + "="*70)
    print("  🎉  A L L   D O N E !  🎉")
    print("="*70)
    print("\nYour results are in the export/ folder:")
    print("  📊 export/stars/          - M-R curves and tidal properties")
    print("  📈 export/radial_profiles/ - Internal structure profiles")
    print("\nOh boy oh boy, we did it! Science complete! 🚀\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOh boy oh boy, interrupted! See you next time! 👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nOh boy oh boy, an error occurred: {e}")
        print("Don't worry, you can still run the scripts manually!")
        print("  python -m tovextravaganza.tov inputCode/<your_eos>.csv")
        print("  python -m tovextravaganza.radial inputCode/<your_eos>.csv\n")
        sys.exit(1)


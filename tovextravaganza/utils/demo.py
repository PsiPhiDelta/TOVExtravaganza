"""
TOV Extravaganza Demo Setup
Downloads/copies example EOS files to your current directory
"""

import os
import shutil
import sys
from pathlib import Path

def main():
    """
    Copy example EOS files to current directory.
    Creates inputCode/ and inputRaw/ folders with example files.
    """
    
    print("========================================")
    print("TOV Extravaganza Demo Setup")
    print("========================================")
    print()
    
    # Find package installation directory
    try:
        import tovextravaganza
        # The package is installed, but we need to find the data files
        # They're in the same directory as tov.py, radial.py, etc.
        package_dir = Path(__file__).parent
    except:
        # Running from source
        package_dir = Path(__file__).parent
    
    # Define source directories (where example files are)
    source_input_code = package_dir / "inputCode"
    source_input_raw = package_dir / "inputRaw"
    
    # Define destination directories (current working directory)
    dest_input_code = Path.cwd() / "inputCode"
    dest_input_raw = Path.cwd() / "inputRaw"
    
    # Check if source files exist
    if not source_input_code.exists():
        print("Example files not found in package installation.")
        print()
        print("Downloading from GitHub instead...")
        print()
        download_from_github()
        return
    
    # Create destination directories
    dest_input_code.mkdir(exist_ok=True)
    dest_input_raw.mkdir(exist_ok=True)
    
    # Check if we're already in the source directory
    if source_input_code.resolve() == dest_input_code.resolve():
        print("Already in the source directory!")
        print()
        print("Files available:")
        print("  * inputCode/test.csv   - Simple test EOS")
        print("  * inputCode/hsdd2.csv  - HS(DD2) realistic EOS")
        print("  * inputCode/csc.csv    - Color-superconducting EOS")
        print()
        print("Try them out:")
        print("  tovx inputCode/hsdd2.csv")
        print("  tovx-wizard")
        print()
        return
    
    print(f"Copying example files to: {Path.cwd()}")
    print()
    
    # Copy files (including subdirectories)
    files_copied = 0
    
    for src_dir, dest_dir, label in [
        (source_input_code, dest_input_code, "inputCode"),
        (source_input_raw, dest_input_raw, "inputRaw")
    ]:
        if src_dir.exists():
            for file in src_dir.glob("**/*.csv"):
                # Calculate relative path to preserve directory structure
                rel_path = file.relative_to(src_dir)
                dest_file = dest_dir / rel_path
                
                if file.resolve() != dest_file.resolve():  # Skip if same file
                    # Create subdirectories if needed
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest_file)
                    print(f"  [OK] {label}/{rel_path}")
                    files_copied += 1
    
    print()
    print(f"========================================")
    print(f"Copied {files_copied} example files!")
    print(f"========================================")
    print()
    print("Files available:")
    print("  * inputCode/test.csv   - Simple test EOS")
    print("  * inputCode/hsdd2.csv  - HS(DD2) realistic EOS")
    print("  * inputCode/csc.csv    - Color-superconducting EOS")
    print("  * inputCode/Batch/     - 6 batch EOS files (CSC + RGNJL series)")
    print("  * inputRaw/batch/      - Raw versions for unit conversion tutorials")
    print()
    print("Try them out:")
    print("  tovx inputCode/hsdd2.csv")
    print("  tovx-radial inputCode/hsdd2.csv -M 1.4")
    print("  tovx --batch inputCode/Batch/")
    print("  tovx-wizard")
    print()
    print("Oh boy oh boy, ready to go!")
    print()


def download_from_github():
    """
    Download example files from GitHub if package files not found.
    """
    import urllib.request
    
    base_url = "https://raw.githubusercontent.com/PsiPhiDelta/TOVExtravaganza/main"
    
    files = [
        ("inputCode/test.csv", "inputCode"),
        ("inputCode/hsdd2.csv", "inputCode"),
        ("inputCode/csc.csv", "inputCode"),
        ("inputRaw/test.csv", "inputRaw"),
        ("inputRaw/hsdd2.csv", "inputRaw"),
        ("inputRaw/csc.csv", "inputRaw"),
        # Batch files for batch processing tutorials
        ("inputRaw/batch/CSC_v0.70d1.45.csv", "inputRaw/batch"),
        ("inputRaw/batch/CSC_v0.80d1.50.csv", "inputRaw/batch"),
        ("inputRaw/batch/CSC_v0.85d1.50.csv", "inputRaw/batch"),
        ("inputRaw/batch/RGNJL_v0.70d1.45.csv", "inputRaw/batch"),
        ("inputRaw/batch/RGNJL_v0.80d1.50.csv", "inputRaw/batch"),
        ("inputRaw/batch/RGNJL_v0.85d1.50.csv", "inputRaw/batch"),
        ("inputCode/Batch/CSC_v0.70d1.45.csv", "inputCode/Batch"),
        ("inputCode/Batch/CSC_v0.80d1.50.csv", "inputCode/Batch"),
        ("inputCode/Batch/CSC_v0.85d1.50.csv", "inputCode/Batch"),
        ("inputCode/Batch/RGNJL_v0.70d1.45.csv", "inputCode/Batch"),
        ("inputCode/Batch/RGNJL_v0.80d1.50.csv", "inputCode/Batch"),
        ("inputCode/Batch/RGNJL_v0.85d1.50.csv", "inputCode/Batch"),
    ]
    
    # Create directories
    Path("inputCode").mkdir(exist_ok=True)
    Path("inputRaw").mkdir(exist_ok=True)
    Path("inputRaw/batch").mkdir(parents=True, exist_ok=True)
    Path("inputCode/Batch").mkdir(parents=True, exist_ok=True)
    
    print("Downloading example files...")
    print()
    
    for file_path, folder in files:
        url = f"{base_url}/{file_path}"
        dest = Path(file_path)
        
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"  [OK] {file_path}")
        except Exception as e:
            print(f"  [FAIL] {file_path} - {e}")
    
    print()
    print("========================================")
    print("Example files downloaded!")
    print("========================================")
    print()
    print("Files available:")
    print("  * inputCode/test.csv, hsdd2.csv, csc.csv")
    print("  * inputCode/Batch/ - 6 batch EOS files")
    print("  * inputRaw/ - Raw versions")
    print()
    print("Try them out:")
    print("  tovx inputCode/hsdd2.csv")
    print("  tovx --batch inputCode/Batch/")
    print("  tovx-wizard")
    print()


if __name__ == "__main__":
    main()


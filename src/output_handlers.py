"""
Output Handlers for TOV Results
Handles CSV writing and plotting
"""
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


class MassRadiusWriter:
    """Writes mass-radius results to CSV and generates plots."""
    
    def __init__(self, output_folder="export/MR"):
        """
        Initialize writer.
        
        Parameters:
        -----------
        output_folder : str
            Output directory
        """
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    def write_stars(self, stars, base_name):
        """
        Write star sequence to CSV and generate M-R plot.
        
        Parameters:
        -----------
        stars : list of NeutronStar
            Star solutions
        base_name : str
            Base filename (without extension)
            
        Returns:
        --------
        str, str
            Paths to CSV and PDF files
        """
        out_csv = os.path.join(self.output_folder, f"{base_name}_stars.csv")
        out_pdf = os.path.join(self.output_folder, f"{base_name}.pdf")
        
        # Get extra columns
        if len(stars) > 0:
            extra_cols = [c for c in stars[0].eos.colnames if c != "p"]
        else:
            extra_cols = []
        
        header = ["p_c", "R", "M"] + [f"{c}(pc)" for c in extra_cols]
        
        with open(out_csv, "w", encoding="utf-8") as f:
            f.write(",".join(header) + "\n")
            
            for star in stars:
                extras = star.interpolate_eos_at_center()
                row_data = [star.central_pressure, star.radius, star.mass_solar]
                row_data += [extras.get(c, 0.0) for c in extra_cols]
                row_str = ",".join(f"{x:.6e}" for x in row_data)
                f.write(row_str + "\n")
        
        # Generate plot (only valid stars)
        valid_stars = [s for s in stars if s.is_valid()]
        if valid_stars:
            R_list = [s.radius for s in valid_stars]
            M_list = [s.mass_solar for s in valid_stars]
            
            plt.figure()
            plt.plot(R_list, M_list, "o-", label="TOV solutions")
            plt.xlabel("R (code units)")
            plt.ylabel("M (solar masses)")
            plt.title(f"M(R) from {base_name}")
            plt.grid(True)
            plt.legend()
            plt.savefig(out_pdf)
            plt.close()
        
        return out_csv, out_pdf


class TidalWriter:
    """Writes tidal deformability results to CSV and generates plots."""
    
    def __init__(self, output_folder="export/MR"):
        """Initialize tidal writer."""
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    def write_results(self, results, base_name):
        """
        Write tidal results to CSV and generate plots.
        
        Parameters:
        -----------
        results : list of dict
            Tidal calculation results
        base_name : str
            Base filename
            
        Returns:
        --------
        str, str
            Paths to CSV and PDF files
        """
        out_csv = os.path.join(self.output_folder, f"{base_name}_tidal.csv")
        out_pdf = os.path.join(self.output_folder, f"{base_name}_tidal.pdf")
        
        # Write CSV
        with open(out_csv, "w", encoding="utf-8") as f:
            f.write("p_c,R,M_code,M_solar,Lambda,k2\n")
            
            for res in results:
                f.write(f"{res['p_c']:.6e},{res['R']:.6e},{res['M_code']:.6e},"
                       f"{res['M_solar']:.6e},{res['Lambda']:.6e},{res['k2']:.6e}\n")
        
        # Filter valid results for plotting
        valid = [r for r in results if r['M_solar'] > 0.01]
        
        if len(valid) > 0:
            M_arr = np.array([r['M_solar'] for r in valid])
            Lambda_arr = np.array([r['Lambda'] for r in valid])
            k2_arr = np.array([r['k2'] for r in valid])
            
            # Create plots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Plot 1: Lambda vs M
            ax1.plot(M_arr, Lambda_arr, 'o-', markersize=4)
            ax1.set_xlabel('Mass (solar masses)')
            ax1.set_ylabel('Dimensionless Tidal Deformability Lambda')
            ax1.set_title(f'Tidal Deformability - {base_name}')
            ax1.grid(True, alpha=0.3)
            ax1.set_yscale('log')
            
            # Plot 2: k2 vs M
            ax2.plot(M_arr, k2_arr, 's-', markersize=4, color='orange')
            ax2.set_xlabel('Mass (solar masses)')
            ax2.set_ylabel('Tidal Love Number k2')
            ax2.set_title(f'Love Number - {base_name}')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(out_pdf, dpi=150)
            plt.close()
        
        return out_csv, out_pdf
    
    @staticmethod
    def interpolate_at_mass(results, target_mass=1.4):
        """
        Interpolate tidal properties at a specific mass.
        
        Parameters:
        -----------
        results : list of dict
            Tidal results
        target_mass : float
            Target mass in solar masses
            
        Returns:
        --------
        dict or None
            Interpolated values at target mass
        """
        valid = [r for r in results if r['M_solar'] > 0.1]
        if len(valid) < 2:
            return None
        
        M_arr = np.array([r['M_solar'] for r in valid])
        
        if M_arr.min() <= target_mass <= M_arr.max():
            Lambda_arr = np.array([r['Lambda'] for r in valid])
            k2_arr = np.array([r['k2'] for r in valid])
            R_arr = np.array([r['R'] for r in valid])
            
            interp_Lambda = interp1d(M_arr, Lambda_arr, kind='linear')
            interp_k2 = interp1d(M_arr, k2_arr, kind='linear')
            interp_R = interp1d(M_arr, R_arr, kind='linear')
            
            return {
                'M': target_mass,
                'R': float(interp_R(target_mass)),
                'Lambda': float(interp_Lambda(target_mass)),
                'k2': float(interp_k2(target_mass))
            }
        
        return None


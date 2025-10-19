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
    
    def __init__(self, output_folder="export/stars"):
        """Initialize tidal writer."""
        self.output_folder = output_folder
        self.csv_folder = os.path.join(output_folder, "csv")
        self.plot_folder = os.path.join(output_folder, "plots")
        if not os.path.exists(self.csv_folder):
            os.makedirs(self.csv_folder)
        if not os.path.exists(self.plot_folder):
            os.makedirs(self.plot_folder)
    
    def write_results(self, results, base_name, show_plot=True, save_png=False):
        """
        Write tidal results to CSV and generate plots.
        
        Parameters:
        -----------
        results : list of dict
            Tidal calculation results
        base_name : str
            Base filename
        save_png : bool
            If True, also save PNG versions (default: False)
            
        Returns:
        --------
        str, str
            Paths to CSV and PDF files
        """
        out_csv = os.path.join(self.csv_folder, f"{base_name}.csv")
        out_pdf = os.path.join(self.plot_folder, f"{base_name}.pdf")
        
        # Write CSV (filter out unphysical stars at R_max and low mass)
        with open(out_csv, "w", encoding="utf-8") as f:
            # Determine all columns dynamically
            if results:
                # Get all keys from first result
                all_keys = list(results[0].keys())
                
                # Define standard columns in order
                standard_cols = ['p_c', 'R', 'M_code', 'M_solar', 'Lambda', 'k2']
                
                # Find additional columns (those starting with 'central_')
                central_cols = [k for k in all_keys if k.startswith('central_')]
                
                # Combine: standard first, then central columns
                all_output_cols = standard_cols + central_cols
                
                # Write header
                f.write(','.join(all_output_cols) + '\n')
            else:
                # Fallback if no results
                f.write("p_c,R,M_code,M_solar,Lambda,k2\n")
                all_output_cols = ['p_c', 'R', 'M_code', 'M_solar', 'Lambda', 'k2']
            
            count = 0
            for res in results:
                # Skip stars that hit r_max (unphysical) or have very low mass
                if res['R'] < 99.0 and res['M_solar'] > 0.05:
                    # Write values for all columns
                    values = []
                    for col in all_output_cols:
                        val = res.get(col, '')
                        # Format numeric values, keep strings as-is
                        if isinstance(val, (int, float, np.number)):
                            values.append(f"{val:.6e}")
                        else:
                            values.append(str(val))
                    f.write(','.join(values) + '\n')
                    count += 1
        
        print(f"  Filtered: kept {count}/{len(results)} physical solutions (R < 99 km, M > 0.05 Msun)")
        
        # Filter valid results for plotting (same as CSV filter)
        valid = [r for r in results if r['M_solar'] > 0.05 and r['R'] < 99.0]
        
        if len(valid) > 0:
            M_arr = np.array([r['M_solar'] for r in valid])
            R_arr = np.array([r['R'] for r in valid])
            Lambda_arr = np.array([r['Lambda'] for r in valid])
            k2_arr = np.array([r['k2'] for r in valid])
            
            # Create plots - 3 panels: M-R, Lambda(M), k2(M)
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
            
            # Plot 1: M-R curve (the classic!)
            ax1.plot(R_arr, M_arr, 'o-', markersize=4)
            ax1.set_xlabel('Radius (km)', fontsize=12)
            ax1.set_ylabel('Mass (solar masses)', fontsize=12)
            ax1.set_title(f'Mass-Radius - {base_name}', fontsize=13)
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Lambda vs M
            ax2.plot(M_arr, Lambda_arr, 'o-', markersize=4, color='red', label='EoS prediction')
            
            # Add GW170817 constraint at 1.4 M☉
            # Constraint: Λ(1.4 M☉) = 190^{+390}_{-120} (90% credible interval)
            # Simplified: Λ ≈ 300 ± 200 with upper limit ~800
            M_gw = 1.4
            Lambda_gw_central = 300
            Lambda_gw_lower = 70   # 300 - 230
            Lambda_gw_upper = 580  # Conservative upper limit
            
            ax2.errorbar(M_gw, Lambda_gw_central, 
                        yerr=[[Lambda_gw_central - Lambda_gw_lower], 
                              [Lambda_gw_upper - Lambda_gw_central]],
                        fmt='*', markersize=12, color='blue', capsize=8, 
                        linewidth=2, label='GW170817 (1.4 M☉)')
            
            ax2.set_xlabel('Mass (solar masses)', fontsize=12)
            ax2.set_ylabel('Tidal Deformability Λ', fontsize=12)
            ax2.set_title(f'Tidal Deformability - {base_name}', fontsize=13)
            ax2.grid(True, alpha=0.3)
            ax2.set_yscale('log')
            ax2.legend(fontsize=10)
            
            # Plot 3: k2 vs M
            ax3.plot(M_arr, k2_arr, 's-', markersize=4, color='green')
            ax3.set_xlabel('Mass (solar masses)', fontsize=12)
            ax3.set_ylabel('Love Number k₂', fontsize=12)
            ax3.set_title(f'Love Number - {base_name}', fontsize=13)
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(out_pdf, dpi=150)
            if save_png:
                out_png = out_pdf.replace('.pdf', '.png')
                plt.savefig(out_png, dpi=150)
            if show_plot:
                plt.show()
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


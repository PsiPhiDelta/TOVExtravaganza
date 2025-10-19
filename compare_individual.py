import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Reference file format:
# central_energy density (MeV.fm^-3), Mass (solar mass), R (km), Inertia, p_c, rho_c(rho_0),?,?,M_B(M_solar),?,Love number,tidal def., sos, phase

files = [
    ("RGgen_v0.70d1.45", "export/reference_tov/RGgen_v0.70d1.45tov.txt", "export/batch_7d4de7f_v0.70/csv/RGgen_v0.70d1.45.csv"),
    ("RGgen_v0.80d1.50", "export/reference_tov/RGgen_v0.80d1.50tov.txt", "export/batch_7d4de7f_v0.80/csv/RGgen_v0.80d1.50.csv"),
    ("RGgen_v0.85d1.50", "export/reference_tov/RGgen_v0.85d1.50tov.txt", "export/batch_7d4de7f_v0.85/csv/RGgen_v0.85d1.50.csv"),
]

for name, ref_file, our_file in files:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Read reference file
    ref = pd.read_csv(ref_file, comment='!', header=None, sep=r'\s+')
    ref.columns = ['e_c', 'M', 'R', 'I', 'p_c', 'rho_c', 'col6', 'col7', 'M_B', 'col9', 'k2', 'Lambda', 'sos', 'phase']
    
    # Read our file
    ours = pd.read_csv(our_file, comment='#')
    
    # Filter valid solutions
    ref_valid = ref[(ref['M'] > 0) & (ref['R'] > 0) & (ref['R'] < 99)]
    ours_valid = ours[(ours['M_solar'] > 0) & (ours['R'] > 0) & (ours['R'] < 99)]
    
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    print(f"Reference: {len(ref_valid)} valid solutions")
    print(f"Ours: {len(ours_valid)} valid solutions")
    
    # Find maximum mass
    ref_max_idx = ref_valid['M'].idxmax()
    ours_max_idx = ours_valid['M_solar'].idxmax()
    
    print(f"\nMaximum Mass:")
    print(f"  Reference: {ref_valid.loc[ref_max_idx, 'M']:.4f} Msun at R={ref_valid.loc[ref_max_idx, 'R']:.2f} km")
    print(f"  Ours:      {ours_valid.loc[ours_max_idx, 'M_solar']:.4f} Msun at R={ours_valid.loc[ours_max_idx, 'R']:.2f} km")
    print(f"  Difference: ΔM={ours_valid.loc[ours_max_idx, 'M_solar']-ref_valid.loc[ref_max_idx, 'M']:.4f} Msun, ΔR={ours_valid.loc[ours_max_idx, 'R']-ref_valid.loc[ref_max_idx, 'R']:.2f} km")
    
    # Find near 1.4 Msun
    ref_near_14 = ref_valid.iloc[(ref_valid['M'] - 1.4).abs().argsort()[:1]]
    ours_near_14 = ours_valid.iloc[(ours_valid['M_solar'] - 1.4).abs().argsort()[:1]]
    
    print(f"\nAt ~1.4 Msun:")
    print(f"  Reference: M={ref_near_14['M'].values[0]:.4f}, R={ref_near_14['R'].values[0]:.2f} km, Lambda={ref_near_14['Lambda'].values[0]:.2f}, k2={ref_near_14['k2'].values[0]:.4f}")
    print(f"  Ours:      M={ours_near_14['M_solar'].values[0]:.4f}, R={ours_near_14['R'].values[0]:.2f} km, Lambda={ours_near_14['Lambda'].values[0]:.2f}, k2={ours_near_14['k2'].values[0]:.4f}")
    
    ref_lambda = ref_near_14['Lambda'].values[0]
    our_lambda = ours_near_14['Lambda'].values[0]
    lambda_diff = (our_lambda - ref_lambda) / ref_lambda * 100
    print(f"  Lambda difference: {lambda_diff:+.2f}%")
    
    # Plot M-R curve
    axes[0, 0].plot(ref_valid['R'], ref_valid['M'], 'o-', label='Reference', color='blue', alpha=0.7, markersize=3)
    axes[0, 0].plot(ours_valid['R'], ours_valid['M_solar'], 's--', label='Ours', color='red', alpha=0.7, markersize=4)
    axes[0, 0].set_xlabel('R (km)', fontsize=12)
    axes[0, 0].set_ylabel('M (Msun)', fontsize=12)
    axes[0, 0].set_title(f'Mass-Radius Curve - {name}', fontsize=14, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot Lambda vs M
    axes[0, 1].plot(ref_valid['M'], ref_valid['Lambda'], 'o-', label='Reference', color='blue', alpha=0.7, markersize=3)
    axes[0, 1].plot(ours_valid['M_solar'], ours_valid['Lambda'], 's--', label='Ours', color='red', alpha=0.7, markersize=4)
    axes[0, 1].set_xlabel('M (Msun)', fontsize=12)
    axes[0, 1].set_ylabel('Lambda', fontsize=12)
    axes[0, 1].set_title(f'Tidal Deformability vs Mass - {name}', fontsize=14, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_yscale('log')
    
    # Plot k2 vs M
    axes[1, 0].plot(ref_valid['M'], ref_valid['k2'], 'o-', label='Reference', color='blue', alpha=0.7, markersize=3)
    axes[1, 0].plot(ours_valid['M_solar'], ours_valid['k2'], 's--', label='Ours', color='red', alpha=0.7, markersize=4)
    axes[1, 0].set_xlabel('M (Msun)', fontsize=12)
    axes[1, 0].set_ylabel('k2', fontsize=12)
    axes[1, 0].set_title(f'Love Number vs Mass - {name}', fontsize=14, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot Lambda vs R
    axes[1, 1].plot(ref_valid['R'], ref_valid['Lambda'], 'o-', label='Reference', color='blue', alpha=0.7, markersize=3)
    axes[1, 1].plot(ours_valid['R'], ours_valid['Lambda'], 's--', label='Ours', color='red', alpha=0.7, markersize=4)
    axes[1, 1].set_xlabel('R (km)', fontsize=12)
    axes[1, 1].set_ylabel('Lambda', fontsize=12)
    axes[1, 1].set_title(f'Tidal Deformability vs Radius - {name}', fontsize=14, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_yscale('log')
    
    plt.tight_layout()
    output_file = f'export/comparison_{name}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved plot to {output_file}")
    plt.show()
    plt.close()


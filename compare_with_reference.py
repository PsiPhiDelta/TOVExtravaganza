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

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for name, ref_file, our_file in files:
    # Read reference file
    ref = pd.read_csv(ref_file, comment='!', header=None, sep=r'\s+')
    ref.columns = ['e_c', 'M', 'R', 'I', 'p_c', 'rho_c', 'col6', 'col7', 'M_B', 'col9', 'k2', 'Lambda', 'sos', 'phase']
    
    # Read our file
    ours = pd.read_csv(our_file, comment='#')
    
    # Filter valid solutions
    ref_valid = ref[(ref['M'] > 0) & (ref['R'] > 0) & (ref['R'] < 99)]
    ours_valid = ours[(ours['M_solar'] > 0) & (ours['R'] > 0) & (ours['R'] < 99)]
    
    print(f"\n=== {name} ===")
    print(f"Reference: {len(ref_valid)} valid solutions")
    print(f"Ours: {len(ours_valid)} valid solutions")
    
    # Find maximum mass
    ref_max_idx = ref_valid['M'].idxmax()
    ours_max_idx = ours_valid['M_solar'].idxmax()
    
    print(f"\nReference Max Mass: {ref_valid.loc[ref_max_idx, 'M']:.4f} Msun at R={ref_valid.loc[ref_max_idx, 'R']:.2f} km")
    print(f"Our Max Mass: {ours_valid.loc[ours_max_idx, 'M_solar']:.4f} Msun at R={ours_valid.loc[ours_max_idx, 'R']:.2f} km")
    
    # Find near 1.4 Msun
    ref_near_14 = ref_valid.iloc[(ref_valid['M'] - 1.4).abs().argsort()[:1]]
    ours_near_14 = ours_valid.iloc[(ours_valid['M_solar'] - 1.4).abs().argsort()[:1]]
    
    print(f"\nReference @ ~1.4 Msun: M={ref_near_14['M'].values[0]:.4f}, R={ref_near_14['R'].values[0]:.2f} km, Lambda={ref_near_14['Lambda'].values[0]:.2f}")
    print(f"Our @ ~1.4 Msun: M={ours_near_14['M_solar'].values[0]:.4f}, R={ours_near_14['R'].values[0]:.2f} km, Lambda={ours_near_14['Lambda'].values[0]:.2f}")
    
    # Plot M-R curve
    if '0.70' in name:
        color = 'blue'
    elif '0.80' in name:
        color = 'red'
    else:
        color = 'green'
    axes[0, 0].plot(ref_valid['R'], ref_valid['M'], 'o-', label=f'{name} (Reference)', color=color, alpha=0.7)
    axes[0, 0].plot(ours_valid['R'], ours_valid['M_solar'], 's--', label=f'{name} (Ours)', color=color, alpha=0.7)
    
    # Plot Lambda vs M
    axes[0, 1].plot(ref_valid['M'], ref_valid['Lambda'], 'o-', label=f'{name} (Reference)', color=color, alpha=0.7)
    axes[0, 1].plot(ours_valid['M_solar'], ours_valid['Lambda'], 's--', label=f'{name} (Ours)', color=color, alpha=0.7)
    
    # Plot k2 vs M
    axes[1, 0].plot(ref_valid['M'], ref_valid['k2'], 'o-', label=f'{name} (Reference)', color=color, alpha=0.7)
    axes[1, 0].plot(ours_valid['M_solar'], ours_valid['k2'], 's--', label=f'{name} (Ours)', color=color, alpha=0.7)
    
    # Plot Lambda vs R
    axes[1, 1].plot(ref_valid['R'], ref_valid['Lambda'], 'o-', label=f'{name} (Reference)', color=color, alpha=0.7)
    axes[1, 1].plot(ours_valid['R'], ours_valid['Lambda'], 's--', label=f'{name} (Ours)', color=color, alpha=0.7)

# Format plots
axes[0, 0].set_xlabel('R (km)', fontsize=12)
axes[0, 0].set_ylabel('M (Msun)', fontsize=12)
axes[0, 0].set_title('Mass-Radius Curve', fontsize=14, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].set_xlabel('M (Msun)', fontsize=12)
axes[0, 1].set_ylabel('Lambda', fontsize=12)
axes[0, 1].set_title('Tidal Deformability vs Mass', fontsize=14, fontweight='bold')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].set_yscale('log')

axes[1, 0].set_xlabel('M (Msun)', fontsize=12)
axes[1, 0].set_ylabel('k2', fontsize=12)
axes[1, 0].set_title('Love Number vs Mass', fontsize=14, fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].set_xlabel('R (km)', fontsize=12)
axes[1, 1].set_ylabel('Lambda', fontsize=12)
axes[1, 1].set_title('Tidal Deformability vs Radius', fontsize=14, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_yscale('log')

plt.tight_layout()
plt.savefig('export/comparison_reference_vs_ours.png', dpi=150, bbox_inches='tight')
plt.savefig('export/comparison_reference_vs_ours.pdf', bbox_inches='tight')
print("\n✓ Saved plots to export/comparison_reference_vs_ours.png and .pdf")
plt.show()


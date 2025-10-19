import pandas as pd
import numpy as np

df = pd.read_csv('export/dd2_7d4de7f/csv/hsdd2.csv', comment='#')
df_valid = df[(df['M_solar'] > 0) & (df['R'] > 0)]

# Find closest to 1.4
idx = (df_valid['M_solar'] - 1.4).abs().argsort()[0]
closest = df_valid.iloc[idx]

print(f"Closest to 1.4 Msun:")
print(f"  M = {closest['M_solar']:.6f} Msun")
print(f"  R = {closest['R']:.2f} km")
print(f"  Lambda = {closest['Lambda']:.2f}")
print(f"  k2 = {closest['k2']:.4f}")

# Interpolate to exactly 1.4
from scipy.interpolate import interp1d

# Sort by mass
df_sorted = df_valid.sort_values('M_solar')
f_lambda = interp1d(df_sorted['M_solar'], df_sorted['Lambda'], kind='cubic')
f_r = interp1d(df_sorted['M_solar'], df_sorted['R'], kind='cubic')
f_k2 = interp1d(df_sorted['M_solar'], df_sorted['k2'], kind='cubic')

if 1.4 >= df_sorted['M_solar'].min() and 1.4 <= df_sorted['M_solar'].max():
    lambda_14 = f_lambda(1.4)
    r_14 = f_r(1.4)
    k2_14 = f_k2(1.4)
    
    print(f"\nInterpolated to EXACTLY 1.4 Msun:")
    print(f"  M = 1.400000 Msun")
    print(f"  R = {r_14:.2f} km")
    print(f"  Lambda = {lambda_14:.2f}")
    print(f"  k2 = {k2_14:.4f}")


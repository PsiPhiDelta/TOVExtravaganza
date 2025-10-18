#!/usr/bin/env python3
"""Quick script to check CompOSE eos.thermo.ns format"""

with open('inputCompose/eos.thermo.ns') as f:
    lines = f.readlines()

print('First line (header with masses):')
print(lines[0])

print('\nSecond line (first data):')
parts = lines[1].split()
print(f'Total columns: {len(parts)}')
print('\nColumn values:')
for i, p in enumerate(parts):
    print(f'  [{i:2d}]: {p}')

print('\n\nLet me also check a line further down where P might be positive:')
for i, line in enumerate(lines[140:145], start=140):
    parts = line.split()
    if len(parts) > 5:
        print(f'\nLine {i}:')
        print(f'  [3]: {parts[3]:20s} (n_b)')
        print(f'  [4]: {parts[4]:20s} (??)')
        print(f'  [5]: {parts[5]:20s} (??)')


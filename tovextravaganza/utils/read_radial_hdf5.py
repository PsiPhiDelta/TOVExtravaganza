"""
Helper functions to read radial profile HDF5 files
"""
import numpy as np

try:
    import h5py
    HAS_HDF5 = True
except ImportError:
    HAS_HDF5 = False
    print("Warning: h5py not installed. Install with: pip install h5py")


def read_radial_hdf5(filename):
    """
    Read radial profiles from HDF5 file.
    
    Parameters:
    -----------
    filename : str
        Path to HDF5 file
        
    Returns:
    --------
    list of dict
        List of profile dictionaries, each containing:
        - 'p_c': central pressure
        - 'R': radius
        - 'M': mass
        - 'r': radial array
        - 'M_r': mass profile array
        - 'columns': dict with all EOS column arrays
        
    Example:
    --------
    >>> profiles = read_radial_hdf5('export/radial_profiles/json/dd2.h5')
    >>> prof0 = profiles[0]
    >>> print(f"Star 0: M={prof0['M']:.3f}, R={prof0['R']:.2f}")
    >>> print(f"Pressure at center: {prof0['columns']['p'][0]:.3e}")
    >>> print(f"Phase at center: {prof0['columns']['phase'][0]}")
    """
    if not HAS_HDF5:
        raise ImportError("h5py is required. Install with: pip install h5py")
    
    profiles = []
    
    with h5py.File(filename, 'r') as hf:
        # Get number of profiles
        num_profiles = len([k for k in hf.keys() if k.startswith('profile_')])
        
        for i in range(num_profiles):
            grp = hf[f'profile_{i}']
            
            # Read metadata
            prof = {
                'p_c': grp.attrs['p_c'],
                'R': grp.attrs['R'],
                'M': grp.attrs['M'],
                'radial_points': grp.attrs['radial_points'],
                'r': grp['r'][:],
                'M_r': grp['M_r'][:],
                'columns': {}
            }
            
            # Read all column data
            col_grp = grp['columns']
            for col_name in col_grp.keys():
                data = col_grp[col_name][:]
                # Convert bytes to strings if needed
                if data.dtype.kind == 'O' or data.dtype.kind == 'S':
                    data = [s.decode('utf-8') if isinstance(s, bytes) else s for s in data]
                prof['columns'][col_name] = data
            
            profiles.append(prof)
    
    return profiles


def print_hdf5_info(filename):
    """
    Print information about HDF5 file structure.
    
    Parameters:
    -----------
    filename : str
        Path to HDF5 file
    """
    if not HAS_HDF5:
        raise ImportError("h5py is required. Install with: pip install h5py")
    
    with h5py.File(filename, 'r') as hf:
        print(f"HDF5 File: {filename}")
        print(f"{'='*60}")
        
        # Count profiles
        profiles = [k for k in hf.keys() if k.startswith('profile_')]
        print(f"Number of profiles: {len(profiles)}")
        
        if profiles:
            # Show first profile as example
            grp = hf[profiles[0]]
            print(f"\nProfile 0 metadata:")
            for attr_name, attr_value in grp.attrs.items():
                print(f"  {attr_name}: {attr_value}")
            
            print(f"\nProfile 0 datasets:")
            print(f"  r: shape={grp['r'].shape}, dtype={grp['r'].dtype}")
            print(f"  M_r: shape={grp['M_r'].shape}, dtype={grp['M_r'].dtype}")
            
            col_grp = grp['columns']
            print(f"\nEOS columns:")
            for col_name in col_grp.keys():
                ds = col_grp[col_name]
                print(f"  {col_name}: shape={ds.shape}, dtype={ds.dtype}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m tovextravaganza.utils.read_radial_hdf5 <file.h5>")
        sys.exit(1)
    
    print_hdf5_info(sys.argv[1])


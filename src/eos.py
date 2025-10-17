"""
Equation of State (EOS) Module
Handles reading and interpolating EOS data
"""
import csv
import numpy as np


class EOS:
    """
    Equation of State class with linear interpolation.
    Handles multi-column EOS data in TOV code units.
    """
    
    def __init__(self, data_dict, colnames):
        """
        Initialize EOS from data dictionary.
        
        Parameters:
        -----------
        data_dict : dict
            Dictionary with column names as keys, numpy arrays as values
        colnames : list
            List of column names in order
        """
        self.data_dict = data_dict
        self.colnames = colnames
        self.p_table = data_dict["p"]
        self.n_points = len(self.p_table)
        
        if self.n_points < 2:
            raise ValueError("Need at least 2 data points for interpolation.")
        
        self.ilast = 0  # Cache for bracket index
    
    @classmethod
    def from_file(cls, filename):
        """
        Create EOS from CSV file.
        
        Parameters:
        -----------
        filename : str
            Path to CSV file with EOS data
            
        Returns:
        --------
        EOS instance
        """
        data_dict, colnames = cls._read_csv(filename)
        return cls(data_dict, colnames)
    
    @staticmethod
    def _read_csv(filename):
        """
        Read EOS from CSV file.
        
        Returns:
        --------
        data_dict : dict
            Column data
        colnames : list
            Column names
        """
        raw_data = []
        header = None

        with open(filename, "r") as fin:
            reader = csv.reader(fin)
            for row in reader:
                if (not row) or row[0].startswith("#"):
                    continue
                # Check if we have a header yet
                if header is None:
                    # Try parsing first 2 columns as float
                    try:
                        float(row[0]), float(row[1])
                        # No exception => numeric => no header
                        raw_data.append(row)
                    except ValueError:
                        # Not numeric => treat as header
                        header = row
                else:
                    raw_data.append(row)

        # If no header found, create a default
        if header is None:
            ncols = len(raw_data[0])
            header = ["p", "e"] + [f"col{i}" for i in range(2, ncols)]

        # Parse data into float arrays
        columns = [[] for _ in header]
        for row in raw_data:
            if len(row) < 2:
                continue
            valid = True
            vals = []
            for i in range(len(header)):
                try:
                    vals.append(float(row[i]))
                except (IndexError, ValueError):
                    valid = False
                    break
            if valid:
                for i in range(len(header)):
                    columns[i].append(vals[i])

        data_dict = {}
        for h, colvals in zip(header, columns):
            data_dict[h] = np.array(colvals, dtype=float)

        # Sort by ascending p
        if "p" not in data_dict:
            raise ValueError("No 'p' column found!")

        sort_idx = np.argsort(data_dict["p"])
        for k in data_dict.keys():
            data_dict[k] = data_dict[k][sort_idx]

        return data_dict, header
    
    def get_value(self, colname, p):
        """
        Interpolate column value at given pressure using linear interpolation.
        
        Parameters:
        -----------
        colname : str
            Column name to interpolate
        p : float
            Pressure value
            
        Returns:
        --------
        float
            Interpolated value
        """
        # Clamp to table bounds
        if p <= self.p_table[0]:
            return self.data_dict[colname][0]
        if p >= self.p_table[-1]:
            return self.data_dict[colname][-1]

        i = self.ilast
        # Move left
        while i > 0 and p < self.p_table[i]:
            i -= 1
        # Move right
        while i < (self.n_points - 1) and p > self.p_table[i+1]:
            i += 1

        p_i = self.p_table[i]
        p_ip1 = self.p_table[i+1]
        c_i = self.data_dict[colname][i]
        c_ip1 = self.data_dict[colname][i+1]

        frac = (p - p_i) / (p_ip1 - p_i)
        val = c_i + frac * (c_ip1 - c_i)

        self.ilast = i
        return val
    
    def get_energy_density(self, p):
        """Get energy density at given pressure."""
        return self.get_value("e", p)
    
    def get_pressure_range(self):
        """Get min and max pressure in the EOS table."""
        return self.p_table[0], self.p_table[-1]
    
    def __repr__(self):
        return f"EOS(n_points={self.n_points}, columns={self.colnames})"


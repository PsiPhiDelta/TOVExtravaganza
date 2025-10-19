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
    
    def __init__(self, data_dict, colnames, string_dict=None):
        """
        Initialize EOS from data dictionary.
        
        Parameters:
        -----------
        data_dict : dict
            Dictionary with column names as keys, numpy arrays as values (numeric columns)
        colnames : list
            List of column names in order
        string_dict : dict or None
            Dictionary with column names as keys, lists of strings as values (string columns)
        """
        self.data_dict = data_dict
        self.colnames = colnames
        self.string_dict = string_dict if string_dict is not None else {}
        self.p_table = data_dict["p"]
        self.n_points = len(self.p_table)
        
        if self.n_points < 2:
            raise ValueError("Need at least 2 data points for interpolation.")
        
        self.ilast = 0  # Cache for bracket index
        
        # Precompute de/dp for tidal calculations (matches their fdedp[])
        self.fdedp = self._precompute_fdedp()
    
    def _precompute_fdedp(self):
        """
        Precompute de/dp at each EOS table point using centered differences.
        Matches their implementation: fdedp[i] = (e[i+1]-e[i-1])/(p[i+1]-p[i-1])
        """
        fdedp = np.zeros(self.n_points)
        e_table = self.data_dict['e']
        
        # Centered differences for interior points
        for i in range(1, self.n_points - 1):
            fdedp[i] = (e_table[i+1] - e_table[i-1]) / (self.p_table[i+1] - self.p_table[i-1])
        
        # Endpoints
        fdedp[0] = fdedp[1]
        fdedp[self.n_points-1] = fdedp[self.n_points-2]
        
        return fdedp
    
    def get_fdedp(self, p):
        """
        Get de/dp at given pressure by interpolating precomputed fdedp[].
        Matches their getF() function.
        """
        # Clamp to table bounds
        if p <= self.p_table[0]:
            return self.fdedp[0]
        if p >= self.p_table[-1]:
            return self.fdedp[-1]
        
        # Find bracket
        i = self.ilast if self.ilast < self.n_points - 1 else 0
        while i > 0 and p < self.p_table[i]:
            i -= 1
        while i < self.n_points - 1 and p > self.p_table[i+1]:
            i += 1
        
        # Linear interpolation
        p_i = self.p_table[i]
        p_ip1 = self.p_table[i+1]
        f_i = self.fdedp[i]
        f_ip1 = self.fdedp[i+1]
        
        frac = (p - p_i) / (p_ip1 - p_i)
        f = f_i + frac * (f_ip1 - f_i)
        
        # Don't update self.ilast here to avoid interfering with other interpolation calls
        return f
    
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
        data_dict, colnames, string_dict = cls._read_csv(filename)
        return cls(data_dict, colnames, string_dict)
    
    @staticmethod
    def _read_csv(filename):
        """
        Read EOS from CSV file.
        InputCode format is STANDARDIZED: col1=p, col2=e, rest=additional
        
        Returns:
        --------
        data_dict : dict
            Column data
        colnames : list
            Column names
        string_dict : dict
            String column data
        """
        raw_data = []
        header = None
        last_comment_row = None

        with open(filename, "r") as fin:
            reader = csv.reader(fin)
            for row in reader:
                if not row:
                    continue
                
                # Skip comment lines but save the last one (likely the header)
                if row[0].startswith("#"):
                    if len(row) >= 2:
                        # Save this as potential header
                        cleaned_row = [row[0].lstrip('#').strip()] + [c.strip() for c in row[1:]]
                        last_comment_row = cleaned_row
                    continue
                
                # Data row
                if header is None:
                    # Try to detect if first row is header or data
                    try:
                        float(row[0]), float(row[1])
                        # Numeric data - use last comment as header if available
                        if last_comment_row and len(last_comment_row) == len(row):
                            header = last_comment_row
                        else:
                            # No header found, create default
                            ncols = len(row)
                            header = ["p", "e"] + [f"col{i}" for i in range(2, ncols)]
                        raw_data.append(row)
                    except ValueError:
                        # Non-numeric, it's a header
                        header = [c.strip() for c in row]
                else:
                    raw_data.append(row)
        
        # Ensure we have header
        if header is None:
            ncols = len(raw_data[0]) if raw_data else 2
            header = ["p", "e"] + [f"col{i}" for i in range(2, ncols)]
        
        # Clean header: remove (code_units) tags, force col1=p, col2=e
        cleaned_header = []
        for i, h in enumerate(header):
            clean = h.replace('(code_units)', '').replace('(code units)', '').strip()
            if i == 0:
                cleaned_header.append('p')  # Force first column to 'p'
            elif i == 1:
                cleaned_header.append('e')  # Force second column to 'e'  
            else:
                cleaned_header.append(clean)  # Keep rest as-is
        
        header = cleaned_header

        # Parse data - separate numeric and string columns
        columns = [[] for _ in header]
        column_types = [None for _ in header]  # Track if numeric or string
        
        for row in raw_data:
            if len(row) < 2:
                continue
            
            # Try to parse each column
            for i in range(len(header)):
                if i >= len(row):
                    continue
                    
                # First row: determine column type
                if column_types[i] is None:
                    try:
                        float(row[i])
                        column_types[i] = 'numeric'
                    except ValueError:
                        column_types[i] = 'string'
                
                # Add value based on type
                if column_types[i] == 'numeric':
                    try:
                        columns[i].append(float(row[i]))
                    except ValueError:
                        columns[i].append(np.nan)  # Handle occasional bad values
                else:
                    columns[i].append(row[i].strip())
        
        # Separate numeric and string columns
        data_dict = {}
        string_dict = {}
        
        for h, colvals, coltype in zip(header, columns, column_types):
            if coltype == 'numeric':
                data_dict[h] = np.array(colvals, dtype=float)
            else:
                string_dict[h] = colvals
        
        # Sort by ascending p
        if "p" not in data_dict:
            raise ValueError("No 'p' column found!")

        sort_idx = np.argsort(data_dict["p"])
        
        # Sort numeric columns
        for k in data_dict.keys():
            data_dict[k] = data_dict[k][sort_idx]
        
        # Sort string columns
        for k in string_dict.keys():
            string_dict[k] = [string_dict[k][i] for i in sort_idx]

        return data_dict, header, string_dict
    
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
    
    def get_string_value(self, colname, p):
        """
        Get string value at given pressure (finds nearest point by ENERGY DENSITY).
        Uses energy density instead of pressure because in first-order phase transitions,
        pressure plateaus while energy density jumps - making energy more unique.
        
        Parameters:
        -----------
        colname : str
            String column name
        p : float
            Pressure value
            
        Returns:
        --------
        str
            String value at nearest energy density point
        """
        if colname not in self.string_dict:
            raise ValueError(f"Column '{colname}' is not a string column")
        
        # Get energy density at this pressure (interpolated)
        e_at_p = self.get_energy_density(p)
        
        # Find nearest energy density index
        e_table = self.data_dict['e']
        idx = np.argmin(np.abs(e_table - e_at_p))
        return self.string_dict[colname][idx]
    
    def get_all_values_at_pressure(self, p):
        """
        Get all column values (numeric and string) at given pressure.
        
        Parameters:
        -----------
        p : float
            Pressure value
            
        Returns:
        --------
        dict
            {column_name: value} for all columns except 'p'
        """
        result = {}
        
        # Get numeric columns (interpolated)
        for col in self.data_dict.keys():
            if col != 'p':
                result[col] = self.get_value(col, p)
        
        # Get string columns (nearest)
        for col in self.string_dict.keys():
            result[col] = self.get_string_value(col, p)
        
        return result
    
    def get_pressure_range(self):
        """Get min and max pressure in the EOS table."""
        return self.p_table[0], self.p_table[-1]
    
    def __repr__(self):
        return f"EOS(n_points={self.n_points}, columns={self.colnames})"


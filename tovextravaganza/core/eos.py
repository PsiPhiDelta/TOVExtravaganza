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
    
    # Defaults for first-order phase-transition detection.
    #
    # A Maxwell construction produces two table rows at the *same* pressure with
    # different energy densities.  We flag such a pair as a transition when the
    # pressure step is negligible AND the energy-density step is a significant
    # *relative* jump.  The relative test matters: absolute thresholds fire on
    # ordinary table steps in the outer crust, where dp is ~1e-14 in code units
    # simply because the pressure itself is ~1e-13.
    TRANSITION_REL_DP = 1e-6   # (p[i+1]-p[i]) / p[i] below this => plateau
    TRANSITION_REL_DE = 1e-3   # (e[i+1]-e[i]) / e[i] above this => real jump

    def __init__(self, data_dict, colnames, string_dict=None,
                 transition_pressures=None,
                 transition_rel_dp=None, transition_rel_de=None):
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
        transition_pressures : sequence of float or None
            Explicit first-order transition pressures (code units).  When given,
            auto-detection is bypassed and only these plateaus are used.  This is
            the robust option for a hybrid EOS: the person who built the Maxwell
            construction already knows P_tr, so it need not be rediscovered by
            scanning the table.
        transition_rel_dp, transition_rel_de : float or None
            Override the relative thresholds used by auto-detection.
        """
        self.data_dict = data_dict
        self.colnames = colnames
        self.string_dict = string_dict if string_dict is not None else {}
        self.p_table = data_dict["p"]
        self.n_points = len(self.p_table)
        
        if self.n_points < 2:
            raise ValueError("Need at least 2 data points for interpolation.")
        
        self.ilast = 0  # Cache for bracket index

        self.transition_rel_dp = (self.TRANSITION_REL_DP if transition_rel_dp is None
                                  else transition_rel_dp)
        self.transition_rel_de = (self.TRANSITION_REL_DE if transition_rel_de is None
                                  else transition_rel_de)

        # Put every pressure plateau in ascending-energy order before anything
        # else looks at the table, so the low-energy (e.g. hadronic) row is
        # always the inner-facing one.
        self._order_plateau_rows()

        # Locate first-order transitions and split the table into single-phase
        # segments.  A single-phase EOS yields exactly one segment covering the
        # whole table, and every code path below then reduces to plain
        # interpolation over the full table.
        self.transitions = self._detect_transitions(transition_pressures)
        self.segments = self._build_segments()
        
        # Precompute de/dp for tidal calculations (matches their fdedp[])
        self.fdedp = self._precompute_fdedp()

    # ------------------------------------------------------------------
    # First-order phase transitions
    # ------------------------------------------------------------------
    def _order_plateau_rows(self):
        """
        Sort each run of equal-pressure rows by ascending energy density.
        
        Reading a CSV only guarantees ordering in p, and a Maxwell construction
        deliberately produces two rows sharing one pressure.  Which of them ends
        up first is then down to the file, or to sort tie-breaking.  Energy
        density rises with pressure along a physical EOS, so ascending e is the
        correct order and fixing it here makes every downstream consumer --
        transition detection, segment bounds, de/dp -- independent of how the
        table happened to be written.
        """
        e_table = self.data_dict["e"]
        p = self.p_table
        order = np.arange(self.n_points)

        i = 0
        while i < self.n_points - 1:
            j = i
            while (j < self.n_points - 1
                   and p[j + 1] - p[j] <= self.transition_rel_dp * abs(p[j])):
                j += 1
            if j > i:
                block = order[i:j + 1]
                order[i:j + 1] = block[np.argsort(e_table[block], kind="stable")]
            i = j + 1

        if np.array_equal(order, np.arange(self.n_points)):
            return

        for k in self.data_dict:
            self.data_dict[k] = self.data_dict[k][order]
        for k in self.string_dict:
            self.string_dict[k] = [self.string_dict[k][i] for i in order]
        self.p_table = self.data_dict["p"]

    def _plateau_candidates(self):
        """
        Indices i where p[i+1] is the same pressure as p[i] (to within the
        relative tolerance) and the energy density increases.  Consecutive
        indices are merged, so a plateau spanning more than two rows counts once.
        """
        e_table = self.data_dict["e"]
        p = self.p_table
        raw = []
        for i in range(self.n_points - 1):
            dp = p[i + 1] - p[i]
            de = e_table[i + 1] - e_table[i]
            scale = abs(p[i]) if p[i] != 0.0 else abs(p[i + 1])
            if scale <= 0.0:
                continue
            if dp <= self.transition_rel_dp * scale and de > 0.0:
                raw.append(i)

        # Merge runs of consecutive indices into (lo, hi) row pairs
        groups = []
        for i in raw:
            if groups and i == groups[-1][1]:
                groups[-1][1] = i + 1
            else:
                groups.append([i, i + 1])
        return groups

    def _detect_transitions(self, transition_pressures=None):
        """
        Build the list of first-order transitions.
        
        Returns:
        --------
        list of dict
            Each dict has 'lo' (last row of the lower-energy phase), 'hi'
            (first row of the higher-energy phase), 'p_tr', 'e_low', 'e_high'
            and 'delta_e'.  Sorted by ascending p_tr.
        """
        e_table = self.data_dict["e"]
        groups = self._plateau_candidates()

        if transition_pressures is not None:
            chosen = []
            for p_req in transition_pressures:
                if not groups:
                    raise ValueError(
                        "No pressure plateau found in the EOS table, so the "
                        "requested transition pressure %g cannot be matched."
                        % p_req)
                lo, hi = min(groups, key=lambda g: abs(self.p_table[g[0]] - p_req))
                chosen.append((lo, hi))
            groups = [list(g) for g in sorted(set(chosen))]
        else:
            # Auto-detection: require a significant *relative* energy-density
            # jump, so that table-resolution steps are not mistaken for physics.
            groups = [g for g in groups
                      if (e_table[g[1]] - e_table[g[0]])
                      > self.transition_rel_de * abs(e_table[g[0]])]

        transitions = []
        for lo, hi in groups:
            transitions.append({
                "lo": lo,
                "hi": hi,
                "p_tr": float(self.p_table[lo]),
                "e_low": float(e_table[lo]),
                "e_high": float(e_table[hi]),
                "delta_e": float(e_table[hi] - e_table[lo]),
            })
        transitions.sort(key=lambda t: t["p_tr"])
        return transitions

    def _build_segments(self):
        """
        Split the table into single-phase segments at the detected transitions.
        
        Returns:
        --------
        list of (start, stop) inclusive index pairs, ordered by ascending
        pressure.  Segment k spans rows [start, stop]; segment 0 is the
        lowest-pressure phase.
        """
        segments = []
        start = 0
        for t in self.transitions:
            segments.append((start, t["lo"]))
            start = t["hi"]
        segments.append((start, self.n_points - 1))
        return segments

    def n_segments(self):
        """Number of single-phase segments (1 for an ordinary EOS)."""
        return len(self.segments)

    def segment_for_pressure(self, p, prefer="high"):
        """
        Index of the segment that contains pressure `p`.
        
        Exactly on a transition plateau the answer is genuinely ambiguous;
        `prefer` picks the side.  During outward TOV integration the core sits
        on the high-energy branch, so 'high' is the right default when choosing
        the segment for a central pressure.
        """
        for k, t in enumerate(self.transitions):
            if p < t["p_tr"]:
                return k
            if p == t["p_tr"] and prefer == "low":
                return k
        return len(self.segments) - 1

    def segment_pressure_range(self, segment):
        """(p_min, p_max) of the given segment."""
        start, stop = self.segments[segment]
        return self.p_table[start], self.p_table[stop]
    
    def _precompute_fdedp(self):
        """
        Precompute de/dp at each EOS table point using centered differences:
        fdedp[i] = (e[i+1]-e[i-1])/(p[i+1]-p[i-1]).
        
        Differences are taken *within* a single-phase segment and never across a
        first-order transition.  A centered difference straddling a Maxwell
        plateau divides a finite de by a vanishing dp, which puts a huge bogus
        value on both plateau rows; linear interpolation of fdedp[] then smears
        that over the two intervals adjacent to the transition.  The physical
        content of the discontinuity is a delta function, which belongs in the
        matching condition applied by TidalCalculator, not in this array.
        """
        fdedp = np.zeros(self.n_points)
        e_table = self.data_dict['e']
        p = self.p_table

        for start, stop in self.segments:
            if stop <= start:
                # Degenerate one-row segment: no slope available.
                fdedp[start] = 1.0
                continue

            # Centered differences for points interior to this segment
            for i in range(start + 1, stop):
                fdedp[i] = (e_table[i+1] - e_table[i-1]) / (p[i+1] - p[i-1])

            # Segment edges.  At the two ends of the *table* keep the original
            # convention (copy the neighbour) so single-phase results are
            # unchanged; at an edge created by a phase transition a copy would
            # reach across the discontinuity, so use a one-sided difference
            # taken entirely within this phase.
            if start == 0:
                fdedp[start] = fdedp[start+1]
            else:
                fdedp[start] = (e_table[start+1] - e_table[start]) / (p[start+1] - p[start])

            if stop == self.n_points - 1:
                fdedp[stop] = fdedp[stop-1]
            else:
                fdedp[stop] = (e_table[stop] - e_table[stop-1]) / (p[stop] - p[stop-1])

        return fdedp
    
    def get_fdedp(self, p, segment=None):
        """
        Get de/dp at given pressure by interpolating precomputed fdedp[].
        Matches their getF() function.
        
        Parameters:
        -----------
        p : float
            Pressure value
        segment : int or None
            Restrict the interpolation to this single-phase segment.  Required
            for an unambiguous answer on a transition plateau; None searches the
            whole table (correct for a single-phase EOS).
        """
        start, stop = self._segment_bounds(segment, p)

        if stop <= start:
            return self.fdedp[start]
        if p <= self.p_table[start]:
            return self.fdedp[start]
        if p >= self.p_table[stop]:
            return self.fdedp[stop]

        i = self._bracket(p, start, stop, update_cache=False)
        
        p_i = self.p_table[i]
        p_ip1 = self.p_table[i+1]
        f_i = self.fdedp[i]
        f_ip1 = self.fdedp[i+1]
        
        dp = p_ip1 - p_i
        if dp <= 0.0:
            return f_i
        frac = (p - p_i) / dp
        return f_i + frac * (f_ip1 - f_i)

    # ------------------------------------------------------------------
    # Bracket search helpers
    # ------------------------------------------------------------------
    def _segment_bounds(self, segment, p=None):
        """
        Inclusive (start, stop) row range to interpolate over.
        
        `segment=None` means "whole table", which is what a single-phase EOS
        always wants.  For a table with transitions it means "let the bracket
        search break the tie", which is only safe away from a plateau.
        """
        if segment is None:
            if len(self.segments) == 1:
                return self.segments[0]
            return 0, self.n_points - 1
        return self.segments[segment]

    def _bracket(self, p, start, stop, update_cache=True):
        """
        Largest i in [start, stop-1] with p_table[i] <= p, found by walking from
        the cached index.  Skips over zero-width plateaus so that the returned
        interval always has p_table[i+1] > p_table[i].
        """
        i = self.ilast
        if i < start or i > stop - 1:
            i = start

        while i > start and p < self.p_table[i]:
            i -= 1
        while i < stop - 1 and p > self.p_table[i+1]:
            i += 1

        # Never return a zero-width interval (two rows of a Maxwell plateau).
        while i < stop - 1 and self.p_table[i+1] == self.p_table[i]:
            i += 1
        while i > start and self.p_table[i+1] == self.p_table[i]:
            i -= 1

        if update_cache:
            self.ilast = i
        return i
    
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

        # A stable sort matters here: a Maxwell construction puts two rows at
        # exactly the same pressure, and the default quicksort orders such ties
        # arbitrarily (it depends on the array length, so the same physics in a
        # slightly longer table can come out with the phases swapped).  'stable'
        # keeps the order the file was written in; EOS.__init__ then enforces
        # ascending energy density on each plateau regardless of the file.
        sort_idx = np.argsort(data_dict["p"], kind="stable")
        
        # Sort numeric columns
        for k in data_dict.keys():
            data_dict[k] = data_dict[k][sort_idx]
        
        # Sort string columns
        for k in string_dict.keys():
            string_dict[k] = [string_dict[k][i] for i in sort_idx]

        return data_dict, header, string_dict
    
    def get_value(self, colname, p, segment=None):
        """
        Interpolate column value at given pressure using linear interpolation.
        
        Parameters:
        -----------
        colname : str
            Column name to interpolate
        p : float
            Pressure value
        segment : int or None
            Restrict interpolation to this single-phase segment.  Values are
            clamped at the segment edges, so asking for a pressure just past a
            transition still returns the branch you asked for rather than
            silently hopping to the other phase.  None searches the whole table.
            
        Returns:
        --------
        float
            Interpolated value
        """
        col = self.data_dict[colname]
        start, stop = self._segment_bounds(segment, p)

        # Clamp to segment bounds
        if stop <= start:
            return col[start]
        if p <= self.p_table[start]:
            return col[start]
        if p >= self.p_table[stop]:
            return col[stop]

        i = self._bracket(p, start, stop)

        p_i = self.p_table[i]
        p_ip1 = self.p_table[i+1]
        c_i = col[i]
        c_ip1 = col[i+1]

        dp = p_ip1 - p_i
        if dp <= 0.0:
            return c_i
        frac = (p - p_i) / dp
        return c_i + frac * (c_ip1 - c_i)
    
    def get_energy_density(self, p, segment=None):
        """
        Get energy density at given pressure.
        
        For a hybrid EOS eps(P) is double-valued at a first-order transition:
        the Maxwell construction puts two rows at the same P.  Pass `segment` to
        say which phase you are in -- the TOV/tidal integrators track it as they
        step outward -- instead of leaving the choice to interpolator
        tie-breaking.
        """
        return self.get_value("e", p, segment=segment)
    
    def get_string_value(self, colname, p, segment=None):
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
        segment : int or None
            Single-phase segment to read from.  When given, the nearest-energy
            search is confined to that segment, so a phase label cannot be
            picked up from the wrong side of a transition.
            
        Returns:
        --------
        str
            String value at nearest energy density point
        """
        if colname not in self.string_dict:
            raise ValueError(f"Column '{colname}' is not a string column")
        
        # Get energy density at this pressure (interpolated)
        e_at_p = self.get_energy_density(p, segment=segment)
        
        # Find nearest energy density index
        e_table = self.data_dict['e']
        if segment is None:
            idx = int(np.argmin(np.abs(e_table - e_at_p)))
        else:
            start, stop = self.segments[segment]
            idx = start + int(np.argmin(np.abs(e_table[start:stop+1] - e_at_p)))
        return self.string_dict[colname][idx]
    
    def get_all_values_at_pressure(self, p, segment=None):
        """
        Get all column values (numeric and string) at given pressure.
        
        Parameters:
        -----------
        p : float
            Pressure value
        segment : int or None
            Single-phase segment to read from (see get_value).
            
        Returns:
        --------
        dict
            {column_name: value} for all columns except 'p'
        """
        result = {}
        
        # Get numeric columns (interpolated)
        for col in self.data_dict.keys():
            if col != 'p':
                result[col] = self.get_value(col, p, segment=segment)
        
        # Get string columns (nearest)
        for col in self.string_dict.keys():
            result[col] = self.get_string_value(col, p, segment=segment)
        
        return result
    
    def get_pressure_range(self):
        """Get min and max pressure in the EOS table."""
        return self.p_table[0], self.p_table[-1]
    
    def __repr__(self):
        return f"EOS(n_points={self.n_points}, columns={self.colnames})"


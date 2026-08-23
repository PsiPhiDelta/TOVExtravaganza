"""
Regression tests for hybrid (first-order phase transition) equations of state.

Covers the three issues reported against the quark-hadron pipeline:

  1. the y-matching condition at a first-order transition (tidal),
  2. eps(P) being double-valued across the transition,
  3. jump auto-detection needing a *relative* threshold.

Plus the pre-existing unstable-sort bug that made a Maxwell table load
non-deterministically, and a guard that single-phase EOS results are unchanged.

Runs under pytest, or standalone:  python3 tests/test_hybrid_eos.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from tovextravaganza.core.eos import EOS                      # noqa: E402
from tovextravaganza.core.tov_solver import TOVSolver         # noqa: E402
from tovextravaganza.core.tidal_calculator import TidalCalculator  # noqa: E402

DD2 = os.path.join(REPO, 'inputCode', 'hsdd2.csv')
CSC = os.path.join(REPO, 'inputCode', 'csc.csv')
HYBRID = os.path.join(REPO, 'tests', 'data', 'hybrid_dd2_csc.csv')

# Properties of the hybrid fixture (Maxwell construction of csc onto DD2)
P_TR = 4.197559e-05
E_LOW = 4.131846e-04
E_HIGH = 7.158503e-04


def _calculator(path):
    return TidalCalculator(TOVSolver(EOS.from_file(path), r_max=30.0, dr=0.001))


# ---------------------------------------------------------------- Issue 3
def test_single_phase_tables_have_no_transitions():
    """Auto-detection must not fire on ordinary table steps.

    The DD2 crust contains a step at p = 1.27e-13 with de = 2.18e-11, which an
    *absolute* dp threshold would flag (dp there is 9.98e-15).  Relative to the
    pressure itself that step is 7.9e-2 wide -- not a plateau at all.
    """
    for path in (DD2, CSC):
        eos = EOS.from_file(path)
        assert eos.transitions == [], f'{path} should have no transitions'
        assert eos.n_segments() == 1


def test_explicit_transition_pressure_overrides_detection():
    """Passing P_tr in explicitly is the robust route for a hybrid EOS."""
    eos = EOS.from_file(HYBRID)
    forced = EOS(dict(eos.data_dict), eos.colnames,
                 transition_pressures=[P_TR * 1.0001],
                 transition_rel_de=10.0)      # threshold that kills auto-detection
    assert len(forced.transitions) == 1
    assert abs(forced.transitions[0]['p_tr'] - P_TR) / P_TR < 1e-6

    auto_off = EOS(dict(eos.data_dict), eos.colnames, transition_rel_de=10.0)
    assert auto_off.transitions == []


# ---------------------------------------------------------------- Issue 2
def test_hybrid_transition_is_detected():
    eos = EOS.from_file(HYBRID)
    assert len(eos.transitions) == 1
    t = eos.transitions[0]
    assert abs(t['p_tr'] - P_TR) / P_TR < 1e-6
    assert abs(t['e_low'] - E_LOW) / E_LOW < 1e-6
    assert abs(t['e_high'] - E_HIGH) / E_HIGH < 1e-6
    assert t['delta_e'] > 0
    assert eos.n_segments() == 2


def test_eps_is_branch_resolved_at_the_transition():
    """eps(P_tr) is double-valued; the caller picks the branch, not the interpolator."""
    eos = EOS.from_file(HYBRID)
    assert abs(eos.get_energy_density(P_TR, segment=0) - E_LOW) / E_LOW < 1e-6
    assert abs(eos.get_energy_density(P_TR, segment=1) - E_HIGH) / E_HIGH < 1e-6

    # Asking for a branch just past the transition stays on that branch
    assert eos.get_energy_density(P_TR * 1.001, segment=0) == eos.get_energy_density(P_TR, segment=0)
    assert eos.get_energy_density(P_TR * 0.999, segment=1) == eos.get_energy_density(P_TR, segment=1)

    assert eos.segment_for_pressure(P_TR * 0.5) == 0
    assert eos.segment_for_pressure(P_TR * 2.0) == 1
    assert eos.segment_for_pressure(P_TR, prefer='high') == 1
    assert eos.segment_for_pressure(P_TR, prefer='low') == 0


def test_plateau_row_order_is_deterministic():
    """A Maxwell plateau must load identically however the file orders its rows.

    np.argsort defaults to quicksort, which is not stable, so the two
    equal-pressure rows used to come out in an order that depended on the array
    length: the same physics in a slightly longer table loaded with the phases
    swapped.
    """
    lines = [l for l in open(HYBRID) if not l.startswith('#') and l.strip()]
    rows = [l.split(',') for l in lines]
    p = np.array([float(r[0]) for r in rows])
    i0 = int(np.where(np.diff(p) == 0)[0][0])

    swapped = rows[:i0] + [rows[i0 + 1], rows[i0]] + rows[i0 + 2:]
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False) as fh:
        fh.write('# p,e,muB,phase\n')
        fh.writelines(','.join(r) for r in swapped)
        path = fh.name
    try:
        a, b = EOS.from_file(HYBRID), EOS.from_file(path)
        assert len(b.transitions) == 1
        for key in ('p_tr', 'e_low', 'e_high', 'delta_e'):
            assert a.transitions[0][key] == b.transitions[0][key], key
        assert a.segments == b.segments
    finally:
        os.unlink(path)


def test_fdedp_is_not_contaminated_by_the_plateau():
    """A centered difference straddling the plateau divides finite de by ~0 dp.

    de/dp must stay comparable to its neighbours on both sides; the physical
    delta function belongs in the matching condition, not in this array.
    """
    eos = EOS.from_file(HYBRID)
    t = eos.transitions[0]
    lo, hi = t['lo'], t['hi']
    f = eos.fdedp
    assert np.all(np.isfinite(f))
    # within a factor of 2 of the neighbour inside the same phase
    assert 0.5 < f[lo] / f[lo - 1] < 2.0, f'hadronic edge de/dp = {f[lo]}'
    assert 0.5 < f[hi] / f[hi + 1] < 2.0, f'quark edge de/dp = {f[hi]}'


# ---------------------------------------------------------------- Issue 1
def test_y_jump_matches_the_analytic_matching_condition():
    """y(r_d^+) = y(r_d^-) - 4 pi r_d^3 Delta_eps / (m + 4 pi r_d^3 p)."""
    r_d, delta_e = 6.0, 3.0e-4
    M, p, H, beta = 1.2, P_TR, 24.0, 5.0
    out = TidalCalculator._apply_transition_jump([M, p, H, beta], r_d, delta_e)

    y_minus = r_d * beta / H
    expected = y_minus - 4.0 * np.pi * r_d**3 * delta_e / (M + 4.0 * np.pi * r_d**3 * p)
    y_plus = r_d * out[3] / H

    assert abs(y_plus - expected) < 1e-12
    assert y_plus < y_minus                      # the shift is negative
    assert out[0] == M and out[1] == p and out[2] == H   # only beta moves


def test_jump_lowers_y_and_raises_lambda_for_a_quark_core():
    """Omitting the matching condition biases Lambda low for hybrid stars."""
    tc = _calculator(HYBRID)
    real = TidalCalculator._apply_transition_jump
    try:
        TidalCalculator._apply_transition_jump = staticmethod(
            lambda s, r, d: np.asarray(s, dtype=float))
        without = tc.compute(2.0e-4)
        TidalCalculator._apply_transition_jump = staticmethod(real)
        with_jump = tc.compute(2.0e-4)
    finally:
        TidalCalculator._apply_transition_jump = staticmethod(real)

    assert with_jump['y_R'] < without['y_R']
    assert with_jump['Lambda'] > without['Lambda']
    # the effect is several percent, not round-off
    assert (with_jump['Lambda'] / without['Lambda'] - 1.0) > 0.05

    # The jump acts on the tidal variables only; the structure is unchanged.
    # M and R still move a little, because odeint advances all four variables
    # under one shared error controller, so perturbing beta nudges the step
    # sizes and hence which grid point the surface lands on.  Tolerances here
    # are a few times the dr = 1e-3 km grid, not round-off.
    assert abs(with_jump['M_solar'] / without['M_solar'] - 1.0) < 1e-6
    assert abs(with_jump['R'] - without['R']) < 0.02


def test_lambda_is_insensitive_to_table_resolution_near_the_transition():
    """Adding hadronic rows below P_tr changes resolution, not physics."""
    lines = [l for l in open(HYBRID) if not l.startswith('#') and l.strip()]
    rows = [l.strip().split(',') for l in lines]
    p = np.array([float(r[0]) for r in rows])
    i0 = int(np.where(np.diff(p) == 0)[0][0])

    import tempfile
    results = []
    for n_extra in (0, 4, 16):
        lo, hi = rows[i0 - 1], rows[i0]
        extra = []
        for k in range(1, n_extra + 1):
            f = k / (n_extra + 1.0)
            extra.append(['%.17e' % (float(lo[0]) + f * (float(hi[0]) - float(lo[0]))),
                          '%.17e' % (float(lo[1]) + f * (float(hi[1]) - float(lo[1]))),
                          lo[2], lo[3]])
        merged = rows[:i0] + extra + rows[i0:]
        with tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False) as fh:
            fh.write('# p,e,muB,phase\n')
            fh.writelines(','.join(r) + '\n' for r in merged)
            path = fh.name
        try:
            results.append(_calculator(path).compute(2.0e-4)['Lambda'])
        finally:
            os.unlink(path)

    spread = (max(results) - min(results)) / np.mean(results)
    assert spread < 1e-3, f'Lambda varies with table resolution: {results}'


# ------------------------------------------------- single-phase regression
def test_dd2_reference_values():
    """DD2 must be unaffected by any of the hybrid machinery.

    Reference values from the C++ port, RK4 with dr = 1e-3 km.
    """
    eos = EOS.from_file(DD2)
    tc = TidalCalculator(TOVSolver(eos, r_max=30.0, dr=0.001))
    pcs = np.logspace(np.log10(1e-6), np.log10(eos.get_pressure_range()[1]), 250)

    M, R, L = [], [], []
    for pc in pcs:
        r = tc.compute(pc)
        if r and r['M_solar'] > 0.05:
            M.append(r['M_solar']); R.append(r['R']); L.append(r['Lambda'])
    M, R, L = np.array(M), np.array(R), np.array(L)

    i = int(np.argmax(M))
    stable = slice(0, i + 1)
    r14 = np.interp(1.4, M[stable], R[stable])
    # interpolate in log Lambda: Lambda ~ M^-6, so linear interpolation
    # under-samples badly (see the sampling caveat in the issue notes)
    l14 = np.exp(np.interp(1.4, M[stable], np.log(L[stable])))

    assert abs(M[i] - 2.4227) < 0.01, f'M_max = {M[i]}'
    assert abs(r14 - 13.234) < 0.05, f'R(1.4) = {r14}'
    assert abs(l14 - 709.2) / 709.2 < 0.05, f'Lambda(1.4) = {l14}'


def _main():
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith('test_') and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print('  PASS  %s' % name)
        except AssertionError as exc:
            failed += 1
            print('  FAIL  %s\n        %s' % (name, exc))
        except Exception as exc:                       # noqa: BLE001
            failed += 1
            print('  ERROR %s\n        %r' % (name, exc))
    print('\n%d/%d passed' % (len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(_main())

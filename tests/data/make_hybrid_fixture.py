"""Maxwell-construct the toy CSC quark EoS onto DD2 -> hybrid test fixture."""
import numpy as np

REPO = '/Users/hoseingholami/code/202602/TOVExtravaganza/'
MEV_FM3 = 1.323790e-06

def load(fn):
    rows = []
    for line in open(REPO + fn):
        if line.startswith('#') or not line.strip():
            continue
        rows.append([float(x) for x in line.split(',')])
    return np.array(rows)

dd2, csc = load('inputCode/hsdd2.csv'), load('inputCode/csc.csv')
p_h, e_h, n_h = dd2[:, 0], dd2[:, 1], dd2[:, 2]
p_q, e_q, mu_q = csc[:, 0], csc[:, 1], csc[:, 2] * 3.0
mu_h = (e_h + p_h) / MEV_FM3 / n_h

lo, hi = max(mu_h.min(), mu_q.min()), min(mu_h.max(), mu_q.max())
g = np.linspace(lo, hi, 400000)
d = np.interp(g, mu_q, p_q) - np.interp(g, mu_h, p_h)
i = np.where(np.diff(np.sign(d)) != 0)[0][0]
# refine by linear root of d
mu_tr = g[i] - d[i] * (g[i+1] - g[i]) / (d[i+1] - d[i])
P_tr = float(np.interp(mu_tr, mu_h, p_h))
e_lo = float(np.interp(mu_tr, mu_h, e_h))
e_hi = float(np.interp(mu_tr, mu_q, e_q))
print('mu_tr = %.4f MeV   P_tr = %.8e   e_lo = %.8e  e_hi = %.8e  de/e = %.4f'
      % (mu_tr, P_tr, e_lo, e_hi, (e_hi - e_lo) / e_lo))

# hadronic branch strictly below P_tr, quark branch strictly above
mh = p_h < P_tr * (1 - 1e-12)
mq = p_q > P_tr * (1 + 1e-12)
P = np.concatenate([p_h[mh], [P_tr, P_tr], p_q[mq]])
E = np.concatenate([e_h[mh], [e_lo, e_hi], e_q[mq]])
phase = ['Hadronic'] * mh.sum() + ['Hadronic', 'Quark'] + ['Quark'] * mq.sum()
MU = np.concatenate([mu_h[mh], [mu_tr, mu_tr], mu_q[mq]])

out = REPO + 'tests/data/hybrid_dd2_csc.csv'
with open(out, 'w') as f:
    f.write('# p(code_units), e(code_units) => first two columns, plus original columns afterward\n')
    f.write('# Maxwell construction: DD2 (hsdd2.csv) <-> toy CSC quark (csc.csv)\n')
    f.write('# P_tr = %.8e code, mu_B,tr = %.4f MeV, de/e = %.4f\n' % (P_tr, mu_tr, (e_hi - e_lo) / e_lo))
    f.write('# p (code_units),epsilon (code_units),muB,phase\n')
    for p, e, m, ph in zip(P, E, MU, phase):
        f.write('%.6e,%.6e,%.6f,%s\n' % (p, e, m, ph))
print('wrote', out, len(P), 'rows')

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

plt.style.use('seaborn-poster')

def ode(t, x):
    dxdt = np.zeros(x.shape)
    ka1 = 0.8
    Km1 = 1.0
    kd1 = 0.06
    ka2 = 0.95
    Km2 = 1.0
    kd2 = 0.7
    dxdt[0] = ka1/(x[1]**4 + Km1**4) - kd1*x[0]
    dxdt[1] = ka2*x[1]*x[0]**2/(x[0]**2 + Km2**2) - kd2*x[1]
    return dxdt

t_eval = np.arange(0, 100, 1)
sol = solve_ivp(ode, [0, 100], [1, 1], t_eval=t_eval)


plt.figure(figsize = (12, 4))
plt.plot(sol.t, sol.y.T)
plt.xlabel('t')
plt.ylabel('x(t)')
plt.legend(["A", "B"])
plt.tight_layout()
plt.show()
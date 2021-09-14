import numpy as np
from scipy.integrate import odeint
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"

# Solve the ODE of 2-node negative feedback loop model
def ode(y, t):
    dydt = np.zeros(y.shape)
    ka1 = 0.8
    Km1 = 1.0
    kd1 = 0.06
    ka2 = 0.95
    Km2 = 1.0
    kd2 = 0.7
    dydt[0] = ka1/(y[1]**4 + Km1**4) - kd1*y[0]
    dydt[1] = ka2*y[1]*y[0]**2/(y[0]**2 + Km2**2) - kd2*y[1]
    return dydt

t = np.arange(0, 100, 1)
y0 = np.array([1., 1.])
y = odeint(ode, y0, t)


fig = plt.figure(figsize=(8, 4))
plt.plot(t, y)
plt.xlabel('Time', fontsize=24, labelpad=10)
plt.ylabel('X(t)', fontsize=24, labelpad=10)
plt.legend(["A", "B"], fontsize=24)
plt.tight_layout()
plt.show()
plt.savefig("2nnfl-time-series.png", dpi=300)
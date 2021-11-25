import numpy as np
from scipy.integrate import odeint
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"

# Solve the ODE of Lorenz system
def ode(s, t):
    sigma = 10
    beta = 2.667
    rho = 28
    x, y, z = s
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

t = np.arange(0, 50, 0.1)
y0 = np.array([0, 1, 1.05])
y = odeint(ode, y0, t)


fig = plt.figure(figsize=(8, 4))
plt.plot(t, y)
plt.xlabel('Time', fontsize=24, labelpad=10)
plt.ylabel('X(t)', fontsize=24, labelpad=10)
plt.legend(["A", "B", "C"], fontsize=24, loc="upper right")
plt.tight_layout()
plt.show()
plt.savefig("lorenz-time-series.png", dpi=300)
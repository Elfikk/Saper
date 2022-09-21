import matplotlib.pyplot as plt
import numpy as np

returns_directory = "checkpoint/returns.txt"
eval_interval = 100

returns = []

with open(returns_directory, "r") as f:
    for line in f:
        returns.append(float(line))

steps = np.arange(0, len(returns), 1) * 50
returns = np.array(returns)

plt.plot(steps, returns)
plt.show()
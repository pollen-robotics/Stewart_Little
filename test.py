import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Création des données de base
x = np.linspace(-4, 4, 100)
y = np.linspace(-4, 4, 100)
x, y = np.meshgrid(x, y)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

# Surface initiale
z = np.sin(np.sqrt(x**2 + y**2))
surf = ax.plot_surface(x, y, z, cmap="viridis")


def update(frame):
    ax.clear()
    z = np.sin(np.sqrt(x**2 + y**2) - 0.3 * frame)
    ax.plot_surface(x, y, z, cmap="viridis")
    ax.set_zlim(-1, 1)
    ax.set_title("Graphique 3D animé avec matplotlib")


# Animation
ani = FuncAnimation(fig, update, frames=60, interval=50)

plt.show()

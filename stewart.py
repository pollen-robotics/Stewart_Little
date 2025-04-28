import os
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# === PARAMÈTRES GÉNÉRAUX ===
R = 155e-3  # Rayon de la base
r = 80e-3  # Rayon de la plateforme mobile
lab = 415e-3  # Longueur du corps de l'actionneur
z0 = 665e-3
zmin, zmax = 415e-3, 915e-3
roll_min, roll_max = -45, 45
pitch_min, pitch_max = -45, 45

B_offset, P_offset, L_offset = 10e-3, 30e-3, 5e-3

# === POSITION DES POINTS Bi ET Pi (CONFIGURATION 3-3) ===
omega, sigma = 10, 50

angles = np.array([0, 120, 240])
B = np.array(
    [
        [-R * np.cos(np.radians(a - omega)), R * np.sin(np.radians(a - omega)), 0]
        for a in angles
    ]
    + [
        [-R * np.cos(np.radians(a + omega)), R * np.sin(np.radians(a + omega)), 0]
        for a in angles
    ]
)

P0 = np.array(
    [
        [-r * np.cos(np.radians(a - sigma)), r * np.sin(np.radians(a - sigma)), 0]
        for a in angles
    ]
    + [
        [-r * np.cos(np.radians(a + sigma)), r * np.sin(np.radians(a + sigma)), 0]
        for a in angles
    ]
)


# === ROTATION MATRICES ===
def rotationX(theta):
    return np.array(
        [
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta), np.cos(theta)],
        ]
    )


def rotationY(psi):
    return np.array(
        [[np.cos(psi), 0, np.sin(psi)], [0, 1, 0], [-np.sin(psi), 0, np.cos(psi)]]
    )


def rotationZ(phi):
    return np.array(
        [[np.cos(phi), -np.sin(phi), 0], [np.sin(phi), np.cos(phi), 0], [0, 0, 1]]
    )


# === CALCUL DES VECTEURS ET LONGUEURS ===
def VecteurLi(Rot_BtoP, P, B, T):
    return T + (Rot_BtoP @ P) - B


def ValeurLi(VecteurLi):
    return np.linalg.norm(VecteurLi)


# === TRACE D'UN CERCLE EN 3D ===
def plot_circle(ax, center, radius, normal, color="k", linestyle="--"):
    alpha = np.linspace(0, 2 * np.pi, 100)
    normal = normal / np.linalg.norm(normal)
    v = np.array([1, 0, 0]) if abs(normal[0]) < abs(normal[1]) else np.array([0, 1, 0])
    v = v - v.dot(normal) * normal
    v /= np.linalg.norm(v)
    w = np.cross(normal, v)
    circle = center[:, None] + radius * (
        v[:, None] * np.cos(alpha) + w[:, None] * np.sin(alpha)
    )
    ax.plot(circle[0], circle[1], circle[2], color=color, linestyle=linestyle)


# === ANIMATION DE LA PLATEFORME ===
def linear_actuator_trajectory(roll_amp, pitch_amp, yaw_amp, xf, yf, zf, steps):
    fig = plt.figure(figsize=(18, 14))
    ax = fig.add_subplot(111, projection="3d")

    def update(frame):
        ax.cla()

        # Paramétrage de la trajectoire (involute)
        t = 3 * 2 * np.pi * frame / steps
        x = 5e-3 * (np.cos(t) + t * np.sin(t))
        y = 5e-3 * (np.sin(t) - t * np.cos(t))
        z = z0
        roll = pitch = yaw = 0

        T = np.array([x, y, z])
        Rot_BtoP = (
            rotationY(np.radians(pitch))
            @ rotationX(np.radians(roll))
            @ rotationZ(np.radians(yaw))
        )

        VectorL, P, L, C = [], [], [], []

        for i in range(6):
            VLi = VecteurLi(Rot_BtoP, P0[i], B[i], T)
            Pi = B[i] + VLi
            li = ValeurLi(VLi)
            ci = li - lab

            VectorL.append(VLi)
            P.append(Pi)
            L.append(li)
            C.append(ci)

        P = np.array(P)

        # Affichage
        ax.scatter(B[:, 0], B[:, 1], B[:, 2], color="#386480", s=100, label="Base")
        ax.scatter(
            P[:, 0], P[:, 1], P[:, 2], color="#f2887c", s=100, label="Plateforme"
        )

        for i in range(6):
            ax.plot(
                [B[i, 0], P[i, 0]],
                [B[i, 1], P[i, 1]],
                [B[i, 2], P[i, 2]],
                "#5f7fbf",
                lw=3,
                linestyle="--",
            )
            ax.plot(
                [B[i, 0], B[i, 0] + lab / L[i] * (P[i, 0] - B[i, 0])],
                [B[i, 1], B[i, 1] + lab / L[i] * (P[i, 1] - B[i, 1])],
                [B[i, 2], B[i, 2] + lab / L[i] * (P[i, 2] - B[i, 2])],
                "#72bdba",
                lw=4,
            )
            ax.plot(
                [B[i, 0] + lab / L[i] * (P[i, 0] - B[i, 0]), P[i, 0]],
                [B[i, 1] + lab / L[i] * (P[i, 1] - B[i, 1]), P[i, 1]],
                [B[i, 2] + lab / L[i] * (P[i, 2] - B[i, 2]), P[i, 2]],
                "#ffd783",
                lw=4,
            )

            ax.text(
                *B[i] + B_offset, f"B{i+1}", color="#386480", fontsize=12, weight="bold"
            )
            ax.text(
                P[i, 0],
                P[i, 1],
                P[i, 2] + P_offset,
                f"P{i+1}",
                color="#f2887c",
                fontsize=12,
                weight="bold",
            )

        plot_circle(ax, np.array([0, 0, 0]), R, np.array([0, 0, 1]), "#386480", "--")
        plot_circle(ax, T, r, Rot_BtoP @ np.array([0, 0, 1]), "#f2887c", "--")

        ax.set_box_aspect([1, 1, 1])
        ax.set_xlim([-0.2, 0.2])
        ax.set_ylim([-0.2, 0.2])
        ax.set_zlim([0, 1])
        ax.set_xlabel("X Axis (m)", fontsize=15, labelpad=18)
        ax.set_ylabel("Y Axis (m)", fontsize=15, labelpad=18)
        ax.set_zlabel("Z Axis (m)", fontsize=15, labelpad=18)
        ax.tick_params(axis="both", which="major", labelsize=12)

        info_text = (
            f"Roll: {roll:.2f}°\nPitch: {pitch:.2f}°\nYaw: {yaw:.2f}°\nHeight: {z:.4f} m\n"
            + "\n".join([f"Stroke C{i+1}: {C[i]:.4f} m" for i in range(6)])
        )
        ax.text2D(
            -0.26,
            0.475,
            info_text,
            transform=ax.transAxes,
            fontsize=15,
            weight="book",
            fontstyle="italic",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.15),
        )

        ax.legend(
            loc=(-0.265, 0.065), prop={"size": 15, "weight": "book", "style": "italic"}
        )

    result_animation = "Trajectory Result P-6DoF Actuators"
    os.makedirs(result_animation, exist_ok=True)
    gif_path = os.path.join(result_animation, "Trajectory P-6DoF Actuators.gif")

    ani = FuncAnimation(fig, update, frames=range(steps), repeat=False)
    # ani.save(gif_path, writer="pillow", fps=40)
    plt.show()


# === LANCEMENT DE L’ANIMATION ===
linear_actuator_trajectory(
    roll_amp=30, pitch_amp=30, yaw_amp=10, xf=0.1, yf=0.05, zf=0.02, steps=300
)

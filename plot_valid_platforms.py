import json
import numpy as np
import matplotlib.pyplot as plt
from src.stewart_controller import Stewart_Platform


# --- Charger tous les designs depuis un JSON ---
def load_designs(filepath):
    with open(filepath, "r") as f:
        designs = json.load(f)
    return designs


# --- Créer un Stewart_Platform à partir d'un design ---
def create_platform_from_design(design):
    platform = Stewart_Platform(
        design["r_B"],
        design["r_P"],
        design["lhl"],
        design["ldl"],
        design["Psi_B"],
        design["Psi_P"],
        5 * np.pi / 6,  # ref_rotation fixé ici
    )
    return platform


# --- Initialiser la plateforme (calculate pour Z=0) ---
def initialize_platform(platform):
    tx, ty, tz = 0, 0, 0  # position neutre
    rx, ry, rz = 0, 0, 0  # pas de rotation
    platform.calculate(np.array([tx, ty, tz]), np.array([rx, ry, rz]))


# --- Plotter la plateforme ---
def plot_platform(platform):
    fig, ax = plt.subplots()
    ax = platform.plot_platform()
    plt.draw()
    plt.show()


# --- Main ---
if __name__ == "__main__":
    # === Modifier ici ===
    design_filepath = "valid_designs.json"

    # Charger tous les designs
    designs = load_designs(design_filepath)

    # Afficher les designs disponibles
    print(f"Il y a {len(designs)} designs disponibles.\n")
    # for idx, design in enumerate(designs):
    #    print(f"[{idx}] r_B={design['r_B']}cm, r_P={design['r_P']}cm, lhl={design['lhl']}cm, ldl={design['ldl']}cm")

    # Choisir un design
    choice = int(input("\nEntrez le numéro du design à plotter : "))

    # Créer et plotter le design choisi
    selected_design = designs[choice]
    platform = create_platform_from_design(selected_design)
    initialize_platform(platform)
    plot_platform(platform)

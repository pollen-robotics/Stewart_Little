import json
import numpy as np
import matplotlib.pyplot as plt
import os
from src.stewart_controller import Stewart_Platform
from PIL import Image


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
def plot_platform(platform, design, save_path):
    fig, ax = plt.subplots()
    ax = platform.plot_platform()
    title = (
        f"r_B={design['r_B']}mm, r_P={design['r_P']}mm, "
        f"lhl={design['lhl']}mm, ldl={design['ldl']}mm\n"
        f"Psi_B={np.degrees(design['Psi_B']):.1f}°, Psi_P={np.degrees(design['Psi_P']):.1f}°"
    )
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)


# --- Générer un GIF animé à partir des PNG ---
def create_gif_from_pngs(folder, gif_name="all_designs.gif", duration=300):
    # Récupérer tous les fichiers .png triés
    images = []
    files = sorted([f for f in os.listdir(folder) if f.endswith(".png")])
    for filename in files:
        img_path = os.path.join(folder, filename)
        img = Image.open(img_path)
        images.append(img)

    if images:
        gif_path = os.path.join(folder, gif_name)
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0,
        )
        print(f"GIF généré : {gif_path}")
    else:
        print("Aucune image trouvée pour créer le GIF.")


# --- Main ---
if __name__ == "__main__":
    design_filepath = "valid_designs.json"
    base_output_folder = "plots"
    output_folder = base_output_folder

    # Vérifier si 'plots' existe déjà, sinon incrémenter plots_1, plots_2, etc.
    counter = 1
    while os.path.exists(output_folder):
        output_folder = f"{base_output_folder}_{counter}"
        counter += 1

    os.makedirs(output_folder)

    designs = load_designs(design_filepath)

    print(
        f"Il y a {len(designs)} designs. Génération des plots dans '{output_folder}/'..."
    )

    for idx, design in enumerate(designs):
        platform = create_platform_from_design(design)
        initialize_platform(platform)
        save_path = os.path.join(output_folder, f"design_{idx:03d}.png")
        plot_platform(platform, design, save_path)

    create_gif_from_pngs(output_folder)

    print(f"Tous les designs ont été enregistrés dans '{output_folder}/'.")
    print("GIF animé créé.")

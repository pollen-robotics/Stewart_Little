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


# --- Créer un Stewart_Platform à partir d'un design + test ---
def create_platform_from_design_test(design, test):
    platform = Stewart_Platform(
        design["r_B"],
        design["r_P"],
        design["lhl"],
        design["ldl"],
        test["Psi_B_rad"],
        test["Psi_P_rad"],
        5 * np.pi / 6,
    )
    return platform


# --- Initialiser la plateforme (calculate pour Z=0) ---
def initialize_platform(platform):
    tx, ty, tz = 0, 0, 0  # position neutre
    rx, ry, rz = 0, 0, 0  # pas de rotation
    platform.calculate(np.array([tx, ty, tz]), np.array([rx, ry, rz]))


# --- Plotter la plateforme ---
def plot_platform(platform, design, test, save_path):
    fig, ax = plt.subplots()
    ax = platform.plot_platform()

    # Construire un titre complet
    title = (
        f"r_B={design['r_B']}mm, r_P={design['r_P']}mm, "
        f"lhl={design['lhl']}mm, ldl={design['ldl']}mm\n"
        f"Psi_B={np.degrees(test['Psi_B_rad']):.1f}°, Psi_P={np.degrees(test['Psi_P_rad']):.1f}°\n"
        f"Max Roll: {test['max_roll_deg']}°, Max Pitch: {test['max_pitch_deg']}°\n"
    )

    # Ajouter les sensibilités si présentes
    if "sensitivity" in test and test["sensitivity"] is not None:
        sens = test["sensitivity"]
        title += (
            f"Sensibilité: ΔX={sens['delta_per_mm_x']:.2f}°/mm, "
            f"ΔY={sens['delta_per_mm_y']:.2f}°/mm, "
            f"ΔZ={sens['delta_per_mm_z']:.2f}°/mm"
        )

    ax.set_title(title, fontsize=8)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)


# --- Générer un GIF animé à partir des PNG ---
def create_gif_from_pngs(folder, gif_name="all_designs.gif", duration=300):
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
    design_filepath = "study_results.json"
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
        f"Chargé {len(designs)} designs. Génération des plots dans '{output_folder}/'..."
    )

    # Construire une liste de tous les couples (design, test)
    design_test_pairs = []
    for design in designs:
        for test in design["tests"]:
            design_test_pairs.append((design, test))

    total_pairs = len(design_test_pairs)

    # Limiter à 200 plots max
    max_images = 200
    if total_pairs <= max_images:
        selected_indices = list(range(total_pairs))
    else:
        selected_indices = np.linspace(0, total_pairs - 1, max_images, dtype=int)

    # Plotter les plateformes sélectionnées
    for plot_idx, pair_idx in enumerate(selected_indices):
        design, test = design_test_pairs[pair_idx]
        platform = create_platform_from_design_test(design, test)
        initialize_platform(platform)
        save_path = os.path.join(output_folder, f"design_{plot_idx:03d}.png")
        plot_platform(platform, design, test, save_path)

    create_gif_from_pngs(output_folder)

    print(f"Tous les designs ont été enregistrés dans '{output_folder}/'.")
    print("GIF animé créé.")

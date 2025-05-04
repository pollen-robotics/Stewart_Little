import os
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from src.stewart_controller import Stewart_Platform

# --- Paramètres géométriques fixes ---
r_B = 50
r_P = 25
lhl = 80
ldl = 130

input_file = "joint_config_amplitudes.json"
output_folder = "platform_plots"
gif_name = "platforms.gif"
max_images = 50

# --- Chargement des configurations ---
with open(input_file, "r") as f:
    configs = json.load(f)

# --- Créer un dossier unique ---
counter = 1
base_folder = output_folder
while os.path.exists(output_folder):
    output_folder = f"{base_folder}_{counter}"
    counter += 1
os.makedirs(output_folder)

# --- Limiter à max_images plateformes ---
if len(configs) > max_images:
    indices = np.linspace(0, len(configs) - 1, max_images, dtype=int)
    selected = [configs[i] for i in indices]
else:
    selected = configs


# --- Plotter une plateforme ---
def initialize_platform(platform):
    platform.calculate(np.array([0, 0, 0]), np.array([0, 0, 0]))


def format_stability(stab):
    if not stab or stab["mean_motor_delta_for_5deg_roll"] is None:
        return "Stability: N/A"
    return (
        f"Δmoteurs pour 5° RPY:\n"
        f"Roll ≈ {stab['mean_motor_delta_for_5deg_roll']:.2f}°, "
        f"Pitch ≈ {stab['mean_motor_delta_for_5deg_pitch']:.2f}°"
    )


# --- Génération des plots ---
print(f"Génération de {len(selected)} plateformes dans '{output_folder}'...")

for idx, conf in enumerate(selected):
    Psi_B = conf["Psi_B_rad"]
    Psi_P = conf["Psi_P_rad"]

    platform = Stewart_Platform(r_B, r_P, lhl, ldl, Psi_B, Psi_P, 5 * np.pi / 6)
    initialize_platform(platform)

    fig, ax = plt.subplots()
    ax = platform.plot_platform()

    stability_txt = format_stability(conf.get("stability"))

    ax.set_title(
        f"Ψ_B={np.degrees(Psi_B):.1f}°, Ψ_P={np.degrees(Psi_P):.1f}°\n"
        f"Max R/P/Y = {conf['max_roll_deg']}° / {conf['max_pitch_deg']}° / {conf['max_yaw_deg']}°\n"
        f"{stability_txt}",
        fontsize=8,
    )

    plt.tight_layout()
    save_path = os.path.join(output_folder, f"platform_{idx:03d}.png")
    plt.savefig(save_path)
    plt.close(fig)

# --- Génération du GIF ---
print("Création du GIF...")

images = []
files = sorted([f for f in os.listdir(output_folder) if f.endswith(".png")])
for file in files:
    img_path = os.path.join(output_folder, file)
    img = Image.open(img_path)
    images.append(img)

if images:
    gif_path = os.path.join(output_folder, gif_name)
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=400,
        loop=0,
    )
    print(f"GIF généré : {gif_path}")
else:
    print("Aucune image trouvée pour créer le GIF.")

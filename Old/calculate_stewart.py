import numpy as np
import warnings
from src.stewart_controller import Stewart_Platform
import json
import os

# Définir les plages de variations
r_B_values = np.linspace(30, 100, 8)  # entre 3cm et 10cm (8 valeurs)
r_P = 25  # fixe
lhl_values = np.linspace(20, 100, 9)  # entre 2cm et 10cm
ldl_values = np.linspace(50, 150, 6)  # entre 5cm et 15cm
# Psi_B_values = np.linspace(0, 2 * np.pi, 12)  # 0 à 360° en rad (12 valeurs)
# Psi_P_values = np.linspace(0, 2 * np.pi, 12)  # 0 à 360° en rad (12 valeurs)
Psi_B = 0.2269
Psi_P = 0.82

# Stockage des designs valides
valid_designs = []

# Désactiver warnings pour arcsin mais capturer les erreurs
warnings.filterwarnings("ignore", category=RuntimeWarning)


# Fonction robuste pour essayer de calculer des angles
def safe_calculate(platform, pos, rot):
    try:
        angles = platform.calculate(pos, rot)
        if np.any(np.isnan(angles)):
            return None
        return angles
    except Exception:
        return None


# Fonction pour vérifier que les angles moteurs restent dans [0, 110] degrés
def check_motor_angles(angles_rad):
    angles_deg = np.degrees(angles_rad)
    return np.all(np.abs(angles_deg) <= 110)


# Boucle sur toutes les combinaisons
for r_B in r_B_values:
    for lhl in lhl_values:
        for ldl in ldl_values:
            # for Psi_B in Psi_B_values:
            # for Psi_P in Psi_P_values:
            platform = Stewart_Platform(r_B, r_P, lhl, ldl, Psi_B, Psi_P, 5 * np.pi / 6)

            # Scénarios de test
            test_cases = [
                (np.array([0, 0, 0]), np.array([0, 0, 0])),
                (np.array([0, 0, 30]), np.array([0, 0, 0])),
                (np.array([0, 0, -30]), np.array([0, 0, 0])),
                (np.array([0, 0, 30]), np.array([5 * np.pi / 180, 0, 0])),
                (np.array([0, 0, 30]), np.array([0, 5 * np.pi / 180, 0])),
                (np.array([0, 0, 30]), np.array([0, 0, 5 * np.pi / 180])),
                (
                    np.array([0, 0, 30]),
                    np.array([0, 0, 60 * np.pi / 180]),
                ),  # +60° yaw
                (
                    np.array([0, 0, 30]),
                    np.array([0, 0, -60 * np.pi / 180]),
                ),  # -60° yaw
            ]

            all_ok = True
            for pos, rot in test_cases:
                angles = safe_calculate(platform, pos, rot)
                if angles is None or not check_motor_angles(angles):
                    all_ok = False
                    break

            if not all_ok:
                continue

            # Design valide
            valid_designs.append(
                {
                    "r_B": r_B,
                    "r_P": r_P,
                    "lhl": lhl,
                    "ldl": ldl,
                    "Psi_B": Psi_B,
                    "Psi_P": Psi_P,
                }
            )

print(f"Nombre de designs valides : {len(valid_designs)}")

# --- Sauvegarder les résultats en gérant les conflits de fichiers ---
base_filename = "valid_designs"
filename = base_filename + ".json"
counter = 1
while os.path.exists(filename):
    filename = f"{base_filename}_{counter}.json"
    counter += 1

with open(filename, "w") as f:
    json.dump(valid_designs, f, indent=4)

print(f"Designs valides sauvegardés dans '{filename}'.")

import numpy as np
import warnings
import os
import json
from src.stewart_controller import Stewart_Platform

# Désactiver warnings pour arcsin
warnings.filterwarnings("ignore", category=RuntimeWarning)


# --- Fonctions auxiliaires ---
def safe_calculate(platform, pos, rot):
    try:
        angles = platform.calculate(pos, rot)
        if np.any(np.isnan(angles)):
            return None
        return angles
    except Exception:
        return None


def check_motor_angles(angles_rad):
    angles_deg = np.degrees(angles_rad)
    return np.all(np.abs(angles_deg) <= 110)


def find_max_roll_pitch(platform):
    max_roll = 0
    max_pitch = 0
    pos = np.array([0, 0, 30])

    for roll_deg in range(0, 91, 1):
        rot = np.array([np.radians(roll_deg), 0, 0])
        angles = safe_calculate(platform, pos, rot)
        if angles is None or not check_motor_angles(angles):
            break
        max_roll = roll_deg

    for pitch_deg in range(0, 91, 1):
        rot = np.array([0, np.radians(pitch_deg), 0])
        angles = safe_calculate(platform, pos, rot)
        if angles is None or not check_motor_angles(angles):
            break
        max_pitch = pitch_deg

    return max_roll, max_pitch


def estimate_sensitivity(platform):
    pos0 = np.array([0, 0, 0])
    rot0 = np.array([0, 0, 0])

    angles_ref = safe_calculate(platform, pos0, rot0)
    if angles_ref is None:
        return None

    pos_dx = np.array([1, 0, 0])
    pos_dy = np.array([0, 1, 0])
    pos_dz = np.array([0, 0, 1])

    angles_dx = safe_calculate(platform, pos_dx, rot0)
    angles_dy = safe_calculate(platform, pos_dy, rot0)
    angles_dz = safe_calculate(platform, pos_dz, rot0)

    if any(a is None for a in (angles_dx, angles_dy, angles_dz)):
        return None

    delta_dx = np.mean(np.abs(np.degrees(angles_dx - angles_ref)))
    delta_dy = np.mean(np.abs(np.degrees(angles_dy - angles_ref)))
    delta_dz = np.mean(np.abs(np.degrees(angles_dz - angles_ref)))

    return {
        "delta_per_mm_x": delta_dx,
        "delta_per_mm_y": delta_dy,
        "delta_per_mm_z": delta_dz,
    }


# --- MAIN ---
if __name__ == "__main__":
    input_filename = "valid_designs.json"

    with open(input_filename, "r") as f:
        designs = json.load(f)

    print(f"Chargé {len(designs)} designs valides.")

    # --- FILTRAGE ---
    # Garde ceux avec r_B < 50mm
    designs = [d for d in designs if d["r_B"] < 50]

    # Puis prendre 1 sur 10
    designs = designs[::10]

    print(f"Après filtrage, {len(designs)} designs sélectionnés pour étude.")

    # --- Test cases sur Psi_B et Psi_P ---
    psi_tests = [
        (0, 0),
        (np.pi / 12, np.pi / 12),  # 15°
        (np.pi / 6, np.pi / 6),  # 30°
        (np.pi / 6, 0),  # asymétrique
        (0, np.pi / 6),
    ]

    study_results = []

    for design_idx, design in enumerate(designs):
        base_info = {
            "r_B": design["r_B"],
            "r_P": design["r_P"],
            "lhl": design["lhl"],
            "ldl": design["ldl"],
        }

        tests = []

        for Psi_B, Psi_P in psi_tests:
            platform = Stewart_Platform(
                design["r_B"],
                design["r_P"],
                design["lhl"],
                design["ldl"],
                Psi_B,
                Psi_P,
                5 * np.pi / 6,
            )

            max_roll, max_pitch = find_max_roll_pitch(platform)
            sensitivity = estimate_sensitivity(platform)

            tests.append(
                {
                    "Psi_B_rad": Psi_B,
                    "Psi_P_rad": Psi_P,
                    "Psi_B_deg": np.degrees(Psi_B),
                    "Psi_P_deg": np.degrees(Psi_P),
                    "max_roll_deg": max_roll,
                    "max_pitch_deg": max_pitch,
                    "sensitivity": sensitivity,
                }
            )

        study_results.append(
            {
                **base_info,
                "tests": tests,
            }
        )

    # --- Sauvegarde ---
    base_filename = "study_results"
    filename = base_filename + ".json"
    counter = 1
    while os.path.exists(filename):
        filename = f"{base_filename}_{counter}.json"
        counter += 1

    with open(filename, "w") as f:
        json.dump(study_results, f, indent=4)

    print(f"Etude sauvegardée dans '{filename}'.")

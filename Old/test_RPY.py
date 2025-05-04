import numpy as np
from src.stewart_controller import Stewart_Platform
import warnings
import json

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Paramètres géométriques fixes (plateforme "standard")
r_B = 50  # mm
r_P = 25  # mm
lhl = 80  # mm
ldl = 130  # mm

# Configurations de vérins à tester
psi_tests = [
    (0, 0),
    (np.pi / 12, np.pi / 12),  # 15°
    (np.pi / 6, np.pi / 6),  # 30°
    (np.pi / 6, 0),  # asymétrie
    (0, np.pi / 6),
]


# Utilitaires
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


def find_max_amplitude(platform, axis="roll"):
    pos = np.array([0, 0, 30])  # position fixe
    max_angle = 0
    for deg in range(0, 91, 1):
        rad = np.radians(deg)
        if axis == "roll":
            rot = np.array([rad, 0, 0])
        elif axis == "pitch":
            rot = np.array([0, rad, 0])
        elif axis == "yaw":
            rot = np.array([0, 0, rad])
        else:
            raise ValueError("Axis must be roll, pitch, or yaw")

        angles = safe_calculate(platform, pos, rot)
        if angles is None or not check_motor_angles(angles):
            break
        max_angle = deg
    return max_angle


def evaluate_stability_from_movement(platform, delta_deg=5):
    """Évalue la stabilité mécanique par la quantité de mouvement moteur nécessaire pour une rotation de la plateforme"""
    delta_rad = np.radians(delta_deg)
    pos = np.array([0, 0, 0])

    # Référence : pas de rotation
    rot0 = np.array([0, 0, 0])
    angles_ref = safe_calculate(platform, pos, rot0)
    if angles_ref is None:
        return None

    results = {}

    # Test Roll
    rot_roll = np.array([delta_rad, 0, 0])
    angles_roll = safe_calculate(platform, pos, rot_roll)
    if angles_roll is not None:
        delta = np.abs(np.degrees(angles_roll - angles_ref))
        results["mean_motor_delta_for_5deg_roll"] = np.mean(delta)
    else:
        results["mean_motor_delta_for_5deg_roll"] = None

    # Test Pitch
    rot_pitch = np.array([0, delta_rad, 0])
    angles_pitch = safe_calculate(platform, pos, rot_pitch)
    if angles_pitch is not None:
        delta = np.abs(np.degrees(angles_pitch - angles_ref))
        results["mean_motor_delta_for_5deg_pitch"] = np.mean(delta)
    else:
        results["mean_motor_delta_for_5deg_pitch"] = None

    return results


# Résultats
results = []

for psi_B, psi_P in psi_tests:
    platform = Stewart_Platform(
        r_B,
        r_P,
        lhl,
        ldl,
        psi_B,
        psi_P,
        5 * np.pi / 6,
    )

    max_roll = find_max_amplitude(platform, "roll")
    max_pitch = find_max_amplitude(platform, "pitch")
    max_yaw = find_max_amplitude(platform, "yaw")
    stability = evaluate_stability_from_movement(platform, 10)

    results.append(
        {
            "Psi_B_rad": psi_B,
            "Psi_P_rad": psi_P,
            "Psi_B_deg": np.degrees(psi_B),
            "Psi_P_deg": np.degrees(psi_P),
            "max_roll_deg": max_roll,
            "max_pitch_deg": max_pitch,
            "max_yaw_deg": max_yaw,
            "stability": stability,
        }
    )

# Affichage console
print("Étude de l'amplitude maximale selon les configurations de vérins :\n")
for res in results:
    print(
        f"Ψ_B = {res['Psi_B_deg']:.1f}°, Ψ_P = {res['Psi_P_deg']:.1f}°  →  "
        f"Roll = {res['max_roll_deg']}°, "
        f"Pitch = {res['max_pitch_deg']}°, "
        f"Yaw = {res['max_yaw_deg']}°"
    )

# Optionnel : sauvegarde JSON
with open("joint_config_amplitudes.json", "w") as f:
    json.dump(results, f, indent=4)

print("\nRésultats sauvegardés dans 'joint_config_amplitudes.json'")


# stat_processor.py

COMBAT_STATS = [
    "main_hand_damage", "off_hand_damage", "weapon_damage",
    "main_hand_efficiency", "off_hand_efficiency", "bodypart_damage", "armor_damage",
    "armor_penetration", "accuracy", "crit_chance", "crit_efficiency", "counter_chance", "fumble_chance",
    "skills_energy_cost", "spells_energy_cost", "cooldowns_duration", "bonus_range",
    "bleed_chance", "daze_chance", "stun_chance", "knockback_chance", "immobilization_chance",
    "stagger_chance", "life_drain", "energy_drain", "experience_gain"
]

SURVIVAL_STATS = [
    "max_health", "health_restoration", "healing_efficiency",
    "energy", "energy_restoration",
    "protection", "block_power", "block_chance", "block_power_recovery",
    "dodge_chance", "stealth", "noise_produced", "lockpicking", "disarming", "vision",
    "fortitude", "damage_reflection", "bleed_resistance", "control_resistance",
    "move_resistance", "hunger_resistance", "intoxication_resistance",
    "pain_resistance", "fatigue_resistance"
]

RESISTANCE_STATS = [
    "total_damage_taken", "physical_resistance",
    "slashing_resistance", "piercing_resistance", "crushing_resistance", "rending_resistance",
    "nature_resistance", "fire_resistance", "frost_resistance", "shock_resistance",
    "poison_resistance", "caustic_resistance",
    "magic_resistance", "arcane_resistance", "unholy_resistance", "sacred_resistance", "psionic_resistance"
]

MAGIC_STATS = [
    "magic_power", "backfire_chance", "backfire_damage",
    "miracle_chance", "miracle_potency",
    "pyromantic_power", "geomantic_power", "venomantic_power", "cryomantic_power", "electromagnetic_power",
    "arcanistic_power", "astromantic_power", "psionic_power", "chronomantic_power"
]

Head_Resistances = [
    "physical_resistance_head", "slashing_resistance_head", "piercing_resistance_head",
    "crushing_resistance_head", "rending_resistance_head", "nature_resistance_head",
    "fire_resistance_head", "frost_resistance_head", "shock_resistance_head",
    "poison_resistance_head", "caustic_resistance_head", "magic_resistance_head",
    "arcane_resistance_head", "unholy_resistance_head", "sacred_resistance_head",
    "psionic_resistance_head", "bleed_resistance_head"
]

Torso_Resistances = [
    "physical_resistance_torso", "slashing_resistance_torso", "piercing_resistance_torso",
    "crushing_resistance_torso", "rending_resistance_torso", "nature_resistance_torso",
    "fire_resistance_torso", "frost_resistance_torso", "shock_resistance_torso",
    "poison_resistance_torso", "caustic_resistance_torso", "magic_resistance_torso",
    "arcane_resistance_torso", "unholy_resistance_torso", "sacred_resistance_torso",
    "psionic_resistance_torso", "bleed_resistance_torso"
]

Hand_Resistances = [
    "physical_resistance_hand", "slashing_resistance_hand", "piercing_resistance_hand",
    "crushing_resistance_hand", "rending_resistance_hand", "nature_resistance_hand",
    "fire_resistance_hand", "frost_resistance_hand", "shock_resistance_hand",
    "poison_resistance_hand", "caustic_resistance_hand", "magic_resistance_hand",
    "arcane_resistance_hand", "unholy_resistance_hand", "sacred_resistance_hand",
    "psionic_resistance_hand", "bleed_resistance_hand"
]

Leg_Resistances = [
    "physical_resistance_leg", "slashing_resistance_leg", "piercing_resistance_leg",
    "crushing_resistance_leg", "rending_resistance_leg", "nature_resistance_leg",
    "fire_resistance_leg", "frost_resistance_leg", "shock_resistance_leg",
    "poison_resistance_leg", "caustic_resistance_leg", "magic_resistance_leg",
    "arcane_resistance_leg", "unholy_resistance_leg", "sacred_resistance_leg",
    "psionic_resistance_leg", "bleed_resistance_leg"
]

THRESHOLD_STATS = [
    "bodypart_damage", "crit_efficiency", "armor_damage",
    "dodge_chance", "main_hand_efficiency", "move_resistance",
    "vision", "bonus_range", "crit_chance", "miracle_chance",
    "max_health", "block_power_recovery", "control_resistance",
    "magic_power", "pain_resistance", "fortitude"
]

def calculate_combined_stats(slot_labels: dict) -> dict:
    combined = {
        "combat": {},
        "survival": {},
        "resistance": {},
        "magic": {}
    }

    for label in slot_labels.values():
        item = getattr(label, "equipped_item", None)
        if not item:
            continue
        stats = item.get("stats", {})
        damage = item.get("damage", {})
        merged = {**stats, **damage}
        for k, v in merged.items():
            k = k.lower()
            if k in COMBAT_STATS:
                combined["combat"][k] = combined["combat"].get(k, 0) + v
            elif k in SURVIVAL_STATS:
                combined["survival"][k] = combined["survival"].get(k, 0) + v
            elif k in RESISTANCE_STATS:
                combined["resistance"][k] = combined["resistance"].get(k, 0) + v
            elif k in MAGIC_STATS:
                combined["magic"][k] = combined["magic"].get(k, 0) + v

    return combined

def calculate_bodypart_resistances(slot_labels: dict) -> dict:
    parts = {
        "head": {},
        "torso": {},
        "hand": {},
        "leg": {}
    }
    for label in slot_labels.values():
        item = getattr(label, "equipped_item", None)
        if not item:
            continue
        stats = item.get("stats", {})

        for stat, value in stats.items():
            for part in parts.keys():
                suffix = f"_{part}"
                if stat.endswith(suffix):
                    base = stat.replace(suffix, "")
                    combined = value
                    # 전체 저항도 존재하면 합산
                    if base in stats:
                        combined += stats[base]
                    parts[part][base] = parts[part].get(base, 0) + combined

    return parts


def format_stats(self, stat_dict: dict) -> str:
    lines = []
    for k, v in sorted(stat_dict.items()):
        label = k.replace('_', ' ').capitalize()
        if isinstance(v, float):
            sign = "+" if v > 0 else "-" if v < 0 else ""
            text = f"{sign}{abs(round(v * 100, 1))}%"
        else:
            sign = "+" if v > 0 else "-" if v < 0 else ""
            text = f"{sign}{abs(int(v))}"
        lines.append(f"{label}: {text}")
    return "\n".join(lines)
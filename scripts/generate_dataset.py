#!/usr/bin/env python3
"""Generate a reproducible educational sample dataset (not fault research).

The default output path overwrites the committed data files. Use only when an
intentional full dataset reset is desired; normal contributions edit JSON data
files directly and validate them without running this script.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANDS = {
    "Samsung": ["Galaxy A15", "Galaxy S24", "Galaxy A35", "Galaxy Z Flip6", "Galaxy S23 FE", "Galaxy A55"],
    "Xiaomi": ["Redmi Note 13", "Redmi Note 13 Pro+", "Xiaomi 14", "POCO X6", "Redmi Note 12", "POCO F6"],
    "Infinix": ["NOTE 40", "HOT 40 Pro", "ZERO 30 5G", "SMART 8", "GT 20 Pro", "NOTE 30 VIP"],
    "Tecno": ["SPARK 20 Pro", "CAMON 30 Premier", "POVA 6 Pro", "PHANTOM V Flip", "POP 8", "CAMON 20 Pro"],
    "Oppo": ["A79 5G", "Reno11 Pro", "Find X7 Ultra", "Find N3 Flip", "A58", "K12"],
    "Vivo": ["Y100", "V30 Pro", "X100 Pro", "T3", "iQOO Neo9 Pro", "iQOO Z9"],
    "iPhone": ["iPhone 15", "iPhone 14", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 13 mini"],
}
# These lists are used only for obvious hardware-level wording. They do not
# assert that any listed device has a particular fault.
OLED_MODELS = {
    "Galaxy A15", "Galaxy S24", "Galaxy A35", "Galaxy Z Flip6", "Galaxy S23 FE", "Galaxy A55",
    "Redmi Note 13", "Redmi Note 13 Pro+", "Xiaomi 14", "POCO X6", "POCO F6",
    "NOTE 40", "ZERO 30 5G", "GT 20 Pro", "NOTE 30 VIP",
    "CAMON 30 Premier", "POVA 6 Pro", "PHANTOM V Flip", "CAMON 20 Pro",
    "Reno11 Pro", "Find X7 Ultra", "Find N3 Flip", "V30 Pro", "X100 Pro", "iQOO Neo9 Pro",
    "iPhone 15", "iPhone 14", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 13 mini",
}
LIGHTNING_IPHONES = {"iPhone 14", "iPhone 13 mini"}
SYMPTOMS = ["no charging", "no display", "network issue", "boot loop", "no sound", "overheating", "battery drain"]
COMPONENTS = {
    "no charging": ["USB-C/Lightning port or cable", "charging adapter", "battery", "charging sub-board"],
    "no display": ["display assembly", "display connector", "backlight circuit", "software display settings"],
    "network issue": ["SIM card", "SIM tray", "antenna path", "carrier or network settings"],
    "boot loop": ["software update state", "storage", "battery", "power button"],
    "no sound": ["speaker grille", "speaker module", "audio settings", "Bluetooth route"],
    "overheating": ["background app load", "charger/cable", "battery", "ventilation or ambient conditions"],
    "battery drain": ["battery condition", "background apps", "screen settings", "network signal conditions"],
}
STEPS = {
    "no charging": ["Inspect the cable and adapter for visible damage; stop using damaged accessories.", "Try a known-good, standards-compliant cable and adapter with a different outlet.", "With power disconnected, check the port visually under good light; do not insert metal tools.", "Restart the phone and observe whether a charging indicator appears."],
    "no display": ["Charge with a known-good accessory for 30 minutes, then try a normal restart.", "Check brightness, accessibility, and display settings if the device responds to touch or audio.", "Call the phone or connect it to a trusted computer to distinguish a display symptom from a full power failure.", "Look for cracks, liquid exposure, or swelling without pressing on the screen."],
    "network issue": ["Check for a carrier outage and confirm the account has service.", "Toggle airplane mode once, then restart the device.", "Reseat the SIM only with the device powered off and use the correct eject tool gently.", "Test the SIM in another compatible phone, or another known-good SIM in this phone."],
    "boot loop": ["Disconnect accessories and use the documented normal restart for the device family.", "Charge using a known-good accessory and allow a short cooling period if warm.", "If available, use the manufacturer's documented recovery/update process without unlocking or wiping first.", "Back up data if the device becomes stable; seek service before factory reset if data matters."],
    "no sound": ["Check ringer, media volume, mute, Do Not Disturb, and the selected audio output.", "Disconnect Bluetooth devices and test with a locally stored audio clip.", "Inspect speaker openings for loose debris; use a soft dry brush only, with no liquid or sharp tools.", "Restart and retest a call and media playback separately."],
    "overheating": ["Stop charging and close demanding apps; move the phone out of direct sun.", "Remove a case temporarily and allow the device to cool naturally on a hard surface.", "Check battery and app-usage screens after cooling; note whether heat recurs during idle use.", "If swelling, odor, smoke, or severe heat is present, stop handling and seek qualified service."],
    "battery drain": ["Compare screen-on and idle drain using the built-in battery usage page.", "Restart, install stable official updates, and review recently added apps.", "Check signal strength and disable unused radios temporarily to see if drain changes.", "Use built-in battery health information where available; never puncture or open the battery."],
}
TOOLS = {
    "no charging": ["known-good certified charger", "USB power meter (optional)", "bright flashlight"],
    "no display": ["known-good charger", "trusted computer (optional)", "flashlight"],
    "network issue": ["known-good compatible SIM", "SIM eject tool", "carrier coverage map"],
    "boot loop": ["known-good charger", "manufacturer support page", "USB cable (optional)"],
    "no sound": ["soft dry brush", "known-good wired/Bluetooth audio output"],
    "overheating": ["timer", "built-in battery/app usage screen"],
    "battery drain": ["built-in battery usage screen", "timer"],
}
COST = {
    "no charging": (0, 45), "no display": (0, 180), "network issue": (0, 35),
    "boot loop": (0, 120), "no sound": (0, 90), "overheating": (0, 100), "battery drain": (0, 110),
}
SAFETY = {
    "no charging": "Unplug before inspection. Do not scrape contacts, use liquids, or charge a wet, swollen, or hot phone.",
    "no display": "Do not press on cracked glass or open the device. Suspected liquid damage needs professional assessment.",
    "network issue": "Do not bypass carrier locks, alter IMEI/baseband data, or install unofficial radio firmware.",
    "boot loop": "Avoid bootloader unlocks, factory resets, and unofficial firmware when preserving data is important.",
    "no sound": "Do not insert pins or liquid into openings; stop if the device has signs of liquid damage.",
    "overheating": "Never puncture, bend, compress, or reflow a battery/device. Do not place it in a freezer or water.",
    "battery drain": "Never puncture, bend, or heat a lithium-ion battery; seek qualified service for swelling or damage.",
}
SAFETY = {key: f"{note} Do not puncture lithium cells, attempt board-level reflow, or bypass carrier/baseband protections." for key, note in SAFETY.items()}
DIFFICULTY = ["beginner", "beginner", "intermediate", "intermediate", "beginner", "advanced"]


def components_for(symptom: str, model: str) -> list[str]:
    components = list(COMPONENTS[symptom])
    if symptom == "no display" and model in OLED_MODELS:
        # OLED panels emit their own light, so a backlight is not a plausible
        # display component for these models. This remains a generic possibility.
        components = ["OLED display assembly", "display connector", "software display settings"]
    elif symptom == "no charging":
        if model in LIGHTNING_IPHONES:
            components[0] = "Lightning port or cable"
        elif model.startswith("iPhone "):
            components[0] = "USB-C port or cable"
        else:
            components[0] = "USB-C port or cable"
    return components


def generate(output_dir: Path | None = None) -> int:
    destination = output_dir or ROOT / "data"
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for brand_index, (brand, models) in enumerate(BRANDS.items()):
        entries = []
        for index, model in enumerate(models):
            symptom = SYMPTOMS[(index + brand_index) % len(SYMPTOMS)]
            # Keep both connector examples visible in the sample set. This is
            # a generic first-check illustration, not a claim of a device fault.
            if brand == "iPhone" and model == "iPhone 15":
                symptom = "no charging"
            entries.append({
                "id": f"{brand.lower().replace(' ', '-')}-{index + 1:02d}",
                "brand": brand,
                "model": model,
                "title": f"{symptom.title()} — safe first checks",
                "symptom": symptom,
                "likely_components": components_for(symptom, model),
                "safe_diagnostic_steps": STEPS[symptom],
                "tools": TOOLS[symptom],
                "difficulty": DIFFICULTY[(index + brand_index) % len(DIFFICULTY)],
                "estimated_cost_usd_parts_only": {"min": COST[symptom][0], "max": COST[symptom][1]},
                "safety_notes": SAFETY[symptom],
                "educational_example": True,
                "disclaimer": "Illustrative training example only; not a verified issue for this brand or model.",
            })
        output = destination / f"{brand.lower().replace(' ', '-')}.json"
        output.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        count += len(entries)
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="write generated files to this directory instead of overwriting repository data/")
    args = parser.parse_args()
    print(f"Generated {generate(args.output_dir)} deterministic educational examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import flet as ft
from pathlib import Path

# --- KOLORY ---
BG = "#0A1421"
PANEL = "#112335"
CARD = "#193147"
BORDER = "#29465B"
WHITE = "#EDF8FF"
GRAY = "#A3B8C8"
CYAN = "#41DDE5"
GREEN = "#51E4AE"
YELLOW = "#FFD06B"
RED = "#FF6474"

STATUS_COLOR = {"ok": GREEN, "warning": YELLOW, "danger": RED, "neutral": GRAY}
STATUS_TEXT = {"ok": "W normie", "warning": "Ostrzeżenie", "danger": "Alarm", "neutral": "Bez oceny"}

# --- ŚCIEŻKI ---
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "calendar_events.json"
BODY_FILE = BASE_DIR / "sylwetka_czlowieka_kontur.svg"

# --- ZAKTUALIZOWANE KATEGORIE ---
CATEGORIES = {
    "Kardiologia": {"icon": ft.Icons.FAVORITE, "name": "Serce i układ krążenia", "metric": "Tętno, EKG, ciśnienie", "desc": "Monitorowanie pracy serca."},
    "Oddech": {"icon": ft.Icons.AIR, "name": "Oddychanie", "metric": "SpO₂, liczba oddechów", "desc": "Szacunkowe wysycenie krwi tlenem."},
    "Temperatura": {"icon": ft.Icons.THERMOSTAT, "name": "Temperatura ciała", "metric": "Temperatura", "desc": "Zmiany temperatury ciała."},
    "Stres": {"icon": ft.Icons.PSYCHOLOGY, "name": "Samopoczucie i stres", "metric": "Skala deklarowana 1–10", "desc": "Zadeklarowane samopoczucie."},
    "Sen": {"icon": ft.Icons.BEDTIME, "name": "Sen i regeneracja", "metric": "Czas snu", "desc": "Czas snu i wypoczynku."},
    "Radiacja": {"icon": ft.Icons.WARNING_AMBER, "name": "Promieniowanie", "metric": "Odczyt dozymetru", "desc": "Bez oceny ryzyka."},
    "Nawodnienie": {"icon": ft.Icons.WATER_DROP, "name": "Nawodnienie", "metric": "Dziennik", "desc": "Dziennik wpisów astronauty."},
}

# --- STREFY CIAŁA ---
BODY_W = 390
BODY_H = round(BODY_W * 1672 / 941)
BODY_ZONES = {
    "Sen": (385, 25, 180, 240),
    "Stres": (510, 270, 100, 120),
    "Kardiologia": (465, 400, 155, 215),
    "Oddech": (320, 400, 145, 215),
    "Temperatura": (225, 350, 100, 370),
    "Radiacja": (620, 350, 105, 370),
    "Nawodnienie": (365, 645, 220, 290),
}
BODY_POINTS = {
    "Sen": (464, 160),
    "Stres": (559, 328),
    "Oddech": (400, 512),
    "Kardiologia": (544, 527),
    "Temperatura": (280, 500),
    "Radiacja": (675, 518),
    "Nawodnienie": (468, 829),
}

# Współdzielone style tekstu i komponentów
def txt(text, size=13, color=WHITE, bold=False):
    return ft.Text(text, size=size, color=color, weight=ft.FontWeight.BOLD if bold else None)

def box(content, pad=16):
    return ft.Container(
        bgcolor=PANEL, border=ft.Border.all(1, BORDER), border_radius=16,
        padding=pad, content=content,
    )
# guidebook_view.py
import flet as ft
from config import box, txt, WHITE, CYAN

GLOSSARY = [
    ("BPM", "Liczba uderzeń serca na minutę."),
    ("SpO₂", "Szacowane wysycenie hemoglobiny tlenem."),
    ("EKG", "Elektrokardiogram."),
    ("Aktygrafia", "Pomiar aktywności dla snu."),
]

def build_guidebook_screen():
    return ft.Column(spacing=14, controls=[
        txt("Podręcznik Procedur", 23, WHITE, True),
        box(ft.Column(spacing=14, controls=[
            ft.Column(spacing=3, controls=[txt(word, 16, CYAN, True), txt(definition, 13, WHITE)])
            for word, definition in GLOSSARY
        ])),
    ])
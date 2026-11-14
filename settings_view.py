import flet as ft
from config import box, txt, WHITE, GRAY, CYAN, CARD, BORDER

def build_settings_screen(state, page):
    mode_buttons_container = ft.Row(wrap=True, spacing=9)

    def update_buttons():
        mode_buttons_container.controls.clear()
        for m in ("Norma", "Ostrzeżenie", "Alarm"):
            # Generowanie przycisków z podświetleniem aktywnego
            btn = ft.Container(
                bgcolor="#234757" if m == state["mode"] else CARD,
                border=ft.Border.all(2 if m == state["mode"] else 1, CYAN if m == state["mode"] else BORDER),
                border_radius=9, 
                padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                ink=True, 
                on_click=lambda e, mode=m: select_mode(mode),
                content=txt(m, 14, WHITE, True),
            )
            mode_buttons_container.controls.append(btn)

    def select_mode(m):
        state["mode"] = m
        update_buttons()
        page.update()

    update_buttons()

    return ft.Column(spacing=15, controls=[
        txt("Ustawienia i Testy Systemu", 23, WHITE, True),
        box(ft.Column(spacing=14, controls=[
            txt("Scenariusze pomiarów", 17, WHITE, True),
            txt("Wymuś zmianę parametrów życiowych, aby przetestować reakcję panelu Monitoringu oraz Alerty.", 13, GRAY),
            mode_buttons_container,
            ft.Divider(color=BORDER, height=20),
            txt("Architektura aplikacji:", 15, WHITE, True),
            txt("• Praca offline w warunkach zerowej łączności.\n• UI zbudowane we frameworku Flet (Flutter).\n• Symulacja danych generowana matematycznie w czasie rzeczywistym.", 13, GRAY),
        ])),
    ])
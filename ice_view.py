import flet as ft
from config import box, txt, WHITE, GRAY, RED, BORDER

def build_ice_screen(state, page):
    # Domyślny ekran instrukcji
    instruction_container = ft.Container(
        content=txt("Wybierz procedurę awaryjną z listy, aby natychmiast wyświetlić instrukcję krok po kroku.", 16, GRAY)
    )

    # Baza procedur ICE 
    procedures = {
        "DEKOMPRESJA": (
            "1. Natychmiast załóż maskę tlenową.\n"
            "2. Sprawdź szczelność skafandra.\n"
            "3. Udaj się do najbliższej śluzy ratunkowej.\n"
            "4. Zgłoś kod czerwony do dowódcy misji."
        ),
        "ZATRZYMANIE KRĄŻENIA": (
            "1. Sprawdź funkcje życiowe na monitorze głównym.\n"
            "2. Rozpocznij RKO (30 uciśnięć / 2 wdechy).\n"
            "3. Użyj defibrylatora (AED) zlokalizowanego w sektorze A.\n"
            "4. Przygotuj adrenalinę zgodnie z protokołem."
        ),
        "URAZ MECHANICZNY / KRWOTOK": (
            "1. Zlokalizuj źródło krwawienia.\n"
            "2. Załóż opaskę uciskową powyżej rany (jeśli dotyczy kończyny).\n"
            "3. Użyj gazy hemostatycznej z apteczki pierwszej pomocy.\n"
            "4. Zeskanuj parametry rannego w zakładce Monitoring."
        )
    }

    def show_procedure(e, procedure_name):
        # Aktualizacja dolnego panelu instrukcją
        instruction_container.content = ft.Column(spacing=10, controls=[
            txt(f"PROCEDURA: {procedure_name}", 22, RED, True),
            txt(procedures[procedure_name], 18, WHITE)
        ])
        page.update()

    buttons = []
    for proc_name in procedures.keys():
        buttons.append(
            ft.Container(
                content=txt(proc_name, 16, WHITE, True),
                bgcolor="#8B0000",
                padding=20,
                border_radius=8,
                alignment=ft.Alignment.CENTER,
                height=70,
                ink=True, # Efekt fali przy naciśnięciu
                on_click=lambda e, name=proc_name: show_procedure(e, name)
            )
        )

    return ft.Column(spacing=20, controls=[
        ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.WARNING, color=RED, size=30),
            txt("ICE Asystent (In Case of Emergency)", 26, RED, True)
        ]),
        box(ft.Column(spacing=15, controls=[
            txt("Wybierz zagrożenie:", 16, WHITE),
            ft.ResponsiveRow(
                controls=[ft.Container(col={"xs": 12, "md": 4}, content=btn) for btn in buttons]
            ),
            ft.Divider(color=BORDER, height=30),
            instruction_container
        ]))
    ])
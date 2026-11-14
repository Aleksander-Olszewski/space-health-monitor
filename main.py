import asyncio
import flet as ft
from datetime import date
from config import BG, PANEL, WHITE, GRAY, txt
from logic import load_events, readings, evaluate_alerts

# Importy z rozdzielonych plików widoków
from guidebook_view import build_guidebook_screen
from settings_view import build_settings_screen
from monitoring_view import build_monitoring_dashboard
from calendar_view import build_calendar_screen

def main(page: ft.Page):
    page.title = "Astronaut Health Monitor"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0

    # Globalny stan aplikacji
    state = {
        "tab": 0, "tick": 0, "running": True,
        "mode": "Norma", "date": date.today(), 
        "month": date.today().replace(day=1),
        "events": load_events(),
    }

    # Główny kontener renderujący widok
    display = ft.AnimatedSwitcher(
        content=txt("Ładowanie panelu...", 14, WHITE), # Tu docelowo: build_monitoring_dashboard()
        duration=240, reverse_duration=140, transition=ft.AnimatedSwitcherTransition.FADE, expand=True,
    )

    scroller = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[
        ft.Container(padding=ft.Padding.symmetric(horizontal=15, vertical=10), content=display, expand=True,)
    ])

    def open_tab(index):
        state["tab"] = index
        navigation.selected_index = index

        scroller.scroll = None if index == 2 else ft.ScrollMode.AUTO 
        
        # Prawdziwa logika podpinania widoków
        if index == 0:
            display.content = build_monitoring_dashboard(state, page)
        elif index == 1:
            display.content = build_calendar_screen(state, page)
        elif index == 2:
            display.content = build_guidebook_screen()
        elif index == 3:
            display.content = build_settings_screen(state, page)
            
        page.update()

    # ZAKTUALIZOWANA KOLEJNOŚĆ I NAZWY
    navigation = ft.NavigationBar(
        selected_index=0, bgcolor=PANEL, indicator_color="#1F4C60",
        on_change=lambda e: open_tab(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.MONITOR_HEART, label="Monitoring"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH, label="Kalendarz"),
            ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Podręcznik"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ustawienia"),
        ],
    )
    
    page.navigation_bar = navigation
    page.add(ft.SafeArea(expand=True, content=ft.Column(expand=True, spacing=0, controls=[
        scroller,
    ])))

    # Uruchom domyślnie pierwszą zakładkę
    open_tab(0)

    from monitoring_view import update_monitoring_data
    
    async def sensor_loop():
        while True:
            if state["running"]:
                state["tick"] += 1
                # Aktualizuj dane w pamięci kontrolera
                update_monitoring_data(state)
                # Odśwież ekran tylko jeśli jesteśmy na zakładce Monitoring
                if state["tab"] == 0:
                    page.update()
            await asyncio.sleep(0.18)

    # Odpalenie pętli w tle
    page.run_task(sensor_loop)

if __name__ == "__main__":
    ft.run(main)
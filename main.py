"""Lunar Health Monitor — animowany PoC, Flet 1.1.2.

Uruchom: py -m pip install -r requirements.txt; py main.py
Wszystkie dane są symulowane: aplikacja nie stawia diagnoz.
"""

import asyncio
import math

import flet as ft


# Kolory interfejsu — zwykłe heksy są obsługiwane przez Flet.
BACKGROUND = "#080D1B"
PANEL = "#111B30" 
PANEL_ALT = "#0D1628"
STROKE = "#253854"
TEXT = "#E9F4FF"
MUTED = "#8BA1B9"
TEAL = "#37E5C5"
BLUE = "#5AA8FF"
ORANGE = "#FFB568"


def panel(content, padding=18):
    return ft.Container(
        content=content,
        bgcolor=PANEL,
        border=ft.Border.all(1, STROKE),
        border_radius=20,
        padding=padding,
    )


def small_label(text):
    return ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color=MUTED)


def metric_card(icon, label, value_control, unit, color):
    return ft.Container(
        expand=True,
        padding=14,
        border_radius=16,
        bgcolor=PANEL_ALT,
        border=ft.Border.all(1, STROKE),
        content=ft.Column(
            spacing=7,
            controls=[
                ft.Icon(icon, size=19, color=color),
                ft.Text(label, size=11, color=MUTED),
                ft.Row(
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        value_control,
                        ft.Text(unit, size=10, color=MUTED),
                    ],
                ),
            ],
        ),
    )


def ecg_height(position):
    """Uproszczony, WYŁĄCZNIE demonstracyjny kształt sygnału EKG."""
    phase = position % 1.0

    def bump(center, width):
        return math.exp(-((phase - center) / width) ** 2)

    value = (
        7
        + 9 * bump(0.18, 0.055)      # P
        - 7 * bump(0.38, 0.025)      # Q
        + 62 * bump(0.43, 0.018)     # R
        - 8 * bump(0.48, 0.027)      # S
        + 17 * bump(0.70, 0.08)      # T
    )
    return max(4, min(74, value))


def main(page: ft.Page):
    page.title = "Lunar Health Monitor | Animated PoC"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BACKGROUND
    page.window.width = 470
    page.window.height = 880
    page.padding = 0

    # Stan demonstracji; bez bazy danych, internetu i urządzeń medycznych.
    state = {"playing": True, "mode": "rest", "tick": 0}

    # Pasek statusu LIVE z pulsującą kropką.
    live_dot = ft.Container(
        width=9,
        height=9,
        border_radius=10,
        bgcolor=TEAL,
        opacity=1,
        animate_opacity=600,
    )
    live_text = ft.Text("SYMULACJA NA ŻYWO", size=10, color=TEAL)

    heart_value = ft.Text("72", size=49, weight=ft.FontWeight.BOLD, color=TEXT)
    oxygen_value = ft.Text("98", size=26, weight=ft.FontWeight.BOLD, color=TEXT)
    activity_value = ft.Text("NISKA", size=15, weight=ft.FontWeight.BOLD, color=TEXT)
    condition_text = ft.Text("Parametry w zakresie demonstracyjnym", size=12, color=TEAL)

    # Dwa animowane okręgi i samo serce.
    outer_ring = ft.Container(
        width=182,
        height=182,
        border_radius=100,
        border=ft.Border.all(2, "#205A66"),
        bgcolor="#0F2631",
        opacity=0.6,
        scale=1.0,
        animate_scale=ft.Animation(580, ft.AnimationCurve.EASE_IN_OUT),
        animate_opacity=580,
    )
    inner_ring = ft.Container(
        width=132,
        height=132,
        border_radius=100,
        border=ft.Border.all(2, "#286F77"),
        bgcolor="#153442",
        scale=1.0,
        animate_scale=ft.Animation(460, ft.AnimationCurve.EASE_IN_OUT),
    )
    heart = ft.Container(
        width=95,
        height=95,
        bgcolor="#1C5060",
        border_radius=90,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.FAVORITE, size=48, color=TEAL),
        scale=1.0,
        animate_scale=ft.Animation(350, ft.AnimationCurve.EASE_IN_OUT),
    )

    heart_graphic = ft.Stack(
        width=300,
        height=190,
        alignment=ft.Alignment.CENTER,
        controls=[outer_ring, inner_ring, heart],
    )

    # 43 pionowe słupki — dynamicznie przesuwany „sygnał” na potrzeby PoC.
    bars = [
        ft.Container(
            width=4,
            height=6,
            bgcolor=TEAL,
            border_radius=4,
            animate=130,
        )
        for _ in range(43)
    ]

    pause_button = ft.Button(content="Pauza", icon=ft.Icons.PAUSE)
    rest_button = ft.Button(content="Spoczynek", bgcolor="#1E645F", color=TEXT)
    effort_button = ft.Button(content="Wysiłek", bgcolor="#263650", color=TEXT)

    def refresh_mode_buttons():
        rest_button.bgcolor = "#1E645F" if state["mode"] == "rest" else "#263650"
        effort_button.bgcolor = "#8E5730" if state["mode"] == "effort" else "#263650"
        condition_text.value = (
            "Tryb spoczynku • wartości symulowane"
            if state["mode"] == "rest"
            else "Tryb wysiłku • wartości symulowane"
        )
        condition_text.color = TEAL if state["mode"] == "rest" else ORANGE

    def switch_mode(mode):
        state["mode"] = mode
        refresh_mode_buttons()
        # Wyraźny sygnał, że przełącznik naprawdę działa, również po pauzie.
        heart_value.value = "72" if mode == "rest" else "124"
        oxygen_value.value = "98" if mode == "rest" else "96"
        activity_value.value = "NISKA" if mode == "rest" else "WYSOKA"
        page.update()

    def toggle_pause(e):
        state["playing"] = not state["playing"]
        pause_button.content = "Pauza" if state["playing"] else "Wznów"
        pause_button.icon = ft.Icons.PAUSE if state["playing"] else ft.Icons.PLAY_ARROW
        live_text.value = "SYMULACJA NA ŻYWO" if state["playing"] else "SYMULACJA WSTRZYMANA"
        live_dot.opacity = 1 if state["playing"] else 0.25
        page.update()

    rest_button.on_click = lambda e: switch_mode("rest")
    effort_button.on_click = lambda e: switch_mode("effort")
    pause_button.on_click = toggle_pause

    # Ekran, zoptymalizowany pod okno mobilne/desktopowe.
    dashboard = ft.Column(
        spacing=18,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.MONITOR_HEART, color=TEAL, size=25),
                            ft.Text("LUNAR / HEALTH", size=16, color=TEXT, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    ft.Container(
                        padding=9,
                        border_radius=12,
                        bgcolor="#14273A",
                        content=ft.Text("POC  •  1.1.2", size=10, color=BLUE),
                    ),
                ],
            ),
            ft.Column(
                spacing=6,
                controls=[
                    ft.Text("Monitor zdrowia", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Text("CREW MEMBER 01   /   DEMO TELEMETRII", size=11, color=MUTED),
                ],
            ),
            panel(
                ft.Column(
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                small_label("UKŁAD KRĄŻENIA"),
                                ft.Row(spacing=7, controls=[live_dot, live_text]),
                            ],
                        ),
                        heart_graphic,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            spacing=8,
                            controls=[heart_value, ft.Text("BPM", size=15, color=MUTED)],
                        ),
                        ft.Text("Symulowany rytm serca", size=12, color=MUTED),
                        ft.Divider(color=STROKE, height=16),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[small_label("EKG • DEMO SYGNAŁU"), small_label("LIVE")],
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(vertical=10),
                            content=ft.Row(
                                spacing=3,
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=bars,
                            ),
                            height=95,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=PANEL_ALT,
                            border_radius=12,
                        ),
                    ],
                ),
                padding=18,
            ),
            ft.Row(
                spacing=10,
                controls=[
                    metric_card(ft.Icons.AIR, "SATURACJA", oxygen_value, "%", BLUE),
                    metric_card(ft.Icons.FITNESS_CENTER, "AKTYWNOŚĆ", activity_value, "", ORANGE),
                ],
            ),
            panel(
                ft.Column(
                    spacing=12,
                    controls=[
                        small_label("STEROWANIE SYMULACJĄ"),
                        ft.Row(spacing=8, controls=[rest_button, effort_button, pause_button]),
                        condition_text,
                        ft.Text(
                            "Wartości i wykres są generowane lokalnie. "
                            "To demonstracja interfejsu, a nie urządzenie medyczne.",
                            color=MUTED,
                            size=11,
                        ),
                    ],
                ),
            ),
        ],
    )

    page.add(
        ft.SafeArea(
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=20, vertical=22),
                        content=dashboard,
                    ),
                ],
            )
        )
    )

    async def animate_demo():
        """Pętla asynchroniczna: UI pozostaje klikalny podczas animacji."""
        while True:
            if not state["playing"]:
                await asyncio.sleep(0.16)
                continue

            tick = state["tick"]
            state["tick"] += 1
            effort = state["mode"] == "effort"
            base = 124 if effort else 72
            heart_value.value = str(base + round(3 * math.sin(tick * 0.17)))
            oxygen_value.value = str(96 if effort else 98)
            activity_value.value = "WYSOKA" if effort else "NISKA"

            # Pulsowanie wykonuje Flet/Flutter — zmieniamy tylko cel animacji.
            beat = tick % 6 in (0, 1)
            heart.scale = 1.15 if beat else 1.0
            inner_ring.scale = 1.08 if beat else 1.0
            outer_ring.scale = 1.1 if beat else 0.97
            outer_ring.opacity = 0.85 if beat else 0.35
            live_dot.opacity = 1.0 if tick % 6 < 3 else 0.35

            # Przesuwamy odczyty co klatkę, bez rysowania zewnętrznego SVG.
            speed = 0.056 if effort else 0.037
            for i, bar in enumerate(bars):
                position = i * 0.036 - tick * speed
                bar.height = ecg_height(position)
                bar.bgcolor = ORANGE if effort else TEAL

            page.update()
            await asyncio.sleep(0.15)

    page.run_task(animate_demo)


if __name__ == "__main__":
    ft.run(main)

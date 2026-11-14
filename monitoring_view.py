import flet as ft
from config import box, txt, WHITE, GRAY, CYAN, GREEN, YELLOW, RED, PANEL, CARD, BORDER, CATEGORIES, STATUS_COLOR, STATUS_TEXT, BODY_W, BODY_H, BODY_ZONES, BODY_POINTS
from logic import readings, evaluate_alerts, ecg_svg
from pathlib import Path

BODY_FILE = Path(__file__).resolve().parent / "sylwetka_czlowieka_kontur.svg"

# Słownik przechowujący referencje do kontrolek, które odświeżają się co 0.2s
ui_refs = {}

def build_monitoring_dashboard(state, page):
    state.setdefault("category", None)
    
    # Inicjalizacja kontrolek tekstowych dla odczytów
    for key in ["hr", "spo2", "pressure", "temp", "breath", "stress", "sleep", "radiation", "water"]:
        ui_refs[key] = txt("", 17 if key != "hr" else 29, WHITE, True)
        
    ui_refs["sensor_label"] = txt("● SYMULACJA NA ŻYWO", 11, GREEN, True)
    ui_refs["alert_summary"] = txt("", 14, WHITE, True)
    ui_refs["alert_column"] = ft.Column(spacing=8)
    ui_refs["ecg_image"] = ft.Image(src=ecg_svg(0, 72), width=380, height=130, fit=ft.BoxFit.CONTAIN, gapless_playback=True)
    ui_refs["heart_icon"] = ft.Container(
        width=47, height=47, border_radius=40, bgcolor="#143E49", alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.FAVORITE, color=CYAN, size=26), animate_scale=220, scale=1.0,
    )
    ui_refs["detail_switcher"] = ft.AnimatedSwitcher(content=ft.Container(), duration=280, transition=ft.AnimatedSwitcherTransition.FADE)

    def load_body_svg():
        try:
            return BODY_FILE.read_text(encoding="utf-8").replace('fill="#000000"', 'fill="#66C5D7"')
        except OSError:
            return None

    def make_details(name, statuses):
        if name is None:
            return ft.Column(spacing=10, controls=[
                ft.Icon(ft.Icons.TOUCH_APP, color=CYAN, size=32),
                txt("Wybierz obszar ciała z sylwetki po lewej stronie.", 18, WHITE, True),
            ])
        d = CATEGORIES[name]
        color = STATUS_COLOR[statuses[name]]
        return ft.Column(spacing=10, controls=[
            ft.Row(spacing=8, controls=[
                ft.Icon(d["icon"], color=color, size=27),
                ft.Container(expand=True, content=txt(name, 19, WHITE, True)),
            ]),
            txt("● " + STATUS_TEXT[statuses[name]], 13, color, True),
            txt(d["metric"], 13, CYAN),
            txt(d["desc"], 13, GRAY),
        ])

    def select_category(e, name):
        state["category"] = name
        current = readings(state["mode"], state["tick"])
        statuses, _ = evaluate_alerts(current)
        ui_refs["detail_switcher"].content = make_details(name, statuses)
        page.update()

    ui_refs["make_details"] = make_details # Zapisujemy funkcję, by użyć jej w updaterze
    ui_refs["detail_switcher"].content = make_details(None, {k: "ok" for k in CATEGORIES})

    # Składanie panelu pomiarów (lewa strona)
    def metric_line(name, value_control, icon_name):
        return ft.Container(
            bgcolor=CARD, padding=ft.Padding.symmetric(horizontal=11, vertical=8), border_radius=10,
            content=ft.Row(spacing=9, controls=[ft.Icon(icon_name, size=19, color=CYAN), ft.Container(expand=True, content=txt(name, 12, GRAY)), value_control]),
        )

    measurements = box(ft.Column(spacing=8, controls=[
        txt("Parametry na żywo", 17, WHITE, True),
        ft.Row(spacing=10, controls=[ui_refs["heart_icon"], txt("Puls", 13, GRAY), ui_refs["hr"]]),
        ui_refs["ecg_image"],
        metric_line("Saturacja", ui_refs["spo2"], ft.Icons.AIR),
        metric_line("Ciśnienie", ui_refs["pressure"], ft.Icons.MONITOR_HEART),
        metric_line("Temperatura", ui_refs["temp"], ft.Icons.THERMOSTAT),
        ft.Divider(height=5, color=BORDER),
        metric_line("Sen", ui_refs["sleep"], ft.Icons.BEDTIME),
        metric_line("Stres", ui_refs["stress"], ft.Icons.PSYCHOLOGY),
    ]), pad=12)

    # Składanie modelu (środek)
    svg_content = load_body_svg()
    layers = [ft.Image(src=svg_content, width=BODY_W, height=BODY_H, fit=ft.BoxFit.FILL)] if svg_content else [txt("Brak SVG", 14, YELLOW)]
    
    for name, (x, y, w, h) in BODY_ZONES.items():
        layers.append(ft.Container(
            left=x * BODY_W / 941, top=y * BODY_H / 1672, width=w * BODY_W / 941, height=h * BODY_H / 1672,
            bgcolor="transparent", ink=True, on_click=lambda e, n=name: select_category(e, n),
        ))

    ui_refs["points"] = {}
    for name, (cx, cy) in BODY_POINTS.items():
        core = ft.Icon(ft.Icons.CIRCLE, size=10, color=GREEN)
        dot = ft.Container(
            left=cx * BODY_W / 941 - 16, top=cy * BODY_H / 1672 - 16,
            width=32, height=32, border_radius=99,
            bgcolor="#092537", border=ft.Border.all(2, GREEN),
            alignment=ft.Alignment.CENTER, content=core,
            animate_scale=190, scale=1.0,
            ink=True, on_click=lambda e, n=name: select_category(e, n),
        )
        ui_refs["points"][name] = (dot, core)
        layers.append(dot)
    
    model = ft.Stack(width=BODY_W, height=BODY_H, controls=layers)
    model_panel = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
        txt("Interaktywny model zdrowia", 19, WHITE, True),
        model
    ])

    # Panel Szczegółów (prawa strona)
    detail_panel = box(ft.Column(spacing=11, controls=[
        txt("Informacje o kategorii", 17, WHITE, True),
        ui_refs["detail_switcher"],
        ft.Divider(color=BORDER),
        txt("Aktywne Alerty", 18, WHITE, True),
        ui_refs["alert_summary"],
        ui_refs["alert_column"],
    ]), pad=13)

    # Inicjalne załadowanie danych
    update_monitoring_data(state)

    return ft.Column(spacing=10, controls=[
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            txt("Główny Monitor Diagnostyczny", 20, WHITE, True), ui_refs["sensor_label"],
        ]),
        ft.ResponsiveRow(spacing=12, run_spacing=12, controls=[
            ft.Container(col={"xs": 12, "md": 5, "lg": 3}, content=measurements),
            ft.Container(col={"xs": 12, "md": 7, "lg": 6}, content=model_panel),
            ft.Container(col={"xs": 12, "md": 12, "lg": 3}, content=detail_panel),
        ]),
    ])

def update_monitoring_data(state):
    """Funkcja wywoływana z pętli w main.py, odświeża interfejs na podstawie tick'ów."""
    if not ui_refs: return # UI jeszcze nie zbudowane

    current = readings(state["mode"], state["tick"])
    statuses, alerts = evaluate_alerts(current)
    
    # Odświeżanie wartości tekstowych
    ui_refs["hr"].value = f'{current["hr"]} bpm'
    ui_refs["spo2"].value = f'{current["spo2"]} %'
    ui_refs["pressure"].value = f'{current["pressure"]} mmHg'
    ui_refs["temp"].value = f'{current["temp"]:.1f} °C'
    ui_refs["breath"].value = f'{current["breath"]} /min'
    ui_refs["stress"].value = f'{current["stress"]}/10'
    ui_refs["sleep"].value = f'{current["sleep"]:.1f} h'
    
    # Odświeżanie grafiki EKG i serca
    ui_refs["ecg_image"].src = ecg_svg(state["tick"], current["hr"])
    ui_refs["heart_icon"].scale = 1.11 if state["tick"] % 4 == 0 else 0.96
    
    # Odświeżanie alertów
    danger_count = sum(level == "danger" for _, level, _ in alerts)
    warning_count = sum(level == "warning" for _, level, _ in alerts)
    ui_refs["alert_summary"].value = f"{danger_count} alarmów • {warning_count} ostrzeżeń"
    ui_refs["alert_summary"].color = RED if danger_count else YELLOW if warning_count else GREEN
    
    ui_refs["alert_column"].controls.clear()
    if not alerts:
        ui_refs["alert_column"].controls.append(txt("Brak alertów medycznych.", 13, GREEN))
    else:
        for cat, level, message in alerts:
            accent = STATUS_COLOR[level]
            ui_refs["alert_column"].controls.append(ft.Container(
                bgcolor=CARD, border=ft.Border.all(1, accent), border_radius=9,
                padding=9, content=ft.Row(spacing=7, controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER, size=19, color=accent),
                    ft.Column(expand=True, spacing=2, controls=[txt(cat, 12, accent, True), txt(message, 11, WHITE)]),
                ])
            ))

    # Odświeżanie kolorów i wielkości kropek na modelu
    if "points" in ui_refs:
        for name, (dot, core) in ui_refs["points"].items():
            active = (state.get("category") == name)
            color = STATUS_COLOR[statuses.get(name, "ok")]
            dot.border = ft.Border.all(3 if active else 2, color)
            dot.bgcolor = "#204957" if active else "#092537"
            dot.scale = 1.15 if active else 1.0
            core.color = color
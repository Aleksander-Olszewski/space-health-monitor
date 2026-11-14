import calendar
from datetime import date
import flet as ft
from config import box, txt, WHITE, GRAY, CYAN, CARD, BORDER, RED
from logic import save_events
import re

def build_calendar_screen(state, page):
    main_container = ft.Container()

    def refresh():
        main_container.content = render_calendar()
        page.update()

    def render_calendar():
        month = state["month"]
        selected = state["date"]
        today = date.today()

        def shift_month(e, amount):
            year, mon = month.year, month.month + amount
            if mon == 0: year, mon = year - 1, 12
            elif mon == 13: year, mon = year + 1, 1
            state["month"] = date(year, mon, 1)
            state["date"] = state["month"]
            refresh()

        def pick_day(e, day):
            state["date"] = date(month.year, month.month, day)
            refresh()

        event_counts = {ev["date"]: sum(1 for e in state["events"] if e["date"] == ev["date"]) for ev in state["events"]}

        grid_rows = [ft.Row(spacing=4, controls=[
            ft.Container(expand=True, alignment=ft.Alignment.CENTER, padding=6, content=txt(day, 12, GRAY, True))
            for day in ("Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz")
        ])]

        for week in calendar.Calendar(firstweekday=0).monthdayscalendar(month.year, month.month):
            cells = []
            for day in week:
                if day == 0:
                    cells.append(ft.Container(expand=True, height=69))
                    continue
                d = date(month.year, month.month, day)
                chosen = (d == selected)
                is_today = (d == today)
                count = event_counts.get(d.isoformat(), 0)
                
                cells.append(ft.Container(
                    expand=True, height=69, border_radius=10,
                    bgcolor="#265166" if chosen else (CARD if is_today else "#122A3C"),
                    border=ft.Border.all(2 if chosen else 1, CYAN if chosen else BORDER),
                    ink=True, on_click=lambda e, dd=day: pick_day(e, dd),
                    padding=5, content=ft.Column(
                        spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            txt(str(day), 15, WHITE, chosen or is_today),
                            txt("●" if count else " ", 12, CYAN),
                        ],
                    ),
                ))
            grid_rows.append(ft.Row(spacing=4, controls=cells))

        day_events = sorted([e for e in state["events"] if e["date"] == selected.isoformat()], key=lambda e: e["time"])
        agenda = []
        if not day_events: agenda.append(txt("Brak wydarzeń w tym dniu.", 13, GRAY))
        
        for ev in day_events:
            def delete_event(e, event=ev):
                state["events"].remove(event)
                save_events(state["events"])
                refresh()
            agenda.append(ft.Container(
                padding=12, bgcolor=CARD, border_radius=10,
                content=ft.Row(spacing=8, controls=[
                    txt(ev["time"], 14, CYAN, True),
                    ft.Container(expand=True, content=txt(ev["title"], 13, WHITE)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=RED, on_click=delete_event),
                ]),
            ))

        title_field = ft.TextField(label="Nowe wydarzenie", hint_text="np. Kontrola EKG", expand=True)
        time_field = ft.TextField(label="Godzina", hint_text="14:30", width=118, value="09:00")
        form_error = txt("", 12, RED)

        def add_event(e):
            if not title_field.value.strip():
                form_error.value = "Wpisz nazwę wydarzenia."
            elif not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", time_field.value.strip()):
                form_error.value = "Format HH:MM."
            else:
                state["events"].append({"date": selected.isoformat(), "time": time_field.value.strip(), "title": title_field.value.strip()})
                save_events(state["events"])
                refresh()
                return
            page.update()

        polish_months = ("", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień")
        
        return ft.Column(spacing=16, controls=[
            txt("Harmonogram Misji", 23, WHITE, True),
            ft.ResponsiveRow(spacing=13, run_spacing=13, controls=[
                ft.Container(col={"xs": 12, "lg": 7}, content=box(ft.Column(spacing=9, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=lambda e: shift_month(e, -1)),
                        txt(f"{polish_months[month.month]} {month.year}", 20, WHITE, True),
                        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=lambda e: shift_month(e, 1)),
                    ]),
                    *grid_rows,
                ]))),
                ft.Container(col={"xs": 12, "lg": 5}, content=box(ft.Column(spacing=12, controls=[
                    txt("Plan dnia", 19, WHITE, True),
                    txt(selected.strftime("%d.%m.%Y"), 16, CYAN, True),
                    *agenda,
                    ft.Divider(color=BORDER),
                    ft.Row(spacing=8, controls=[time_field, title_field]),
                    form_error,
                    ft.Button(content="Dodaj", icon=ft.Icons.ADD, on_click=add_event),
                ]))),
            ]),
        ])

    main_container.content = render_calendar()
    return main_container
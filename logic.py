import json
import math
from datetime import date, timedelta
from config import DATA_FILE, CATEGORIES, STATUS_COLOR

def load_events():
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [e for e in data if isinstance(e, dict) and all(k in e for k in ("date", "time", "title"))]
        except (OSError, ValueError):
            pass
    today = date.today()
    return [
        {"date": today.isoformat(), "time": "08:00", "title": "Kontrola parametrów zdrowia"},
        {"date": today.isoformat(), "time": "17:30", "title": "Trening i regeneracja"},
        {"date": (today + timedelta(days=1)).isoformat(), "time": "09:15", "title": "Ocena snu i samopoczucia"},
    ]

def save_events(events):
    DATA_FILE.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")

def readings(mode, tick):
    jitter = round(3 * math.sin(tick * 0.27) + 2 * math.sin(tick * 0.17))
    if mode == "Ostrzeżenie":
        return dict(hr=107 + jitter, spo2=93, temp=37.9, breath=21, pressure="128/82", stress=7, sleep=5.7, radiation=0.12, water=0.8)
    if mode == "Alarm":
        return dict(hr=155 + jitter, spo2=88, temp=39.6, breath=29, pressure="145/90", stress=8, sleep=5.3, radiation=0.12, water=0.7)
    return dict(hr=72 + jitter, spo2=98, temp=36.6, breath=15, pressure="110/70", stress=3, sleep=7.5, radiation=0.12, water=1.7)

def evaluate_alerts(r):
    statuses = {name: "ok" for name in CATEGORIES}
    statuses["Radiacja"] = "neutral"
    alerts = []

    def add(cat, level, message):
        priority = {"ok": 0, "neutral": 0, "warning": 1, "danger": 2}
        if priority[level] > priority[statuses[cat]]:
            statuses[cat] = level
        alerts.append((cat, level, message))

    if r["hr"] >= 140: add("Kardiologia", "danger", "Bardzo wysokie tętno")
    elif r["hr"] > 100: add("Kardiologia", "warning", "Tętno poza zakresem")
    if r["spo2"] <= 90: add("Oddech", "danger", "Niski odczyt SpO₂")
    elif r["spo2"] < 95: add("Oddech", "warning", "SpO₂ poniżej progu")
    if r["temp"] >= 39.5: add("Temperatura", "danger", "Wysoka temperatura")
    elif r["temp"] >= 37.8: add("Temperatura", "warning", "Podwyższona temperatura")
    if r["stress"] >= 7: add("Stres", "warning", "Wysoki poziom stresu")
    
    alerts.sort(key=lambda a: 0 if a[1] == "danger" else 1)
    return statuses, alerts

def ecg_svg(tick, hr, width=380, height=130):
    def gauss(x, center, sigma): return math.exp(-0.5 * ((x - center) / sigma) ** 2)
    def signal(phase):
        return (7 * gauss(phase, 0.17, 0.035) - 9 * gauss(phase, 0.385, 0.012) + 
                58 * gauss(phase, 0.415, 0.009) - 21 * gauss(phase, 0.443, 0.013) + 
                14 * gauss(phase, 0.690, 0.065))

    beat_width = max(74, min(158, 122 * 72 / max(hr, 1)))
    offset = tick * 9
    baseline = height * 0.62
    
    grid = []
    for x in range(0, width + 1, 20): grid.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#1C5660" stroke-width="{1 if x % 100 == 0 else 0.5}" opacity="0.38"/>')
    for y in range(0, height + 1, 20): grid.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#1C5660" stroke-width="{1 if y % 100 == 0 else 0.5}" opacity="0.38"/>')
    
    pts = [f"{x},{(baseline - signal(((x + offset) % beat_width) / beat_width)):.1f}" for x in range(0, width + 1, 2)]
    wave = " ".join(pts)
    
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<rect width="100%" height="100%" rx="9" fill="#0C2432"/>' + "".join(grid) +
            f'<polyline points="{wave}" fill="none" stroke="#0D544F" stroke-width="5" opacity="0.38" stroke-linejoin="round"/>' +
            f'<polyline points="{wave}" fill="none" stroke="#50F5C6" stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round"/></svg>')
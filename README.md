# 🚗 Vehicle Passport
### An Artificial Brain for Intelligent Vehicle Health Management

Vehicle Passport is a web-based application that acts as a digital health
record ("passport") for your vehicles. It uses a rule-based **Artificial
Brain** (`brain.py`) to analyze sensor readings and generate:

- ✅ An overall **Health Score** (0–100)
- 📊 A **component-wise breakdown** (engine, oil, battery, tires, brakes, coolant, fuel efficiency)
- ⚠️ **Predictive maintenance alerts** in plain English
- ⏳ **Estimated Remaining Useful Life (RUL)** for key wear components
- 📈 **History tracking** with a live chart of health score over time

---

## 🧠 How the "Artificial Brain" Works

The core intelligence lives in `brain.py` inside the `VehicleBrain` class.

1. **Ideal Ranges** — Each sensor parameter (engine temperature, oil level,
   battery voltage, tire pressure, brake pad %, coolant level, fuel
   efficiency) has a defined "safe" range.
2. **Component Scoring** — Every reading is compared against its ideal
   range. Values inside the range score 100; values outside are penalized
   proportionally to how far they deviate.
3. **Weighted Health Score** — Component scores are combined using
   importance weights (e.g., brakes and engine temperature are weighted
   heavier than fuel efficiency) to produce one overall **Health Score**.
4. **Classification** — The score is translated into a status:
   - 85–100 → **Excellent**
   - 65–84 → **Good**
   - 45–64 → **Warning**
   - 0–44 → **Critical**
5. **Predictive Alerts** — The brain generates specific, human-readable
   warnings (e.g., "Battery voltage 11.8V indicates the battery may be
   weak..."), including a mileage-based **scheduled service predictor**.
6. **Remaining Useful Life (RUL)** — Heuristic estimates of how many more
   kilometers (or months, for the battery) a component is likely to last.

---

## 📁 Project Structure

```
VehiclePassport/
├── app.py                  # Flask application (routes, DB logic)
├── brain.py                # The Artificial Brain (AI diagnostic engine)
├── requirements.txt        # Python dependencies
├── data/                   # SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css       # Modern dark-themed dashboard UI
└── templates/
    ├── base.html            # Shared layout (navbar, footer, flash messages)
    ├── index.html           # Dashboard - list of all vehicles
    ├── add_vehicle.html      # Register a new vehicle
    ├── log_reading.html      # Form to submit a new sensor reading
    └── vehicle_detail.html   # Full AI diagnostic report + history + chart
```

---
<img width="1350" height="566" alt="Screenshot 2026-06-14 190930" src="https://github.com/user-attachments/assets/5dee1d83-9d5f-4743-b8a8-1002173a9a2f" />

---
<img width="1326" height="805" alt="Screenshot 2026-06-14 190914" src="https://github.com/user-attachments/assets/b3dba345-2d50-491c-9269-c074d4fbc758" />

---
<img width="927" height="650" alt="Screenshot 2026-06-14 190851" src="https://github.com/user-attachments/assets/a4b763d9-dfa5-43eb-aceb-21abb437d7af" />

---
<img width="889" height="528" alt="Screenshot 2026-06-14 190838" src="https://github.com/user-attachments/assets/e529c557-0c9c-4c21-bf4f-78d981e39e94" />

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
python app.py
```

The app will start at **http://localhost:5000** and automatically create the
SQLite database (`data/vehicle_passport.db`) on first run.

---

## 🖥️ Using the App

1. **Add a Vehicle** — Click "+ Add Vehicle" and enter details (name, number
   plate, owner, type, year, current mileage, mileage at last service).
2. **Log a Reading** — Open a vehicle and click "+ Log New Reading" to enter
   the latest sensor values (engine temp, oil level, battery voltage, tire
   pressure, brake pad %, coolant level, fuel efficiency).
3. **View AI Report** — Instantly see:
   - Overall health score & status badge
   - Component-by-component health bars
   - AI-generated alerts and recommendations
   - Estimated remaining life for brakes, tires, battery, and oil
   - A history chart tracking score trends over time

---

## 🔌 JSON API

Vehicle Passport also exposes a simple JSON API for integration with other
tools (e.g., mobile apps, dashboards):

```
GET /api/vehicle/<vehicle_id>/report
```

Returns the latest AI diagnostic report as JSON, including the overall
score, component scores, alerts, and remaining life estimates.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (zero-config, file-based)
- **Frontend:** HTML5, CSS3 (custom dark dashboard theme), Chart.js
- **AI Logic:** Custom rule-based weighted scoring engine (`brain.py`)

---

## 📈 Sample Sensor Ranges Used by the Brain

| Parameter         | Ideal Range     | Weight |
|-------------------|------------------|--------|
| Engine Temp       | 75 – 105 °C      | 20%    |
| Oil Level         | 60 – 100 %       | 18%    |
| Battery Voltage   | 12.4 – 14.7 V    | 15%    |
| Tire Pressure     | 30 – 35 PSI      | 12%    |
| Brake Pad         | 30 – 100 %       | 20%    |
| Coolant Level     | 50 – 100 %       | 10%    |
| Fuel Efficiency   | 10 – 100 km/l    | 5%     |

These values and weights can be tuned directly in `brain.py` to match
real-world vehicle specifications or specific OBD-II sensor data.

---
## 🌐 Live Demo

Experience the application online:

🔗 **Vehicle Passport:** https://basic-vehiclepassport.onrender.com

> **Note:** This project is hosted on Render's free tier. The application may take 30–60 seconds to start if it has been inactive.
> 
---

## 🔮 Future Enhancements

- Integration with real OBD-II / IoT sensor hardware for live data
- Machine learning models trained on historical fleet data for more
  accurate failure prediction
- User authentication & multi-user fleet management
- Push notifications / email alerts for critical issues
- Export AI reports as PDF for service center records

---

## 📄 License

This project is provided for academic and educational purposes. Feel free
to modify and extend it for your own coursework or personal projects.

"""
app.py - Vehicle Passport
==========================
An Artificial Brain for Intelligent Vehicle Health Management.

Flask web application that lets users:
  - Register vehicles (the "Passport")
  - Log sensor readings (engine temp, oil, battery, tires, brakes, etc.)
  - View an AI-generated health score, alerts, and predictive maintenance
  - Track history over time with charts
"""

import os
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g

from brain import VehicleBrain

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "vehicle_passport.db")

app = Flask(__name__)
app.secret_key = "vehicle-passport-secret-key-change-in-production"

# Create the data directory and database when the app starts
def init_db():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    ...
    conn.commit()
    conn.close()

# Initialize database
init_db()

# ----------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------
@app.route("/")
def index():


# ----------------------------------------------------------------------
# DATABASE HELPERS
# ----------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS vehicle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number_plate TEXT NOT NULL,
            owner TEXT,
            vehicle_type TEXT,
            year INTEGER,
            mileage INTEGER DEFAULT 0,
            last_service_km INTEGER DEFAULT 0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS reading (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            engine_temp REAL,
            oil_level REAL,
            battery_voltage REAL,
            tire_pressure REAL,
            brake_pad REAL,
            coolant_level REAL,
            fuel_efficiency REAL,
            health_score REAL,
            status TEXT,
            created_at TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicle (id)
        );
        """
    )
    conn.commit()
    conn.close()


# ----------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------
@app.route("/")
def index():
    db = get_db()
    vehicles = db.execute("SELECT * FROM vehicle ORDER BY created_at DESC").fetchall()

    vehicle_summaries = []
    for v in vehicles:
        latest = db.execute(
            "SELECT * FROM reading WHERE vehicle_id = ? ORDER BY id DESC LIMIT 1",
            (v["id"],),
        ).fetchone()

        if latest:
            score = latest["health_score"]
            status, status_class = VehicleBrain.classify(score)
        else:
            score, status, status_class = None, "No Data", "secondary"

        vehicle_summaries.append({
            "vehicle": v,
            "score": score,
            "status": status,
            "status_class": status_class,
        })

    return render_template("index.html", vehicle_summaries=vehicle_summaries)


@app.route("/vehicle/add", methods=["GET", "POST"])
def add_vehicle():
    if request.method == "POST":
        db = get_db()
        db.execute(
            """INSERT INTO vehicle
               (name, number_plate, owner, vehicle_type, year, mileage, last_service_km, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form["name"],
                request.form["number_plate"],
                request.form.get("owner", ""),
                request.form.get("vehicle_type", ""),
                request.form.get("year") or None,
                request.form.get("mileage") or 0,
                request.form.get("last_service_km") or 0,
                datetime.datetime.now().isoformat(timespec="seconds"),
            ),
        )
        db.commit()
        flash("Vehicle added to Passport successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add_vehicle.html")


@app.route("/vehicle/<int:vehicle_id>")
def vehicle_detail(vehicle_id):
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicle WHERE id = ?", (vehicle_id,)).fetchone()
    if vehicle is None:
        flash("Vehicle not found.", "danger")
        return redirect(url_for("index"))

    readings = db.execute(
        "SELECT * FROM reading WHERE vehicle_id = ? ORDER BY id DESC",
        (vehicle_id,),
    ).fetchall()

    report = None
    if readings:
        latest = dict(readings[0])
        brain = VehicleBrain(dict(vehicle), latest)
        report = brain.full_report()

    chart_data = {
        "labels": [r["created_at"] for r in reversed(readings)],
        "scores": [r["health_score"] for r in reversed(readings)],
    }

    return render_template(
        "vehicle_detail.html",
        vehicle=vehicle,
        readings=readings,
        report=report,
        chart_data=chart_data,
    )


@app.route("/vehicle/<int:vehicle_id>/log", methods=["GET", "POST"])
def log_reading(vehicle_id):
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicle WHERE id = ?", (vehicle_id,)).fetchone()
    if vehicle is None:
        flash("Vehicle not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        reading = {
            "engine_temp": float(request.form["engine_temp"]),
            "oil_level": float(request.form["oil_level"]),
            "battery_voltage": float(request.form["battery_voltage"]),
            "tire_pressure": float(request.form["tire_pressure"]),
            "brake_pad": float(request.form["brake_pad"]),
            "coolant_level": float(request.form["coolant_level"]),
            "fuel_efficiency": float(request.form["fuel_efficiency"]),
        }

        new_mileage = request.form.get("mileage")
        if new_mileage:
            db.execute(
                "UPDATE vehicle SET mileage = ? WHERE id = ?",
                (int(new_mileage), vehicle_id),
            )
            db.commit()
            vehicle = db.execute("SELECT * FROM vehicle WHERE id = ?", (vehicle_id,)).fetchone()

        brain = VehicleBrain(dict(vehicle), reading)
        report = brain.full_report()

        db.execute(
            """INSERT INTO reading
               (vehicle_id, engine_temp, oil_level, battery_voltage, tire_pressure,
                brake_pad, coolant_level, fuel_efficiency, health_score, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                vehicle_id,
                reading["engine_temp"],
                reading["oil_level"],
                reading["battery_voltage"],
                reading["tire_pressure"],
                reading["brake_pad"],
                reading["coolant_level"],
                reading["fuel_efficiency"],
                report["overall_score"],
                report["status"],
                datetime.datetime.now().isoformat(timespec="seconds"),
            ),
        )
        db.commit()

        flash("New reading analyzed by the AI Brain!", "success")
        return redirect(url_for("vehicle_detail", vehicle_id=vehicle_id))

    return render_template("log_reading.html", vehicle=vehicle)


@app.route("/vehicle/<int:vehicle_id>/delete", methods=["POST"])
def delete_vehicle(vehicle_id):
    db = get_db()
    db.execute("DELETE FROM reading WHERE vehicle_id = ?", (vehicle_id,))
    db.execute("DELETE FROM vehicle WHERE id = ?", (vehicle_id,))
    db.commit()
    flash("Vehicle removed from Passport.", "info")
    return redirect(url_for("index"))


@app.route("/api/vehicle/<int:vehicle_id>/report")
def api_report(vehicle_id):
    """JSON API endpoint returning the latest AI diagnostic report."""
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicle WHERE id = ?", (vehicle_id,)).fetchone()
    if vehicle is None:
        return jsonify({"error": "Vehicle not found"}), 404

    latest = db.execute(
        "SELECT * FROM reading WHERE vehicle_id = ? ORDER BY id DESC LIMIT 1",
        (vehicle_id,),
    ).fetchone()

    if latest is None:
        return jsonify({"error": "No readings logged yet"}), 404

    brain = VehicleBrain(dict(vehicle), dict(latest))
    return jsonify(brain.full_report())


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)

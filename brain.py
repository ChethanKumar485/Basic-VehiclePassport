"""
brain.py - The Artificial Brain of Vehicle Passport
=====================================================
This module contains the core intelligence engine that analyzes
vehicle sensor data and produces:
  - A Health Score (0-100)
  - Component-wise condition status
  - Predictive maintenance alerts
  - Estimated remaining useful life (RUL) for key components
  - Natural-language diagnostic summary

The logic here is a rule-based + weighted-scoring "expert system"
that mimics how an AI diagnostic brain would reason about a vehicle's
condition using multiple sensor streams.
"""

import datetime


class VehicleBrain:
    """The Artificial Brain class - analyzes a vehicle's latest readings."""

    # Ideal / safe operating ranges for each parameter
    IDEAL_RANGES = {
        "engine_temp": (75, 105),      # Celsius
        "oil_level": (60, 100),        # %
        "battery_voltage": (12.4, 14.7),  # Volts
        "tire_pressure": (30, 35),     # PSI
        "brake_pad": (30, 100),        # % remaining
        "coolant_level": (50, 100),    # %
        "fuel_efficiency": (10, 100),  # km/l (relative)
    }

    # Weight of each parameter in the overall health score
    WEIGHTS = {
        "engine_temp": 0.20,
        "oil_level": 0.18,
        "battery_voltage": 0.15,
        "tire_pressure": 0.12,
        "brake_pad": 0.20,
        "coolant_level": 0.10,
        "fuel_efficiency": 0.05,
    }

    SERVICE_INTERVAL_KM = 5000  # default service interval

    def __init__(self, vehicle, reading):
        """
        vehicle: dict with vehicle info (mileage, last_service_km, etc.)
        reading: dict with latest sensor reading values
        """
        self.vehicle = vehicle
        self.reading = reading

    # ------------------------------------------------------------------
    # CORE SCORING LOGIC
    # ------------------------------------------------------------------
    def _param_score(self, key):
        """Return a 0-100 score for a single parameter based on deviation
        from its ideal range."""
        value = self.reading.get(key)
        if value is None:
            return 100  # No data -> assume fine, don't penalize

        low, high = self.IDEAL_RANGES[key]

        if low <= value <= high:
            return 100

        # Penalize proportional to how far outside the range it is
        if value < low:
            deviation = (low - value) / max(low, 1)
        else:
            deviation = (value - high) / max(high, 1)

        score = max(0, 100 - deviation * 200)
        return round(score, 1)

    def component_scores(self):
        """Return a dict of component_name -> score (0-100)."""
        return {key: self._param_score(key) for key in self.IDEAL_RANGES}

    def overall_health_score(self):
        """Weighted overall health score (0-100)."""
        scores = self.component_scores()
        total = 0
        for key, weight in self.WEIGHTS.items():
            total += scores.get(key, 100) * weight
        return round(total, 1)

    # ------------------------------------------------------------------
    # STATUS CLASSIFICATION
    # ------------------------------------------------------------------
    @staticmethod
    def classify(score):
        if score >= 85:
            return "Excellent", "success"
        elif score >= 65:
            return "Good", "info"
        elif score >= 45:
            return "Warning", "warning"
        else:
            return "Critical", "danger"

    # ------------------------------------------------------------------
    # PREDICTIVE ALERTS
    # ------------------------------------------------------------------
    def generate_alerts(self):
        """Generate human-readable predictive maintenance alerts."""
        alerts = []
        r = self.reading
        scores = self.component_scores()

        if scores["engine_temp"] < 70:
            alerts.append({
                "level": "danger" if scores["engine_temp"] < 40 else "warning",
                "component": "Engine",
                "message": (
                    f"Engine temperature reading {r.get('engine_temp')}°C is "
                    "outside the safe range. Possible coolant leak, faulty "
                    "thermostat, or overheating risk. Schedule inspection soon."
                ),
            })

        if scores["oil_level"] < 70:
            alerts.append({
                "level": "danger" if scores["oil_level"] < 40 else "warning",
                "component": "Engine Oil",
                "message": (
                    f"Oil level at {r.get('oil_level')}% is low. Running with "
                    "insufficient oil accelerates engine wear. Top-up or "
                    "schedule an oil change."
                ),
            })

        if scores["battery_voltage"] < 70:
            alerts.append({
                "level": "danger" if scores["battery_voltage"] < 40 else "warning",
                "component": "Battery",
                "message": (
                    f"Battery voltage {r.get('battery_voltage')}V indicates the "
                    "battery may be weak, overcharging, or near end-of-life. "
                    "Consider a battery health test."
                ),
            })

        if scores["tire_pressure"] < 70:
            alerts.append({
                "level": "warning",
                "component": "Tires",
                "message": (
                    f"Tire pressure {r.get('tire_pressure')} PSI is outside the "
                    "recommended range. This affects fuel efficiency, handling, "
                    "and tire lifespan. Inflate/deflate to recommended PSI."
                ),
            })

        if scores["brake_pad"] < 70:
            alerts.append({
                "level": "danger" if scores["brake_pad"] < 40 else "warning",
                "component": "Brakes",
                "message": (
                    f"Brake pad remaining at {r.get('brake_pad')}%. Replace "
                    "brake pads soon to maintain safe stopping distances."
                ),
            })

        if scores["coolant_level"] < 70:
            alerts.append({
                "level": "warning",
                "component": "Cooling System",
                "message": (
                    f"Coolant level at {r.get('coolant_level')}% is low. "
                    "Refill coolant to avoid engine overheating."
                ),
            })

        if scores["fuel_efficiency"] < 70:
            alerts.append({
                "level": "info",
                "component": "Fuel System",
                "message": (
                    "Fuel efficiency has dropped below normal. This could "
                    "indicate clogged air/fuel filters, poor tire pressure, "
                    "or engine tuning issues."
                ),
            })

        # Service-due prediction based on mileage
        mileage = self.vehicle.get("mileage", 0)
        last_service = self.vehicle.get("last_service_km", 0)
        km_since_service = mileage - last_service
        if km_since_service >= self.SERVICE_INTERVAL_KM:
            alerts.append({
                "level": "warning",
                "component": "Scheduled Service",
                "message": (
                    f"Vehicle has run {km_since_service} km since last service "
                    f"(interval: {self.SERVICE_INTERVAL_KM} km). A general "
                    "service is due."
                ),
            })
        elif km_since_service >= self.SERVICE_INTERVAL_KM * 0.9:
            remaining = self.SERVICE_INTERVAL_KM - km_since_service
            alerts.append({
                "level": "info",
                "component": "Scheduled Service",
                "message": (
                    f"Only {remaining} km remaining before the next scheduled "
                    "service is due."
                ),
            })

        if not alerts:
            alerts.append({
                "level": "success",
                "component": "Overall",
                "message": (
                    "All monitored systems are operating within normal "
                    "parameters. No action required at this time."
                ),
            })

        return alerts

    # ------------------------------------------------------------------
    # REMAINING USEFUL LIFE (RUL) ESTIMATION
    # ------------------------------------------------------------------
    def estimate_remaining_life(self):
        """Rough heuristic estimation of remaining useful life of key
        wear components, expressed in kilometers."""
        r = self.reading
        estimates = {}

        # Brake pads: assume pad wears ~1% per 150 km of driving
        brake_pad = r.get("brake_pad")
        if brake_pad is not None:
            estimates["Brake Pads"] = max(0, round(brake_pad * 150))

        # Tires: assume linked to pressure deviation + generic wear
        tire_pressure = r.get("tire_pressure")
        if tire_pressure is not None:
            base_life = 40000
            low, high = self.IDEAL_RANGES["tire_pressure"]
            if tire_pressure < low or tire_pressure > high:
                base_life = int(base_life * 0.7)
            estimates["Tires"] = base_life

        # Battery: assume voltage decline maps to remaining months
        voltage = r.get("battery_voltage")
        if voltage is not None:
            if voltage >= 12.6:
                estimates["Battery"] = "18+ months"
            elif voltage >= 12.0:
                estimates["Battery"] = "6-12 months"
            else:
                estimates["Battery"] = "Replace soon (<3 months)"

        # Engine oil: km until next change based on oil level
        oil_level = r.get("oil_level")
        if oil_level is not None:
            estimates["Engine Oil"] = max(0, round(oil_level * 50))

        return estimates

    # ------------------------------------------------------------------
    # FULL DIAGNOSTIC REPORT
    # ------------------------------------------------------------------
    def full_report(self):
        score = self.overall_health_score()
        status, status_class = self.classify(score)
        return {
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "overall_score": score,
            "status": status,
            "status_class": status_class,
            "component_scores": self.component_scores(),
            "alerts": self.generate_alerts(),
            "remaining_life": self.estimate_remaining_life(),
        }

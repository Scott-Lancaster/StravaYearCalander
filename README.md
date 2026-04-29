# 🏆 Strava Year in Motion
**A clean, automated calendar visualization of your year on Strava.**

This tool fetches your Strava activities via the V3 API and generates a modern, interactive HTML dashboard. It visualizes your daily consistency, mileage, activity types, and workout streaks in a single-file portable report.

## ✨ Features
* **Full-Year Grid:** A comprehensive 12-month view optimized for both desktop and mobile.
* **Intelligent Emoji Mapping:** Automatically assigns icons (🏃‍♂️, 🚴, 🏊, etc.) based on `sport_type`.
* **Streak Tracking:** Calculates and displays your current consecutive workout streak (🔥).
* **Detailed Tooltips:** Each day shows total miles, duration, and the location (State).
* **Performance Summary:** Automatically calculates total miles, total active days, and average minutes per session for the year.
* **Secure Credential Handling:** Uses a local `config.json` to manage OAuth2 tokens and refresh cycles.

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.7+
* The `requests` library:
    ```bash
    pip install requests
    ```

### 2. Strava API Setup
To access your data, you need to create a Strava "Application":
1.  Visit the [Strava API Settings](https://www.strava.com/settings/api).
2.  Create an application (use `localhost` as the Authorization Domain).
3.  Copy your **Client ID** and **Client Secret**.
4.  **Obtain a Refresh Token:** Ensure you generate a token with `activity:read_all` scope.

### 3. Installation
1.  **Run the script** for the first time to generate the configuration template:
    ```bash
    python3 StravaCalendarReview.py
    ```
2.  **Edit the newly created `config.json`** with your details:
    ```json
    {
        "CLIENT_ID": "YOUR_ID",
        "CLIENT_SECRET": "YOUR_SECRET",
        "REFRESH_TOKEN": "YOUR_TOKEN",
        "YEAR": 2026
    }
    ```

---

## 🛠️ Usage
Execute the script to update your calendar with your latest activities:
```bash
python3 StravaCalendarReview.py
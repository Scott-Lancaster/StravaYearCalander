#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime, timezone
import os

# ========================= CONFIGURATION =========================
CONFIG_FILE = "config.json"

# Default config if file doesn't exist
DEFAULT_CONFIG = {
    "CLIENT_ID": "",
    "CLIENT_SECRET": "",
    "REFRESH_TOKEN": "",
    "YEAR": 2026
}

# Load or create config
if not os.path.exists(CONFIG_FILE):
    print(f"⚠️  {CONFIG_FILE} not found. Creating blank config file...")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    print(f"✅ Created {CONFIG_FILE}. Please fill in your Strava credentials and run again.")
    exit()

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

CLIENT_ID = config.get("CLIENT_ID", "")
CLIENT_SECRET = config.get("CLIENT_SECRET", "")
REFRESH_TOKEN = config.get("REFRESH_TOKEN", "")
YEAR = config.get("YEAR", 2026)

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("❌ Missing credentials in config.json. Please fill in CLIENT_ID, CLIENT_SECRET, and REFRESH_TOKEN.")
    exit()
# ================================================================

HTML_FILENAME = f"strava_{YEAR}_calendar.html"

EMOJI_MAP = {
    "Run": "🏃‍♂️", "Ride": "🚴", "VirtualRide": "🚴", "Swim": "🏊",
    "Hike": "🥾", "Walk": "🚶", "AlpineSki": "⛷️", "Snowboard": "🏂",
    "WeightTraining": "🏋️", "Workout": "💪", "Yoga": "🧘",
}

def get_emoji(act_type: str) -> str:
    for key, emoji in EMOJI_MAP.items():
        if key.lower() in act_type.lower():
            return emoji
    return "🏃"

def refresh_access_token():
    print("🔑 Refreshing access token...")
    response = requests.post("https://www.strava.com/api/v3/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    })
    if response.status_code != 200:
        print(f"❌ Token refresh failed: {response.status_code}")
        print(response.text)
        raise SystemExit("Token refresh failed.")
    print("✅ Access token refreshed")
    return response.json()["access_token"]

def get_all_activities(access_token):
    activities = []
    page = 1
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    after_ts = int(datetime(YEAR, 1, 1, tzinfo=timezone.utc).timestamp())
    before_ts = int(datetime(YEAR + 1, 1, 1, tzinfo=timezone.utc).timestamp())

    print(f"📡 Fetching activities for {YEAR}...")
    while True:
        params = {"after": after_ts, "before": before_ts, "per_page": 200, "page": page}
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 429:
            print("⏳ Rate limit hit — waiting 60s...")
            time.sleep(60)
            continue
            
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        activities.extend(batch)
        print(f"   Page {page}: +{len(batch)} activities (total: {len(activities)})")
        time.sleep(0.7)
        page += 1
    
    print(f"✅ Loaded {len(activities)} activities")
    return activities

# ======================== MAIN ========================
if __name__ == "__main__":
    access_token = refresh_access_token()
    activities = get_all_activities(access_token)

    daily_data = {}
    total_minutes = 0

    for act in activities:
        date_str = act.get("start_date_local", "")[:10]
        if not date_str: 
            continue
            
        miles = round(act.get("distance", 0) / 1609.34, 2)
        moving_time_min = round(act.get("moving_time", 0) / 60, 1)
        act_type = act.get("sport_type") or act.get("type", "Workout")
        state = act.get("location_state") or "??"
        
        if state in ("??", None, "", "null"):
            if "Los_Angeles" in act.get("timezone", "") or "Pacific" in act.get("timezone", ""):
                state = "CA"
        
        emoji = get_emoji(act_type)
        
        if date_str not in daily_data:
            daily_data[date_str] = {
                "emoji": emoji,
                "miles": miles,
                "state": state,
                "minutes": moving_time_min
            }
        else:
            daily_data[date_str]["miles"] += miles
            daily_data[date_str]["minutes"] += moving_time_min
            if state not in ("??", None, "", "null") and daily_data[date_str]["state"] in ("??", None, "", "null"):
                daily_data[date_str]["state"] = state
            if emoji != "🏃" and daily_data[date_str]["emoji"] == "🏃":
                daily_data[date_str]["emoji"] = emoji

        total_minutes += moving_time_min

    print(f"📊 Found {len(daily_data)} workout days")

    daily_json = json.dumps(daily_data, ensure_ascii=False)

    # Calculate average minutes per workout day
    avg_minutes = round(total_minutes / len(daily_data), 1) if daily_data else 0

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🏆 {YEAR} Strava Full Calendar</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: #0a0f1c;
      color: #e2e8f0;
      margin: 0;
      padding: 40px 20px;
    }}
    .header {{
      text-align: center;
      margin-bottom: 45px;
    }}
    .header h1 {{
      font-size: 2.7rem;
      color: #22c55e;
      margin: 0 0 10px 0;
    }}
    .subtitle {{
      color: #94a3b8;
      font-size: 1.25rem;
    }}
    .calendar-container {{
      max-width: 2000px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(610px, 1fr));
      gap: 35px;
    }}
    .month {{
      background: #1e2937;
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }}
    .month-header {{
      text-align: center;
      font-size: 1.9rem;
      font-weight: bold;
      color: #67e8f9;
      margin-bottom: 22px;
    }}
    .weekdays {{
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      text-align: center;
      font-weight: bold;
      color: #94a3b8;
      margin-bottom: 16px;
      font-size: 1.1rem;
      gap: 4px;
    }}
    .weekday {{
      padding: 6px 0;
    }}
    .days {{
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 8px;
    }}
    .day {{
      aspect-ratio: 1 / 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border-radius: 12px;
      background: #334155;
      padding: 8px 4px;
      transition: all 0.2s;
    }}
    .day:hover {{
      transform: scale(1.05);
      box-shadow: 0 10px 20px rgba(74, 222, 128, 0.3);
    }}
    .day.rest {{
      background: #1e2937;
      color: #64748b;
    }}
    .day.workout {{
      background: #14532d;
      border: 2px solid #4ade80;
    }}
    .day-top {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 1.22rem;
      font-weight: bold;
      margin-bottom: 5px;
    }}
    .day-details {{
      font-size: 0.84rem;
      line-height: 1.25;
      text-align: center;
    }}
    .day-details small {{
      color: #a1a1aa;
      font-size: 0.81rem;
    }}
    .summary {{
      text-align: center;
      margin: 55px 0 25px 0;
      font-size: 1.7rem;
      color: #86efac;
    }}
    @media (max-width: 1300px) {{
      .calendar-container {{ grid-template-columns: repeat(auto-fit, minmax(550px, 1fr)); }}
    }}
    @media (max-width: 800px) {{
      .calendar-container {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🏆 Your {YEAR} Strava Year in Motion</h1>
    <p class="subtitle">Every workout • Miles • Emoji • Location</p>
  </div>

  <div id="calendar" class="calendar-container"></div>

  <div class="summary" id="summary"></div>

  <script>
    const dailyData = {daily_json};

    let totalMiles = 0;
    let workoutDays = Object.keys(dailyData).length;
    Object.values(dailyData).forEach(d => {{ totalMiles += d.miles || 0; }});

    document.getElementById("summary").innerHTML = 
      `You worked out on <strong>${{workoutDays}}</strong> days and covered <strong>${{totalMiles.toFixed(1)}}</strong> miles in {YEAR} (avg ${{ {avg_minutes} }} min/day) 💪`;

    const months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    const container = document.getElementById("calendar");

    months.forEach((monthName, m) => {{
      const monthNum = m + 1;
      const firstDay = new Date({YEAR}, m, 1).getDay();
      const daysInMonth = new Date({YEAR}, monthNum, 0).getDate();
      
      let html = `<div class="month">
        <div class="month-header">${{monthName}} {YEAR}</div>
        <div class="weekdays">
          <div class="weekday">Su</div>
          <div class="weekday">Mo</div>
          <div class="weekday">Tu</div>
          <div class="weekday">We</div>
          <div class="weekday">Th</div>
          <div class="weekday">Fr</div>
          <div class="weekday">Sa</div>
        </div>
        <div class="days">`;
      
      for (let i = 0; i < firstDay; i++) {{
        html += `<div class="day rest"></div>`;
      }}
      
      for (let d = 1; d <= daysInMonth; d++) {{
        const dateStr = `{YEAR}-${{monthNum.toString().padStart(2,'0')}}-${{d.toString().padStart(2,'0')}}`;
        const info = dailyData[dateStr];
        
        if (info) {{
          html += `<div class="day workout">
            <div class="day-top">
              <span>${{info.emoji}}</span>
              <span>${{d}}</span>
            </div>
            <div class="day-details">
              ${{info.miles.toFixed(1)}}mi<br>
              <small>${{info.state}}</small>
            </div>
          </div>`;
        }} else {{
          html += `<div class="day rest"><div class="day-top"><span>${{d}}</span></div></div>`;
        }}
      }}
      html += `</div></div>`;
      container.innerHTML += html;
    }});
  </script>
</body>
</html>
"""

    with open(HTML_FILENAME, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n🎉 Final calendar created: {HTML_FILENAME}")
    print(f"   Config loaded from: {CONFIG_FILE}")
    print("   Open the HTML file to view your beautiful Strava year calendar!")
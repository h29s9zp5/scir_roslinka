from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

CHANNEL_ID = "3371992"      
READ_API_KEY = "DJMZFABU9W7IEWJW"   

def pobierz_dane_z_thingspeak(ilosc=20):
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
    params = {
        "api_key": READ_API_KEY,
        "results": ilosc
    }
    
    response = requests.get(url, params=params)
    dane = response.json()
    
    pomiary = []
    for wpis in dane.get("feeds", []):
        gleba = float(wpis.get("field4", 0)) if wpis.get("field4") else None
        # Jeśli gleba = -1, zamień na None (brak danych) lub 0
        if gleba == -1.0 or gleba == -1:
            gleba = None  # lub gleba = 0 (wybierz, co wolisz)
        
        pomiary.append({
            "czas": wpis.get("created_at"),
            "temperatura": float(wpis.get("field1", 0)) if wpis.get("field1") else None,
            "wilgotnosc": float(wpis.get("field2", 0)) if wpis.get("field2") else None,
            "cisnienie": float(wpis.get("field3", 0)) if wpis.get("field3") else None,
            "gleba": gleba
        })
    
    return pomiary

@app.route("/")
def index():
    """Strona główna z dashboardem"""
    pomiary = pobierz_dane_z_thingspeak(20)
    return render_template("index.html", pomiary=pomiary)

@app.route("/api/dane")
def api_dane():
    """Endpoint API dla odświeżania danych (AJAX)"""
    pomiary = pobierz_dane_z_thingspeak(20)
    return jsonify(pomiary)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
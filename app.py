from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

CHANNEL_ID = "3371992"      
READ_API_KEY = "DJMZFABU9W7IEWJW"   

def pobierz_dane_z_thingspeak(ilosc=20):
    """Pobiera ostatnie N pomiarow z ThingSpeak"""
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
    params = {
        "api_key": READ_API_KEY,
        "results": ilosc
    }
    
    response = requests.get(url, params=params)
    dane = response.json()
    
    pomiary = []
    for wpis in dane.get("feeds", []):
        temperatura = float(wpis.get("field1", 0)) if wpis.get("field1") else None
        wilgotnosc = float(wpis.get("field2", 0)) if wpis.get("field2") else None
        cisnienie = float(wpis.get("field3", 0)) if wpis.get("field3") else None
        gleba = float(wpis.get("field4", 0)) if wpis.get("field4") else None
        
        if gleba == -1.0:
            gleba = None
            
        pomiary.append({
            "czas": wpis.get("created_at"),
            "temperatura": temperatura,
            "wilgotnosc": wilgotnosc,
            "cisnienie": cisnienie,
            "gleba": gleba
        })
    
    return pomiary

def pobierz_dane_z_tygodnia(ilosc_prob=20):
    """
    Pobiera ostatnie 2000 pomiarow i zwraca ilosc_prob rownomiernie rozlozonych probek.
    
    """
    # Pobranie pomiarów - 2000, 8000 to limit dla ThingSpeak 
    wszystkie = pobierz_dane_z_thingspeak(8000)
    
    if len(wszystkie) == 0:
        return []
    
    if len(wszystkie) <= ilosc_prob:
        return wszystkie
    
    # Probkowanie rownomierne
    krok = len(wszystkie) / ilosc_prob
    probkowane = []
    for i in range(ilosc_prob):
        idx = int(i * krok)
        probkowane.append(wszystkie[idx])
    
    return probkowane

@app.route("/")
def index():
    """Strona glowna z dashboardem"""
    return render_template("index.html")

@app.route("/api/dane")
def api_dane():
    """Endpoint API – zwraca dane w zaleznosci od parametru 'tryb'"""
    tryb = request.args.get('tryb', 'ostatnie')  # 'ostatnie' lub 'tydzien'
    
    if tryb == 'tydzien':
        pomiary = pobierz_dane_z_tygodnia(20)
    else:
        pomiary = pobierz_dane_z_thingspeak(20)
    
    return jsonify(pomiary)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

measurements = []

# Obsługa zarówno POST jak i GET
@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        # Jeśli ESP32 wysyła GET, zwróć instrukcję
        return jsonify({
            "message": "Użyj metody POST do wysyłania danych",
            "example": {
                "temp": 22.5,
                "hum": 45.2,
                "press": 1013.5,
                "soil_hum": 68
            }
        }), 200
    
    # POST - odbierz dane
    try:
        content = request.get_json()
        
        # Dodaj timestamp
        content['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Zapisz
        measurements.append(content)
        
        # Wyświetl
        print("\n" + "="*50)
        print(f"Odebrano pomiar: {content.get('timestamp')}")
        print(f"Temp: {content.get('temp', '?')}°C")
        print(f"Wilg: {content.get('hum', '?')}%")
        print(f"Cisn: {content.get('press', '?')} hPa")
        print(f"Gleba: {content.get('soil_hum', '?')}%")
        print("="*50)
        
        return jsonify({"status": "ok", "received": content}), 200
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>🌱 Serwer BME280</h1>
    <p>Serwer działa!</p>
    <p>ESP32 powinno wysyłać POST na: <code>/data</code></p>
    <p><a href='/view'>Zobacz wszystkie dane</a></p>
    """

@app.route('/view', methods=['GET'])
def view_data():
    if not measurements:
        return "Brak danych - jeszcze nie odebrano żadnego pomiaru"
    
    html = "<h1>Odebrane pomiary</h1>"
    html += f"<p>Liczba pomiarów: {len(measurements)}</p>"
    html += "<table border='1' style='border-collapse: collapse;'>"
    html += "<tr style='background-color: #ddd;'><th>#</th><th>Czas</th><th>Temp</th><th>Wilgotność</th><th>Ciśnienie</th><th>Gleba</th></tr>"
    
    for i, m in enumerate(measurements[-20:], 1):
        bg = '#f0f0f0' if i % 2 == 0 else 'white'
        html += f"<tr style='background-color: {bg};'>"
        html += f"<td>{i}</td>"
        html += f"<td>{m.get('timestamp', '')}</td>"
        html += f"<td>{m.get('temp', '')}°C</td>"
        html += f"<td>{m.get('hum', '')}%</td>"
        html += f"<td>{m.get('press', '')} hPa</td>"
        html += f"<td>{m.get('soil_hum', '')}%</td>"
        html += "</tr>"
    
    html += "</table>"
    html += "<br><a href='/'>Powrót</a>"
    
    return html

if __name__ == '__main__':
    print("SERWER STARTUJE...")
    print("Adres: http://localhost:5000")
    print("Endpoint: POST http://localhost:5000/data")
    print("Podgląd: http://localhost:5000/view")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=True)
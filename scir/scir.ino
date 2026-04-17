#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define SDA_PIN 25
#define SCL_PIN 26
#define SOIL_PIN 34

Adafruit_BME280 bme;

// ===== SIEĆ =====
// ustaw poprawne wartosci 
const char* ssid = ""; 
const char* password = "";


const char* serverName = "http://192.168.1.93:5000/data";  // ZMIEŃ NA SWÓJ IP

unsigned long startTime;
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000;  // Wysyłaj co 2 sekundy

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Serial.println("\n\nStarting BME280 Sensor...");

  // Inicjalizacja I2C
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);
  
  // Inicjalizacja BME280
  if (!bme.begin(0x76)) {
    Serial.println("BME280 not found! Check wiring.");
    Serial.println("Trying address 0x77...");
    if (!bme.begin(0x77)) {
      Serial.println("BME280 still not found!");
      while (1) {
        delay(1000);
        Serial.print(".");
      }
    }
  }
  Serial.println("BME280 initialized!");

  // Połączenie WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Connecting to server: ");
    Serial.println(serverName);
  } else {
    Serial.println("\nWiFi connection failed!");
  }

  
  
  startTime = millis();
}

// ===== ODCZYT GLEBY =====
int readSoil() {
  int sum = 0;
  int count = 0;

  // Odczytaj 10 próbek
  for (int i = 0; i < 10; i++) {
    int val = analogRead(SOIL_PIN);
    if (val > 0 && val < 4095) {  // ESP32 ma 12-bit ADC (0-4095)
      sum += val;
      count++;
    }
    delay(10);
  }

  if (count == 0) return -1;
  
  int avg = sum / count;
  
  // Mapuj wartość na procent (opcjonalnie)
  // Sucha gleba: ~3000, Mokra gleba: ~1000
  int percent = map(avg, 1000, 3000, 100, 0);
  percent = constrain(percent, 0, 100);
  
  return percent;  // Zwracaj procent wilgotności
}

// ===== WYSYŁANIE DANYCH =====
void sendData(float temperature, float humidity, float pressure, int soilValue) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    return;
  }
  
  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);
  
  // Stwórz JSON
  String jsonData = "{";
  jsonData += "\"temp\":" + String(temperature, 2) + ",";
  jsonData += "\"hum\":" + String(humidity, 2) + ",";
  jsonData += "\"press\":" + String(pressure, 2) + ",";
  jsonData += "\"soil_hum\":" + String(soilValue);
  jsonData += "}";
  
  Serial.println("\nSending: " + jsonData);
  
  // Wyślij POST
  int httpResponseCode = http.POST(jsonData);
  
  if (httpResponseCode > 0) {
    Serial.print("HTTP Response: ");
    Serial.println(httpResponseCode);
    
    String response = http.getString();
    Serial.print("Server response: ");
    Serial.println(response);
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
    Serial.print("Error: ");
    Serial.println(http.errorToString(httpResponseCode));
  }
  
  http.end();
}

// ===== LOOP =====
void loop() {
  unsigned long currentMillis = millis();
  
  // Wysyłaj dane co sendInterval
  if (currentMillis - lastSendTime >= sendInterval) {
    lastSendTime = currentMillis;
    
    // Odczytaj czujniki
    float temperature = bme.readTemperature();
    float humidity = bme.readHumidity();
    float pressure = bme.readPressure() / 100.0F;
    int soilValue = readSoil();
    
    // Sprawdź czy odczyty są poprawne
    if (isnan(temperature) || isnan(humidity) || isnan(pressure)) {
      Serial.println("Failed to read from BME280!");
      return;
    }
    
    // Oblicz czas od startu
    unsigned long elapsed = currentMillis - startTime;
    int minutes = elapsed / 60000;
    int seconds = (elapsed % 60000) / 1000;
    
    // Wyświetl na serial monitor
    Serial.println("\n=================================");
    Serial.print("Czas: ");
    Serial.print(minutes);
    Serial.print(" min ");
    Serial.print(seconds);
    Serial.println(" s");
    Serial.print("Temperatura: ");
    Serial.print(temperature, 2);
    Serial.println(" °C");
    Serial.print("Wilgotność powietrza: ");
    Serial.print(humidity, 2);
    Serial.println(" %");
    Serial.print("Ciśnienie: ");
    Serial.print(pressure, 2);
    Serial.println(" hPa");
    Serial.print("Wilgotność gleby: ");
    Serial.print(soilValue);
    Serial.println(" %");
    Serial.println("=================================");
    
    // Wyślij dane na serwer
    sendData(temperature, humidity, pressure, soilValue);
  }
  
  delay(100);  // Małe opóźnienie
}
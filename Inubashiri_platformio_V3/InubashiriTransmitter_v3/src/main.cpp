/*
- main.cpp -

EBYTE LoRa E220

Receive messages on CHANNEL 23
Uncomment #define ENABLE_RSSI true in this sketch
if the sender send RSSI also

by Renzo Mischianti <https://www.mischianti.org>
modified by takurx, 2025/10/01

https://www.mischianti.org
E220		  ----- esp32		     
M0       ----- 21 (or GND) 	
M1       ----- 19 (or GND)
TX       ----- 16, TX2 (PullUP)	
RX       ----- 17, RX2 (PullUP)
AUX      ----- 15  (PullUP)	
VCC      ----- 3.3v/5v
GND      ----- GND

ESP32 UART x3
COM0 RX: RXD0
COM0 TX: TXD0

COM1 RX: GPIO09 -> modify, GPIO27 -> GNSS TX
COM1 TX: GPIO10 -> modify, GPIO26 -> GNSS RX

COM2 RX: GPIO16 -> LoRa TX
COM2 TX: GPIO17 -> LoRa RX

- ~/.platformio/packages/framework-arduinoespressif32/cores/esp32/HardwareSerial.cpp
#if CONFIG_IDF_TARGET_ESP32
#define SOC_RX0 3
#define SOC_TX0 1

#define RX1 9
#define TX1 10

#define RX2 16
#define TX2 17

Simple Serial1 to Serial forwarder - GPGGA sentences only
*/

// If you want use RSSI uncomment
//#define ENABLE_RSSI true

#include <Arduino.h>
#include <LoRa_E220.h>

// ---------- esp32 pins --------------
LoRa_E220 e220ttl(&Serial2, 15, 21, 19); //  RX AUX M0 M1

//LoRa_E220 e220ttl(&Serial2, 22, 4, 18, 21, 19, UART_BPS_RATE_9600); //  esp32 RX <-- e220 TX, esp32 TX --> e220 RX AUX M0 M1
// -------------------------------------

unsigned int counter = 0;
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

String nmeaBuffer = "";
bool receivingNmea = false;

String gpggaSentence = "";
bool flag_gpgga_received = false;

void setup() {
  Serial.begin(115200);
  delay(500);

  // Startup all pins and UART
  e220ttl.begin(); // Initialize Serial2 (LoRa) for input
  
  // Initialize Serial1 (GNSS) for input
  Serial1.begin(9600, SERIAL_8N1, 27, 26); // RX, TX

  Serial.println("Start receiving!");
}

void loop() {
  // Check if data is available on Serial1
  if (Serial1.available() > 0) {
    char receivedChar = Serial1.read();
    
    // Start of NMEA sentence
    if (receivedChar == '$') {
      nmeaBuffer = "$";
      receivingNmea = true;
    }
    // End of NMEA sentence
    else if (receivedChar == '\n' && receivingNmea) {
      nmeaBuffer += receivedChar;
      
      // Check if it's a GPGGA sentence
      if (nmeaBuffer.startsWith("$GPGGA")) {
        flag_gpgga_received = true;
        gpggaSentence = nmeaBuffer;
        // Serial.print(nmeaBuffer);
        // e220ttl.sendMessage(nmeaBuffer);
      }
      
      // Reset for next sentence
      nmeaBuffer = "";
      receivingNmea = false;
    }
    // Middle of NMEA sentence
    else if (receivingNmea) {
      nmeaBuffer += receivedChar;
    }
  }

  currentMillis = millis();
  if (currentMillis - previousMillis > 1000) {
    Serial.println("currentMillis: " + String(currentMillis));
    Serial.println("previousMillis: " + String(previousMillis));
    // e220ttl.sendMessage("Hello, I'm transmitter side\n");
    Serial.println("Sending heart beat counter: " + String(counter));
    
    if (flag_gpgga_received) {
      e220ttl.sendMessage(gpggaSentence);
      Serial.print(gpggaSentence);
      gpggaSentence = "";
      flag_gpgga_received = false;
    } else {
      // e220ttl.sendMessage("No GPGGA received yet, heart beat: " + String(counter) + "\n");
    }
    counter++;

    previousMillis = currentMillis;
  }

  /*
  // If something available
  if (e220ttl.available() > 1) {
    Serial.println("Message received!");

    // read the String message
#ifdef ENABLE_RSSI
    ResponseContainer rc = e220ttl.receiveMessageRSSI();
#else
    ResponseContainer rc = e220ttl.receiveMessage();
#endif
    // Is something goes wrong print error
    if (rc.status.code != 1) {
      Serial.println(rc.status.getResponseDescription());
    } else {
      // Print the data received
      Serial.println(rc.status.getResponseDescription());
      Serial.println(rc.data);
#ifdef ENABLE_RSSI
      Serial.print("RSSI: "); Serial.println(rc.rssi, DEC);
#endif
    }
  }
  */
}

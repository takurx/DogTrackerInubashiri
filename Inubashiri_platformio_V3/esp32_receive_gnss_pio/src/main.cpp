/*
- main.cpp -

ESP32 UART x3
COM0 RX: RXD0
COM0 TX: TXD0

COM1 RX: GPIO09 -> modify, GPIO12 -> GNSS TX
COM1 TX: GPIO10 -> modify, GPIO14 -> GNSS RX

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

#include <Arduino.h>

String nmeaBuffer = "";
bool receivingNmea = false;

void setup() {
  // Initialize Serial (USB) for output
  Serial.begin(115200);
  delay(1000);
  Serial.println("Serial1 to Serial forwarder started (GPGGA only)");

  // Initialize Serial1 (GNSS) for input
  Serial1.begin(9600, SERIAL_8N1, 12, 14);

  //Serial2.begin(9600); // Initialize Serial2 (LoRa) for input
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
        Serial.print(nmeaBuffer);
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
}

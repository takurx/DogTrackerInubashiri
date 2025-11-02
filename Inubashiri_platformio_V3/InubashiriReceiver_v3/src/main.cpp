/*
 * EBYTE LoRa E220
 *
 * Receive messages on CHANNEL 23
 * Uncomment #define ENABLE_RSSI true in this sketch
 * if the sender send RSSI also
 *
 * by Renzo Mischianti <https://www.mischianti.org>
 * modified by takurx, 2025/10/01
 *
 * https://www.mischianti.org
 *
 * E220		  ----- esp32		     
 * M0       ----- 21 (or GND) 	
 * M1       ----- 19 (or GND)
 * TX       ----- 16, TX2 (PullUP)	
 * RX       ----- 17, RX2 (PullUP)
 * AUX      ----- 15  (PullUP)	
 * VCC      ----- 3.3v/5v
 * GND      ----- GND
 *
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

void setup() {
  Serial.begin(9600);
  delay(500);

  // Startup all pins and UART
  e220ttl.begin();
  Serial.println("Start receiving!");
}

void loop() {
  currentMillis = millis();
  if (currentMillis - previousMillis > 1000) {
    e220ttl.sendMessage("Hello, I'm receiver side\n");
    e220ttl.sendMessage("heart beat counter: " + String(counter++));
    // delay(1000);
    previousMillis = currentMillis;
  }

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
}

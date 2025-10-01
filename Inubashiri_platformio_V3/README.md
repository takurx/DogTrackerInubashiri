# Inubashiri_platformio_V3

## components
1. ESP32 DevKitC x2
2. E220 x2
3. bread board x2
4. bread board wire

## diagram
```
ESP32 DevKitC - (UART) - E220 <---> E220 - (UART) - ESP32 DevKitC
```


| ESP32 DevKitC | E220  | E220  | ESP32 DevKitC |
| :------------ | :---- | :---- | :------------ |
| 3V3           | 2 VCC | 2 VCC | 3V3           |
| GND           | 1 GND | 1 GND | GND           |
| GPIO15        | 3 AUX | 3 AUX | GPIO15        |
| GPIO16        | 4 TXD | 4 TXD | GPIO16        |
| GPIO17        | 5 RXD | 5 RXD | GPIO17        |
| GPIO19        | 6 M1  | 6 M1  | GPIO19        |
| GPIO21        | 7 M0  | 7 M0  | GPIO21        |






// ESP32 LED Blinking Code
const int ledPin = 2; // ESP32 ka built-in LED pin

void setup() {
  pinMode(ledPin, OUTPUT); // LED pin ko output mode pe set karo
}

void loop() {
  digitalWrite(ledPin, HIGH); // LED ON
  delay(1000);                // 1 sec wait
  digitalWrite(ledPin, LOW);  // LED OFF
  delay(1000);                // 1 sec wait
}

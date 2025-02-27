// LED Blinking Code for Arduino
void setup() {
  pinMode(13, OUTPUT); // LED pin set karna
}

void loop() {
  digitalWrite(13, HIGH); // LED ON
  delay(1000);            // 1 sec wait
  digitalWrite(13, LOW);  // LED OFF
  delay(1000);            // 1 sec wait
}

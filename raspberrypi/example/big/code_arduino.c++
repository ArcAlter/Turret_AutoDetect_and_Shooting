
#include <Servo.h>

Servo myservo;
int pos = 0;
int led_level = 0;
int  led_pins[] = {3,4,5,6,7,8,9,10};


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  myservo.attach(2);
  for (int i = 0; i < 8 ; i++) {
      pinMode(led_pins[i], OUTPUT);
  }
  for (int i = 0; i < 8 ; i++) {
      pinMode(led_pins[i], HIGH);
  }



}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
      pos = Serial.parseInt();
      led_level = map(pos,0,180,0,8);
      myservo.write(pos);
      Serial.println(led_level);
      light_on(led_level);
  }
}



void light_on(int index){
  for (int i = 0; i < 8; i++) {
    digitalWrite(led_pins[i], HIGH);
  }
  if (index != 0);
    digitalWrite(led_pins[index - 1],LOW);


}

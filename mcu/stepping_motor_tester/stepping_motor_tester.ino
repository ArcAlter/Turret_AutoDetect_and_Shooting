// Define pin connections
const int dirPin = 18;
const int stepPin = 19;

// Global settings - Adjusted for 1/16 microstepping
// 1000 / 16 is approx 62, but we'll use 100 for a stable start
int baseStepDelay = 100;   // Target speed (lower = faster)
bool running = false;
bool scanMode = false;
int direction = HIGH;

// Scan Mode Variables - Scaled by 16x
long currentStep = 0;
const long stepsPerScan = 16000; // Total microsteps (1000 full steps * 16)
const int rampSteps = 4800;      // Ramp length (300 full steps * 16)
const int slowDelay = 400;       // Starting speed (2000 / 16 = 125, but 400 is smoother for starts)

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  Serial.begin(115200);
  printMenu();
}

void loop() {
  if (Serial.available() > 0) {
    handleCommand(Serial.read());
  }

  if (running) {
    int effectiveDelay;

    if (scanMode) {
      effectiveDelay = calculateScanDelay();
      
      digitalWrite(dirPin, direction);
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(effectiveDelay);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(effectiveDelay);

      currentStep++;

      if (currentStep >= stepsPerScan) {
        direction = !direction;
        currentStep = 0;
        Serial.println(">>> Scanning: Changing Direction");
      }
    } else {
      digitalWrite(dirPin, direction);
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(baseStepDelay);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(baseStepDelay);
    }
  }
}

int calculateScanDelay() {
  if (currentStep < rampSteps) {
    return map(currentStep, 0, rampSteps, slowDelay, baseStepDelay);
  } 
  else if (currentStep > (stepsPerScan - rampSteps)) {
    return map(currentStep, stepsPerScan - rampSteps, stepsPerScan, baseStepDelay, slowDelay);
  }
  return baseStepDelay;
}

void handleCommand(char cmd) {
  switch (cmd) {
    case '1': running = true; scanMode = false; Serial.println(">>> Mode: STANDARD"); break;
    case '0': running = false; Serial.println(">>> Motor: STOPPED"); break;
    case 's': 
      scanMode = true; running = true; currentStep = 0;
      Serial.println(">>> Mode: SCAN (1/16 Microstepping)");
      break;
    case 'd': direction = !direction; break;
    case '+': 
      baseStepDelay = max(20, baseStepDelay - 10); // Fine-tuned increment
      Serial.print(">>> Delay: "); Serial.println(baseStepDelay);
      break;
    case '-': 
      baseStepDelay += 10; 
      Serial.print(">>> Delay: "); Serial.println(baseStepDelay);
      break;
    case 'h': printMenu(); break;
  }
}

void printMenu() {
  Serial.println("\n--- Stepper 1/16 Step Menu ---");
  Serial.println("[1] Standard  [0] Stop");
  Serial.println("[s] Scan Mode (Smooth Ramp)");
  Serial.println("[+] Faster    [-] Slower");
  Serial.println("------------------------------");
}
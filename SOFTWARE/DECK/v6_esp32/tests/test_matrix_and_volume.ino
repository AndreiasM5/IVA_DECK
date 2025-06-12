//keys
const int numRows = 3; // number of rows
const int numCols = 3; // number of cols
const int rowPins[numRows] = {26, 27, 4}; // set pins for row
const int colPins[numCols] = {32, 33, 25}; // set pins for col
bool keyStates[numRows][numCols] = {false};

//volume
const int Volume0 = 36;
const int Volume1 = 39;
const int Volume2 = 34;

int previousVolume = 0;
int previousGameControl = 0;
int previousSpotifyControl = 0;


void setup() {
  Serial.begin(9600);

  // keys
  for (int col = 0; col < numCols; col++) {
    pinMode(colPins[col], INPUT_PULLUP);
  }
  for (int row = 0; row < numRows; row++) {
    pinMode(rowPins[row], OUTPUT);
    digitalWrite(rowPins[row], HIGH);
  }

  //volume
  previousVolume = analogRead(Volume0);
  previousGameControl = analogRead(Volume1);
  previousSpotifyControl = analogRead(Volume2);
}

void loop() {
  
  // keys
  for (int row = 0; row < numRows; row++) {
    digitalWrite(rowPins[row], LOW);
    for (int col = 0; col < numCols; col++) {
      if (digitalRead(colPins[col]) == LOW) {
        keyStates[row][col] = true;
        Serial.print("Key pressed at row ");
        Serial.print(row);
        Serial.print(", col ");
        Serial.println(col);
      } else {
        keyStates[row][col] = false;
      }
    }
    digitalWrite(rowPins[row], HIGH);
  }
  delay(50); // debounce the keys

  //Volume
  // Read potentiometer values
  int volumeReading = analogRead(Volume0);
  int gameControlReading = analogRead(Volume1);
  int spotifyControlReading = analogRead(Volume2);

  if(previousVolume - volumeReading > 10 || previousVolume - volumeReading < -10){
    Serial.print("Volume: ");
    Serial.println(volumeReading);
    previousVolume = volumeReading;
  }
  if(previousGameControl - gameControlReading > 10 || previousGameControl - gameControlReading < -10){
    Serial.print("Game Control: ");
    Serial.println(gameControlReading);
    previousGameControl = gameControlReading;
  }
  if(previousSpotifyControl - spotifyControlReading > 10 || previousSpotifyControl - spotifyControlReading < -10){
    Serial.print("Spotify Control: ");
    Serial.println(spotifyControlReading);
    previousSpotifyControl = spotifyControlReading;
  }
  
  previousVolume = volumeReading;
  previousGameControl = gameControlReading;
  previousSpotifyControl = spotifyControlReading;
  
  delay(100); // Adjust the delay as needed for responsiveness
}

#include <TimerOne.h>        // 16 bit counter with uS resolution

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

// variables to hold the parsed data
char Song[numChars] = {0};
float BPM = 120;
float newBPM = 0;
int TimeLine = 0;
int newTimeLine = 0;
int BigSky = 0;
int newBigSky = 0;
unsigned long PERIOD;         // microseconds, setting Timer1
char tempString[10]; // for sprintf
char songstuff[4][32];

boolean newData = false;

void MIDI_CLOCK() // ISR: send MIDI CLock
{
  Serial1.write(0xF8);
}
  
void setNewBPM(){
  BPM = newBPM;
  PERIOD = 2.5e6 / BPM;  // period in microseconds, 24x beat clock
  Timer1.initialize(PERIOD);
}

void setNewTimeLine(){
  if (TimeLine < 127 && newTimeLine > 127) {
      Serial1.write(0xB0);
      Serial1.write((byte)0x00);
      Serial1.write(0x01);
    }
  else if (TimeLine > 127 && newTimeLine < 127) {
      Serial1.write(0xB0);
      Serial1.write((byte)0x00);
      Serial1.write((byte)0x00);
    }
    
  if (newTimeLine > 127) {
      Serial1.write(0xC0);
      Serial1.write((newTimeLine-128));
   }
  else {
      Serial1.write(0xC0);
      Serial1.write(newTimeLine);
   }
   
  TimeLine = newTimeLine;
}

void setNewBigSky(){
  if (newBigSky <= 127 && 127 < BigSky) {
      Serial1.write(0xB1);
      Serial1.write((byte)0x00);
      Serial1.write(0x00);
    }
  else if ((127 < newBigSky && newBigSky <= 255) && (BigSky<=127 || BigSky>255)) {
      Serial1.write(0xB1);
      Serial1.write((byte)0x00);
      Serial1.write((byte)0x01);
    }
  else if (255 < newBigSky  && BigSky <= 255 ) {
      Serial1.write(0xB1);
      Serial1.write((byte)0x00);
      Serial1.write((byte)0x02);
    }



  if (newBigSky > 255) {
      Serial1.write(0xC1);
      Serial1.write((newBigSky-256));
  }
  else if ((127 < newBigSky && (newBigSky <=255))) {
      Serial1.write(0xC1);
      Serial1.write((newBigSky-128));
   }
  else {
      Serial1.write(0xC1);
      Serial1.write(newBigSky);
   }
   
  BigSky = newBigSky;
}

//============

void setup() {
    
    Serial.begin(115200);  // serial monitor
    Serial1.begin(31250);   // MIDI baud = 31250
    Serial.println("<Arduino is ready>");

    PERIOD = 2.5e6 / BPM;  // period in microseconds, 24x beat clock
    Timer1.initialize(PERIOD);
    Timer1.attachInterrupt( MIDI_CLOCK ); // set interrupt handler
    Serial2.begin(9600);
    Serial2.setTimeout(200);
}


//============

void loop() {
    Timer1.attachInterrupt( MIDI_CLOCK );  // enable interrupt, set handler
    //static uint32_t lasttime;
    //uint32_t currtime = micros();

     //if (currtime - lasttime >= PERIOD)
     //{
        //MIDI_CLOCK();
        //lasttime = currtime;
     //}

     int len = Serial2.available();
     if (len){
//        char* s = malloc(sizeof(char) * (len+1));
//        for (int i = 0; i < len; ++i){
//          s[i] = Serial2.read();
//        }
        String s = Serial2.readString();
        char buf[64];
        s.toCharArray(buf, sizeof(buf));
     //Serial.print(s);

        char *p = buf;
        char *str;
        for (int i = 0; i < 4; ++i)
        {
          str = strtok_r(p, ",", &p);
          strcpy(songstuff[i], str);
          //Serial.println(str);
        }
        
        strcpy(Song, songstuff[0]);          // copy it to messageFromPC
        newBPM = atof(songstuff[1]);     // convert this part to an int
        newTimeLine = atoi(songstuff[2]);     // convert this part to an integer
        newBigSky = atoi(songstuff[3]);     // convert this part to an integer

        Serial.print("Song ");
        Serial.println(Song);
        Serial.print("BPM ");
        Serial.println(newBPM);
        Serial.print("TimeLine ");
        Serial.println(newTimeLine);
        Serial.print("BigSky ");
        Serial.println(newBigSky);
        
        setNewBPM();
        setNewTimeLine();
        setNewBigSky();
     }
}

//============

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial2.available() > 0 && newData == false) {
        rc = Serial2.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index
    
    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(Song, strtokIndx);          // copy it to messageFromPC
    
    strtokIndx = strtok(NULL, ",");
    newBPM = atoi(strtokIndx);     // convert this part to an int
 
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    TimeLine = atoi(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    BigSky = atoi(strtokIndx);     // convert this part to an integer
}

//============

void showParsedData() {
    Serial.print("Song ");
    Serial.println(Song);
    Serial.print("BPM ");
    Serial.println(newBPM);
    Serial.print("TimeLine ");
    Serial.println(newTimeLine);
    Serial.print("BigSky ");
    Serial.println(BigSky);
}

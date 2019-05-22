#include <TimerOne.h>        // 16 bit counter with uS resolution
#include "LPD8806.h"
#include "SPI.h"

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

// constants won't change. They're used here to set pin numbers:
const int startPedaling = 3;     // pin number for the enabling serial connection

// variables
char Song[numChars] = {0};
float BPM = 100;
float newBPM = 120;
int TimeLine = 0;
int newTimeLine = 0;
int BigSky = 0;
int newBigSky = 0;
unsigned long PERIOD;         // microseconds, setting Timer1
char tempString[10]; // for sprintf
char songstuff[4][32];
int programStarted = 0;
boolean serialEnabled = false; 
boolean newData = false;
int nLEDs = 60;
LPD8806 strip = LPD8806(nLEDs);
float beat =  60000000/BPM;
int lit = 0;



void MIDI_CLOCK() // ISR: send MIDI CLock
{
  Serial1.write(0xF8);
}

void lightsOn(){
  int i;
  for (i=0; i < strip.numPixels(); i++) {
     strip.setPixelColor(i, strip.Color (0, 15, 0));
     strip.show();}
}

void lightsOff(){
  int i;
  for (i=0; i < strip.numPixels(); i++) {
     strip.setPixelColor(i, 0);
     strip.show();}
}
  
void setNewBPM(){
  BPM = newBPM;
  PERIOD = 2.5e6 / BPM;  // period in microseconds, 24x beat clock
  Timer1.initialize(PERIOD);
  beat =  60000000/BPM;
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

void setup() {
    
    Serial.begin(115200);  // serial monitor
    Serial1.begin(31250);   // MIDI baud = 31250
    Serial.println("<Arduino is ready>");

    PERIOD = 2.5e6 / BPM;  // period in microseconds, 24x beat clock
    Timer1.initialize(PERIOD);
    pinMode(startPedaling, INPUT);
    // start the led strip
    strip.begin();
    strip.show();
}

void loop() {
    Timer1.attachInterrupt( MIDI_CLOCK );  // enable interrupt, set handler

    if ((programStarted == LOW)){
      programStarted = digitalRead(startPedaling);    
     }


    if ((programStarted == HIGH) && (serialEnabled == false)){
          Serial2.begin(9600);
          Serial2.setTimeout(200);
          serialEnabled = true;
     }

    
    static uint32_t oldTime;
    uint32_t currtime = micros();

     if (currtime > oldTime && !lit){
        lightsOn();
        lit=1;
        oldTime = currtime + (beat/3);
     }
     else if (currtime > oldTime && lit){
        lightsOff();
        lit=0;
        oldTime = currtime + ((2*beat)/3);
     }
     

     int len = Serial2.available();
     if (len){
        String s = Serial2.readString();
        char buf[64];
        s.toCharArray(buf, sizeof(buf));

        char *p = buf;
        char *str;
        for (int i = 0; i < 4; ++i)
        {
          str = strtok_r(p, ",", &p);
          strcpy(songstuff[i], str);
        }
        
        strcpy(Song, songstuff[0]);          // copy it to messageFromPC
        newBPM = atof(songstuff[1]);     // convert this part to an float
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

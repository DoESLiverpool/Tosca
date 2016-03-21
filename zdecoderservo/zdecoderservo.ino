// this one plugs into the BeagleBone with P9.26 (Steppin02) to IRQ
// and P9.24 (dirpin02) to digital pin 5.

// integrates the position from the step and direction and 
// sends the word in the payload out to the RF

#include <Servo.h>

// Serial port used for logging
#define LOG Serial
//#include "SoftwareSerial.h"
//SoftwareSerial gLogSerial(10, 11); // RX, TX
//#define LOG gLogSerial

#ifdef LOG
#define P(X) LOG.print(X)
#define PH(X) LOG.print(X, HEX)
#else
#define P(X)
#define PH(X)
#endif

Servo penservo; 

int pinstep = 3; // irq1
int pindirection = 5;   // check PIND value below

int ledpin = 13; 
int actuatorpin = 6; 

int initialposition; 
bool binitialpositionset = false; 

long servolo = 20; 
long servohi = 160; 

long zlo = -100; 
long zhi = 10; 

void initialcycle(bool bshowactuate) 
{
    // initial flow through two cycles to see it move
    for (int i = 0; i < 2; i++) {
        P("actuate "); 
        P(i); 
        P("\r\n"); 
        for (int j = 50; j <= 200; j++) {
            if (bshowactuate)
                penservo.write(map(j, 50, 200, servolo, servohi)); 
            delay(5); 
            digitalWrite(ledpin, (((j/10) % 2) == 1 ? HIGH : LOW)); 
        }
        for (int j = 200; j >= 50; j--) {
            if (bshowactuate)
                penservo.write(map(j, 50, 200, servolo, servohi)); 
            delay(5); 
            digitalWrite(ledpin, (((j/10) % 2) == 1 ? HIGH : LOW)); 
        }
    }
    binitialpositionset = false; 
}

void setup() 
{
#ifdef LOG
    LOG.begin(9600);
#endif
    P("Hello world\r\n");
    pinMode(pinstep, INPUT); 
    pinMode(pindirection, INPUT); 
    attachInterrupt(1, incz, RISING);
    P("Let's go!\r\n");
    pinMode(ledpin, OUTPUT); 

    penservo.attach(actuatorpin); 
    
    //while (true) 
    delay(1000);
    initialcycle(true); 
}

volatile int zpos = 0; 
void incz() 
{
    if (PIND & 0x20)  // pindirection==5!
        zpos++; 
    else
        zpos--; 
}

int prevzpos; 
int ncount = 0; 
long npingcount = 1000; 
int ledtoggle; 

void loop() 
{
    digitalWrite(ledpin, ((++ledtoggle) % 2 ? HIGH : LOW)); 
    int servopos = map(constrain(zpos, zlo, zhi), zlo, zhi, servolo, servohi); 
    penservo.write(servopos); 
#if 0
    P("\r\nZ");
    P(zpos);
    P(" S");
    P(servopos);
#endif
    delay(20);
}





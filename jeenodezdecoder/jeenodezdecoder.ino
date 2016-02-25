// this one plugs into the BeagleBone with P9.26 (Steppin02) to IRQ
// and P9.24 (dirpin02) to digital pin 5.

// integrates the position from the step and direction and 
// sends the word in the payload out to the RF

#include <JeeLib.h>

#define P(X) Serial.print(X)
#define PH(X) Serial.print(X, HEX)

const byte network = 212; // network group (can be in the range 1-255).
const byte myNodeID = 3; // unique node ID of receiver (1 through 30)
const byte freq = RF12_433MHZ; // Match freq to module
const byte RF12_NORMAL_SENDWAIT = 0;

const int payloadCount = 2; // the number of integers in the payload message
int payload[payloadCount];

void setup() 
{
    Serial.begin(9600);
    pinMode(3, INPUT); 
    pinMode(5, INPUT); 
    attachInterrupt(1, incz, RISING);
    rf12_initialize(myNodeID, freq, network); // Initialize RFM12
    pinMode(6, OUTPUT); 
}

int zpos = 0; 
void incz() 
{
    if (PIND & 0x20)
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
    if ((zpos != prevzpos) || (--npingcount == 0)) {
        while (!rf12_canSend()) 
            rf12_recvDone(); // no, so service the driver
        prevzpos = zpos; 
        payload[0] = prevzpos; 
        payload[1] = ncount++; 
        rf12_sendStart(1, payload, payloadCount*sizeof(int));
        rf12_sendWait(RF12_NORMAL_SENDWAIT); // wait for send completion
        npingcount = 100000;
        P("Z"); 
        P(prevzpos); 
        P("\n"); 
        digitalWrite(6, ((++ledtoggle) % 2 ? HIGH : LOW));         
        delay(50);
    }
}





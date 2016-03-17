// this one plugs into the BeagleBone with P9.26 (Steppin02) to IRQ
// and P9.24 (dirpin02) to digital pin 5.

// integrates the position from the step and direction and 
// sends the word in the payload out to the RF

#include <XBee.h>

// Which Polargraph are we?
#define TOSCA
//#define KNUT

// If you're using a Mega, you can use different hardware serial ports for both the XBee and the logging.
// In that case (unless you're using an XBee shield), it's easiest to use Serial for logging, and Serial1 to talk to the XBee
// If you're using an Uno (or similar), which only has one hardware serial port, it's best to use Serial for the XBee
// and then SoftwareSerial (coupled to a USB-to-serial adapter) for logging

// Serial port used to communicate with the XBee module
#define XBEE  Serial

// Serial port used for logging
//#define LOG Serial
#include "SoftwareSerial.h"
SoftwareSerial gLogSerial(10, 11); // RX, TX
#define LOG gLogSerial

#ifdef LOG
#define P(X) LOG.print(X)
#define PH(X) LOG.print(X, HEX)
#else
#define P(X)
#define PH(X)
#endif

int ledpin = 6; 
const int payloadCount = 2; // the number of integers in the payload message
int payload[payloadCount];
int pinstep = 3; // irq1
int pindirection = 5;   // check PIND value below

// Comms details
XBee gXBee = XBee();
#ifdef TOSCA
// Specify the address of the remote XBee (this is the SH + SL)
XBeeAddress64 gActuatorAddr64 = XBeeAddress64(0x0013a200, 0x40d9d49f);
#else // KNUT
// Specify the address of the remote XBee (this is the SH + SL)
XBeeAddress64 gActuatorAddr64 = XBeeAddress64(0x0013a200, 0x40d9d5cf);
#endif

void setup() 
{
    XBEE.begin(9600);
    // Tell XBee to use Hardware Serial. It's also possible to use SoftwareSerial
    gXBee.setSerial(XBEE);

#ifdef LOG
    LOG.begin(9600);
#endif
    P("Hello world\r\n");
    pinMode(pinstep, INPUT); 
    pinMode(pindirection, INPUT); 
    attachInterrupt(1, incz, RISING);
    P("Let's go!\r\n");
    pinMode(ledpin, OUTPUT); 
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
    if ((zpos != prevzpos) || (--npingcount == 0)) 
    {
        prevzpos = zpos; 
        payload[0] = prevzpos; 
        payload[1] = ncount++; 

        // special cases
        if ((payload[1] == 999) || (payload[1] == -998))
        {
            payload[1] = 0; 
        }
        
        // Create a TX Request...
        //ZBTxRequest zbTx = ZBTxRequest(gActuatorAddr64, (uint8_t*)payload, sizeof(payload));
        Tx64Request tx = Tx64Request(gActuatorAddr64, (uint8_t*)payload, sizeof(payload));
        // ...and send it
        gXBee.send(tx);

        npingcount = 100000;
        P("Z"); 
        P(prevzpos); 
        P("\r\n"); 
        digitalWrite(ledpin, ((++ledtoggle) % 2 ? HIGH : LOW));         
        delay(50);
    }
}





/*
   Copyright (c) 2018, circuits4you.com
   All rights reserved.
   Create a TCP Server on ESP8266 NodeMCU.
   TCP Socket Server Send Receive Demo
*/

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

int port = 5050; // Port number
WiFiUDP UDP;
char data[10];
// Server connect to WiFi Network
const char *ssid = "TP-LINK";          // Enter your wifi SSID
const char *password = "Givehimmercy"; // Enter your wifi Password

// Set your Static IP address
IPAddress local_IP(192, 168, 1, 69);
// Set your Gateway IP address
IPAddress gateway(192, 168, 1, 1);

IPAddress subnet(255, 255, 0, 0);

IPAddress primaryDNS(8, 8, 8, 8);   // optional
IPAddress secondaryDNS(8, 8, 4, 4); // optional
//=======================================================================
//                    Power on setup
//=======================================================================
int frpin = 14;
int fgpin = 12;
int fbpin = 13;

int srpin = 5;
int sgpin = 4;
int sbpin = 0;

void setup()
{

  // initiates rgb pins for the first led strip
  pinMode(frpin, OUTPUT);
  pinMode(fgpin, OUTPUT);
  pinMode(fbpin, OUTPUT);

  // initiates rgb pins for the second led strip
  pinMode(srpin, OUTPUT);
  pinMode(sgpin, OUTPUT);
  pinMode(sbpin, OUTPUT);

  Serial.begin(9600);
  Serial.println();

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS))
  {
    Serial.println("STA Failed to configure");
  }
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); // Connect to wifi

  // Wait for connection
  Serial.println("Connecting to Wifi");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(100);
    Serial.print(".");
  }

  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  UDP.begin(port);
  Serial.print("Open Telnet and connect to IP:");
  Serial.print(WiFi.localIP());
  Serial.print(" on port ");
  Serial.println(port);
}
//=======================================================================
//                    Loop
//=======================================================================

int R = 255;
int G = 0;
int B = 0;

void loop()
{
  int data_len = UDP.parsePacket();
  if (data_len >= 10)
  {
    // read data from the connected client
    UDP.readBytes(data, 10);

    R = (data[1] - 48) * 100 + (data[2] - 48) * 10 + (data[3] - 48);
    G = (data[4] - 48) * 100 + (data[5] - 48) * 10 + (data[6] - 48);
    B = (data[7] - 48) * 100 + (data[8] - 48) * 10 + (data[9] - 48);
    if (data[0] == 'b')
    {
      analogWrite(frpin, R);
      analogWrite(srpin, R);
      analogWrite(fgpin, G);
      analogWrite(sgpin, G);
      analogWrite(fbpin, B);
      analogWrite(sbpin, B);
    }
    else if (data[0] == 'f')
    {
      analogWrite(frpin, R);
      analogWrite(fgpin, G);
      analogWrite(fbpin, B);
    }
    else if (data[0] == 's')
    {
      analogWrite(srpin, R);
      analogWrite(sgpin, G);
      analogWrite(sbpin, B);
    }

    int data_len = UDP.parsePacket();
    if (data_len >= 10 * 5)
    {
      if (data_len % 10 == 0)
      {
        char extra_data[data_len - 10];
        UDP.readBytes(extra_data, data_len - 10);
      }
    }
  }
}
//=======================================================================

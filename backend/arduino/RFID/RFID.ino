#include <SPI.h>
#include <MFRC522.h>
#include <EEPROM.h>
#include "hmac_sha256.h"


#define RST_PIN         9
#define SS_PIN          10

MFRC522 mfrc522(SS_PIN, RST_PIN);

MFRC522::StatusCode status;
MFRC522::MIFARE_Key key;

byte secretKey[64]; 


void setup() {
  Serial.begin(9600);           // Initialize serial communications with the PC
  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
  SPI.begin();        // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522 card             // Init MFRC522
  //ShowReaderDetails();            // Show details of PCD - MFRC522 Card Reader details
  //Serial.println(F("Scan PICC to see UID, type, and data blocks..."));
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
}

void loop() {
  //String stream = "1Hackathon2026SecretKeyForRFIDDemoSecureAccessControlSystem111111";
  String stream = "";
  if(Serial.available()){
    stream = Serial.readString();
  }
  
  byte streamArray[stream.length()];
  if(stream.length() != 0){
    stream.getBytes(streamArray, stream.length());
    streamArray[stream.length() - 1] = stream[stream.length() - 1];
    byte MSG_TYPE = streamArray[0];
    
    if(MSG_TYPE == 0x30){
      if ( ! mfrc522.PICC_IsNewCardPresent() || ! mfrc522.PICC_ReadCardSerial() ) {
        delay(50);
        return;
      }

      //STORE SECRET KEY IN SECTOR 1 BLOCK 0, 1, 2 AND SECTOR 2 BLOCK 0
      subArray(streamArray, secretKey, 1, 65);
      //dump_byte_array(secretKey, 64);
      byte sub1[16], sub2[16], sub3[16], sub4[16];

      subArray(secretKey, sub1, 0, 16);
      subArray(secretKey, sub2, 16, 32);
      subArray(secretKey, sub3, 32, 48);
      subArray(secretKey, sub4, 48, 64);

        
      if (writeDataBlock(1, 0, sub1) && writeDataBlock(1, 1, sub2) && writeDataBlock(1, 2, sub3) && writeDataBlock(2, 0, sub4)) {
        EEPROM.write(0, 0);
        Serial.println(0x00);
      } else {
        Serial.println(0x01);
      }
  
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();

    } else if(MSG_TYPE == 0x31){
        if ( ! mfrc522.PICC_IsNewCardPresent() || ! mfrc522.PICC_ReadCardSerial() ) {
          delay(50);
          return;
        }
        
        byte sub1[16], sub2[16], sub3[16], sub4[16];

        if (readDataBlock(1, 0, sub1) && readDataBlock(1, 1, sub2) && readDataBlock(1, 2, sub3) & readDataBlock(2, 0, sub4)) {
          memcpy(secretKey, sub1, 16);
          memcpy(secretKey + 16, sub2, 16);
          memcpy(secretKey + 32, sub3, 16);
          memcpy(secretKey + 48, sub4, 16);
          
          byte out[32]; 
          int count = EEPROM.read(0);
          custom_jwt_hmac_sha256(secretKey,
                              64,
                              (byte*) &count,
                              sizeof(count),
                              out,
                              32);
          EEPROM.update(0, count + 1);
          Serial.print(0x00);
          dump_byte_array(out, 32);
        }  else {
            Serial.print(0x01);
        }

        mfrc522.PICC_HaltA();
        mfrc522.PCD_StopCrypto1();

    } else {
      Serial.println("Invalid Message Type!");  
    }
  }


  // Look for new cards, and select one if present
  
  //printCardUID();

    
    // 


    

    // byte data[16] = {0}; 
    // int length = sizeof(data) / sizeof(data[0]);
    // byte sector = 2;
    // byte blockOff = 1;
    // byte buffer[16];
    
    // if(readDataBlock(sector, blockOff, buffer)){
    //   Serial.print(F("Data in block ")); Serial.print(2 * 4 + 1); Serial.println(F(":"));
    //   dump_byte_array(buffer, 16); Serial.println();
    // }

    // if (writeDataBlock(sector, blockOff, data, length)) {
    //   Serial.println("Write successful!");
    // } else {
    //   Serial.println("Write failed!");
    // }

}

bool readDataBlock(byte sector, byte blockOffset, byte *outputBuffer){
  // checks to ensure that we dont corrupt rfid tag
  if(sector == 0 && blockOffset == 0){
    Serial.println("Manufacturer Block, Do not access!");
    return false;
  }

  if (sector > 15) {
    Serial.println("Invalid sector!");
    return false;
  }

  if (blockOffset >= 3) {
    Serial.println("Invalid block offset!");
    return false;
  } //reject blockoffsets of 3 (trailer block)
  
  byte buffer[18];
  byte size = sizeof(buffer);

  byte trailerBlock = sector * 4 + 3;
  byte blockAddy = sector * 4 + blockOffset;
  //Authenticate and give key A (factory key is 0xFFFFFF in this case)
  status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
      Serial.print(F("PCD_Authenticate() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return false;
  }

  //Read data in rfid memory
  status = mfrc522.MIFARE_Read(blockAddy, buffer, &size);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Read failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }

  for (int i = 0; i < 16; i++) {
    outputBuffer[i] = buffer[i];
  }

  return true;
}

//DATA MUST BE a 16 BYTE ARRAY
bool writeDataBlock(byte sector, byte blockOffset, byte *data){
  // checks to ensure that we dont corrupt rfid tag
  if(sector == 0 && blockOffset == 0){
    Serial.println("Manufacturer Block, Do not access!");
    return false;
  }

  if (sector > 15) {
    Serial.println("Invalid sector!");
    return false;
  }

  if (blockOffset >= 3) {
    Serial.println("Invalid block offset!");
    return false;
  } //reject blockoffsets of 3 (trailer block)

  byte trailerBlock = sector * 4 + 3;
  byte blockAddy = sector * 4 + blockOffset;

  status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
      Serial.print(F("PCD_Authenticate() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return false;
  }

  status = mfrc522.MIFARE_Write(blockAddy, data, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Write failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }

  return true;
}

void dump_byte_array(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);
    }
}

bool subArray(byte* source, byte* dest, int start, int length) {
  for (int i = 0; i < length; i++) {
    dest[i] = source[start + i];
  }
}

void printCardUID(){
  Serial.print(F("Card UID:"));
  dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
  Serial.println();
}
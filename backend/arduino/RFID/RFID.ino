#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         9
#define SS_PIN          10

MFRC522 mfrc522(SS_PIN, RST_PIN);

MFRC522::MIFARE_Key key; 

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
  // Look for new cards, and select one if present
  if ( ! mfrc522.PICC_IsNewCardPresent() || ! mfrc522.PICC_ReadCardSerial() ) {
    delay(50);
    return;
  }
  
  //Now a card is selected. The UID and SAK is in mfrc522.uid.
    Serial.print(F("Card UID:"));
    dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
    Serial.println();

    
    byte data[16] = {0}; 
    int length = sizeof(data) / sizeof(data[0]);
    byte sector = 2;
    byte blockOff = 1;
    byte buffer[16];


    //STORE SECRET KEY IN SECTOR 1 BLOCK 0, 1, 2 AND SECTOR 2 BLOCK 0
    
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
  // adding checks to ensure that we dont corrupt rfid tag
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

  MFRC522::StatusCode status;

  status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
      Serial.print(F("PCD_Authenticate() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return false;
  }

  status = mfrc522.MIFARE_Read(blockAddy, buffer, &size);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Read failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }

  for (int i = 0; i < 16; i++) {
    outputBuffer[i] = buffer[i];
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  return true;
}

bool writeDataBlock(byte sector, byte blockOffset, byte *data, int length){
  // adding checks to ensure that we dont corrupt rfid tag

  if (length != 16) {
    Serial.print("Write size is not 16 bytes!");
  }

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

  MFRC522::StatusCode status;

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

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  return true;
}

void dump_byte_array(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);
    }
}
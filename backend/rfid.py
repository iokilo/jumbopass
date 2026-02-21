"""
RFID Reader Module

This module provides functionality to connect to and read RFID tags from an Arduino-based
RFID reader over USB serial connection. It handles device detection, connection management,
and tag scanning with timeout support.

Configuration:
    BAUD_RATE: Serial communication speed (9600)
    BOARD_MANUFACTURER: Expected Arduino manufacturer name
    BOARD_SERIAL: Specific board serial number for security verification
"""
import serial
import serial.tools.list_ports
import time

# --- CONFIG ---

BAUD_RATE = 9600
BOARD_MANUFACTURER = "Arduino"
BOARD_SERIAL = "5573532373535151D062"

def print_ports():
    """
    Print detailed information about all available serial ports.
    
    Useful for debugging and identifying connected devices.
    """
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(vars(p))
        print()
    return

def get_reader_port():
    """
    Locate and return the serial port for the authorized RFID reader.
    
    Searches all available serial ports for a device matching both the configured
    manufacturer name and serial number to ensure only authorized hardware is used.
    
    Returns:
        str: Device path of the RFID reader (e.g., '/dev/cu.usbmodem1234')
    
    Raises:
        RuntimeError: If no serial ports are found or if no matching device is found
    """
    ports = list(serial.tools.list_ports.comports())

    if not ports:
        raise RuntimeError("RFID reader not found. Is it plugged in?")
    
    # Find port matching manufacturer
    serial_match = [
    p for p in ports
    if (p.manufacturer or "") and BOARD_MANUFACTURER in (p.manufacturer or "")
    and (p.serial_number or "") and BOARD_SERIAL in (p.serial_number or "")
    ]

    if not serial_match:
        raise RuntimeError("Unrecognized scanner! Only use official hardware!")
    
    print(serial_match[0].device)
    return serial_match[0].device


def connect_reader():
    """
    Open a serial connection to the RFID reader.
    
    Automatically detects the correct port and establishes communication
    at the configured baud rate.
    
    Returns:
        serial.Serial: Active serial connection to the RFID reader, or None if connection fails
    """
    SERIAL_PORT = get_reader_port()

    try:
        reader = serial.Serial(
            port = SERIAL_PORT,
            baudrate= BAUD_RATE,
            timeout=1
        )
    except Exception as e:
        print(f"Reader init failed: {e}")
        return None
    return reader

def start_scan(timeout_seconds = 30):
    """
    Perform a complete RFID scan cycle: read current tag, then read newly written tag.
    
    This method coordinates a two-step authentication process:
    1. Reads the current RFID tag UID (for verification against database)
    2. Reads the new RFID tag UID (to be saved to database after verification)
    
    Args:
        timeout_seconds (int): Maximum time to wait for each scan phase (default: 30)
    
    Returns:
        list: A two-element list [current_uid, new_uid] where:
              - current_uid is the existing tag UID from the database
              - new_uid is the freshly written tag UID to be stored
              Either element may be None if that particular scan failed.
    """
    reader = connect_reader()
    if reader is None:
        return [None, None]
    
    try:
        # Phase 1: Read current tag
        current_uid = await_scan(timeout_seconds, reader)
        return current_uid
        
        # Phase 2: Read newly written tag
        # NEW UID NOT IMPLEMENTED RN
        #new_uid = await_new(timeout_seconds, reader)
        
        #print([current_uid, new_uid])
        #return [current_uid, new_uid]
    
    except KeyboardInterrupt:
        print("Scan cycle terminated.")
        return None
        #return [None, None]
    finally:
        reader.close()


def await_new(timeout_seconds = 30, reader = None):
    """
    Wait for a newly written RFID code from the board.
    
    After the Arduino writes a new UID to a tag, this function waits for
    the board to transmit that new code back over serial. Returns the raw
    string as formatted by the Arduino.
    
    Args:
        timeout_seconds (int): Maximum time to wait for new code (default: 30)
        reader (serial.Serial): Existing serial connection, or None to create new one
    
    Returns:
        str: The newly written UID (raw format from Arduino), or None if timeout/error occurred
    """
    if reader is None:
        reader = connect_reader()
        if reader is None:
            return None
    
    try:
        start = time.time()
        while time.time() - start < timeout_seconds:
            line = reader.readline()
            if line:
                try:
                    decoded = line.decode('utf-8').strip()
                    if decoded:  # Return any non-empty line
                        print(f"New tag received: {decoded}")
                        return decoded
                except UnicodeDecodeError:
                    continue
            time.sleep(0.1)
        return None  # Timeout
    except KeyboardInterrupt:
        print("New tag read terminated.")
        return None
    except Exception as e:
        print(f"New tag read error: {e}")
        return None


def await_scan(timeout_seconds = 30, reader = None):
    """
    Wait for an RFID tag to be scanned within a specified timeout period.
    
    Continuously polls the RFID reader for tag data. When a valid tag is detected,
    its UID is extracted and returned.
    
    Args:
        timeout_seconds (int): Maximum time to wait for a scan in seconds (default: 30)
        reader (serial.Serial): Existing serial connection, or None to create new one
    
    Returns:
        str: The UID of the scanned RFID tag (e.g., "67 AE 7B B4"), or None if
             no tag was scanned within the timeout period or if an error occurred
    """
    if reader is None:
        reader = connect_reader()
        if reader is None:
            return None

    try:
        start = time.time()
        while time.time() - start < timeout_seconds:
            tag_uid = read_tag(reader)
            if tag_uid:
                print(f"Scanned: {tag_uid}")
                return tag_uid
            time.sleep(0.1) #delay
        return None # Function timed out.
    except KeyboardInterrupt:
        print("scanning terminated.")
        return None


def read_tag(reader):
    """
    Read a single line from the RFID reader and extract the tag UID if present.
    
    Parses the serial data for lines containing "Card UID:" and extracts the
    hexadecimal UID value. Handles various error conditions gracefully.
    
    Args:
        reader (serial.Serial): Active serial connection to the RFID reader
    
    Returns:
        str: The extracted UID (e.g., "67 AE 7B B4") if a valid tag line is read,
             or None if no valid data is available or an error occurs
    """
    try:
        line = reader.readline()
        if line:
            decoded = line.decode('utf-8').strip()
            
            # Only return lines that contain "Card UID:"
            if decoded and decoded.startswith('Card UID:'):
                # Extract just the UID part (e.g., "67 AE 7B B4")
                uid = decoded.replace('Card UID:', '').strip()
                return uid
        return None
    except UnicodeDecodeError:
        return None
    except KeyboardInterrupt:
        print("read terminated.")
        return None
    except Exception as e:
        print(f"line read error: {e}")
        return None

start_scan()
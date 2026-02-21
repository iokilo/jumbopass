import serial
import serial.tools.list_ports
import time

# --- CONFIG ---

BAUD_RATE = 9600

def print_ports():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p)
    return

print_ports()

def get_reader_port():
    ports = list(serial.tools.list_ports.grep("READER_UID"))
    if not ports:
        raise RuntimeError("RFID reader not found. Is it plugged in?")

    return ports[0].device

def connect_reader():

    """
    Opens a connnection to the RFID reader
    serial.Serial()
    """

    SERIAL_PORT = get_reader_port()

    try:
        reader = serial.Serial(
            port = SERIAL_PORT,
            baudrate= BAUD_RATE,
            timeout=1
        )
    except:
        print("Reader init failed.")
    return reader

def await_scan(timeout_seconds = 30):

    reader = connect_reader()

    try:
        start = time.time()
        while time.time() - start < timeout_seconds:
            tag_uid = read_tag(reader)
            if tag_uid:
                return tag_uid
            time.sleep(0.1) #delay
        return None # Function timed out.
    
    finally:
        reader.close()

def read_tag(reader):

    ram = ""
    try:
        ram = reader.readline()
        print(ram, end="\n")
    except KeyboardInterrupt:
        print("read terminated.")
    except:
        print("line read error", end="\n")
    return ram

def write_tag():
    return




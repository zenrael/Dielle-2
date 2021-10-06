import socket

from enum import Enum

UDP_IP = "127.0.0.1"
UDP_PORT = 29373

class Telemetry(Enum):
    # Defined in the order of appearence in packet.
    TELEMETRY_ID = 1409286401
    RPM = 0x00
    MP = 0x01
    ALT = 0x0a
    P2 = 0x02
    P3 = 0x03
    GEAR = 0x04
    GEAR_ROT = 0x05
    SPD = 0x06
    P7 = 0x07
    P8 = 0x08
    P9 = 0x09
    FLAPS = 0x0b
    P12 = 0x0c

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024) #buffer size

        offset = 4

        # Packet ID
        packet_id = int.from_bytes(data[0:offset], byteorder='little')
        print(packet_id)

        if packet_id == 1409286401:
            # Packet Size (Noting that offset is still 4)
            packet_size = int.from_bytes(data[offset:offset+2], byteorder='little')
            print(packet_size)
            offset += 2

            # Server Tick
            server_tick = int.from_bytes(data[offset:offset+4], byteorder='little')
            print(server_tick)
            offset += 4

            # Number of Parameters
            param_count = int(data[offset])
            offset += 1  

            # And away we go!
            for p in range(param_count):
                param_id = int(data[offset])
                offset += 2
                param_count = int(data[offset])
                param_data = []
                for q in range(0, param_count):
                    param_data.append(int.from_bytes(data[offset:offset+4], byteorder='little'))
                    offset += 4
                offset += 1

            
    

if __name__ == "__main__":
    main()

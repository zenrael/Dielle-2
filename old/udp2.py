import socket, struct, sys

UDP_IP = '127.0.0.1'
UDP_PORT = 29373

class Telemetry():
    def __init__(self):
        self.pids = {
            0 : 'engine_rpm',
            1 : 'engine_mp',
            2 : 'param_two',
            3 : 'param_three',
            4 : 'gear_deploy',
            5 : 'gear_rot',
            6 : 'speed',
            7 : 'param_seven',
            8 : 'param_eight',
            9 : 'param_nine',
            10 : 'altitude',
            11 : 'flaps',
            12 : 'param_c',
        }
        self.sim_tick = 0
        self.engine_rpm = []
        self.engine_mp = []
        self.altitude = []
        self.param_two = []
        self.param_three = []
        self.gear_deploy = []
        self.gear_rot = []
        self.speed = []
        self.param_seven = []
        self.param_eight = []
        self.param_nine = []
        self.flaps = []
        self.param_c = []

    def update(self, param_id, values):
        #locals()[self.pids[param_id]] = values # Check this - we want locals relative to instance if possible
        vars(self)[self.pids[param_id]] = values

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    telemetry = Telemetry()

    while True:
        data, addr = sock.recvfrom(1024) #buffer size
        # First pull apart the packet 'header'...
        packet_id, packet_size, telemetry.sim_tick, param_count = struct.unpack('<IhIB', data[0:11])
        if packet_id != 1409286401:
            continue
        # And away we go!..
        offset = 11
        for param in range(0, param_count):
            values = []
            param_id, val_count = struct.unpack('<BxB', data[offset:offset+3])
            offset += 3
            for x in range(val_count):
                values.append(struct.unpack('<f', data[offset:offset+4]))
                offset += 4  
            telemetry.update(param_id, values)
        print(telemetry.param_seven)

if __name__ == '__main__':
    main()
    sys.exit(app.exec_())
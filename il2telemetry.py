import asyncio, math, socket, struct, sys, time

_parameter_ids = {
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
    12 : 'param_c'
}

class _Pressure(list):
    def __init__(self, *args):
        list.__init__(self, *args)
    def psi(self):
        return [round(pa/6894.75729) for pa in self]
    def boost_psi(self):
        return [round((pa - 101325)/6894.75729, 1) for pa in self]

class _Altitude():
    def __init__(self, value):
        self.alt = value
    def __repr__(self):
        return repr(self.alt)
    def __int__(self):
        return int(self.alt)
    def __float__(self):
        return float(self.alt)
    def __str__(self):
        return str(self.alt)
    def feet(self):
        return int(self.alt*3.28084)

class _Speed:
    def __init__(self, value):
        self.spd = float(value)
    def __repr__(self):
        return repr(self.spd)
    def __mul__(self, value):
        return self.spd.__mul__(value)
    def __rmul__(self, value):
        return self.spd.__rmul__(value)
    def fpm(self):
        return 196.85*self.spd
    def mph(self):
        return int(self.spd*2.237)
    def kph(self):
        return self.spd*3.6
    def knots(self):
        return self.spd*1.94384

class Telemetry:
    def __init__(self):
        self.sim_tick = 50                          # 1/50th second, default to 50 so conversion doesn't break when started. Less costly than a conditional.
        self.engine_rpm = [0]
        self.engine_mp = _Pressure([0])
        self.__dict__['altitude'] = _Altitude(0)
        self.param_two = [0]
        self.param_three = [0]
        self.gear_deploy = [0]
        self.gear_rot = [0]
        self.__dict__['speed'] = _Speed(0)
        self.param_seven = [0]
        self.param_eight = [0,0,0]
        self.param_nine = [0]
        self.flaps = [0]
        self.param_c = [0]
        self.direction_vector = [0,0,0]
        self.spin_vector = [0,0,0]
        self.accel_vector = [0,0,0]

    def __setattr__(self, name, value):
        if name == 'altitude':
            self.__dict__[name].alt = value
        elif name == 'speed':
            self.__dict__[name].spd = value
        elif name == 'engine_mp':
            self.__dict__[name] = _Pressure(value)
        else:
            self.__dict__[name] = value
        
    def start(self, address, port):
        asyncio.create_task(self._connect(address, port))

    def finish(self):
        self._transport.close()

    def elapsed_time(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.sim_tick/50))

    def heading(self):
        if(0 < self.direction_vector[0]):
            return round(360-math.degrees(self.direction_vector[0]))
        else:
            return round(-math.degrees(self.direction_vector[0]))

    def vs_mps(self):
        return self.speed*math.cos(math.degrees(self.direction_vector[1]))

    def vs_fpm(self):
        return round(self.speed.fpm() * math.cos(-math.degrees(self.direction_vector[1])))

    def slip(self):
        return self.direction_vector
        
        #
        # return max(-40, min(40, round((10000/350) * self.param_eight[2])))

        # FSD on the a-20b seems to be about +/- 40

    class IL2Protocol:
        def __init__(self, outer):
            self.outer = outer
        def connection_made(self, transport):
            print("Connected")
            self.transport = transport
        def datagram_received(self, data, addr):
            packet_id = data[0:4].hex()
            if packet_id == '01010054':
                _, packet_size, self.outer.sim_tick, param_count = struct.unpack('<IhIB', data[0:11])
                self.outer._parse_telemetry_data(data, param_count)
            elif packet_id == '00014c49':
                self.outer._parse_motion_data(data)
            else:
               pass
        def connection_lost(self, exc):
            print("Connection closed")

    def _parse_telemetry_data(self, data, param_count):
    # I don't like this 'offset' nonsense, there has to be a more elegant way
        offset = 11
        for _ in range(param_count):
            param_id, val_count = struct.unpack('<BxB', data[offset:offset+3])
            offset += 3
            if param_id == 10:
                self.altitude = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
            elif param_id == 6:
                self.speed = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
            else:
                vars(self)[_parameter_ids[param_id]].clear()
                for _ in range(val_count):
                    vars(self)[_parameter_ids[param_id]].append(struct.unpack('<f', data[offset:offset+4])[0])
                    offset += 4

    def _parse_motion_data(self, data):
        self.direction_vector = [val for val in struct.unpack('<fff', data[8:20])]
        self.spin_vector = [val for val in struct.unpack('<fff', data[20:32])]
        self.accel_vector = [val for val in struct.unpack('<fff', data[32:44])]

    async def _connect(self, address, port):
        self._loop = asyncio.get_running_loop()
        self._transport, protocol = await self._loop.create_datagram_endpoint(
            lambda: self.IL2Protocol(self),
            local_addr=(address, port))


async def main():
    il2 = Telemetry()
    il2.start('127.0.0.1', 29373)
    for _ in range(100):
        print(il2.elapsed_time())
        await asyncio.sleep(1)
    il2.finish()

if __name__ == '__main__':
    asyncio.run(main())

    
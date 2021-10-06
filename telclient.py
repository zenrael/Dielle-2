import asyncio, il2telemetry, serial, struct, random

il2 = il2telemetry.Telemetry()

async def main():
    ser = serial.Serial('COM7', 115200)
    il2.start('127.0.0.1', 29373)
    while True:
        packet = bytearray()
        packet.append(0x3A)
        packet.extend('A'.encode())
        packet.extend(str(il2.altitude.feet()).encode('ascii'))
        packet.extend('S'.encode())
        packet.extend(str(il2.speed.mph()).encode('ascii'))
        packet.extend('R'.encode())
        packet.extend(str(round(il2.engine_rpm[0])).encode('ascii'))
        packet.extend('P'.encode())
        packet.extend(str(il2.engine_mp.boost_psi()[0]).encode('ascii'))
        packet.extend('H'.encode())
        packet.extend(str(il2.heading()).encode('ascii'))
        packet.extend('B'.encode())
        packet.extend(str(il2.slip()).encode('ascii'))
        packet.append(0x3A)
        ser.write(packet)
        await asyncio.sleep(0.1)

async def testdata(il2):
    while True:
        for i in range(100):
            il2.altitude = str(i*100)
            await asyncio.sleep(5)    

if __name__ == '__main__':
    asyncio.run(main())
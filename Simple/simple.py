
from bluepy.btle import Scanner, DefaultDelegate, Peripheral

# perf = Peripheral("00:07:80:BD:23:BE")
perf = Peripheral("00:07:80:BD:1C:3A")
print("Firmware: ", perf.readCharacteristic(0x000a))
print("Hardware: ", perf.readCharacteristic(0x000c))

val = perf.writeCharacteristic(0x001a,chr(20),withResponse=False)
print("test: ", perf.readCharacteristic(0x001a), val)

#perf.writeCharacteristic(0x001a,chr(1) + chr(0) + chr(1) + chr(100) + chr(1) + chr(0) + chr(200)+ chr(2) + chr(0) + chr(200)+ chr(3) + chr(0) + chr(200))
# perf.writeCharacteristic(0x001a,chr(0) + chr(0) + chr(1) + chr(2) + chr(3))


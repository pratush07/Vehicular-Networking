# Vehicular-Networking
Vehicular networking in a P2P fashion

1. python3 base_station.py : to run the base station
2. python3 device.py python3 Generate_vehicles.py --top-port 31000 --car-port 31005 --devices 4:  to run a network of 4 devices topology listening ports starting from 31000 to 31003 and car update ports starting from 31005  to 31008.


For testing with two vehicles
python base_station.py

vehicle("0",'localhost',30201,'localhost',31000,31010,1000,50)


vehicle("1",'localhost',30201,'localhost',31001,31011,700,60)
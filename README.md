# Vehicular-Networking
Vehicular networking in a P2P fashion

# On pi 1
1. python3 base_station.py --host 10.35.70.41 --port 30201: to run the base station
#2. python3 Generate_vehicles.py --top-port 31000 --car-port 31005 --devices 4:  to run a network of 4 devices topology listening ports starting from 31000 to 31003 and car update ports starting from 31005  to 31008. (Please remove peer discovery, peer_messages and stability logs when you create a network for the 1st time)

#On pi 2
#Case - 1
3. python3 platoon_simulation.py --base-host 10.35.70.41 --base-port 30201 --car-host 10.35.70.42 --simulation 1: 2 cars form a platoon first. 3rd car catches up from behind to join the platoon

#Case - 2
4. python3 platoon_simulation.py --base-host 10.35.70.41 --base-port 30201 --car-host 10.35.70.42 --simulation 2: two cars forming platoon first.. platoon catches up with a car in the front and they form a platoon

#Case - 3
5. python3 platoon_simulation.py --base-host 10.35.70.41 --base-port 30201 --car-host 10.35.70.42 --simulation 3: two cars forming platoon first.. platoon catches up with a car in the front and they form a platoon. platoon catches with 4th car ahead.

For the simulations see the stability logs in stability_logs folder.
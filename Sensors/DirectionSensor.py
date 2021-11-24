from Sensors.sensor import Sensor

class Positionsensor(Sensor):
    def __init__(self, header):
        Sensor.__init__(self, header)
        
    def Sensor_data():
        record_data = {'id': self.header, 'Direction': "East"}

        data = json.dumps(record_data)
        print("Direction Generated")
        print("Data:", data)
        return data
        
    def send_data(self, PORT1, PORT2):
    try:
        self.data = self.sensor_data()
        # send data
        sdr.send(self.data, PORT1)
    except:
        print("Server not available")
        self.data = self.sensor_data()
        # send data
        sdr.send(self.data, PORT2)
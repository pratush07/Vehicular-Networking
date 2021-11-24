import random
import json

class Fuelsensor:
    def __init__(self, header):
        self.header = header
        
    def Sensor_data(self):
        record_data = {'id': self.header, 'X': random.uniform(0, 65)}

        data = json.dumps(record_data)
        print("Fuel Generated")
        print("Data:", data)
        return data
        
    def send_data(self):
        return  self.Sensor_data()


import random
import json

class Lightsensor:
    
    data = {}
    
    def __init__(self, header):
        self.header = header
        self.generate_data()
        
    def generate_data(self):
        record_data = {'id': self.header, 'Beam Intensity': random.uniform(0, 4500)}

        self.data = json.dumps(record_data)
        #print("Fuel Generated")
        #print("Data:", data)
        #return data
        
    def get_data(self):
        return  self.data
        
    def set_data(self, val):
        self.data['Beam Intensity'] = val
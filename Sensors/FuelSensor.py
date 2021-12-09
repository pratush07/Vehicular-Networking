#Sole contribution of Zoya Yasin
import random
import json

class Fuelsensor:
    
    data = {}
    
    def __init__(self, header):
        self.header = header
        self.generate_data()
        
    def generate_data(self):
        record_data = {'id': self.header, 'X': random.uniform(0, 65)}

        self.data = record_data
        
    def get_data(self):
        return  self.data
        
    def set_data(self, val):
        self.data['X'] = val


import random
import json


class Speedsensor:

    data = {}

    def __init__(self, header):
        self.header = header
        self.generate_data()

    def generate_data(self):
        record_data = {'id': self.header, 'speed': random.uniform(30, 70)}
        self.data = record_data

    def get_data(self):
        return self.data

    def get_speed(self):
        return self.data['speed']

    def set_data(self, val):
        self.data['speed'] = val

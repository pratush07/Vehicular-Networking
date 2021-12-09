#Sole contribution of Zoya Yasin
import json


class Powerlevelindicator:

    data = {}

    def __init__(self, header):
        self.header = header
        self.generate_data()

    def generate_data(self):
        record_data = {'id': self.header, 'PowerLevel': 100}
        self.data = record_data

    def get_data(self):
        return self.data

    def get_power_level(self):
        return self.data['PowerLevel']

    def set_data(self, val):
        self.data['PowerLevel'] = val

#Sole contribution of Zoya Yasin
import json
import random


class Lanewidthsensor:

    data = {}

    def __init__(self, header):
        self.header = header
        self.generate_data()

    def generate_data(self):
        record_data = {'id': self.header, 'LaneWidth': random.uniform(3, 5)}
        self.data = record_data

    def get_data(self):
        return self.data

    def get_lane_width(self):
        return self.data['LaneWidth']

    def set_data(self, val):
        self.data['LaneWidth'] = val

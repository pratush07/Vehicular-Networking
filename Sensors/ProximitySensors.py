#Sole contribution of Zoya Yasin
import json
import random


class Proximitysensor:

    data = {}

    def __init__(self, header):
        self.header = header
        self.generate_data()

    def generate_data(self):
        record_data = {'id': self.header,
                       'ObstacleDetected': False}
        self.data = record_data

    def get_data(self):
        return self.data

    def get_obstacle_distance(self):
        return self.data['ObstacleDetected']

    def set_data(self, val):
        self.data['ObstacleDetected'] = val

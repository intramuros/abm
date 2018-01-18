
"""
Created on Fri Jan 12 13:56:17 2018
---
Uses the Forest Fire model: https://github.com/projectmesa/mesa/blob/master/examples/forest_fire/Forest%20Fire%20Model.ipynb
"""
from mesa import Model
from mesa.time import RandomActivation, SimultaneousActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from .agent import Patch


import random
import numpy as np

class EcoModel(Model):
    """..."""
    def __init__(self,  height, width, b, m):
        
        #Initialize model variables
        self.height = height
        self.width = width
        self.num_agents = self.width*self.height
        self.schedule = SimultaneousActivation(self)
        self.delta = 0
        self.c = 0.3
        self.r = 0
        self.d = 0.2
        self.f = 0.8
        self.m = m
        self.b = b
        self.emp_dens = 0.25
        self.deg_dens = 0.25
        self.rho_veg = 1 - self.emp_dens - self.deg_dens
        self.count_veg = int(self.rho_veg*self.num_agents)
        
        # Set up model objects
        self.grid = Grid(self.height, self.width, torus=True) # the first paper mentions periodic boundary condition
        self.datacollector = DataCollector({"Empty": lambda m: self.count_type(m, "Empty"),
                                            "Vegetated": lambda m: self.count_type(m, "Vegetated"),
                                            "Degraded": lambda m: self.count_type(m, "Degraded"),
                                            "qplusplus": lambda m: self.calculate_local_densities(m)[0],
                                            "qplusminus": lambda m: self.calculate_local_densities(m)[1],
}
                                           )
        # Define patches
        for x in range(self.width):
            for y in range(self.height):
                rand_num = random.random()
                if rand_num < self.deg_dens:
                    new_patch = Patch(self, (x, y), "Degraded")
                    self.grid[y][x] = new_patch
                    self.schedule.add(new_patch)
                elif rand_num < self.emp_dens+self.deg_dens:
                    new_patch = Patch(self, (x, y), "Empty")
                    self.grid[y][x] = new_patch
                    self.schedule.add(new_patch)
                else:
                    new_patch = Patch(self, (x, y), "Vegetated")  # Create a patch
                    self.grid[y][x] = new_patch
                    self.schedule.add(new_patch)

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        # calculate rho?
        self.count_veg = self.count_type(self, "Vegetated")
        self.rho_veg = self.count_veg / self.num_agents
        self.schedule.step()
        self.datacollector.collect(self)
        
        print("Vegetated: " + str(self.count_veg))
        print("Empty: " + str(self.count_type(self, "Empty")))
        print("Degraded: " + str(self.count_type(self, "Degraded")))

    @staticmethod
    def count_type(model, patch_condition):
        '''Helper method to count given condition in a given model.'''
        count = 0
        for patch in model.schedule.agents:
            if patch.condition == patch_condition:
                count += 1
        return count

    @staticmethod
    def calculate_local_densities(model):
        '''Helper method to count vegetated neighbours.'''
        qplusplus = []
        qplusminus = []

        for patch in model.schedule.agents:
            neighbors = patch.model.grid.get_neighbors(patch.pos, moore=False)

            num_veg = 0
            for neighbor in neighbors:
                if neighbor.condition == "Vegetated":
                    num_veg += 1
            q = num_veg / len(neighbors)

            if patch.condition == "Empty":
                qplusminus.append(q)
            elif patch.condition == "Vegetated":
                qplusplus.append(q)

        return(np.mean(qplusplus), np.mean(qplusminus))



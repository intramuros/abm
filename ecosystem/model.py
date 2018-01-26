
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
import json


class EcoModel(Model):
    """..."""
    def __init__(self, b, m, config_file):
        # open json file with parameters
        params = json.load(open(config_file))

        # Initialize model variables
        self.height = params["height"]
        self.width = params["width"]
        self.num_agents = self.width*self.height
        self.schedule = SimultaneousActivation(self)
        self.delta = params["delta"]
        self.c = params["c"]
        self.r = params["r"]
        self.d = params["d"]
        self.f = params["f"]
        self.m = m
        self.b_base = b
        self.b = b
        self.emp_dens = params["emp_dens"]
        self.deg_dens = params["deg_dens"]
        self.rho_veg = 1 - self.emp_dens - self.deg_dens

        # Set up flowlength parameters
        self.use_fl = params["Use Flowlength"]
        if self.use_fl:
            self.patch_size = params["Patch size"]  # patch side size in meters
            self.L = self.height
            self.theta = np.radians(params["theta"])
            self.d_s = self.patch_size / np.cos(self.theta)
            self.max_fl = params["Maximum Flowlength"]
            self.alpha_feedback = params["alpha_feedback"]
            self.alpha_bare = params["alpha_bare"]
            q = self.alpha_bare * (1 - self.rho_veg)
            self.fl = (1 - self.rho_veg) * ((1 - q) * self.L - q * (1 - q**self.L)) * self.d_s / ((1-q)**2 * self.L)
            self.b = self.b_base*(1 - self.alpha_feedback * self.fl/self.max_fl)
            
            # variables for infrequent rainfall
            self.infr_rain = params["infr_rain"]
            if self.infr_rain == True:
            	self.rain_period = params["rain_period"]
            	self.no_rain_period = params["no_rain_period"]
            	self.water_on = 0
            	self.water_off = self.no_rain_period
   
        self.count_veg = int(self.rho_veg*self.num_agents)
        
        # Set up model objects
        self.grid = Grid(self.height, self.width, torus=params["Torus"]) # the first paper mentions periodic boundary condition
        self.datacollector = DataCollector({"Empty": lambda m: self.count_type(m, "Empty"),
                                            "Vegetated": lambda m: self.count_type(m, "Vegetated"),
                                            "Degraded": lambda m: self.count_type(m, "Degraded"),
                                            "qplusplus": lambda m: self.calculate_local_densities(m)[0],
                                            "qminusplus": lambda m: self.calculate_local_densities(m)[1],
                                            "qminusminus": lambda m: self.calculate_local_densities(m)[2],
                                            "flowlength": lambda m: self.fl,
                                            "b": lambda m: self.b
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
        # Set values of q to the defined patches
        for patch in self.schedule.agents:
            patch.getQ()
        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.datacollector.collect(self)
        self.count_veg = self.count_type(self, "Vegetated")
        self.rho_veg = self.count_veg / self.num_agents
        
        # rain 
        if self.use_fl:
            rho_minusminus = float(self.datacollector.get_model_vars_dataframe().qminusminus.tail(1)) * (1 - self.rho_veg)
            self.alpha_bare = rho_minusminus / (1 - self.rho_veg)**2
            q_flowlength = self.alpha_bare * (1 - self.rho_veg)
            self.fl = (1 - self.rho_veg) * ((1 - q_flowlength) * self.L - q_flowlength * (1 - q_flowlength ** self.L))\
                      * self.d_s / ((1 - q_flowlength) ** 2 * self.L)
            self.b = self.b_base * (1 - self.alpha_feedback * self.fl / self.max_fl)
            
            # infrequent rain
            if self.infr_rain == True and self.water_on < self.rain_period:
            
                # keep track of water steps
	        self.water_on += 1
		    
	        # if maximum number of rain steps is reached, switch to no rain
	        if self.water_on == self.rain_period - 1:
	            self.water_off = 0
        
	    # no rain
	    elif self.infr_rain == True and self.water_off < self.no_rain_period:
	        self.b = self.b_base
		self.water_off += 1
		    
		# if maximum number of no rain is reached, let it rain
		if self.water_off == self.no_rain_period:
		    self.water_on = 0
   
        self.schedule.step()
	
        #print("Vegetated: " + str(self.count_type(self, "Vegetated")))
        #print("Empty: " + str(self.count_type(self, "Empty")))
        #print("Degraded: " + str(self.count_type(self, "Degraded")))

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
        qminusplus = []
        qminusminus = []
        for patch in model.schedule.agents:
            if patch.condition == "Vegetated":
                qplusplus.append(patch.getQ())
                qminusplus.append(patch.getQminus())
            else:
                qminusminus.append(patch.getQnonveg())

        return (np.mean(qplusplus), np.mean(qminusplus), np.mean(qminusminus))







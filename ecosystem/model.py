
"""
Implementation of the model class for Dryland Dynamics Model.

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
    '''
    Represents the landscape in the dryland model as a two-dimensional square grid
    '''
    def __init__(self, b, m, config_file):
        '''
            Create a new grid.

            Args:

            b: plant establishment probability.
            m: mortality probability of a vegetated site
            config_file: a .json file with remaining parameters
        '''
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
        self.emp_dens = params["Empty sites density"]
        self.deg_dens = params["Degraded sites density"]
        self.rho_veg = 1 - self.emp_dens - self.deg_dens

        # Set up flowlength parameters
        self.use_fl = params["Use Flowlength"]
        if self.use_fl:
            self.patch_size = params["Patch size"]  # patch side size in meters
            self.L = self.height
            self.theta = np.radians(params["Theta"])
            self.d_s = self.patch_size / np.cos(self.theta)
            self.max_fl = self.d_s * (self.height + 1)/2
            self.alpha_feedback = params["alpha_feedback"]
            self.alpha_bare = 1
            q = self.alpha_bare * (1 - self.rho_veg)
            self.fl = (1 - self.rho_veg) * ((1 - q) * self.L - q * (1 - q**self.L)) * self.d_s / ((1-q)**2 * self.L)
            self.b = self.b_base*(1 - self.alpha_feedback * self.fl/self.max_fl)
            
            # variables for infrequent rainfall
            self.infr_rain = params["Use infrequent rain"]
            if self.infr_rain:
                self.rain_period = params["Rain period"]
                self.no_rain_period = params["No rain period"]
                self.is_raining = True
                self.water_on = 0
                self.water_off = self.no_rain_period
   
        self.count_veg = int(self.rho_veg*self.num_agents)

        # Set up the model and data collection
        self.grid = Grid(self.height, self.width, torus=params["Use Torus"])
        if self.fl:
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
        else:
            self.datacollector = DataCollector({"Empty": lambda m: self.count_type(m, "Empty"),
                                                "Vegetated": lambda m: self.count_type(m, "Vegetated"),
                                                "Degraded": lambda m: self.count_type(m, "Degraded"),
                                                "qplusplus": lambda m: self.calculate_local_densities(m)[0],
                                                "qminusplus": lambda m: self.calculate_local_densities(m)[1],
                                                "qminusminus": lambda m: self.calculate_local_densities(m)[2],
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

        self.datacollector.collect(self)
        self.running = True

    def step(self):
        '''
        Advance the model by one step.
        '''

        # Calculate vegetation density
        self.count_veg = self.count_type(self, "Vegetated")
        self.rho_veg = self.count_veg / self.num_agents
        
        # Calculate Flowlength index
        if self.use_fl:

            # calculate probability of having neighbouring non-vegetated sites
            rho_minusminus = float(self.datacollector.get_model_vars_dataframe().qminusminus.tail(1)) * (1 - self.rho_veg)
            self.alpha_bare = rho_minusminus / (1 - self.rho_veg)**2
            q_flowlength = self.alpha_bare * (1 - self.rho_veg)

            # calculate Flowlength index based on the connectivity of non-vegetated patches
            self.fl = (1 - self.rho_veg) * ((1 - q_flowlength) * self.L - q_flowlength * (1 - q_flowlength ** self.L))\
                      * self.d_s / ((1 - q_flowlength) ** 2 * self.L)

            # get the establishment probability as the function of Flowlength and connectivity strength
            self.b = self.b_base * (1 - self.alpha_feedback * self.fl / self.max_fl)

            # calculations involving infrequent rain
            if self.infr_rain:
                if self.is_raining:
                    if self.water_on < self.rain_period-1:
                        self.water_on += 1
                    else:
                        self.is_raining = False
                        self.water_off = 0
                        self.b = self.b_base
                else:
                    if self.water_off < self.no_rain_period-1:
                        self.water_off += 1
                        self.b = self.b_base
                    else:
                        self.is_raining = True
                        self.water_on = 0

        self.datacollector.collect(self)
        self.schedule.step()

    @staticmethod
    def count_type(model, patch_condition):
        '''
        Helper method to count patches with a given condition in a given model
        '''

        count = 0
        for patch in model.schedule.agents:
            if patch.condition == patch_condition:
                count += 1
        return count

    @staticmethod
    def calculate_local_densities(model):
        '''
        Helper method to calculate global averages for conditional probabilities
        for having vegetated or degraded neighbors given the vegetated state,
        and for having non-vegetated neighbors given the non-vegetated state.
        (non-vegetated = empty or degraded)
        '''

        qplusplus = []
        qminusplus = []
        qminusminus = []
        for patch in model.schedule.agents:
            if patch.condition == "Vegetated":
                qplusplus.append(patch.get_q())
                qminusplus.append(patch.get_q_minus())
            else:
                qminusminus.append(patch.get_q_nonveg())

        return (np.mean(qplusplus), np.mean(qminusplus), np.mean(qminusminus))







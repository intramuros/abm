#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 13:56:17 2018
---
Uses the Forest Fire model: https://github.com/projectmesa/mesa/blob/master/examples/forest_fire/Forest%20Fire%20Model.ipynb
"""
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner

import random
import numpy as np
import matplotlib.pyplot as plt

class EcoAgent(Agent):
    """..."""
    def __init__(self, model, pos, cond):
        super().__init__(pos, model) 
        self.pos = pos #gives position
        self.unique_id = pos #gives agents a unique ID based on position
        self.condition = cond
        self.model = model
        
    def step(self):
        #create a neighbor array
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False) #van Neumann neighborhood
        
        #calculate the amount of neighbors
        num_veg = 0
        for neighbor in neighbors:
            if neighbor.condition == "Vegetated":
                num_veg += 1
        q = num_veg/4 #MAYBE THIS SHOULD BE CALCULATED DIFFERENTLY? USE GLOBAL neighborhoods?
                
        
        #calculate vars:
        w_mor = self.model.m
        w_deg = self.model.d
        
        count_empty = self.model.count_type(self.model, "Empty")
        count_deg = self.model.count_type(self.model, "Degraded")
        count_veg = self.model.count_type(self.model, "Vegetated")
        rho_veg = count_veg/(count_empty+count_deg+count_veg)
        
        w_reg = (self.model.delta*rho_veg+(1-self.model.delta)*(q/len(neighbors)))*(self.model.b-self.model.c*count_veg) #w_-_0, regeneration
        w_col = self.model.r + self.model.f*q   #w_0_plus, colonization

        #apply rules
        if self.condition == "Empty":
            rand_num = random.random() 
            if rand_num < w_col: #probability
                self.condition = "Vegetated"
            elif rand_num > w_col and rand_num < w_col+w_deg:
                self.condition = "Degraded"

        elif self.condition == "Degraded":
            rand_num = random.random()
            if rand_num < w_reg:
                self.condition = "Empty"
                
        elif self.condition == "Vegetated":
            rand_num = random.random()
            if rand_num < w_mor:
                self.condition = "Empty"

class EcoModel(Model):
    """..."""
    def __init__(self, N):
        
        #Initialize model variables
        self.width = 20 #100
        self.height = 20 #100
        #self.density = 
        self.num_agents = self.width*self.height
        self.schedule = RandomActivation(self)
        self.delta = 0.1
        self.c = 0.2
        self.r = 0.01
        self.d = 0.1
        self.f = 0.9
        self.m = 0.1
        self.b = 0.5
        self.emp_dens = 0.25
        self.deg_dens = 0.25
        
        # Set up model objects
        self.grid = Grid(self.height, self.width, torus=False)
        self.dc = DataCollector({"Empty": lambda m: self.count_type(m, "Empty"),
                                "Vegetated": lambda m: self.count_type(m, "Vegetated"),
                                "Degraded": lambda m: self.count_type(m, "Degraded")})
    
        #Define patches
        for x in range(self.width):
            for y in range(self.height):
                rand_num = random.random()
                if rand_num < self.deg_dens:
                    new_patch = EcoAgent(self, (x, y), "Degraded")
                    self.grid[y][x] = new_patch
                    self.schedule.add(new_patch)
                elif rand_num > self.emp_dens and rand_num < self.emp_dens+self.deg_dens:
                    new_patch = EcoAgent(self, (x, y), "Empty")
                    self.grid[y][x] = new_patch
                    self.schedule.add(new_patch)
                else:
                    new_patch = EcoAgent(self, (x, y), "Vegetated") # Create a tree
                    self.grid[y][x] = new_patch
                    self.schedule.add(new_patch)    
        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        #calculate rho?
        self.schedule.step()
        self.dc.collect(self)
        
        print("Vegetated: "+str(self.count_type(self,"Vegetated")))
        print("Empty: "+str(self.count_type(self,"Empty")))
        print("Degraded: "+str(self.count_type(self,"Degraded")))
    
    @staticmethod
    def count_type(model, tree_condition):
        '''Helper method to count given condition in a given model.'''
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count
    
if __name__ == "__main__":
    """Run the model from here"""
    N = 100 #Model runs
    
    model = EcoModel(10)
    for i in range(N):
        model.step()
        agent_wealth = []
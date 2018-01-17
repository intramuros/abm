
from mesa import Agent
import random


class Patch(Agent):
    """..."""

    def __init__(self, model, pos, cond):
        super().__init__(pos, model)
        self.pos = pos  # gives position
        self.unique_id = pos  # gives agents a unique ID based on position
        self.condition = cond
        self.model = model

    def step(self):
        # create a neighbor array
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False)  # von Neumann neighborhood

        # # calculate the amount of neighbors
        num_veg = 0
        for neighbor in neighbors:
            if neighbor.condition == "Vegetated":
                num_veg += 1
        q = num_veg / len(neighbors)  # MAYBE THIS SHOULD BE CALCULATED DIFFERENTLY? USE GLOBAL neighborhoods?

        # params fig a
        x, y = self.pos
        rel_x = x/self.model.width
        rel_y = 1- y/self.model.height
        b = .3 + .7*rel_x
        f = rel_y
        m, r, d, c, delta = .1, 0, .2, .3, .1

        # # params fig b
        # y, x = self.pos
        # rel_x = round(x/self.model.width,5)
        # rel_y = round(y/self.model.height,5)
        # print(rel_x, rel_y)
        # b = .3 + .7*rel_x
        # m = 0.005 + 0.295*rel_y
        # f, r, d, c, delta = .9, 0, .2, .3, .1

        # # params fig c
        # x, y = self.pos
        # rel_x = x/self.model.width
        # rel_y = y/self.model.height
        # b = .3 + .7*rel_x
        # d = rel_y
        # m, r, f, c, delta = .1, 0, .9, .3, .1

        # # params fic d
        # x, y = self.pos
        # rel_x = x/self.model.width
        # rel_y = y/self.model.height
        # b = .1 + .9*rel_x
        # r = 0.05*rel_y
        # m, f, d, c, delta = .1, .9, .2, .3, .1

        # calculate rates:
        w_mor = m
        w_deg = d
        w_col = (
                    delta * self.model.rho_veg +
                    (1 - delta) * q
                ) * \
                (b - c * self.model.rho_veg) # w_0_plus, colonization
        w_reg = r + f * q  # w_-_0, regeneration

        # apply rules
        if self.condition == "Empty":
            rand_num = random.random()
            if rand_num < w_col:  # probability
                self.new_condition = "Vegetated"
            elif rand_num < w_deg + w_col:
                self.new_condition = "Degraded"
            else: self.new_condition = "Empty"

        elif self.condition == "Degraded":
            rand_num = random.random()
            if rand_num < w_reg:
                self.new_condition = "Empty"
            else: self.new_condition = "Degraded"

        elif self.condition == "Vegetated":
            rand_num = random.random()
            if rand_num < w_mor:
                self.new_condition = "Empty"
            else: self.new_condition = "Vegetated"

    def advance(self):
        self.condition = self.new_condition

    def get_pos(self):
        return self.pos

from mesa import Agent
import random


class Patch(Agent):
    """..."""

    def __init__(self, model, pos, cond):
        super().__init__(pos, model)
        self.pos = pos  # gives position
        self.unique_id = pos  # gives agents a unique ID based on position
        self.condition = cond
        self.new_condition = cond
        self.model = model
        self.q = 1  # dummy initial value

    def step(self):

        self.calculate_q()
        # calculate rates:
        w_mor = self.model.m
        w_deg = self.model.d
        w_col = (self.model.delta * self.model.rho_veg +
                 (1 - self.model.delta) * self.q) * \
                (self.model.b - self.model.c * self.model.rho_veg) # w_0_plus, colonization
        w_reg = self.model.r + self.model.f * self.q  # w_-_0, regeneration

        # apply rules
        if self.condition == "Empty":
            states = ["Vegetated", "Degraded"]
            t = [random.random() < w_col,
                 random.random() < w_deg]
            n = random.choice([0, 1])
            new_state = states[n]
            if t[n]:  # probability
                self.new_condition = new_state

        elif self.condition == "Degraded":
            rand_num = random.random()
            if rand_num < w_reg:
                self.new_condition = "Empty"

        elif self.condition == "Vegetated":
            rand_num = random.random()
            if rand_num < w_mor:
                self.new_condition = "Empty"

    def advance(self):
        self.condition = self.new_condition

    def get_pos(self):
        return self.pos

    def calculate_q(self):
        # create a neighbor array
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False)  # von Neumann neighborhood
        # calculate the amount of neighbors
        num_veg = 0
        for neighbor in neighbors:
            if neighbor.condition == "Vegetated":
                num_veg += 1
        self.q = num_veg / len(neighbors)

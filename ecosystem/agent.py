from mesa import Agent
import random


class Patch(Agent):
    '''
    Represents a single site in the landscape (a cell in the grid). Can be vegetated, empty or degraded
    '''

    def __init__(self, model, pos, cond):
        '''

        Create a new patch.

        Args:
        pos: initial location.
        cond: Indicator for the patch type

        '''
        super().__init__(pos, model)
        self.pos = pos
        self.unique_id = pos
        self.condition = cond
        self.new_condition = cond
        self.model = model
        self.q = 0

    def get_q(self):
        ''' Method to calculate fraction of vegetated neighbours '''
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
        num_veg = 0
        for neighbor in neighbors:
            if neighbor.condition == "Vegetated":
                num_veg += 1
        q = num_veg / len(neighbors)
        return q

    def get_q_minus(self):
        '''
        Method to calculate fraction of degraded neighbours
        '''
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
        num_deg = 0
        for neighbor in neighbors:
            if neighbor.condition == "Degraded":
                num_deg += 1
        q_minus = num_deg / len(neighbors)
        return q_minus

    def get_q_nonveg(self):
        '''
        Method to calculate fraction of non-vegetated neighbours
        (non-vegetated = empty or degraded)
        '''
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
        num_non_veg = 0
        for neighbor in neighbors:
            if neighbor.condition != "Vegetated":
                num_non_veg += 1
        q_nonveg = num_non_veg / len(neighbors)
        return q_nonveg

    def step(self):
        '''
        Calculate the state of an agent after one step
        '''
        self.q = self.get_q()
        # calculate rates:
        w_mor = self.model.m # mortality rate
        w_deg = self.model.d # degradation rate
        w_col = (self.model.delta * self.model.rho_veg +
                 (1 - self.model.delta) * self.q) * \
                (self.model.b - self.model.c * self.model.rho_veg)  # colonization rate
        w_reg = self.model.r + self.model.f * self.q  # regeneration rate

        # apply rules
        if self.condition == "Empty":
            rand_num = random.random()
            if rand_num < w_col:
                self.new_condition = "Vegetated"
            elif rand_num < w_col + w_deg:
                # print("proba sum",w_col+w_deg)
                self.new_condition = "Degraded"

        elif self.condition == "Degraded":
            rand_num = random.random()
            if rand_num < w_reg:
                self.new_condition = "Empty"

        elif self.condition == "Vegetated":
            rand_num = random.random()
            if rand_num < w_mor:
                self.new_condition = "Empty"

        #self.condition = self.new_condition

    def advance(self):
        '''
        Advance the agent by one step
        '''
        self.condition = self.new_condition

    def get_pos(self):
        return self.pos

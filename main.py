#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ecosystem.model import EcoModel


N = 20  # Model runs

model = EcoModel(20,20)
for i in range(N):
    model.step()
    agent_wealth = []
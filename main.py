#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ecosystem.model import EcoModel


N = 20  # Model runs

model = EcoModel(0.1, 0.02, "ecosystem/config_file.json")
for i in range(N):
    model.step()




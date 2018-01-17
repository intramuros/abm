from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from .model import EcoModel

# define colors
COLORS = {"Vegetated": "#00AA00",
          "Empty": "#880000",
          "Degraded": "#000000"}

# gridsize
height = 50
width = 50

def eco_model_portrayal(patch):
    if patch is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    (x, y) = patch.get_pos()
    portrayal["x"] = x
    portrayal["y"] = y
    portrayal["Color"] = COLORS[patch.condition]
    return portrayal

# add sliders
b_slider = UserSettableParameter('slider', "Establishment probability (b)", 0, 0, 1, 0.001)
m_slider = UserSettableParameter('slider', "Mortality probability vegetated sites (m)", 0, 0.005, 1, 0.001)

canvas_element = CanvasGrid(eco_model_portrayal, height, width, 500, 500)

patch_chart = ChartModule([{"Label": label, "Color": color} for (label, color) in COLORS.items()])

model_params = {
    "b": b_slider,
    "m": m_slider,
    "height": height,
    "width": width,
}
server = ModularServer(EcoModel, [canvas_element, patch_chart], "Ecosystem Dynamics", model_params)

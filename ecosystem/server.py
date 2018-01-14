from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from .model import EcoModel

COLORS = {"Vegetated": "#00AA00",
          "Empty": "#880000",
          "Degraded": "#000000"}


def eco_model_portrayal(patch):
    if patch is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    (x, y) = patch.get_pos()
    portrayal["x"] = x
    portrayal["y"] = y
    portrayal["Color"] = COLORS[patch.condition]
    return portrayal


canvas_element = CanvasGrid(eco_model_portrayal, 50, 50, 500, 500)
patch_chart = ChartModule([{"Label": label, "Color": color} for (label, color) in COLORS.items()])

model_params = {
    "height": 50,
    "width": 50,
}
server = ModularServer(EcoModel, [canvas_element, patch_chart], "Ecosystem Dynamics", model_params)
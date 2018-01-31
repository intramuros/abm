# Dryland Dynamics Model

## Summary

The [dryland dynamics model](https://www.sciencedirect.com/science/article/pii/S0040580906001250) is an agent-based simulation of spatial dynamics of vegetation in arid conditions. The environment is a grid of cells, representing a square piece of land. Each cell can either be degraded {-}, empty (unoccupied) {0} or vegetated {+}. The possible transitions are:

 - degraded to empty: {-} to {0}
 - empty to degraded: {0} to {-}
 - empty to vegetated: {0} to {+}
 - vegetated to empty: {+} to {0}

## How to Run

Launch an interactive server by Running ``run.py``:

```
    $ python run.py
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) move sliders to set the parameters and press Reset, then Run. 

To view and run the model analyses, use the ``Analyse`` Notebook.

## Files

### ``ecosystem/agent.py``

The agent class is called **Patch**. Each Patch object is placed on the grid, and its condition is assigned at the model initialization based on user-specified parameters. Its transitions between different states are governed by the rates calculated at each step. 

### ``ecosystem/model.py``

The **EcoModel** class is the model container. It is instantiated with parameters ``b`` - plant establishment probability of an empty site, ``m`` - mortality probability of a vegetated site, and additional parameters found in the accompanying ``config_file.json`` file. 


### ``ecosystem/server.py``

This code defines and launches the in-browser visualization for the model. Each cell is a rectangle, with a color based on its condition. *Vegetated* sites are green, *Empty* sites red, and *Degraded* sites are black.

### ``ecosystem/config_file.json``

This file contains initial parameters for the model simulation. 

## Further Reading

Kefi, S., Rietkerk, M., Alados, C. L., Pueyo, Y., Papanastasis, V. P., ElAich, A., and De Ruiter, P. C. (2007a).  Spatial vegetation patterns and imminent desertification in Mediterranean arid ecosystems. Nature, 449(7159):213–217. - (https://www.sciencedirect.com/science/article/pii/S0040580906001250)

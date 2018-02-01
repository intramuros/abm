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

## Short description of parameters in the config_file.json

Detailed information on the parameters can be found in the accompanying literature 

Parameter | Description | Value
----------|-------------|----------
"height" | height of the model landscape | 50-100 (recommended)
"width"  | width of the model landscape | 50-100 (recommended) 
"delta"  | fraction of seeds globally dispersed | 0.1

sometext
"c"  | includes germination probability and competitive effect from vegetated sites | 0.2
"r"  | regeneration probability of a degraded site without vegetation in its neighbourhood
"d"  | degradation probability of empty sites
"f"  | positive effect of a neighbouring vegetated site on a degraded site
"Empty sites density"  | initial density of empty sites
"Degraded sites density"  | initial density of degraded sites
"Use Torus" | if Torus configuration is used set this parameter to 1, otherwise 0
"Use Flowlength" | if Flowlength parameter is used set to 1, otherwise 0
"alpha_feedback" | strengh of feedback between plant pattern and resource leakiness. 
"Maximum Flowlength" : 26.7,
"alpha_bare" : 1.1,
"Patch size" : 0.5,
"Theta" : 20,
"Use infrequent rain" : 0,
"Rain period" : 5,
"No rain period" : 10

## Further Reading

Kefi, S., Rietkerk, M., Alados, C. L., Pueyo, Y., Papanastasis, V. P., ElAich, A., and De Ruiter, P. C. (2007a).  Spatial vegetation patterns and imminent desertification in Mediterranean arid ecosystems. Nature, 449(7159):213–217 - (https://www.nature.com/articles/nature06111)

Kefi, S., Rietkerk, M., van Baalen, M., and Loreau, M. (2007b).  Local facilitation, bistability and transitions in arid ecosystems.
Theoretical Population Biology, 71(3):367–379. - (https://www.sciencedirect.com/science/article/pii/S0040580906001250)

Mayor,A.  G.,  Bautista,  S.,  Small,  E.  E.,  Dixon,  M.,  and  Bellot,  J.  (2008). Measurement  of  the  connectivity  of  runoff  source  areas  as  determined  by vegetation pattern and topography:  A tool for assessing potential water and soil losses in drylands.
Water Resources Research, 44(10):1–13.

Mayor,A. G., K ́efi, S., Bautista, S., Rodr ́ıguez, F., Carten ́ı, F., and Rietkerk, M.(2013). Feedbacks between vegetation pattern and resource loss dramatically decrease  ecosystem  resilience  and  restoration  potential  in  a  simple  dryland model. 
Landscape Ecology, 28(5):931–942

Rodriguez,  F.,  Mayor,  A.  G.,  Rietkerk,  M.,  and  Bautista,  S.  (2017).   A  null model  for  assessing  the  cover-independent  role  of  bare  soil  connectivity  as indicator of dryland functioning and dynamics. Ecological indicators. - (https://www.sciencedirect.com/science/article/pii/S1470160X1730660X)



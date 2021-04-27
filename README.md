# Fonts causal anaylsis
code to analyze font embeddings created by a neural net. This repo contains mostly jupyter notebooks and is organized as follows

## Data sources `data`
* The data for this anaylsis comes from the `UT research project datasets` from monotype in a folder called `datasets`. I've written the code without global file paths assuming `datasets` is saved outside of this folder i.e. 

```
fonts_project    
└───datasets
│   └─── New Pangram 2
│   └─── UT research project datasets
│   │   │ Style Sku Family.csv
└───fonts_replication
```

### Creating the panel
* Running `Gravity_Dist.py` creates the gravity distance measure. This file is computationally intesive to run and takes about 24 hours on relatively weak hardware i.e. I5-6260U CPU @ 1.80GHz × 4 and 16 GB RAM. It takes `embeddings_full.csv` as input and returns `embeddings_avg.csv` and `gravity_dist_avg.csv` as outputs.
* `covariate_construction.py` merges the other relevant data into the synthetic control.
* The resulting file is called `fonts_panel_biannual_new.csv`.

### Estimating the synthetic control
* `synth_biannual_plots.R` - runs the synthetic control with the Synth package to save .png image in the directory.
* `synth_biannual_tables.R` - runs the synthetic control with the Synth package to print tables to the R terminal.
* `functions_conformal_012` - inference methods from ["An Exact and Robust Conformal Inference Method for Counterfactual and Synthetic Controls"]: https://arxiv.org/abs/1712.09089.
* Running the synthetic control will require R version > 4. I ran the code on ubuntu 18.03. 
* The code is currently written to produce tables for the inverse distance measure. To use the distance from Averia, you can modify lines 60 and 71 with the appropriate variables i.e. change `gravity_dist` and `gravity_var` to `Distance.from.Mean` and `mean_var` from `fonts_panel_biannual_new.csv`.

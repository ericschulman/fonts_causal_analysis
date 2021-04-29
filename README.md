# Causal Analysis of Merger using Font Embeddings

This repo contains the codes to conduct causal analysis of merger using font embeddings created by fontnet in https://github.com/ericschulman/fontnet.

## Data sources `data`
* The data for this anaylsis come from the `main_dataset` in a folder called `datasets`. We have written the code without global file paths assuming `datasets` is saved outside of this folder, i.e., 

```
fonts_project    
└───datasets
│   └─── raw_pangrams
│   └─── main_dataset
│   │   │ Style Sku Family.csv
└───fonts_causal_analysis
```

## Creating the panel
* Running `Gravity_Dist.py` creates the gravity distance measure. This file is computationally intesive to run and takes about 24 hours on relatively weak hardware, i.e., I5-6260U CPU @ 1.80GHz × 4 and 16 GB RAM. It takes `embeddings_full.csv` as the input and returns `embeddings_avg.csv` and `gravity_dist_avg.csv` as the outputs.
* `covariate_construction.py` merges the other relevant data into the synthetic control. It also computes the other distance measure, i.e., the distance from Averia, which is denoted as `Distance.from.Mean`.
* The resulting file is called `fonts_panel_biannual_new.csv`.

## Estimating the treatment effects of merger using the synthetic control method
* `synth_biannual_plots.R` - runs the synthetic control with `Synth` `R` package to save .png image in the directory.
* `synth_biannual_tables.R` - runs the synthetic control with `Synth` `R` package to print tables to the `R` terminal.
* `functions_conformal_012` - implements the inference method from [An Exact and Robust Conformal Inference Method for Counterfactual and Synthetic Controls](https://arxiv.org/abs/1712.09089).
* Running the synthetic control will require R version > 4. We ran the code on ubuntu 18.03. 
* The code is currently written to produce tables for the gravity distance measure. To use the distance from Averia, you can modify lines 60 and 71 with the appropriate variables i.e. change `gravity_dist` and `gravity_var` to `Distance.from.Mean` and `mean_var` from `fonts_panel_biannual_new.csv`.

# Causal Analysis of Merger using Font Embeddings

This repo contains the codes to conduct causal analysis of merger using font embeddings created by fontnet in https://github.com/ericschulman/fontnet. Refer to Han et al. (2020) for details of the merger analysis.

## Data sources
* The data for this anaylsis come from the `main_dataset` in a folder called `datasets`. We have written the code without global file paths assuming `datasets` is saved outside of this folder, i.e., 

```
fonts_project
└───fonts_causal_analysis
└───datasets
│   └─── raw_pangrams
│   └─── crop7_test
│   └─── crop7_train
│   └─── main_dataset
│   │   │ Style Sku Family.csv
│   │   │ ...
└───models
└───logs
└───fontnet
```

## Creating the panel
* Running `Gravity_Dist.py` creates the gravity distance measure. This file is computationally intesive to run and takes about 24 hours on relatively weak hardware, i.e., I5-6260U CPU @ 1.80GHz × 4 and 16 GB RAM. It takes `embeddings_full.csv` as the input and returns `embeddings_avg.csv` and `gravity_dist_avg.csv` as the outputs.
* `covariate_construction.py` merges the other relevant data into the synthetic control. It also computes the other distance measure, i.e., the distance from Averia, which is denoted as `Distance.from.Mean`.
* The resulting file is called `fonts_panel_biannual_new.csv`.

## Estimating the treatment effects of merger using the synthetic control method
* `synth_biannual_plots.R` - runs the synthetic control with `Synth` `R` package to save .png image in the directory.
* `synth_biannual_tables.R` - runs the synthetic control with `Synth` `R` package to print tables to the `R` terminal.
* `functions_conformal_012` - implements the inference method from Chernozhukov et al. (2021).
* Running the synthetic control will require `R` version >= 4. We ran the code on Ubuntu 18.03. 
* The code is currently written to produce tables for the gravity distance measure. To use the distance from Averia, you can modify lines 60 and 71 with the appropriate variables i.e. change `gravity_dist` and `gravity_var` to `Distance.from.Mean` and `mean_var` from `fonts_panel_biannual_new.csv`.

## References
* [Chernozhukov, V., Wüthrich, K., & Zhu, Y. (2021). An exact and robust conformal inference method for counterfactual and synthetic controls. Journal of the American Statistical Association.](https://arxiv.org/abs/1712.09089)

* [Han, S., Schulman, E., Grauman, K., & Ramakrishnan, S. (2020). Shapes as product differentiation: Neural network embedding in the analysis of markets for fonts.](https://sites.google.com/site/universs01/mypdf/font_embedding.pdf)


## License

The codes and the dataset (separately shared) for this repository are protected by the Creative Commons non-commerical no-derivative license.

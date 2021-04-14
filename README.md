# fonts_analysis
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


### data cleaning
* Running `Gravity_Dist.py` creates the gravity distance measure. This file is computationally intesive to run and takes about 24 hours on relatively weak hardware i.e. I5-6260U CPU @ 1.80GHz × 4 and 16 GB RAM. It takes `embeddings_full.csv` as input and returns `embeddings_avg.csv` and `gravity_dist_avg.csv` as outputs.
* `covariate_construction.py` merges the other relevant data into the synthetic control.

### estimation
* `synth_perm_biannual.R` - runs the synthetic control with the Synth package to create a nice figure
* `functions_conformal_012` - inference methods from ["An Exact and Robust Conformal Inference Method for Counterfactual and Synthetic Controls"]: https://arxiv.org/abs/1712.09089. The replication code is saved here [source]: https://drive.google.com/file/d/10xX8cj1HHpTgR9kT3GBljTfhXox0EJ9c/view
* Running the synthetic control will require R version > 4. I ran the code on ubuntu 18.03. 


### Using mean embeddings/modifying the code.

"""
Created on Fri Aug 21 01:34:01 2020
Updated on Thur Aug 27 

@author: kyungholee
@author: Eric Schulman
"""

import pandas as pd
import time
import numpy as np

def get_avg_embeddings(data_path):
    embeddings = pd.read_csv(data_path+'embeddings_full.csv')
    embeddings = embeddings.dropna()
    embeddings[['style','family']] = embeddings[['style','family']] .astype(int)
    embeddings = embeddings.groupby(['style','crop_name'],as_index=False).mean() #this is here to fix a bug in 
    #write embeddings...
    embeddings_sty = embeddings.groupby(['style']).mean()
    embeddings_sty.to_csv(data_path+"embeddings_avg.csv")


def main(data_path):
    ######load data######
    embeddings = pd.read_csv(data_path+ "embeddings_avg.csv")
    families = pd.read_csv(data_path+ "Families.csv")

    ## drop a row with nan data.
    embeddings = embeddings.dropna()

    regular_fonts = embeddings.groupby("family").mean()
    regular_fonts = regular_fonts.iloc[:,1:]
    
    #for each embeddings
    embedding_names = ['embedding {}'.format(i) for i in range(1,129)]
    gravity_dist = regular_fonts.copy()
    gravity_dist.insert(0,"gravity_dist",np.nan)

    len_grvt = len(gravity_dist)

    """ Calculating Pairwise Diff by Double For loop """

    t = time.time()

    pairwise_diff = np.zeros(shape = (len_grvt,len_grvt))
    emebedding_vectors = gravity_dist.loc[:,embedding_names]
    for i in range(len_grvt):
        ith_emb = emebedding_vectors.iloc[i,:]
        for j in range(i+1,len_grvt):
            jth_emb = emebedding_vectors.iloc[j,:]
            pairwise_diff[i,j] = np.linalg.norm(ith_emb - jth_emb)
         
    elapsed = time.time() - t
    print("Time taken is : {}".format(elapsed))

    pd.DataFrame(pairwise_diff).to_csv(data_path+"pairwise_diff.csv")
    pairwise_diff_sum = pairwise_diff + pairwise_diff.T
    pairwise_diff_sum_reverse = 1/pairwise_diff_sum
    pairwise_diff_sum_reverse[pairwise_diff_sum_reverse == np.inf] = 0
    gravity_dist.loc[:,'gravity_dist'] = -1 * pairwise_diff_sum_reverse.sum(axis=0) ## taking (-1)
    gravity_dist.loc[:,'log_gravity_dist'] = -1 * np.log(pairwise_diff_sum_reverse.sum(axis=0)) ## taking (-1)
    gravity_dist.to_csv(data_path+"gravity_dist_avg.csv")


if __name__ == "__main__":
    data_path = "../datasets/UT research project datasets/"
    get_avg_embeddings(data_path)
    main(data_path)
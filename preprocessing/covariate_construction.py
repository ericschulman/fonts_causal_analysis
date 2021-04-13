"""

Created on Tue Aug 25 2020

@author: Kyungho(George) Lee (SNU Econ)
@author: Eric Schulman (UT Econ)

"""

import pandas as pd
import datetime
import numpy as np
import csv
import os
from sklearn.decomposition import PCA


def clean_date(df):
    """ Cleaning date data """
    df['year'] = df['Start Date'].str[0:4]
    df['yymm'] = df['Start Date'].str[0:7]
    df = df[df['year'] != '0000'] ## Drop data recorded with 0000 year
    df['yymm'] = pd.to_datetime(df['yymm'])
    return df


def get_languages(data_path):
    """ There is 'Language IDs' data in Skus.csv with , separation.
    i.e. 2,3 in the cell of the Skus.csv Language IDs column indacate that the font supports laguage 2 and 3.
    So, it is the number of supported laugage if we count the number of ',' and add 1."""

    sku = pd.read_csv(data_path + "Skus.csv") 

    sku['comma_count'] = sku['Language IDs'].str.count(',')
    sku['laguage_count'] = sku['comma_count'] + 1
    sku = clean_date(sku)

    #saving monthly language counts/sum
    monthly_language = pd.DataFrame()

    sku_grouped = sku.groupby(['Foundry ID','yymm'])
    monthly_language['total_count'] = sku_grouped.sum()['laguage_count']
    monthly_language['language_count_mean'] = sku_grouped.mean()['laguage_count']

    return monthly_language


def get_maturity(data_path):
    """ Monthly cumulative sum of families by foundries
    
    Apply groupby twice to Families.csv """
    families = pd.read_csv(data_path + "Families.csv")

    #Cleaning date datas
    families = clean_date(families)

    #calculating/saving monthly language counts/sum
    families_cumsum = families.groupby(['Foundry ID', 'yymm']).count().groupby(level=0).cumsum().reset_index()
    families_cumsum = families_cumsum.rename(columns = {"Family ID": "Cumulative_families"})
    families_cumsum[['Foundry ID','yymm','Cumulative_families']].to_csv(data_path+"monthly_families_cumsum.csv",index = False)

    return families_cumsum


def get_industry_tags(data_path):
    tags_6 = pd.read_csv(data_path+'tag_dummy_six.csv')
    families = pd.read_csv(data_path + "Families.csv")
    #tags_2 = pd.read_csv(data_path+'tag_dummy_two.csv')
    dfs = [tags_6]#,tags_2]
    for df in dfs:
        df['groups'] = 0
        rel_columns = list(df.columns[4:-1])
        for j in range(len(rel_columns)):
            df['groups'] = df['groups'] + (2**j)*df[rel_columns[j]]
    tags_6 = dfs[0]
    tags_6_fam = tags_6.groupby('family_id',as_index=False).first()
    tags_6_fam = tags_6_fam.rename(columns={'family_id':'Family ID'})
    foundry_tag_data = pd.merge(tags_6_fam,families,on="Family ID")
    foundry_tag_data['yymm'] = foundry_tag_data['Start Date'].str[0:7]
    foundry_tag_data['year'] = foundry_tag_data['Start Date'].str[0:4]
    foundry_tag_data['month'] = foundry_tag_data['Start Date'].str[5:7]
    foundry_tag_data = foundry_tag_data[ (foundry_tag_data['month']!='00') & (foundry_tag_data['year']!='0000')  ]
    foundry_tag_data['yymm'] = pd.to_datetime(foundry_tag_data['yymm'])
    foundry_tag_grouped = foundry_tag_data[['yymm','Foundry ID','groups']]
    foundry_tag_grouped = foundry_tag_grouped.groupby(['yymm','Foundry ID'],as_index=False).agg({'groups':'nunique' })
    return foundry_tag_grouped


def create_date_label(Main_Data_Supply):
    """Marking quartely date"""

    ## this code is to disentagle start_date into year, month, day.
    freq = 2
    year_list = []
    month_list = []
    yymm_list = []

    for i in range(len(Main_Data_Supply)):

        year_list.append(Main_Data_Supply['Start Date'][i][0:4])
        month_list.append(Main_Data_Supply['Start Date'][i][5:7])
        yymm_list.append(Main_Data_Supply['Start Date'][i][0:7])

    Main_Data_Supply['yymm'] = yymm_list
    Main_Data_Supply['year'] = np.array(year_list).astype(int)
    Main_Data_Supply['year_month'] = np.array(year_list).astype(int)
    month_frac = (np.array(month_list).astype(int)-1)/12


    ## Marking Starts
    for i in range(0,freq):
        current_freq = i/freq
        next_freq = (i+1)/freq
        added_date =  (month_frac >= current_freq) & (next_freq > month_frac)
        Main_Data_Supply['year_month'] = Main_Data_Supply['year_month']+ current_freq*( added_date )
            

    ## Measurement Error, Drop data with 0000-00 date record
    Main_Data_Supply = Main_Data_Supply[Main_Data_Supply['yymm'] != '0000-00']
    Main_Data_Supply['yymm'] = pd.to_datetime(Main_Data_Supply['yymm'])
    ## Rest index
    Main_Data_Supply = Main_Data_Supply.reset_index().iloc[:,1:]
    return Main_Data_Supply


def cal_distance_from_benchmark(embedding_vectors,benchmark_vector):
    #### Note that mean_vector is calculated by using regular fonts
    embedding_names = ['embedding {}'.format(i) for i in range(1,129)]
    return pd.DataFrame(np.linalg.norm(embedding_vectors.loc[:,embedding_names] - benchmark_vector,axis=1),columns=['distance'])
    

def split_cal_dist(period, mean_vector, median_vector):
    embedding_names = ['embedding {}'.format(i) for i in range(1,129)]
    per_period = pd.merge(period,embeddings,left_on ='Style ID',right_on = 'style')
    embedding_vectors = per_period.loc[:,embedding_names]
    mean_dist = cal_distance_from_benchmark(embedding_vectors)
    median_dist = cal_distance_from_benchmark(embedding_vectors)

    return pd.DataFrame([mean_dist.mean(),median_dist.dropna().median()])


def calculate_mean_dist(Main_Data_Supply):
    """
    Calculating Benchmark(Mean/Median) Vector

    Note: Since embeddings(gravity_dist_avg.csv) we use in this code only consists of 'regular'(i.e. Defauly Style ID) fonts,
    It is ok to use embeddings to calculate benchmark vector """
    embeddings = pd.read_csv(data_path+ "gravity_dist_avg.csv")
    embedding_names = ['embedding {}'.format(i) for i in range(1,129)]

    mean_vector = np.mean(embeddings.loc[:,embedding_names],axis=0)
    median_vector = np.median(embeddings.loc[:,embedding_names],axis=0)

    Main_Data_Supply["Distance from Mean"] = cal_distance_from_benchmark(Main_Data_Supply,mean_vector) ### Calculate distance from the mean vector
    Main_Data_Supply["Distance from Median"] = cal_distance_from_benchmark(Main_Data_Supply,median_vector) ### Calculate distance from the median vector
    return Main_Data_Supply


def get_data_supply(data_path):
    """     Constructing Data for analysis """
    embeddings = pd.read_csv(data_path+ "gravity_dist_avg.csv")
    style = pd.read_csv(data_path+ "Styles.csv",parse_dates = ['Start Date'])
    style_sku_family = pd.read_csv(data_path+ "Style Sku Family.csv")
    families = pd.read_csv(data_path+ "Families.csv",parse_dates = ['Start Date'])
    sku = pd.read_csv(data_path+ "Skus.csv")
    foundries = pd.read_csv( data_path+ "Foundries.csv")

    ## drop a row with nan data.
    embeddings = embeddings.dropna()

    Main_Data_Supply = pd.merge(embeddings,style.loc[:,['Style ID','Family ID','Glyph Count']],left_on = 'family',right_on = 'Family ID')
    Main_Data_Supply = Main_Data_Supply.reset_index().iloc[:,1:]
    Main_Data_Supply = pd.merge(Main_Data_Supply,families,on='Family ID')
    Main_Data_Supply = pd.merge(Main_Data_Supply,foundries.loc[:,["Foundry ID","Foundry Name"]],on='Foundry ID')
    Main_Data_Supply = calculate_mean_dist(Main_Data_Supply)
    Main_Data_Supply = create_date_label(Main_Data_Supply)
    return Main_Data_Supply


def generate_data(data_path,industry_tags=True):
    column_list = ['style', 'gravity_dist']
    column_list = column_list + ["embedding {}".format(i) for i in range(1,129)]
    column_list = column_list + ['Family ID', 'Family Name', 'Foundry ID', 'Foundry Name', 'yymm' ,
    'Glyph Count', 'year_month']
    column_list = column_list + ["Distance from Mean", "Distance from Median"]

    Main_Data_Supply = get_data_supply(data_path)
    merged_data = Main_Data_Supply.loc[:, column_list]

    if industry_tags:
        tags = get_industry_tags(data_path)
        merged_data = pd.merge(merged_data, tags, on = ['Foundry ID','yymm'], how='left')

    languages = get_languages(data_path)
    merged_data = pd.merge(merged_data, languages, on = ['Foundry ID','yymm'], how='left')

    maturity = get_maturity(data_path)
    merged_data = pd.merge(merged_data, maturity, on = ['Foundry ID','yymm'], how='left')

    return merged_data


def balance_panel(Main_Data_Supply):
    freq = 2
    years= np.arange(2000,2018,1/freq)
    
    #select relevant years
    foundry_selection =  ((Main_Data_Supply['Distance from Mean'].notna()) & (Main_Data_Supply['year_month']>=2002) 
                          & (Main_Data_Supply['Foundry Name']!='') & (Main_Data_Supply['Foundry Name'].notna()))

    foundry_selection = foundry_selection & Main_Data_Supply['Foundry Name'].apply(lambda x: str(x).find('moulding') == -1)
    foundry_sizes = (Main_Data_Supply[foundry_selection]).groupby('Foundry Name').size()
    foundry_list = foundry_sizes[ (foundry_sizes >= 5) ]
    foundry_list = foundry_list.index.unique()

    #create a multi-index
    n_years = len(years)
    n_foundries = len(foundry_list)
    panel_index = pd.MultiIndex.from_product([years,foundry_list],
        names=['year_month','Foundry Name'])

    #most numerical attributes
    panel = pd.DataFrame(index=panel_index)

    #select relevant attributes
    attribute_names = ['Distance from Mean', 'Distance from Median', "Glyph Count",
     'gravity_dist', "total_count","groups" ]

    attr_array = Main_Data_Supply[['year_month','Foundry Name']+ attribute_names]

    #create count and attr
    count_array = attr_array.groupby(by=['year_month','Foundry Name']).size()
    count_array= count_array.rename('new obs')
    attr_array = attr_array.groupby(by=['year_month','Foundry Name']).mean()

################### work in progress ####################

    #compute count array a higher frequency...
    num_obs_array = (Main_Data_Supply.copy()) [['yymm','year_month','Foundry Name', 'Distance from Mean']]
    num_obs_array = num_obs_array.groupby(by=['yymm','Foundry Name','year_month'], as_index=False).count()
    num_obs_array = num_obs_array.rename(columns={'Distance from Mean':'entry periods'})
    num_obs_array['entry periods'] = 1*(num_obs_array['entry periods'] >= 0)
    #then do a second group by, but take the max....
    num_obs_array = num_obs_array.groupby(by=['year_month','Foundry Name']).sum()
    num_obs_array = num_obs_array['entry periods']
    print(num_obs_array.shape, num_obs_array.max(), num_obs_array.min())
    #print(num_obs_array)

################# work in progress ####################
    
    #use 10 pca embeddings
    embedding_names = ['embedding %s'%(i+1) for i in range(128)]
    pca = PCA(n_components=10, svd_solver='arpack')
    pca_embeddings_raw = pca.fit_transform(Main_Data_Supply[embedding_names])
    pca_embeddings = Main_Data_Supply[['year_month','Foundry Name']]
    pca_embeddings[['pca embedding %s'%(i+1) for i in range(10)]] = pd.DataFrame(pca_embeddings_raw)
    pca_embeddings= pca_embeddings.groupby(by=['year_month','Foundry Name']).mean()

    #count number of fonts
    print(panel.shape)
    panel = panel.join(attr_array,how='left')
    print(panel.shape)
    panel = panel.join(count_array,how='left')
    print(panel.shape)
    panel = panel.join(pca_embeddings,how='left')
    print(panel.shape)
    panel = panel.join(num_obs_array,how='left')
    print(panel.shape)
    print('--------')

    #add number of nas as a covariate?
    no_nas = panel['Distance from Mean'].count(level=1)
    panel = panel.join(no_nas,on='Foundry Name',rsuffix='_x')
    panel = panel.rename(columns={'Distance from Mean_x':'no_nas'})
    raw_consec = 1*panel['Distance from Mean'].isna()

    #document which rows are empty
    attr_0s = ['new obs', "total_count","entry periods","groups"]    
    panel[attr_0s ] = panel[attr_0s].fillna(0)

    #fillnas with forward propogation...
    print(panel[panel.index.get_level_values(0)>=2002].dropna().shape)
    panel = panel.groupby(by=['Foundry Name']).fillna(method='ffill')
    panel = panel[panel.index.get_level_values(0)>=2002] #drop older observation

    #drop remaining foundries that have no data
    no_data = np.array( panel.index.to_list())[panel.isnull().any(axis=1),1]
    no_data =  np.unique(no_data)
    print(len(no_data))
    panel = panel[~panel.index.get_level_values(1).isin(no_data)]

    #drop foundries with no variance i.e. same distance for all
    no_variance = panel['Distance from Mean'].groupby(level=[1]).var() <= 1e-6
    no_variance = np.array(no_variance.index)[no_variance]
    no_variance =  np.unique(no_variance)
    panel = panel[~panel.index.get_level_values(1).isin(no_variance)]

    #include var as a covariate
    panel_var = panel.copy()#[panel.index.get_level_values(0) < 2014.5 ] 
    var_attr = ['Distance from Mean','gravity_dist','Glyph Count']+ ['pca embedding %s'%(i+1) for i in range(10)]
    panel_var = panel_var[var_attr]
    panel_var['gravity_dist'] = -1*np.log(-1*panel_var['gravity_dist'])
    panel_var = panel_var.var(level=1)
    panel = panel.join(panel_var,on='Foundry Name',rsuffix='_var')
    panel = panel.rename(columns={'Distance from Mean_var':'mean_var','gravity_dist_var':'gravity_var'}) 


    #figure out number of periods with a change
    panel.insert(len(panel.columns)-1,"consec",0)
    for foundry in list(panel.index.get_level_values(1)):
        y = raw_consec[raw_consec.index.get_level_values(1)==foundry] #max number of consuecutive entries
        y =  y * (y.groupby((y != y.shift()).cumsum()).cumcount() + 1)
        panel['consec'][panel.index.get_level_values(1)==foundry] = y 

    #check to see if the panel is balanced
    #print(panel.shape)
    #print(panel.groupby(by='year_month').size())

    #something with foundries/coming up with unique ids for them
    num_years = panel.groupby('Foundry Name').size().max()
    num_foundries = panel.groupby(by='year_month').size().max()
    panel['Foundry Id'] = np.tile(range(1, num_foundries +1),  num_years)

    return panel


if __name__ == "__main__":
    data_path = "../datasets/UT research project datasets/"
    Main_Data_Supply = generate_data(data_path)
    Main_Data_Supply.to_csv(data_path + "Main_Data_Supply_merged_bi.csv")
    Main_Data_Supply = pd.read_csv(data_path + "Main_Data_Supply_merged_bi.csv")
    panel = balance_panel(Main_Data_Supply)
    panel.to_csv(data_path+ 'fonts_panel_biannual_new.csv',quoting=csv.QUOTE_MINIMAL)
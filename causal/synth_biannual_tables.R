###########################################################################################################
# Preliminaries
###########################################################################################################

rm(list = ls())
setwd("~/Documents/fonts/fonts_replication/")

###########################################################################################################
# Packages
###########################################################################################################


#note for Ubuntu the following dependency is needed: sudo apt-get install libgmp3-dev  sudo apt-get install libmpfr-dev
library(haven)
library(xtable)
library(CVXR)
library(Synth)


###########################################################################################################
################# set up variables for analysis ###########################################################
###########################################################################################################


### load the Functions
source("causal/functions_conformal_012.R")

### load the data Data
fonts_data<- read.csv("../datasets/UT research project datasets/fonts_panel_biannual_new.csv")
fonts_data$gravity_dist = -1*(log(-1*fonts_data$gravity_dist))
fontfontid<-11

#setup control ids, this code is awful...
controls0<-unique(fonts_data$Foundry.Id)
controls_id<-c()
for (i in c(1:length(controls0))) {
  if (controls0[i] != fontfontid)
    controls_id<-append(controls_id,controls0[i])
}


fonts_data$Foundry.Name <-as.character(fonts_data$Foundry.Name)

# setup covariates for prediction purposes
embedding_pred <- c()
for (i in c(1:10)){
  embedding_pred <- append(embedding_pred,paste("pca.embedding.",toString(i),sep=""))
}

embedding_spec <- c()
for (i in c(1:10)){
  embedding_spec[[length(embedding_spec)+1]] <- list(paste("pca.embedding.",toString(i),sep=""),seq(2002.0,2014.5,by=.5),c("mean"))
}

embedding_var <- c()
for (i in c(1:10)){
  embedding_spec[[length(embedding_spec)+1]] <- list(paste("pca.embedding.",toString(i), "_var",sep=""),seq(2002.0,2014.5,by=.5),c("mean"))
}

predictors_list <- c("gravity_dist", embedding_pred, "gravity_var", "Glyph.Count","consec", "no_nas")

#####################################################################################################
# calculate treatment effects #######################################################################
#####################################################################################################

calculate_treatment<-function(pre_treatment,post_treatment){
  relevant_years<-c(pre_treatment,post_treatment)
  dataprep.out<-dataprep(foo = fonts_data,
                         predictors = predictors_list,
                         predictors.op = "mean",
                         dependent = "gravity_dist",
                         unit.variable = "Foundry.Id",
                         time.variable = "year_month",
                         treatment.identifier = fontfontid,
                         controls.identifier = controls_id,
                         time.predictors.prior = relevant_years, #pre_treatment ##, #relevant_years, #, # #average w over all years 
                         time.optimize.ssr = relevant_years, #pre_treatment, #relevant_years, #, #compute v weights over all years
                         unit.names.variable = "Foundry.Name",
                         time.plot = relevant_years)
  
  
  ## choose average v instead of something more sophisticated for now...
  v = 1/length(predictors_list) * rep(1,length(predictors_list))
  synth.out <- synth(dataprep.out,custom.v=v)
  
  
  y1 <- dataprep.out$Y1plot
  y_synth <- dataprep.out$Y0plot%*%synth.out$solution.w
  
  T0 <- length(pre_treatment)
  T1 <- length(post_treatment)
  
  
  treatment <- mean(y1[(T0:(T0+T1))] - y_synth[(T0:(T0+T1))])
  #compute confidence interval
  p_block <- moving.block(y1, y_synth, T0, T1)
  p_all <- all(y1, y_synth, T0, T1,5000)
  return(list(treatment,p_block,p_all,synth.out,dataprep.out))
}


#####################################################################
###################### print results ################################
#####################################################################


print_treat<-function(results_info, index){
  lines<-c("effect (pre-treatment control) ", "p-value (block) ",
           "p-value (all) ")
  for (j in c(1:3)){
    line <- lines[j]
    for (i in c(index[1]:index[2])){
      line <- paste(line, " & ")
      line <- paste(line, round( results_info[i,j] ,4)) 
    }
    line <- paste(line, " \\")
    print(line)
  }
  
}

#####################################################################
###################### pre treatment placebo, yearly ################
#####################################################################

placebo_years<- c()
for (i in c(2003:2014)){
  placebo_years[[length(placebo_years)+1]] <- list(c(i,i+.5))
}

p_blocks <- c()
p_alls <- c()
treatments <- c()

for (i in c(1:12)){
  pre_treatment <- c( c(2002.,2002.5), c(placebo_years[1:i-1]) )
  pre_treatment <- unlist(pre_treatment)
  post_treatment <- unlist(placebo_years[[i]])
  print(pre_treatment)
  print(post_treatment)
  treatment_result <- calculate_treatment(pre_treatment,post_treatment)
  
  
  #save results
  treatment <-treatment_result[[1]]
  p_block <-treatment_result[[2]]
  p_all  <-treatment_result[[3]]
  synth.out <- treatment_result[[4]]
  
  
  #save the results
  treatments <- append(treatments,treatment)
  p_blocks <- append(p_blocks,p_block)
  p_alls <- append(p_alls,p_all)
}


results_info <-array(c(treatments,p_blocks,p_alls),
                     dim= c(length(treatments) ,3))

#actually print results
print_treat(results_info,c(1,5))
print_treat(results_info,c(6,10))
print_treat(results_info,c(11,12))




#####################################################################
###################### pre treatment placebo, biannual ##############
#####################################################################

placebo_years<- seq(2012.,2014.,by=.5)
p_blocks <- c()
p_alls <- c()
treatments <- c()

for (i in c(1:5)){
  pre_treatment <- c( seq(2002.,2011.5,by=.5), c(placebo_years[1:i-1]) )
  post_treatment <- c(placebo_years[i])
  print(pre_treatment)
  print(post_treatment)
  
  treatment_result <- calculate_treatment(pre_treatment,post_treatment)
  
  
  #save results
  treatment <-treatment_result[[1]]
  p_block <-treatment_result[[2]]
  p_all  <-treatment_result[[3]]
  synth.out <- treatment_result[[4]]
  
  
  #save the results
  treatments <- append(treatments,treatment)
  p_blocks <- append(p_blocks,p_block)
  p_alls <- append(p_alls,p_all)
}


results_info <-array(c(treatments,p_blocks,p_alls),
                     dim= c(length(treatments) ,3))

#actually print results
print_treat(results_info,c(1,5))

#############################################################
########## print results ####################################
#############################################################


pre_treatment <- seq(2002,2014.,by=.5)
post_treatment <- seq(2014.5,2017.5,by=.5)
treatment_durations <- c( seq(2014.5,2017.5,by=.5),
                          list( seq(2015.,2015.5,by=.5)), list(seq(2016.,2016.5,by=.5)),  list(seq(2017.,2017.5,by=.5)),
                          list( seq(2014.5,2015.5,by=.5), seq(2014.5,2016.5,by=.5), seq(2014.5,2017.5,by=.5)) )

p_blocks <- c()
p_alls <- c()
treatments <- c()

for (post_treatment in treatment_durations) { 
  
  #compute treatment
  treatment_result <- calculate_treatment(pre_treatment,post_treatment) 
  treatment <-treatment_result[[1]]
  p_block <-treatment_result[[2]]
  p_all  <-treatment_result[[3]]
  
  #save the results
  treatments <- append(treatments,treatment)
  p_blocks <- append(p_blocks,p_block)
  p_alls <- append(p_alls,p_all)
  
}



results_info <-array(c(treatments,p_blocks,p_alls),
                     dim= c(length(treatments) ,3))

#actually print results
print_treat(results_info,c(1,7))
print_treat(results_info,c(8,14))
print_treat(results_info,c(15-7,17-7))
print_treat(results_info,c(18-7,20-7))





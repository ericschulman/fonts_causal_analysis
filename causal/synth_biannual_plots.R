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
fontfontid<-9

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
  synth.out <- synth(dataprep.out)
  
  
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
################## create a plot ####################################
#####################################################################

# set up relevant years
pre_treatment <- seq(2002,2014.,by=.5)
post_treatment <- seq(2014.5,2017.5,by=.5)
treatment_result <- calculate_treatment(pre_treatment,post_treatment) 
dataprep.out <- treatment_result[[5]]
synth.out <- treatment_result[[4]]

print(synth.out$solution.w)

##------------ plot in levels (treated and synthetic) ---------
png(filename="~/Documents/fonts_replication/plots/synth_plot_inverse50.png")
path.plot(dataprep.res= dataprep.out, synth.res= synth.out, Xlab="Year", Ylab="Inverse Distance", tr.intake=2014.5,Ylim=c(-10,-9),
          Legend = c("Treated","Synthetic"))
dev.off()


#create custom plot against average
average <- (synth.out)
average$solution.w <- 1/(length(controls_id)) * rep(1, length(controls_id))

png(filename="~/Documents/fonts_replication/plots/avg_plot_inverse50.png")
path.plot(dataprep.res= dataprep.out, synth.res= average, Xlab="Year", Ylab="Inverse Distance", tr.intake=2014.5,Ylim=c(-10,-9),
          Legend = c("Treated","Average"))
dev.off()
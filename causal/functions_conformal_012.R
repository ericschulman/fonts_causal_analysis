########################################################################################################

# Generic functions

# Paper: An exact and robust conformal inference approach for counterfactual and synthetic controls

# Authors: V. Chernozhukov, K. Wuthrich, Y. Zhu

# DISCLAIMER: This is a preliminary version. This software is provided "as is" without warranty 
# of any kind, expressed or implied. 

# Questions/error reports: kwuthrich@ucsd.edu

########################################################################################################

# Moving block permutations
moving.block <- function(y1,yJ,T0,T1){
  T01 <- T0+T1
  u.hat = y1 - yJ

  sub.size <- T1
  u.hat <- c(u.hat,u.hat)
  hatM <- NULL
  for (s in 1:(T01)){
    hatM <- cbind(hatM,(1/sqrt(T1))*sum(abs(u.hat[s:(s+sub.size-1)])))
  }
  ind <- T0+1
  p <- mean(hatM>=hatM[ind])
  return(p)
}

# All/iid permutations (use subsample of all permutations)
all <- function(y1,yJ,T0,T1,nperm){
  T01 <- T0+T1
  u.hat = y1 - yJ
  
  post.ind <- ((T0+1):T01)
  pre.ind <- (1:T0)

  test.stat <- (1/sqrt(T1))*sum(abs(u.hat[post.ind]))
  test.stat.p <- NULL
  for (r in 1:nperm){
    ind.p <- sample(1:T01,replace=F)
    u.hat.p <- u.hat[ind.p]
    test.stat.p <- cbind(test.stat.p,((1/sqrt(T1))*sum(abs(u.hat.p[post.ind]))))
  }
  p <- 1/(nperm+1)*(1+sum(test.stat.p>=test.stat))
  return(p)
}

# Confidence interval via test inversion based on moving block permutations
moving.block.ci <- function(y1,yJ,T0,alpha,grid){
  T01 <- T0 + 1
  p.grid <- NULL
  for (g in grid){
    y10 <- y1
    y10[T01] <- y10[T01]-g
    p.grid <- cbind(p.grid,moving.block(y10,yJ,T0,1,M))
  }
  ci <- grid[(p.grid > alpha)] 
  return(ci)
}
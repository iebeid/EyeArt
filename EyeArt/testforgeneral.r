######
#
#  This file contains functions that computes p-values based on u1 
#
# 
#
#####.
#
#  List of functions:
#
#
#
#	transition.x(x) computes transition count matrix N of a sequence x
#
#	transition2.x(x) computes second order transition count matrix of a sequence x
#
#	u1(x) computes u1 statistics for a sequence x0,x1,x2,…,xn.
#
#	classical.u1.pvalue(x)  computes p-value based on asymptotic distribution of u1
#
#
#	MC.u1.pvalue(x, m, m0) computes p-value based on u1 using Monte Carlo sampling of Eulerian trails. 
#
#



## function to compute transition count matrix of a sequence x

transition.x<-function(x) {
	s=length(table(x))
	table(factor(x[1:(length(x)-1)],levels=1:s), factor(x[2:length(x)],levels=1:s))
	}




## function to compute second order transition count matrix of a sequence x

transition2.x<-function(x) {
	s=length(table(x))
	table(factor(x[1:(length(x)-2)],levels=1:s), factor(x[2:(length(x)-1)],levels=1:s), factor(x[3:length(x)], levels=1:s))
	}




## function to compute u1 statistics for a sequence x0,x1,x2,…,xn.

u1<-function(x){
	s=length(table(x))
	tran=transition2.x(x)


loglik1=0
loglik2=0
for(i in 1:s){
    for(j in 1:s){
        for(k in 1:s){
            if(tran[i,j,k]>0){
v1=sum(tran[,j,k])/sum(tran[,j,])
v2=tran[i,j,k]/sum(tran[i,j,])
loglik2=loglik2 + tran[i,j,k]*log(v2)
loglik1=loglik1 + tran[i,j,k]*log(v1)
             }        
        }
    }
}

2*(loglik2-loglik1)
	
}






###  function to compute p-value based on asymptotic distribution of u1

classical.u1.pvalue<-function(x){
n=length(x)
s=length(table(x))	
N=transition.x(x)
stat1=u1(x)
ndf=s*(s-1)^2

lrt=list()
lrt$pval=1-pchisq(stat1,ndf)
lrt$u=stat1
lrt$df=ndf
lrt
}


###  function to compute p-value based on Monte Carlo sampling of Eulerian trails.

MC.u1.pvalue<-function(x,m){
	n=length(x)
	s=length(table(x))
	N=transition.x(x)
	stat=rep(0,m)
	stat[1]=u1(x)


# new sequences will be stroed in y

y=x


for(r in 2:m){

# construct T the T inbound spanning tree

K=N-diag(diag(N),s,s)
startx=x[1]
endx=x[n]
if(endx!=startx)  K[endx,startx]=K[endx,startx]+1
visits=rep(1,s)
visits[endx]=0
T0=matrix(0,s,s)
vertex=endx

while( sum(visits)> 0){
 new=sample(1:s,1,prob=K[,vertex]/sum(K[,vertex]))
 if(visits[new]==1){
  visits[new]=0
  T0[new,vertex]=1
 }
 vertex=new
}

# construct an eulerian tour y

K=N-T0
y[1]=startx
vertex=startx

for( i in 1:(n-1)){
   if( sum(K[vertex,])>0){
      new=sample(1:s,1,prob=K[vertex,]/sum(K[vertex,]))
      y[(i+1)]=new
      K[vertex,new]=K[vertex,new]-1
      vertex=new
   }   
   else{
      new=which(T0[vertex,]==1)
      y[(i+1)]=new
      T0[vertex,new]=0
      vertex=new
   }

}

stat[r]=u1(y)

}

    mc=list()
    mc$stat=stat
    mc$pvalue= 1-rank(stat)[1]/m
    mc

}

main<-function(input){
  ## Application for DNA data from Avery and Henderson (1999).
  
  
  # x=scan("C:/Users/islam/Desktop/dnadata.txt")
  #x<-c(1, 1, 4, 3, 2, 1, 4, 4, 2, 2, 3, 3, 2, 2, 1, 3, 2, 2, 1, 4, 4, 3, 3, 2, 1, 2, 2, 2, 2, 2, 2)
  #x<-c('1', '1', '4', '3', '2', '1', '4', '4', '2', '2', '3', '3', '2', '2', '1', '3', '2', '2', '1', '4', '4', '3', '3', '2', '1', '2', '2', '2', '2', '2', '2')
  #x=scan("C:/Users/islam/Desktop/data.txt")
  x<-input
  #print(x)
  
  #c=classical.u1.pvalue(x)
  
  
  mc=MC.u1.pvalue(x,1000)
  return(mc$pvalue)
  #return(c$pval)
}
Sys.setenv(java.home="/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home")
Sys.setenv(LD_LIBRARY_PATH="/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home/jre/lib/server")
options(java.home="/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home")


library(rJava)
require(XLConnect)
require(irr)

setwd("/Users/arian/Dropbox/research/thesis/code/msc-thesis-code/data/interim/")

wb = loadWorkbook(data_dir + "UMASS-COESAO.xlsx")

########################
# UMASS
d = readWorksheet(wb, sheet = "UMASS", header = TRUE)

# Pearson UMASS
AS<-c("CIRO","LUCAS","MARCELA")
GS<-unique(d$GRUPO)

#sapply(GS,function(g) cor(d$UMASS[d$GRUPO==g],d$CIRO[d$GRUPO==g]))
#sapply(GS,function(g) cor(d$UMASS[d$GRUPO==g],d[d$GRUPO==g,"CIRO"]))

pearsonUMASS<-sapply(AS,
  function(a) 
    sapply(GS,function(g) cor(d$UMASS[d$GRUPO==g],d[d$GRUPO==g,a]))
)
rownames(pearsonUMASS)<-1:6
barplot(t(pearsonUMASS),beside = T,main="UMass vs Cohesion",xlab="Class",ylab="Pearson correlation",
        legend.text=c("A1","A2","A3"),args.legend=list(x="bottomright",bty="n"),cex.axis=1.5,cex.names=1.5,cex.lab=1.5)

# Spearman UMASS
AS<-c("CIRO","LUCAS","MARCELA")
GS<-unique(d$GRUPO)

#sapply(GS,function(g) cor(d$UMASS[d$GRUPO==g],d$CIRO[d$GRUPO==g]))
#sapply(GS,function(g) cor(d$UMASS[d$GRUPO==g],d[d$GRUPO==g,"CIRO"]))

spearmanUMASS<-sapply(AS,
       function(a) 
         sapply(GS,function(g) cor(d$UMASS[d$GRUPO==g],d[d$GRUPO==g,a],method="spearman"))
)
rownames(spearmanUMASS)<-1:6
barplot(t(spearmanUMASS),beside = T,xlab="Class",ylab="Spearman correlation",
        #legend.text=c("A1","A2","A3"),args.legend=list(x="bottomright",bty="n"),
        cex.axis=1.5,cex.names=1.5,cex.lab=1.5)

# Fleiss kappa

k<-unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["value",])
rownames(pearsonUMASS)<-1:6
barplot(k,beside = T,main="Cohesion inter rater agreement",xlab="Class",ylab="Fleiss kappa")
legend(c("A1","A2","A3"))

kglobal<-kappam.fleiss(as.matrix(d[,2:4]))

# Fleiss kappa 3 níveis

d[d==2]<-1
d[d==5]<-4

kappa.UMASS<-data.frame(p.value=round(unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["p.value",]),3),
                      kappa=round(unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["value",]),3))

k<-unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["value",])
barplot(k,beside = T,main="Cohesion inter rater agreement - 3 levels",xlab="Groups",ylab="Fleiss kappa")



########################
# UCI
d = readWorksheet(wb, sheet = "UCI", header = TRUE)

# Pearson UCI
AS<-c("CIRO","LUCAS","MARCELA")
GS<-unique(d$GRUPO)

#sapply(GS,function(g) cor(d$UCI[d$GRUPO==g],d$CIRO[d$GRUPO==g]))
#sapply(GS,function(g) cor(d$UCI[d$GRUPO==g],d[d$GRUPO==g,"CIRO"]))

pearsonUMASS<-sapply(AS,
                     function(a) 
                       sapply(GS,function(g) cor(d$UCI[d$GRUPO==g],d[d$GRUPO==g,a]))
)
rownames(pearsonUMASS)<-1:6
barplot(t(pearsonUMASS),beside = T,main="UCI vs Comprehension",xlab="Groups",ylab="Pearson correlation")

# Spearman UCI
AS<-c("CIRO","LUCAS","MARCELA")
GS<-unique(d$GRUPO)

#sapply(GS,function(g) cor(d$UCI[d$GRUPO==g],d$CIRO[d$GRUPO==g]))
#sapply(GS,function(g) cor(d$UCI[d$GRUPO==g],d[d$GRUPO==g,"CIRO"]))

spearmanUCI<-sapply(AS,
                      function(a) 
                        sapply(GS,function(g) cor(d$UCI[d$GRUPO==g],d[d$GRUPO==g,a],method="spearman"))
)
rownames(spearmanUCI)<-1:6
# main="UCI vs Comprehension"
barplot(t(spearmanUCI),beside = T,xlab="Class",ylab="Spearman correlation",
        #legend.text=c("A1","A2","A3"),args.legend=list(x="bottomright",bty="n"),
        cex.axis=1.5,cex.names=1.5,cex.lab=1.5)

# Fleiss kappa

k<-unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["value",])
barplot(k,beside = T,main="Comprehension inter rater agreement",xlab="Groups",ylab="Fleiss kappa")

d[d==2]<-1
d[d==5]<-4

kappa.UCI<-data.frame(p.value=round(unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["p.value",]),3),
                      kappa=round(unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["value",]),3))

list(UCI=t(kappa.UCI),UMASS=t(kappa.UMASS))

k<-unlist(sapply(GS,function(g) kappam.fleiss(as.matrix(d[d$GRUPO==g,2:4])))["value",])
barplot(k,beside = T,main="Comprehension inter rater agreement - 3 levels",xlab="Groups",ylab="Fleiss kappa")

###########
# ggplotting

require(ggplot2)

data.m <- melt(data, id.vars='Names')
umass.barplot <- ggplot(data=pearsonUMASS,geom="bar")
umass.barplot

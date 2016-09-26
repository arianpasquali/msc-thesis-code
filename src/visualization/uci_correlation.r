Sys.setenv(java.home="/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home")
setwd("/Users/arian/Dropbox/research/thesis/code/msc-thesis-code/data/interim/")

#library(mallet)
library(rJava)
require(XLConnect)
require(irr)


wb = loadWorkbook("human_coherence_evaluation-R.xls")
wb = loadWorkbook("human_cohesion_evaluation-R.xls")

########################
# extrinsic_uci
d = readWorksheet(wb, sheet = "extrinsic_uci", header = TRUE)

AS<-c("ciro","lucas","marcela")
GS<-unique(d$facebook_page_class)

# Spearman Extrinsic UCI
spearmanExtrinsicUCI<-sapply(AS,
                    function(a) 
                      sapply(GS,function(g) cor(d$extrinsic_uci[d$facebook_page_class==g],d[d$facebook_page_class==g,a],method="spearman"))
)
rownames(spearmanExtrinsicUCI)<-1:6
barplot(t(spearmanExtrinsicUCI),beside = T,xlab="Class",ylab="Spearman correlation",
        legend.text=c("A1","A2","A3"),args.legend=list(x="topright",bty="n"),
        main="Extrinsic UCI Inter rater agreement",
        cex.axis=1.5,cex.names=1.5,cex.lab=1.5)


########################
# intrinsic_uci
d = readWorksheet(wb, sheet = "intrinsic_uci", header = TRUE)
AS<-c("ciro","lucas","marcela")
GS<-unique(d$facebook_page_class)
# Spearman Intrinsic UCI
spearmanIntrinsicUCI<-sapply(AS,
                    function(a) 
                      sapply(GS,function(g) cor(d$intrinsic_uci[d$facebook_page_class==g],d[d$facebook_page_class==g,a],method="spearman"))
)

rownames(spearmanIntrinsicUCI)<-1:6
barplot(t(spearmanIntrinsicUCI),beside = T,xlab="Class",ylab="Spearman correlation",
        legend.text=c("A1","A2","A3"),args.legend=list(x="topright",bty="n"),
        main="Intrinsic UCI Inter rater agreement",
        cex.axis=1.5,cex.names=1.5,cex.lab=1.5)


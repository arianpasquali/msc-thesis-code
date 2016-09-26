Sys.setenv(java.home="/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home")
options(java.home="/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home")

setwd("/Users/arian/Dropbox/research/thesis/code/msc-thesis-code/data/interim/")

library(rJava)
require(XLConnect)
require(irr)

wb = loadWorkbook("human_coherence_evaluation-R.xls")
wb = loadWorkbook("human_cohesion_evaluation-R.xls")

########################
# intrinsic_umass
d = readWorksheet(wb, sheet = "intrinsic_umass", header = TRUE)

# Spearman UMASS
AS<-c("ciro","lucas","marcela")
GS<-unique(d$facebook_page_class)

spearmanIntrinsicUMASS<-sapply(AS,
                      function(a) 
                        sapply(GS,function(g) cor(d$intrinsic_umass[d$facebook_page_class==g],d[d$facebook_page_class==g,a],method="spearman"))
)
rownames(spearmanIntrinsicUMASS)<-1:6
barplot(t(spearmanIntrinsicUMASS),beside = T,xlab="Class",ylab="Spearman correlation",
        legend.text=c("A1","A2","A3"),args.legend=list(x="bottomright",bty="n"),
        main="Intrinsic UMass Inter rater agreement",
        cex.axis=1.5,cex.names=1.5,cex.lab=1.5)

########################
# extrinsic_umass
d = readWorksheet(wb, sheet = "extrinsic_umass", header = TRUE)

# Spearman
AS<-c("ciro","lucas","marcela")
GS<-unique(d$facebook_page_class)

spearmanExtrinsicUmass<-sapply(AS,
                      function(a) 
                        sapply(GS,function(g) cor(d$extrinsic_umass[d$facebook_page_class==g],d[d$facebook_page_class==g,a],method="spearman"))
)
rownames(spearmanExtrinsicUmass)<-1:6
barplot(t(spearmanExtrinsicUmass),beside = T,xlab="Facebook Page Class",ylab="Spearman correlation",
        main="Extrinsic UMass Inter rater agreement",
        legend.text=c("A1","A2","A3"),args.legend=list(x="bottomright",bty="n"),
        cex.axis=1.5,cex.names=1.5,cex.lab=1.5)

jpeg('rplot.jpg')
plot(x,y)
dev.off()
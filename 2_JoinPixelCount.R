## This is the second step in prepping NVC group hexagons for inclusion in the NVC map review
## The following joins the count of each pixel, in each 7 sqmi hexagon, for each NVC group and 
## puts individual group hexagon layers with this information into a gdb.
## Code written by Patrick M Feb 2024

library(sf)
library(arcgisbinding)
library(tidyverse)
library(doParallel)

arc.check_product()

# Set the workspace (geodatabase) paths
feature_gdb_path <- "S:/Projects/Ecology/GroupMap_v0pt9/HexCreation/Data/ExtractedGroups.gdb"
table_gdb_path <- "S:/Projects/Ecology/GroupMap_v0pt9/HexCreation/Data/IntermediateTables.gdb"

# Set output workspace
output_gdb <- "S:/Projects/Ecology/GroupMap_v0pt9/HexCreation/Data/ExtractedGroups_wCount.gdb"

# Connect to the geodatabases
feature_gdb <- arc.open(feature_gdb_path)
table_gdb <- arc.open(table_gdb_path)

#feature_gdb@children$FeatureClass #returns list of feature classes
feature_layers<-st_layers(feature_gdb_path) #list layers in the focal gdb
feature_layer_names<-feature_layers$name #return list of names of layers in the focal gdb


table_layers<-st_layers(table_gdb_path) #list layers in the focal gdb
table_layer_names<-table_layers$name #return list of names of layers in the focal gdb

feature_layer_names%in%table_layer_names#checking that names are identical

#single- easier to troubleshoot

for (i in 1:length(feature_layer_names)){
  sel_feature<-st_read(feature_gdb_path, feature_layer_names[i])  #use sf to read in feature layer
  sel_table<-st_read(table_gdb_path, feature_layer_names[i]) #use sf to read in tables (give warning, but works, detects that its a table without geometry)
  feature_w_count<-left_join(sel_feature, sel_table%>%select(cog_id, Count), by="cog_id") #join Counts to feature
  arc.write(file.path(output_gdb, feature_layer_names[i]), feature_w_count, overwrite=T) # write to geodatabase
}


i



detectCores()
cpus <- 4
cl <- makeCluster(cpus)
registerDoParallel(cl)
#i=5





#parallell- faster, harder to figure out an error

foreach(i=1:length(feature_layer_names), .packages=c("arcgisbinding", "sf", "tidyverse")) %dopar% {
  
  arc.check_product() #call arcgisbinding within foreah loop
  sel_feature<-st_read(feature_gdb_path, feature_layer_names[i])  #use sf to read in feature layer
  sel_table<-st_read(table_gdb_path, feature_layer_names[i]) #use sf to read in tables (give warning, but works, detects that its a table without geometry)
  feature_w_count<-left_join(sel_feature, sel_table%>%select(cog_id, Count), by="cog_id") #join Counts to feature
  arc.write(file.path(output_gdb, feature_layer_names[i]), feature_w_count, overwrite=T) # write to geodatabase


}

stopCluster((cl))


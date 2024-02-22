# This is the final step in creating a hexagonized version of the NVC group map to be used in NVC map review
# The purpose of this code is to merge all the individual hexagon layers for each group together, then to add
# all NVC heirarchy information to the final product.

import arcpy, os, re
from arcpy.sa import *
import datetime

current_datetime = datetime.datetime.now()
timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
print("Script started at: " + timestamp)

# Check out any necessary licenses.
arcpy.CheckOutExtension("spatial")

## Input Variables
hexgrid = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\SetupLayers.gdb\nhf_cogs_smoothed_copy" ## UPDATE: with entire 343 hex grid, or extract of area of interest
#WorkingHabitat = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\SetupLayers.gdb\NVC_Groups_v0p9_extract" ## UPDATE: with entire habtiat layer or extract of area of interest
WorkingHabitat = r"S:\Projects\Ecology\GroupMap_v0pt9\Symbology\NVCmap_symbology\IVC_v0p9.gdb\NVC_Groups_v0p9_RemovedPixels_16bitunsig" ## UPDATE: with entire habtiat layer or extract of area of interest

## Set environments
intWorkspace = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\IntermediateTables.gdb" #UPDATE
intOutputs = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\ExtractedGroups.gdb"#UPDATE
finalOutputs = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\FinalOutput.gdb" #UPDATE
arcpy.env.workspace =  r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\SetupLayers.gdb" #UPDATE
arcpy.env.overwriteOutput =  True

 
print("===============================================================================")
print("1. Merging NVC Group hexes together")
print("===============================================================================")

# create list of feature classes
arcpy.env.workspace = intOutputs
group_hexes = arcpy.ListFeatureClasses()

# merge all groups
mergedFCs = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\FinalOutput.gdb\NVC_GroupsbyHex_v0p9"
arcpy.management.Merge(group_hexes, mergedFCs)
print("Hexes merged")

print("===============================================================================")
print("2. Joining NVC hierarchy info to merged hexes")
print("===============================================================================")

# Join NVC info
arcpy.management.JoinField(mergedFCs, "IVC_Code", WorkingHabitat, "IVC_Code", ["Formation_", "Formation1", "Subbiome_c", "Subbiome_N", "Biome_code", "Biome_Name"])
print("hierarchy info joined")

current_datetime = datetime.datetime.now()
timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
print("Script complete at: " + timestamp)

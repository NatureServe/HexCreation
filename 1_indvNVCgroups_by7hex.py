# The purpose of this script is to create a 7sqmi hexagon based version of the NVC group map
# Prior to running this, create a new field in your "WorkingHabitat" raster that combines the NVC group code with the NVC group name
# so that it looks like this example: G749 Sierra-Cascade Red Fir - Mountain Hemlock Forest
#
# This is the first of a series of 3 scripts that should be used in the creation of the hexagonized NVC group map. All three code files can be found
# here: S:\Projects\Ecology\GroupMap_v0pt9\HexCreation
#
# Below outlines the steps that are completed during this script:
# 1.) Tabulate area of habitat codes in each 7 sq mi hex
# 2.) Extract individual tables by habitat code - listing hexids that overlap that habitat
# 3.) Loop through habitat code tables and select hexgrid layer by attribute, feature class to feature class to return
#     hexes where each habitat is found.
#
# NOTE: if you are planning to upload these range maps to AGOL there are additional steps you must complete in ArcGIS Pro
# before publishing
# --- Using batch processing, run the tool Feature Class to Feature Class on each layer, creating a new feature class for each
#     range map in a new gdb. Creating the fcs in ArcGIS pro automatically defaults the display field to be "Display" (created
#     in this script) and will then allow you to publish to AGOL without manually changing the display field for each layer.

import arcpy, os, re
from arcpy.sa import *
import datetime

current_datetime = datetime.datetime.now()
timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
print("Script started at: " + timestamp)

# Check out any necessary licenses.
arcpy.CheckOutExtension("spatial")

## Input Variables
hexgrid = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\SetupLayers.gdb\nhf_cogs_smoothed_clip" ## UPDATE: with entire 343 hex grid, or extract of area of interest
WorkingHabitat = r"S:\Projects\Ecology\GroupMap_v0pt9\Symbology\NVCmap_symbology\IVC_v0p9.gdb\NVC_Groups_v0p9_RemovedPixels_16bitunsig" ## UPDATE: with entire habtiat layer or extract of area of interest
#WorkingHabitat = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\SetupLayers.gdb\NVC_Groups_v0p9_extract"

## Set environments
intWorkspace = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\IntermediateTables.gdb" #UPDATE
intOutputs = r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\ExtractedGroups.gdb"#UPDATE
arcpy.env.workspace =  r"S:\Projects\Ecology\GroupMap_v0pt9\HexCreation\Data\SetupLayers.gdb" #UPDATE
arcpy.env.overwriteOutput =  True

value_list = [] 
with arcpy.da.SearchCursor(WorkingHabitat, ["IVC_Code","IVC_Code_N"]) as cursor:
    for row in cursor:
        value_list.append(row)

col_idx = 1

print("===============================================================================") 
print("Tabulate area of " + str(len(value_list)) + " NVC groups by 7sqmi hex")
print("===============================================================================")

## Tabulate area
TabArea_out = fr"TabArea_GroupinHex_v0p9_test"
arcpy.sa.TabulateArea(hexgrid, "cog_id", WorkingHabitat, "IVC_Code_N", TabArea_out, WorkingHabitat, "CLASSES_AS_ROWS")

print("===============================================================================")
print("1) Looping through and extracting tables of habitats by hex")
print("===============================================================================")

## Get a list of unique habitat codes and extract individual tabulate area tables for each habitat
#TabArea_out = r"S:\Projects\Ecology\GroupMap_v0pt9\QCefforts\Default.gdb\TabArea_GroupinHex" #Un comment this line if you have already ran the tabulate area step above, and comment out the above step
group_codes = set(row[0] for row in arcpy.da.SearchCursor(TabArea_out, "IVC_Code_N"))

for groupcode in group_codes:
    print(f"Working on {groupcode}")
    
    # select hexids for each habitat code
    w_clause = "IVC_Code_N = '{}'".format(groupcode)

    cleaned_string = re.sub(re.compile(r'[^a-zA-Z0-9]'), '', groupcode)

    table_export = arcpy.conversion.TableToTable(TabArea_out, out_path = intWorkspace, out_name =f"{cleaned_string}", where_clause = w_clause)
    print(str(groupcode) + " Table exported")

## Clear memory and selection from loop above
del groupcode
    
print("===============================================================================")
print("2) Looping through habitat tables and creating individual habitat/hex outputs")
print("===============================================================================")

### create a list of tables
arcpy.env.workspace = intWorkspace
habitat_tables = arcpy.ListTables()

# loop through tables and join them to hexgrid
for table in habitat_tables:
    output_name = f"{table}"
    link_field = "cog_id"

    #get a list of hex ids from the table
    hexid = []
    with arcpy.da.SearchCursor(table, [link_field]) as cursor:
        for row in cursor:
            hexid.append(row[0])
            
    # Create a query string to use in the selection
    query = "{} IN ({})".format(link_field, ', '.join(map(str, hexid)))

    # Escape single quotes if the field's data type is string/text
    if arcpy.ListFields(hexgrid, link_field)[0].type == "String":
        query = "{} IN ({})".format(link_field, ', '.join(map(lambda x: f"'{x}'", hexid)))

    print("working on " + table)
    #perform selection based on query
    selected_features = arcpy.SelectLayerByAttribute_management(in_layer_or_view=hexgrid, where_clause = query)

    #create new feature class from selected features
    arcpy.FeatureClassToFeatureClass_conversion(in_features = selected_features, out_path = intOutputs, out_name =output_name)
    print(table + " complete")

## Clear memory and selection from loop above
del table
  
print("===============================================================================")
print("3) Looping through individual habitat outputs and adding descriptive fields")
print("===============================================================================")

# create a list of feature classes
arcpy.env.workspace = intOutputs
group_hexes = arcpy.ListFeatureClasses()

# create function to add spaces before capitalized letters
def add_spaces_to_capitalized(text):
    # Insert spaces before each capitalized letter
    return ''.join([' ' + c if c.isupper() else c for c in text]).lstrip()

# loop through final feature classes and add contextual fields
for fc in group_hexes:
    # Add GroupCode field
    IVC_code_expression = '"{}"'.format(fc[:4])  # Extract the first four characters of the original feature class name
    print(IVC_code_expression)
    arcpy.management.AddField(fc, "IVC_Code", "TEXT")
    arcpy.management.CalculateField(fc, "IVC_Code", IVC_code_expression)
    print("GroupCode field created")

    # Join Group name
    arcpy.management.JoinField(fc, "IVC_Code", WorkingHabitat, "IVC_Code", "IVC_Name")
    print("IVC_Name joined")

    # Clean up - remove unnecessary fields
    arcpy.management.DeleteField(fc, ["InPoly_FID", "SimPgnFlag", "MaxSimpTol", "MinSimpTol"])

current_datetime = datetime.datetime.now()
timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
print("Script complete at: " + timestamp)

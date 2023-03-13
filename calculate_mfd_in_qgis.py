# Get the polygon of segment fault area
fault_layers = QgsProject.instance().mapLayersByName('Fault Segment Area')
faultlayers = fault_layers[0]

#fault_features = faultlayers.getFeatures()
## Get the fault name
#faultname = []
#faultgeom = []
#for fault in fault_features:
#    faultname.append(fault.attributes()[0])
#    faultgeom.append(fault.geometry())

#print(dir(faultlayers))
faultlayers.selectByExpression('"Drawings"=\'seulimum-north\'')
fault_selected = faultlayers.selectedFeatures()[0]
#print(fault_selected)

# Get the earthquake data
eq = QgsProject.instance().mapLayersByName('SUMRELBMKGUSGSDLT40_1906_2022_DEC_INFAULT')

# earthquake point 
eq_layers = eq[0]

res = processing.run(
    "native:selectbylocation", {
    'INPUT':eq_layers,
    'PREDICATE':[6],
    'INTERSECT':QgsProcessingFeatureSourceDefinition(
                'D:/EQ_DATA/RISPRO/SUMATRA/SEGMENT_AREA/segment_fault_area.shp|layername=segment_fault_area', 
                selectedFeaturesOnly=True, 
                featureLimit=-1, 
                geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
    'METHOD':0})

#print(type(res['OUTPUT']))

import pandas as pd

get_feature_in_res = res['OUTPUT'].selectedFeatures()

get_data = []
for f in get_feature_in_res:
    get_data.append(f.attributes())

print(dir(res['OUTPUT']))

df = pd.DataFrame(get_feature_in_res)
df.columns = ['Date', 'EventID', 'Magnitude', 'MagnitudeType', 'DecimalYear', 'DayOfYear', 'X', 'Y', 'Z', 'Longitude', 'Latitude', 'Depth']
print(df.head())
#for sf in selection:
#    faultselected.append(sf)

#print(faultname)
#idx = faultname.index('seulimum-north')
#print(idx)
#get_geom = faultgeom[idx]

# convert to vector layer 

#faultlayers.selectByExpression('"Drawings"=\'seulimum-north\'')

## Get the earthquake data
#eq = QgsProject.instance().mapLayersByName('SUMRELBMKGUSGSDLT40_1906_2022_DEC_INFAULT')
#
## earthquake point 
#eq_layers = eq[0]
#eq_features = eq[0].getFeatures()
#
#eq_geom = []
#for eqf in eq_features:
#    eq_geom.append(eqf.geometry())

# Select by location
#processing.run(
#    "native:selectbylocation",
#    {'INPUT':eq_layers,
#    'PREDICATE':[6],
#    'INTERSECT':fault_selected,
#    'METHOD':0}
#    )

import pandas as pd
from seislib import mfd_mle

# Get the polygon of segment fault area
fault_layers = QgsProject.instance().mapLayersByName('Fault Segment Area')
faultlayers = fault_layers[0]

fault_features = faultlayers.getFeatures()

# Get the fault name
faultname = []
faultgeom = []
aValue, bValue, stdbValue, McValue, MmaxValue = [], [], [], [], []
for fault in fault_features:
#    faultname.append(fault.attributes()[0])
#    faultgeom.append(fault.geometry())
#    selected_faultname = faultname[0]

    #print(dir(faultlayers))
    #faultlayers.selectByExpression('"Drawings"=\'seulimum-north\'')
    faultlayers.selectByExpression('"Drawings"=\'%s\'' % fault.attributes()[0])
    fault_selected = faultlayers.selectedFeatures()[0]
    #print(fault_selected)

    # Get the earthquake data
    eq = QgsProject.instance().mapLayersByName('SUMRELBMKGUSGSDLT40_1906_2022_DEC_INFAULT')

    # earthquake point  layers
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
    
    get_feature_in_res = res['OUTPUT'].selectedFeatures()
    
    if len(get_feature_in_res) != 0:
        try:
            df = pd.DataFrame(get_feature_in_res, columns=['Date', 'EventID', 'Magnitude', 'MagnitudeType', 'DecimalYear', 'DayOfYear', 'X', 'Y', 'Z', 'Longitude', 'Latitude', 'Depth'])
            print(df.head())

            # calculate the MFD
            Mc, max_count_mc, Mmax, a_mle, b_mle, stdbMLE, _, _, _ = mfd_mle.mfd(fault.attributes()[0], df, 'Magnitude')
            faultname.append(fault.attributes()[0])
            aValue.append(a_mle)
            bValue.append(b_mle)
            stdbValue.append(stdbMLE)
            McValue.append(Mc)
            MmaxValue.append(Mmax)
        except pd.errors.EmptyDataError or pandas.errors.IndexingError:
            print('Data is empty')
    else:
        continue

collect_data = {
    'Fault': faultname,
    'a-value': aValue,
    'b-value': bValue,
    'stdbValue': stdbValue,
    'McValue': McValue,
    'MmaxValue':MmaxValue
}

df_mfd = pd.DataFrame(collect_data)
print(df_mfd.head())

# save to csv 
df_mfd.to_excel('D:\EQ_DATA\RISPRO\SUMATRA\ALLCATALOG\ZMAP3\CODE\mfd_sumatra.xlsx', sheet_name='mdf')
    
    
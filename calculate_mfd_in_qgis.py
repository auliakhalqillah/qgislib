import pandas as pd
from openpyxl import load_workbook
from seislib.mfd_mle import mfd

# Get the polygon of segment fault area
#fault_layers = QgsProject.instance().mapLayersByName('Fault Segment Area')
#fault_layers = QgsProject.instance().mapLayersByName('megathrust')
fault_layers = QgsProject.instance().mapLayersByName('Grid_1_degree')
faultlayers = fault_layers[0]

fault_features = faultlayers.getFeatures()

# Get the fault name
faultname = []
faultgeom = []
aValue, bValue, stdbValue, McValue, MmaxValue = [], [], [], [], []
for fault in fault_features:
    #print(dir(faultlayers))
    #faultlayers.selectByExpression('"Drawings"=\'seulimum-north\'')
    # faultlayers.selectByExpression('"Drawings"=\'%s\'' % fault.attributes()[0])
#    faultlayers.selectByExpression('"Region"=\'%s\'' % fault.attributes()[5])
    faultlayers.selectByExpression('"id"=\'%f\'' % fault.attributes()[0])
    fault_selected = faultlayers.selectedFeatures()[0]
#    print('>', fault_selected)

    # Get the earthquake data
    # eq = QgsProject.instance().mapLayersByName('SUMRELBMKGUSGSDLT40_1906_2022_DEC_INFAULT')
#    eq = QgsProject.instance().mapLayersByName('SUMRELBMKGUSGSD20TO50_1906_2022_DEC_INTERFACE')
#    eq = QgsProject.instance().mapLayersByName('SUMRELBMKGUSGSD50~TO300_1906_2022_DEC_INTRASLAB')
    eq = QgsProject.instance().mapLayersByName('SUMRELBMKGUSGS_1906_2022_BGSOURCES')

    # earthquake point  layers
    eq_layers = eq[0]
    
    # 'D:/EQ_DATA/RISPRO/SUMATRA/SEGMENT_AREA/segment_fault_area.shp|layername=segment_fault_area'
#    'D:\SHP\FAULTH_DAN_MEGATRUSHT\megathrust.shp'
    res = processing.run(
        "native:selectbylocation", {
        'INPUT':eq_layers,
        'PREDICATE':[6],
        'INTERSECT':QgsProcessingFeatureSourceDefinition(
                    'D:\EQ_DATA\RISPRO\SUMATRA\AREA_FAULT\BoundaryBoxSumatra\Grid_1_degree.shp', 
                    selectedFeaturesOnly=True, 
                    featureLimit=-1, 
                    geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0})

    #print(type(res['OUTPUT']))
    
    get_feature_in_res = res['OUTPUT'].selectedFeatures()
    
    if len(get_feature_in_res) != 0:
        try:
            df = pd.DataFrame(get_feature_in_res, columns=['Date', 'EventID', 'Magnitude', 'MagnitudeType', 'DecimalYear', 'DayOfYear', 'X', 'Y', 'Z', 'Longitude', 'Latitude', 'Depth'])
            #print(df.head())
    
            # calculate the MFD
            print(fault.attributes()[0])
            proc = mfd(df)
            meanMag, Mc, avalue, bvalue, stdbvalue = proc.mle(doplot=False, savefig=False)
            #Mc, max_count_mc, Mmax, a_mle, b_mle, stdbMLE, _, _, _ = mfd_mle.mfd(fault.attributes()[0], df, 'Magnitude')
            faultname.append(fault.attributes()[0])
            aValue.append(avalue)
            bValue.append(bvalue)
            stdbValue.append(stdbvalue)
            McValue.append(Mc)
            #MmaxValue.append(Mmax)
        except pd.errors.EmptyDataError or pandas.errors.IndexingError:
            pass
#            print('Data is empty')
            
    else:
        continue

collect_data = {
    'Fault': faultname,
    'a-value': aValue,
    'b-value': bValue,
    'stdbValue': stdbValue,
    'McValue': McValue
}

df_mfd = pd.DataFrame(collect_data)
print(df_mfd.head())

# save to csv 
FilePath = 'D:\EQ_DATA\RISPRO\SUMATRA\ALLCATALOG\ZMAP3\CODE\mfd_sumatra.xlsx'
ExcelWorkbook = load_workbook(FilePath)
writer = pd.ExcelWriter(FilePath, engine = 'openpyxl')
writer.book = ExcelWorkbook
df_mfd.to_excel(writer, sheet_name='mdf_bgsources')
writer.save()
writer.close()
#df_mfd.to_excel(, sheet_name='mdf_interface')
    
    
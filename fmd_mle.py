import pandas as pd 
import datetime
import statistics as st
import matplotlib.pyplot as plt 
import numpy as np
from sklearn.linear_model import LinearRegression
import os


class mfd():
    def __init__(self,data):
        self.data = pd.read_csv(data)
    
    def validate(self):
        '''
        Input:

        data : earthquake data (datframe) that consist magnitude field. Please makesure the magnitude field is written as "Magnitude".
        '''

        if "Magnitude" in self.data.columns:
            pass
        else:
            raise ValueError('There is no filed by name Magnitude. Please makesure the magnitude field is written "Magnitude"')
    
    def getMc(self):
        self.Mc = st.mode(self.data['Magnitude'])

        return self.Mc
    
    def getNonCumulative(self):
        self.nonCumData = self.data['Magnitude'].value_counts().reset_index()
        self.nonCumData.columns = ['Magnitude', 'Count']
        self.nonCumData.sort_values(by='Magnitude', inplace=True)
        self.nonCumData['log10(Count)'] = np.log10(self.nonCumData['Count'])

    def getCumulative(self):
        # Calculating the cumulative magnitude
        # # Creating magnitude list
        self.magBin, self.magStart, self.magEnd = 0.1, 0, self.data['Magnitude'].max()+0.1
        self.magCumlist = np.arange(self.magStart,self.magEnd,self.magBin)

        # # Calculate the cumulative magnitude that greater than magnitude_i
        cumlist = []
        for mag in self.magCumlist:
            cumlist.append(self.nonCumData.loc[self.nonCumData['Magnitude'] >= np.round(mag,1), 'Count'].sum())
        cumlist.sort(reverse=True) # sort descending

        # Calculating log10(cumlist)
        log10_cumlist = np.log10(cumlist)

        self.CumData = pd.DataFrame({
            'Magnitude':self.magCumlist,
            'Cumulative':cumlist,
            'log10(Cumulative)':log10_cumlist
            })
        
        self.nMc = self.CumData[self.CumData['Magnitude'] == self.Mc]['Cumulative'].values
        
    def getDataMoreMc(self):
        self.DataMoreMc = self.CumData[self.CumData['Magnitude'] >= self.Mc]

    def bValue(self):
        '''
        Calculating a-value, b-value and standard deviatiion of b-value by using maximum likelihood estimation

        Source:

        Aki, K. (1965) Maximum Likelihood Estimate of b in the Formula log10N=a-bm and Its Confidence Limits. Bulletin of Earthquake Research, 43, 237-239.
        '''
        meanMagnitude = np.mean(self.data[self.data['Magnitude'] >= self.Mc]['Magnitude'])
        self.bvalue = 0.4343/(meanMagnitude - self.Mc)
        self.avalue = np.log10(self.nMc) + (self.bvalue * self.Mc)
        self.stdValue = self.bvalue/np.sqrt(self.nMc)

        return self.avalue, self.bvalue, self.stdValue

    def GutenbergRichter(self):
        '''
        Calculating the model of Gutenberg-Richter's Law log10(N) = a - bM
        '''

        self.log10N = self.avalue - (self.bvalue * self.DataMoreMc['Magnitude'])
        self.lambdaRate = 10**self.log10N
        
    def plotMFD(self):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,5))
        ax.scatter(self.nonCumData['Magnitude'],self.nonCumData['Count'],50, marker='s', edgecolors='k',label='Non-cumulative')
        ax.scatter(self.CumData['Magnitude'],self.CumData['Cumulative'],50,edgecolors='k', label='Cumulative')
        ax.plot(self.Mc, self.nMc,'vk', markersize=10, label=('Mc=%.1f' % self.Mc))
        ax.plot(self.DataMoreMc['Magnitude'],self.lambdaRate,'r',lw=3, label='GR Fitting (MLE)')
        ax.set_xlabel('Magnitude Greater Than ${M_i}$')
        ax.set_ylabel('Number of Earthquake')
        # ax.set_title('Frequency-Magnitude Distribution (a-value:%.2f, b-value:%.2f (+/-%.2f))' % (a_mle,b_mle,stdbMLE))
        ax.set_ylim([1, max(self.CumData['Cumulative'])+(max(self.CumData['Cumulative']))])
        ax.set_yscale('log')
        ax.legend()
        fig.patch.set_facecolor('white')
        plt.grid(which='both', axis='both')

        # if savefigure == True:
            # plt.savefig('Mc_MLE_'+inputfile+'.png')
            # plt.savefig(dirimage + '\\Mc_MLE_'+inputfile+'.png')
        plt.show()

    def mle(self, doplot=False):
        Mc = self.getMc()
        self.getNonCumulative()
        self.getCumulative()
        self.getDataMoreMc()
        aValue, bValue, stdbValue = self.bValue()
        self.GutenbergRichter()
        if doplot == True:
            self.plotMFD()
        else:
            pass

        return Mc, aValue, bValue, stdbValue

# Input file
inputFile = 'eq1999.csv'
proc = mfd(inputFile)
Mc, aValue, bValue, stdbValue = proc.mle(doplot=True)
print(Mc, aValue, bValue, stdbValue)

# image_dir = "D:\\EQ_DATA\\RISPRO\\SUMATRA\\ALLCATALOG\\ZMAP3\\Mc3"

# all_file, all_Mc, all_Mmax, all_aMLE, all_bMLE, all_stdbMLE, all_rMLE = [],[],[],[],[],[],[]
# for file in inputFile:
#     filename = file[:-4]
#     print('File >>:', filename)
#     df = pd.read_csv(file)
#     Mc, Mmax, a_mle, b_mle, stdbMLE, rMLE = cal_fmd(filename, df, 'Magnitude', image_dir)

#     all_file.append(filename)
#     all_Mc.append(Mc)
#     all_Mmax.append(Mmax)
#     all_aMLE.append(a_mle)
#     all_bMLE.append(b_mle)
#     all_stdbMLE.append(stdbMLE)
#     all_rMLE.append(rMLE)

# collect = {
#         'Input':all_file,
#         'Mc':all_Mc,
#         'Mmax': all_Mmax,
#         'a-value (MLE)': all_aMLE,
#         'b-value (MLE)':all_bMLE,
#         'std b-value (MLE)': all_stdbMLE,
#         'R2 (MLE)' : all_rMLE
#     }




import pandas as pd
import numpy as np
import datetime as dt
import readingMergingFile
import categoriseFile
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot
from pandas import ExcelWriter

# needed to able to write the output in the transaction details as one line
pd.set_option('max_colwidth', 400)

# TODO Read all filenams in a folder?
# FILENAMES HERE

# filename = 'BB 06-2015 tm 05-2016.STA'
# fileName = 'BW 06-2015 tm 05-2016-utf.STA'
# filename = 'DEA Q1 .swi'
# fileName = 'Mous 01-06-2015_31-05-2016.940'
# filename = 'DEA Q2 .swi'
# fileName = 'TA_01-06-2015_31-05-2016.940'

path = '/Users/NCJ/Google Drive/20160707 SwishFund/'
inputFolder = 'Input/'
fileName = 'Mous/'
inputName = path + inputFolder + fileName

import os
listOfFiles = os.listdir(inputName)
for i in range(len(listOfFiles)):
    listOfFiles[i] = path+inputFolder+fileName+listOfFiles[i]
inputName = listOfFiles

print('Reading and Merging File')
transactionDf = readingMergingFile.readingMerging(inputName)

# TODO: In the case of .STA files we can easily retrieve IBAN numbers etc. Every interesting parameter starts with a tag. F.e. IBAN: ... BIC: ... etc.

print('Categorising File')
transactionDf = categoriseFile.categorise(transactionDf)

# Output the transactions to excel
outputName = path + 'Output/' + (fileName.split('/')[0])
writer = ExcelWriter(outputName + '.xlsx')
transactionDf.to_excel(writer, 'Sheet1')
writer.save()
print('Succesfully exported transactions to ' + outputName)

#####################################
# ###We will calculate totals and the rest of the financial model here
#####################################


# We will group on a 14 day basis starting at the start of the loan
startDateOfLoan = dt.datetime(2016, 11, 1)  # set the start date of the loan
startDateOfHistory = startDateOfLoan - relativedelta(years=1)
loanDuration = 3  # set the loan duration in months
daysInPeriod = 14  # set the period in days
endDateOfLoan = startDateOfLoan + relativedelta(months=loanDuration)  # TODO look for the correct datetime operation to add 6 months to the start date
endDateOfHistory = startDateOfHistory + relativedelta(months=loanDuration)
# Remove dates for which we don't need to forecast
transactionDf = transactionDf[transactionDf.date < endDateOfHistory]

# Here we define the 'relevant' costs, costs that we take into account
transactionDf['RelevantCosts'] = transactionDf.Costs - transactionDf.Dividend

#Plot the costs and the profit
pyplot.plot(transactionDf[['eMoney','Salaries','Belastingen']])

#Create groups for reporting
transactionDf['periodGroups'] = (transactionDf['date'] - startDateOfHistory).dt.days  # calculate the number of days between loan start date and the transaction date
transactionDf['Period'] = np.floor(transactionDf['periodGroups'] / daysInPeriod)  # get the group number


# Now we group by the period year parameter
ESales = transactionDf.eMoney.groupby(transactionDf['Period']).sum()
Profit = transactionDf.Profit.groupby(transactionDf['Period']).sum()
Costs = transactionDf.RelevantCosts.groupby(transactionDf['Period']).sum()
FreeCash = Profit + Costs
FreeCash.name = 'FreeCash'

NumberOfTransactions = transactionDf['Numb_transactions'].groupby(transactionDf['Period']).sum()
NumberOfTransactions.name = 'NumberOfSalesTransactions'

# TODO Add the correct start and end date in a period based on startdate loan + 14 days
e1 = transactionDf['date'].groupby(transactionDf['Period']).min()
e2 = transactionDf['date'].groupby(transactionDf['Period']).max()

#1 Current cashflow
PeriodAggDf = pd.concat([ESales, Profit, Costs, FreeCash], axis=1)
# testing with the pyplot
#pyplot.plot(PeriodAggDf)


#2 Calculation of the max loan amount
PeriodAggDf = PeriodAggDf[PeriodAggDf.index >=0]  # Only leave actuals needed for the forecast
PeriodAggDf['RiskFactors'] = 0.9-(PeriodAggDf.index)/50

eMoneyPerc = 0.35 # percentage of the emoney used to calculate the max loan amount?
PremiePerc = 0.03  # interest per month
AfsluitProvisiePerc = 0.025

PeriodAggDf['LowerBoundFreeCash'] = np.where(PeriodAggDf.FreeCash > 0, PeriodAggDf.FreeCash * PeriodAggDf.RiskFactors,PeriodAggDf.FreeCash * (1-PeriodAggDf.RiskFactors)+PeriodAggDf.FreeCash)
PeriodAggDf['LowerBoundeMoney'] = PeriodAggDf.eMoney * PeriodAggDf.RiskFactors * eMoneyPerc

BeschikbareCashFlow = max(min(PeriodAggDf.LowerBoundFreeCash.sum(), PeriodAggDf.LowerBoundeMoney.sum()),0)
Voorschot = BeschikbareCashFlow / (1 + PremiePerc * loanDuration)
Premie = Voorschot * PremiePerc * loanDuration
AfsluitProvisie = Voorschot * AfsluitProvisiePerc
TotaalBedrag = Voorschot + Premie
UitTeBetalenBedrag = Voorschot - AfsluitProvisie
print('Uit te betalen bedrag = ', UitTeBetalenBedrag)

# 3 Calculation of the afsplitsingspercentage and the cashflow repayment prognosis
VerwachtePinOmzet = (PeriodAggDf.eMoney * PeriodAggDf.RiskFactors).sum()
AfsplitsingsPercentage = TotaalBedrag / VerwachtePinOmzet
print('Afsplitsingspercentage = ', AfsplitsingsPercentage)
#TODO Cashflowprognose
#new dataframe with the new dates and start end date of periods
ForeCast = pd.DataFrame(PeriodAggDf.eMoney * AfsplitsingsPercentage)
ForeCast['PeriodStartDate'] = startDateOfLoan + pd.TimedeltaIndex(ForeCast.index * daysInPeriod, unit='D')  # Add the number of days to the start date of the loan to define the start period
ForeCast['PeriodEndDate'] = startDateOfLoan + pd.TimedeltaIndex((ForeCast.index+1) * daysInPeriod, unit='D') # Add the number of days since the start of the loan to define the end of a period
ForeCast['EndDateOfLoan'] = endDateOfLoan   # Add the end date as a seperate column to correct the last period to be no longer then the end date of the loan
ForeCast['PeriodEndDate'] = np.where(ForeCast.PeriodEndDate>ForeCast.EndDateOfLoan,ForeCast.EndDateOfLoan,ForeCast.PeriodEndDate) # Correction for the last period
ForeCast['RiskFactors'] = PeriodAggDf['RiskFactors']
if UitTeBetalenBedrag > 0:
    print(ForeCast[['PeriodStartDate','PeriodEndDate','eMoney','RiskFactors']])
    pyplot.plot(ForeCast.eMoney)
else:
    print('No Loan')



######DONE





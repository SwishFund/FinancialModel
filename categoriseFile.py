def categorise(n):
    import pandas as pd
    import numpy as np
    import datetime as dt
    from dateutil.relativedelta import relativedelta
    from matplotlib import pyplot

    transactionDf = n

    #Define the Categories may be handy for easy plotting of the data
    transactionDf['Category'] = np.where(transactionDf.transaction_details2.str.contains('AmericanExpress|AMEX|Betaalautomaat', case=False),'eMoney','Other')
    transactionDf.ix[transactionDf.transaction_details2.str.contains('storting|sealbag', case=False),['Category']]='Storting'
    transactionDf.ix[
        transactionDf.transaction_details2.str.contains('dividend', case=False), ['Category']] = 'Dividend'
    transactionDf.ix[
        transactionDf.transaction_details2.str.contains('salaris|salary', case=False), ['Category']] = 'Salaries'
    transactionDf.ix[
        transactionDf.transaction_details2.str.contains('belasting', case=False), ['Category']] = 'Belastingen'
    transactionDf.ix[
        transactionDf.transaction_details2.str.contains('lening|afbetaling|rente', case=False), ['Category']] = 'LeningenRente'
    transactionDf.ix[
        transactionDf.transaction_details2.str.contains('incasso', case=False), [
            'Category']] = 'AutoIncasso'

    # All incoming (Debit) Transactions
    transactionDf['Profit'] = np.where((transactionDf['status'].str.contains('C', case=False)), transactionDf.amount, 0)
    # Split of the (Debit) Transactions
    transactionDf['eMoney'] = np.where((transactionDf['transaction_details2'].str.contains(
        'AmericanExpress|Amex|Betaalautomaat', case=False) & transactionDf['status'].str.contains('C', case=False)),
                                       transactionDf.amount, 0)
    transactionDf['Amex'] = np.where((
                                     transactionDf['transaction_details2'].str.contains('AmericanExpress', case=False) &
                                     transactionDf['status'].str.contains('C', case=False)), 1, 0)
    transactionDf['Storting'] = np.where((transactionDf['transaction_details2'].str.contains('storting|sealbag',
                                                                                             case=False) &
                                          transactionDf['status'].str.contains('C', case=False)), 1, 0)

    # All outgoing (Credit) Transactions
    transactionDf['Costs'] = np.where((transactionDf['status'].str.contains('D', case=False)), transactionDf.amount, 0)
    # Split of the (Credit) Transactions
    transactionDf['Dividend'] = np.where((transactionDf['transaction_details2'].str.contains('dividend', case=False) &
                                          transactionDf['status'].str.contains('D', case=False)), transactionDf.amount,
                                         0)
    transactionDf['Salaries'] = np.where((transactionDf['transaction_details2'].str.contains('salaris|salary',
                                                                                             case=False) &
                                          transactionDf['status'].str.contains('D', case=False)), transactionDf.amount,
                                         0)
    transactionDf['LoansAndInterest'] = np.where((transactionDf['transaction_details2'].str.contains(
        'lening|afbetaling|rente', case=False) & transactionDf['status'].str.contains('D', case=False)),
                                                 transactionDf.amount, 0)
    transactionDf['Belastingen'] = np.where((transactionDf['transaction_details2'].str.contains('belasting',
                                                                                                case=False) &
                                             transactionDf['status'].str.contains('D', case=False)),
                                            transactionDf.amount, 0)
    transactionDf['AutoIncasso'] = np.where((transactionDf['transaction_details2'].str.contains('incasso', case=False) &
                                             transactionDf['status'].str.contains('D', case=False)),
                                            transactionDf.amount, 0)


    n = transactionDf
    return (n)


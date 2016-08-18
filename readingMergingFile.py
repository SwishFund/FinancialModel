def readingMerging(n):
    import mt940
    import pandas as pd
    import numpy as np
    pd.set_option('max_colwidth', 400)

    columns = ['amount', 'bank_reference', 'currency', 'customer_reference', 'date', 'entry_date', 'extra_details',
               'funds_code', 'id', 'status', 'transaction_details', 'transaction_reference']


    transactionDfTot = pd.DataFrame(columns=columns)

    for i in range(len(n)):

        transactions = mt940.parse(n[i])

        transactionDf = pd.DataFrame(columns=columns)
        for transaction in transactions:
            # need to do this here because of the linesize of the transaction details.
            #  transaction.data['transaction_details'] = " ".join((transaction.data['transaction_details']).split())  # do this to get individual words (there will still be some spaces left in words due to the linebreak in the orginal file)
            transaction.data['transaction_details2'] = "".join((transaction.data[
                                                                'transaction_details']).split())  # do this to append everything to one big line of characters (easier to search for words)
            transactionDf = transactionDf.append(pd.DataFrame(transaction.data, index=[transactions.index(transaction)]))
        frames = [transactionDfTot, transactionDf]
        transactionDfTot = pd.concat(frames)

    transactionDf = transactionDfTot
    transactionDf.sort_values(by='date', axis=0, ascending=True, inplace=True)  # sort the dataframe on the date asc.
    transactionDf = transactionDf.reset_index(drop=True)  # reset the index of the dataframe
    transactionDf = transactionDf.astype(
        str)  # convert all data types explicitly to strings to able to do all data manipulations
    transactionDf = transactionDf.apply(lambda x: x.str.strip())  # strip all leading and trailing spaces
    # TODO Replace all important names that have a space  in their name
    # TODO Replace the replacement of the spaces with a function like ...apply(lamda x: for len(wordname) insert space)
    # TODO Implement a text search over the transaction details. Use tf-idf.
    replacements = {
        'amount': {'<': '', '>': '', 'EUR': ''}
    }
    transactionDf.replace(replacements, regex=True,
                          inplace=True)  # replace certain values in out transactions dataframe
    transactionDf.amount = transactionDf.amount.astype('float')  # convert the amount to a float

    # Dummy variables for interesting features from the transaction details
    # All incoming (Debit) Payments
    transactionDf['C_Betaalautomaat'] = np.where((transactionDf['transaction_details2'].str.contains('BETAALAUTOMAAT',
                                                                                                     case=False) &
                                                  transactionDf['status'].str.contains('C', case=False)), 1, 0)
    transactionDf['C_Amex'] = np.where((transactionDf['transaction_details2'].str.contains('AmericanExpress',
                                                                                           case=False) & transactionDf[
                                            'status'].str.contains('C', case=False)), 1, 0)
    transactionDf['C_Storting'] = np.where((transactionDf['transaction_details2'].str.contains('storting|sealbag',
                                                                                               case=False) &
                                            transactionDf['status'].str.contains('C', case=False)), 1, 0)
    transactionDf['C_Sales'] = np.where((transactionDf['transaction_details2'].str.contains(
        'AmericanExpress|Amex|Betaalautomaat', case=False) & transactionDf['status'].str.contains('C', case=False)), 1,
                                        0)


    # All outgoing (Credit) Payments
    transactionDf['D_Dividend'] = np.where((transactionDf['transaction_details2'].str.contains('dividend', case=False) &
                                            transactionDf['status'].str.contains('D', case=False)), 1, 0)
    transactionDf['D_Salaries'] = np.where((transactionDf['transaction_details2'].str.contains('salaris|salary',
                                                                                               case=False) &
                                            transactionDf['status'].str.contains('D', case=False)), 1, 0)
    transactionDf['D_LoansAndInterest'] = np.where((transactionDf['transaction_details2'].str.contains(
        'lening|afbetaling|rente', case=False) & transactionDf['status'].str.contains('D', case=False)), 1, 0)
    # transactionDf['D_InterestOnLoans'] = (transactionDf['transaction_details2'].str.contains('rente|procent', case=False) & transactionDf['status'].str.contains('D', case=False))
    transactionDf['D_Belastingen'] = np.where((transactionDf['transaction_details2'].str.contains('belasting',
                                                                                                  case=False) &
                                               transactionDf['status'].str.contains('D', case=False)), 1, 0)
    transactionDf['D_AutoIncasso'] = np.where((transactionDf['transaction_details2'].str.contains('incasso',
                                                                                                  case=False) &
                                               transactionDf['status'].str.contains('D', case=False)), 1, 0)
    transactionDf['D_Costs'] = np.where((transactionDf['status'].str.contains('D', case=False)), 1, 0)

    # Datetime manipulations
    transactionDf['date'] = pd.to_datetime(transactionDf['date'])
    transactionDf['month'] = transactionDf['date'].dt.month
    transactionDf['year'] = transactionDf['date'].dt.year
    transactionDf['week'] = transactionDf['date'].dt.week
    transactionDf['monthYear'] = pd.to_datetime(
        transactionDf['year'].astype(str) + '-' + transactionDf['month'].astype(str) + '-01')
    # transactionDf['dividend'] = transactionDf['transaction_details2'].str.contains('dividend', case=False)


    # SPLIT the transaction details after the word aant or aant.
    # TODO apply re function to column, instead of running through column via for-loop

    import numbTransactions
    transactionDf['Numb_transactions'] = numbTransactions.numbTrans(transactionDf['transaction_details2'])
    transactionDf['Numb_transactions'] = transactionDf['Numb_transactions'].astype('float')

    n = transactionDf

    return (n)





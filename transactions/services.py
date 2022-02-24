import transactions.models as tr_models
import pandas as pd
from django.db import transaction

import transactions.models as t_models


class TransactionCRUDService():

    def __init__(self, request):
        self.request = request
    
    def create(self, data, user):
        error_code = 'TR01'
        try:
            transaction = tr_models.Transaction.objects.create(
                amount=data['amount'],
                reference=data['reference'],
                description=data['description'],
                created_by= user,
            )

            if transaction:
                return ('', True, transaction)
            
        except Exception as e:
            print('ERROR {}, creating transaction: {}'.format(error_code, str(e)))
            return ()

        return ('', False, None)

    def delete_transaction(self, transaction):
        try:
            banktransaction = transaction.reference

            banktransaction.status = t_models.BANK_TRANSACTION_STATUS[0][0]
            banktransaction.save()

            transaction.delete()

            return ('', True, None)

        except Exception as e:
            return ('ERROR, deleting share transaction: {}'.format(str(e)),False, transaction)

class BankStatementParserService():
    
    def parse_xlsx_file(self, filename, column_names):
        try:
            xlsx_file = pd.ExcelFile(filename, engine='openpyxl')
            
            df2 = []

            for sheet in xlsx_file.sheet_names:
                
                df = self.parse_xlsx_sheet( xlsx_file, sheet, column_names)

                df2.append(df)
                        
            df2 = pd.concat(df2)
            # contain_values = df2[df2['Tran Particulars'].str.contains('PAY JACQUELINE', na=False)]
            # print(contain_values)
            return df2
        except Exception as e:
            print('ERROR, parsing xlsx file, {}: {}'.format(filename, str(e)))
            return pd.DataFrame()


    def parse_xlsx_sheet(self,xlsx_file, sheet, column_names):

        try:
            df = xlsx_file.parse(sheet)
            column_name_array = df.columns.values.tolist()

            if isinstance(column_name_array, list):

                if column_names == column_name_array:

                    for index, row in df.iterrows():

                        df = self._parse_statement_row(df,row, index, column_names)

                    # df = df[pd.notnull(df[column_names[0]])]
                    df = df.dropna(subset=[column_names[0], column_names[1]])

                    return df

                return pd.DataFrame()

            return pd.DataFrame()

        except Exception as e:
            print('ERROR, parsing xlsx sheet: {}'.format(str(e)))
            return pd.DataFrame()

    def _parse_statement_row(self, df,row, index, column_names):

        try:
            if  pd.isnull(row[column_names[0]]) | pd.isnull(row[column_names[1]]):

                return df

            if index+1 in df.index.values:
                                    
                if pd.isnull(df.loc[index+1, column_names[0]]):
                    # df[column_names[2]][index] = df[column_names[2]][index]+" "+df[column_names[2]][index+1]
                    df.loc[index, column_names[2]] = df[column_names[2]][index]+" "+df[column_names[2]][index+1]
            
            return df
        except Exception as e:
            print('ERROR, parsing bank statement row: {}'.format(str(e)))
            return df

    def create_bank_transaction_db(self, data, column_names, user):
        transactions = []

        try:
            if user.is_staff:

                with transaction.atomic():

                    for index, row in data.iterrows():

                        type, amount_valid, amount = self._get_row_amount(row, column_names)

                        if not amount_valid:
                            continue

                        banktransaction, created = tr_models.BankTransaction.objects.get_or_create(
                            amount = amount,
                            date_trans = row[column_names[0]],
                            date_value = row[column_names[1]],
                            description = row[column_names[2]],
                            balance = row[column_names[6]],
                            defaults={
                                'instrument_id' : row[column_names[3]],
                                'type' : type,
                                'status' : tr_models.BANK_TRANSACTION_STATUS[0][0],
                                'created_by' : user,
                            }
                            
                        )

                        if not created:
                            print('Bank transaction already exists')

                        transactions.append(banktransaction)

                return '',True,transactions

            return 'User permission fails', False, []
        except Exception as e:
            print('ERROR, saving bank statement transaction to db: {}'.format(str(e)))
            return ('Error saving bank statement transaction to db ', False, [])

    
    def _get_row_amount(self, row, column_names):

        if not pd.isnull(row[column_names[4]]):
            amount = row[column_names[4]]
            return (tr_models.TRANSACTION_TYPE[0][0], True, amount)

        elif not pd.isnull(row[column_names[5]]):
            amount = row[column_names[5]]
            return (tr_models.TRANSACTION_TYPE[1][0], True, amount)

        else:
            return ('', False, None)
                        
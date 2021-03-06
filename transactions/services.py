from core.utils import log_error
from expenses.models import Expense
from loans.models import Loan, LoanFormFee, LoanInsuranceFee, LoanInterest, LoanProcessingFee, LoanRepayment
from members.models import Member
from savings.services import SavingCRUDService
from shares.services import ShareCrudService
import transactions.models as tr_models
import pandas as pd
from django.db import transaction
from expenses.services import ExpenseCrudService
import transactions.models as t_models
import logging
logger = logging.getLogger(__name__)


class BaseTransactionService():

    def change_bank_transaction_status(self, bank_transaction, status):
        if bank_transaction:
            bank_transaction.status = status
            bank_transaction.save()
            return True
        return False

class TransactionCRUDService(BaseTransactionService):

    def create_transaction_from_banktransaction(self, uuid, **kwargs):
        
        try:
            banktransaction = tr_models.BankTransaction.objects.get(id=uuid)

            transaction_crud = TransactionCRUDService()

            amount = kwargs['amount'] if ('amount' in kwargs) and not (kwargs['amount'] == '')  else banktransaction.amount
            
            description = kwargs['description'] if ('description' in kwargs) and (not kwargs['description'] == '') else banktransaction.description

            msg, tr_created, transaction = transaction_crud.create_transaction(
                banktransaction,
                amount = amount,
                description = description,
                status= t_models.TRANSACTION_STATUS[1][0],
                created_by = kwargs['created_by']
            )

            if not tr_created:
                return (msg,False, None, None)

            status = t_models.BANK_TRANSACTION_STATUS[1][0]  if amount == banktransaction.amount else t_models.BANK_TRANSACTION_STATUS[2][0]
            self.change_bank_transaction_status(banktransaction, status)

            return '', True, banktransaction, transaction

        except Exception as e:
            msg = "ERROR, creating transaction from bank transaction"
            log_error(msg, e)
            return (msg,False, None, None)

    def create_transaction(self, banktransaction, **kwargs):
        try:
            transaction = tr_models.Transaction.objects.create(
                amount= kwargs['amount'], 
                description=kwargs['description'],
                reference=banktransaction, 
                type=banktransaction.type,
                created_by = kwargs['created_by'],
                status= kwargs['status'],
            )

            if transaction:
                return ('', True, transaction)
            
        except Exception as e:
            msg = "ERROR, saving transaction"
            log_error(msg, e)

        return ('', False, None)

    def delete_transaction(self, transaction):
        try:
            self.change_bank_transaction_status(transaction.reference, t_models.BANK_TRANSACTION_STATUS[0][0])

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

    def create_bank_transaction_db(self, data, column_names, user, **kwargs):
        transactions = []
        try:
            # filename = kwargs['filename'] 
            transactions_created = False
            filename = kwargs['filename']
            bankstatement = self.create_bankstatement(filename=filename, created_by=user) 
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
                            'bankstatement':bankstatement
                        }
                        
                    )
                    transactions_created = transactions_created or created

                    if not created:
                        print('Bank transaction already exists')

                    transactions.append(banktransaction)
                
                if not transactions_created:
                    self.delete_bankstatement_object(bankstatement)

            return '',True,transactions

        except Exception as e:
            self.delete_bankstatement_object(bankstatement)
            log_error('Error, fails to add transactions to db', e)
            return ('Error saving bank statement transaction to db ', False, [])


    def create_bankstatement(self, **kwargs):
        try:
            filename = kwargs['filename']
            created_by = kwargs['created_by']
            bankstatement =t_models.BankStatement.objects.create(filename=filename, created_by=created_by)
            logger.info('Success, bank statement created: {}'.format(filename))
            return bankstatement

        except Exception as e:
            log_error('Error, fails to create bankstatement', e)
            return None

    def delete_bankstatement_object(self, bankstatement):
        try:
            bankstatement.delete()
            return True
        except Exception as e:
            log_error('Error, fails delete bankstatement', e)
            return False


    def _get_row_amount(self, row, column_names):

        if not pd.isnull(row[column_names[4]]):
            amount = row[column_names[4]]
            return (tr_models.TRANSACTION_TYPE[0][0], True, amount)

        elif not pd.isnull(row[column_names[5]]):
            amount = row[column_names[5]]
            return (tr_models.TRANSACTION_TYPE[1][0], True, amount)

        else:
            return ('', False, None)


class BankTransactionAssignmentService(BaseTransactionService):

    def assign_banktransactions_with_action(self, uuids, **kwargs):

        try:
            action = kwargs['action']
            if action == 'assign_to_shares':
                return self.assign_banktransactions_multiple(self.assign_banktransaction_to_share, uuids, **kwargs)

            if action == 'assign_to_expenses':
                return self.assign_banktransactions_multiple(self.assign_banktransaction_to_expense, uuids, **kwargs)

            if kwargs['action'] == 'assign_to_loans':
                return self.assign_banktransactions_multiple(self.assign_banktransaction_to_loan, uuids, **kwargs)

            if action == 'assign_to_savings':
                return self.assign_banktransactions_multiple(self.assign_banktransaction_to_saving, uuids, **kwargs)

            if action == 'assign_to_loanrepayments':
                return self.assign_banktransactions_multiple(self.assign_banktransaction_to_loanrepayment, uuids, **kwargs)

            else:
                return [{'msg':'Not a valid action: '.format(action), 'created':False, 'object':None}]

        except Exception as e:
            print('Error, assigning banktransaction to multipe:{}'.format(str(e)))
            return [{'msg':'Error, assigning banktransaction to multipe:{}'.format(str(e)), 'created':False, 'object':None}]

    def assign_banktransaction_single_with_action(self, action, uuid,  **kwargs):

        try:
            if action == 'assign_to_shares':
                return self.assign_banktransaction_to_share(uuid, **kwargs)

            if action == 'assign_to_expenses':
                return self.assign_banktransaction_to_expense(uuid, **kwargs)

            if action == 'assign_to_savings':
                return self.assign_banktransaction_to_saving(uuid, **kwargs)

            if action == 'assign_to_loanrepayments':
                return self.assign_banktransaction_to_loanrepayment(uuid, **kwargs)

            if action == 'assign_to_loans':
                return self.assign_banktransaction_to_loan(uuid, **kwargs)

            else:
                raise Exception('assigned action can not be executed:{}'.format(action))

        except Exception as e:
            print('Error, assigning banktransaction to multiple:{}'.format(str(e)))
            return 'Error, assigning banktransaction to multiple:{}'.format(str(e)), False, []

    def assign_banktransactions_multiple(self, assign_func,  uuids, **kwargs):
        
        try:
            results = []
            for uuid in uuids:
                msg, created,object = assign_func(uuid, **kwargs)
                results.append({'msg':msg, 'created':created, 'object':object})
                
            return results

        except Exception as e:
            print('ERROR, assign banktransaction to expense multiple: {}'.format(str(e)))
            return ('ERROR,  assign banktransaction to expense multiple', False, None)
 
    def assign_banktransaction_to_expense(self, uuid, **kwargs):

        try:
            transaction_crud = TransactionCRUDService()

            msg, created, banktransaction, transaction = transaction_crud.create_transaction_from_banktransaction(uuid, **kwargs)

            if not created:
                return (msg, False, None)

            if banktransaction.type == 'credit':
                raise Exception('Cannot assign credit transaction to expense')

            expense_crud = ExpenseCrudService()
            msg, ex_created, expense = expense_crud.create_expense_from_transaction(transaction, **kwargs)

            if not created:
                transaction_crud.delete_transaction(transaction)

            return msg, ex_created, expense

        except Exception as e:
            if transaction is not None:
                transaction_crud.delete_transaction(transaction)

            print('ERROR, creating expense: {}'.format(str(e)))
            return ('Error creating expense', False, None)

    def assign_banktransaction_to_share(self, uuid, **kwargs):
        #Retrieving data
        try:
            transaction_crud = TransactionCRUDService()
            
            msg, created, banktransaction, transaction = transaction_crud.create_transaction_from_banktransaction(uuid, **kwargs)

            if not created:
                return (msg, False, None)

            if banktransaction.type == 'debit':
                raise Exception('Cannot assign debit transaction to shares')

            share_crud = ShareCrudService()
            msg, created, share = share_crud.create_share_from_banktransaction(transaction, **kwargs)

            if not created:
                transaction_crud.delete_transaction(transaction) 

            return (msg, created, share)

            
        except Exception as e:

            if transaction is not None:
                transaction_crud.delete_transaction(transaction)

            print('ERROR, creating share: {}'.format(str(e)))
            return ('Error creating share', False, None)

    def assign_banktransaction_to_loanrepayment(self, uuid, **kwargs):
        try:
            transaction_crud = TransactionCRUDService()
            
            msg, created, banktransaction, transaction = transaction_crud.create_transaction_from_banktransaction(uuid, **kwargs)

            if not created:
                return (msg, False, None)

            if transaction.type == 'debit':
                raise Exception('Cannot assign debit transaction to loanrepayment')

            msg, created, loanrepayment = self.create_loanrepayment_from_transaction(transaction, **kwargs)

            if not created:
                transaction_crud.delete_transaction(transaction)   

            return msg, created, loanrepayment

        except Exception as e:
            #Delete Transaction
            if transaction:
                transaction.delete()
            return ('Error creating loan repayment:{}'.format(str(e)), False, None)

    def create_loanrepayment_from_transaction(self, transaction, **kwargs):
        try:
            #Member Id
            loan = Loan.objects.get(id=kwargs['loan'])

            loanrepayment = LoanRepayment.objects.create(
                loan= loan,
                transaction = transaction,
                created_by = kwargs['created_by'],
            )

            return '', True, loanrepayment

        except Exception as e:
            print('Error creating loan repayment:{}'.format(str(e)))
            return ('Error creating loan repayment', False, None)

    def assign_banktransaction_to_loan(self, uuid, **kwargs):
        try:
            transaction_crud = TransactionCRUDService()
            
            msg, created, banktransaction, transaction = transaction_crud.create_transaction_from_banktransaction(uuid, **kwargs)

            if not created:
                return (msg, False, None)

            if banktransaction.type == 'credit':
                raise Exception('Cannot assign credit transaction to loan')

            msg, created, loan = self.create_loan_from_transaction(transaction, **kwargs)

            if not created:
                transaction_crud.delete_transaction(transaction)              

            return msg, created, loan 

        except Exception as e:
            #Delete Transaction
            if transaction is not None:
                transaction.delete()
            return ('error creating loan from bank transaction: {}'.format(str(e)), False, None)

    def create_loan_from_transaction(self, transaction, **kwargs):
        try:
            #Member Id
            member = Member.objects.get(id=kwargs['owner'])

            #Get FormFee
            form_fee = LoanFormFee.objects.filter(status='active', type=kwargs['loan_type']).latest('date_created')

            #Get Interest
            interest = LoanInterest.objects.filter(status='active', type=kwargs['loan_type']).latest('date_created')

            #Get LoanFormFee
            loanprocessing = LoanProcessingFee.objects.filter(status='active').latest('date_created')

            #Get LoanInsuranceFee
            insurance = LoanInsuranceFee.objects.filter(status='active').latest('date_created')

            #Calculate Principle
            principle = ((transaction.amount + form_fee.amount)*100)/98#((bankTransaction.amount + form_fee.amount)*100)/98

            #Calculate forminsurance
            insurance_fee = principle * (insurance.percentage/100)

            #Calculate loanfee
            loan_fee = principle * (loanprocessing.percentage/100)

            #RepaidAmount
            duration = int(kwargs['duration'])
            interest_amount = (principle*(1+ (interest.percentage*duration)))/100

            #Monthly installment
            installment_amount = (principle + interest_amount)/duration

            #form fee amount

            loan = Loan.objects.create(
                type = kwargs['loan_type'],
                principle = principle,
                duration = duration,
                interest_rate = interest.percentage,
                status = 'issued',
                member = member,
                amount_issued = transaction.amount,
                loan_fee = loan_fee,
                insurance_fee = insurance_fee,
                form_fee = form_fee.amount,
                interest_amount = interest_amount,
                transaction = transaction,
                installment_amount = installment_amount,
                created_by = kwargs['created_by']
            )

            return '', True, loan

        except Exception as e:
            print('Error creating loan : {}'.format(str(e)))
            return ('Error creating loan', False, None)

    def assign_banktransaction_to_saving(self, uuid, **kwargs):
        #Retrieving data
        try:
            transaction_crud = TransactionCRUDService()
            
            msg, created, banktransaction, transaction = transaction_crud.create_transaction_from_banktransaction(uuid, **kwargs)

            if not created:
                return (msg, False, None)

            if transaction.type == 'debit':
                raise Exception('Cannot assign debit transaction to saving')

            saving_crud = SavingCRUDService()
            msg, created, saving = saving_crud.create_saving_from_transaction(transaction, **kwargs)

            if not created:
                transaction_crud.delete_transaction(transaction)    

            return msg, created, saving
            
        except Exception as e:
            #Delete Transaction
            if transaction:
                transaction.delete()
            return ('error creating saving from bank transaction', False, None)

    
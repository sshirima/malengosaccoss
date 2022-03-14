from django.contrib import messages
from django import forms
from loans.models import Loan, LoanLimits

from members.models import Member
from .models import BankTransaction, Transaction
from django.core.validators import FileExtensionValidator
import transactions.models as tr_model
from loans.models import LOAN_TYPE
from django.utils.translation import gettext as _

class TransactionCreateForm(forms.ModelForm):
   

    class Meta:
        fields = ['amount', 'reference', 'description']
        model = Transaction

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TransactionCreateForm, self).__init__(*args, **kwargs)


    def clean_reference(self):
        reference = self.cleaned_data['reference']
        if Transaction.objects.filter(reference=reference).exists():
            raise forms.ValidationError("Transaction exists with same reference")
        return reference
    
class TransactionUpdateForm(forms.ModelForm):
   

    class Meta:
        fields = ['amount', 'reference', 'description']
        model = Transaction

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TransactionUpdateForm, self).__init__(*args, **kwargs)

class BankStatementImportForm(forms.Form):
    import_file = forms.FileField(validators=[FileExtensionValidator(['xlsx'])])

class BankTransactionAssignForm(forms.Form):

    assign_scope = forms.CharField(max_length=20, required=True)

    def __init__(self, uuid, *args, **kwargs):
        super(BankTransactionAssignForm, self).__init__(*args, **kwargs)
        self.uuid = uuid
    
    def clean_assign_scope(self):
        assign_scope = self.cleaned_data['assign_scope']

        if not assign_scope in ['shares', 'savings','expenses', 'loans','loanrepayment']:
            raise forms.ValidationError("Not a valid selection: "+assign_scope)

        return assign_scope



    def get_error_messages_from_form(self, request, form):
        if form.errors:
            for field in form:
                for error in field.errors:
                    messages.error(request, '{} : {}'.format(field.label, error))

class BankTransactionMultipleAssignForm(forms.Form):

    action = forms.CharField(max_length=50, required=True)
    selection = forms.CharField(required=True)

    def clean_action(self):
        action = self.cleaned_data['action']
        available_actions = tr_model.get_transaction_assignment_action_all()

        if not action in [*available_actions]:
           raise forms.ValidationError("Action not a valid selection")

        return action

    def clean_selection(self):
        
        selections = self.cleaned_data.get('selection').split(',')

        action = self.cleaned_data.get('action')


        if action == 'assign_to_loans' and len(selections) > 1:
            raise forms.ValidationError("Can not assign more than 1 bank transaction to loans")

        if action in ['assign_to_shares','assign_to_savings','assign_to_loanrepayments'] and len(selections) > 2:
            raise forms.ValidationError("Selection limit reached")

        if action in ['assign_to_expenses'] and len(selections) > 5:
            raise forms.ValidationError("Selection limit reached")

        validation_errors = []

        for transaction in BankTransaction.objects.filter(id__in=selections).only('id', 'status','type'):
        
            if transaction.status == 'assigned':
                # error_message += "Transaction ({}) is already assinged, ".format(transaction, action)
                validation_errors.append(forms.ValidationError(_('%(object)s already assigned: '), code='error1', params={'object':transaction}))
                continue

            type = transaction.type
            actions_by_type = [*tr_model.get_transaction_assignment_action_by_type(type)]
            if action not in actions_by_type:
                validation_errors.append(forms.ValidationError(
                    _('%(object)s transaction type: %(type)s does not match assigments: %(action)s'), 
                    code='error2',
                    params={
                        'object':transaction,
                        'type':type,
                        'action':action,
                        }))

        if validation_errors :
            raise forms.ValidationError(validation_errors)



        return selections

    def get_error_messages_from_form(self, request, form):
        if form.errors:
            for field in form:
                for error in field.errors:
                    messages.error(request, '{} : {}'.format(field.label, error))

class BankTransactionMultipleAssignShareForm(BankTransactionMultipleAssignForm):

    owner = forms.CharField(required=True)
    description = forms.CharField(required=False)

    def clean_owner(self):
        owner = self.cleaned_data['owner']
        if not Member.objects.filter(id=owner).exists():
            raise forms.ValidationError("Owner does not exists")
        return owner

class BankTransactionMultipleAssignSavingForm(BankTransactionMultipleAssignForm):

    owner = forms.CharField(required=True)
    description = forms.CharField(required=False)

    def clean_owner(self):
        owner = self.cleaned_data['owner']
        if not Member.objects.filter(id=owner).exists():
            raise forms.ValidationError("Owner does not exists")
        return owner

class BankTransactionMultipleAssignLoanRepaymentForm(BankTransactionMultipleAssignForm):

    owner = forms.CharField(required=True)
    loan = forms.CharField(required=True)
    description = forms.CharField(required=False)

    def clean_owner(self):
        owner = self.cleaned_data['owner']
        try:
            member = Member.objects.get(id=owner)
        except Member.DoesNotExist as e:
            member = None

        if not member:
            raise forms.ValidationError("Owner does not exists")

        if hasattr(member, 'loan'):
            raise forms.ValidationError("No loan exist for selected member")

        return owner


    def clean_loan(self):
        loan = self.cleaned_data['loan']
        if not Loan.objects.filter(id=loan).exists():
            raise forms.ValidationError("Selected owner not exist")
        return loan

class BankTransactionMultipleAssignLoanForm(BankTransactionMultipleAssignForm):

    owner = forms.CharField(required=True)
    loan_type = forms.CharField(max_length=255,required=True)
    duration = forms.CharField(max_length=10,required=True)
    description = forms.CharField(required=False)

    def clean_owner(self):
        owner = self.cleaned_data['owner']
        if not Member.objects.filter(id=owner).exists():
            raise forms.ValidationError("Owner does not exists")
        return owner

    def clean_loan_type(self):
        loan_type = self.cleaned_data['loan_type']
        loan_types = [x[0] for x in LOAN_TYPE]

        if loan_type not in loan_types:
            raise forms.ValidationError("Loan Type not a valid selection: "+loan_type)

        return loan_type


    def clean_duration(self):

        duration = self.cleaned_data['duration']

        loan_type = self.cleaned_data['loan_type']

        loan_limit = LoanLimits.objects.filter(status='active', type=loan_type).latest('date_created')
        
        if float(duration) > loan_limit.max_duration:
            raise forms.ValidationError("Greater than max limit: {}".format(duration))

        return duration

class BankTransactionMultipleAssignExpenseForm(BankTransactionMultipleAssignForm):

    description = forms.CharField(required=False)


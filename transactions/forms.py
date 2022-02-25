from django import forms
from .models import BankTransaction, Transaction
from django.core.validators import FileExtensionValidator

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

class BankTransactionMultipleAssignForm(forms.Form):

    action = forms.CharField(max_length=20, required=True)

    def __init__(self, *args, **kwargs):
        self.request =  kwargs.pop('request', None)
        super(BankTransactionMultipleAssignForm, self).__init__(*args, **kwargs)
       

    def clean_action(self):
        action = self.cleaned_data['action']

        if not action in ['assign_to_share', 'assign_to_expense']:
           raise forms.ValidationError("Action not a valid selection")

        selections = self.request.POST.getlist('selection')

        error_message = ''

        for transaction in BankTransaction.objects.filter(id__in=selections):

            if transaction.status == 'assigned':
                error_message += "Transaction ({}) is already assinged, ".format(transaction, action)
                
            if transaction.type == 'debit' and action not in ['assign_to_expense', 'assign_to_loan']:
                error_message += "Can not assign transaction ({}) to ({}), ".format(transaction.type, action)

            if transaction.type == 'credit' and action not in ['assign_to_share', 'assign_to_saving']:
                error_message += "Can not assign transaction ({}) to ({}), ".format(transaction.type, action)

        if not error_message == '':
            raise forms.ValidationError(error_message)

        return action
    
    
    # def clean_selection(self):
    #     selection = self.request.POST.getlist('selection')
    #     print(selection)

    #     # if not assign_scope in ['shares', 'savings','expenses']:
    #     #     raise forms.ValidationError("Assign Scope not a valid selection")

    #     #Check if selection are of the same and correct type

    #     #Check if selections are of same and correct status

    #     #Check action and type are allowed


    #     raise forms.ValidationError("Some errors")


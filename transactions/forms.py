from django import forms
from .models import BankTransaction, Transaction
from django.core.validators import FileExtensionValidator
import transactions.models as tr_model

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




from django.utils.translation import gettext as _

class BankTransactionMultipleAssignForm(forms.Form):

    action = forms.CharField(max_length=20, required=True)

    def __init__(self, *args, **kwargs):
        self.request =  kwargs.pop('request', None)
        super(BankTransactionMultipleAssignForm, self).__init__(*args, **kwargs)
       

    def clean_action(self):
        action = self.cleaned_data['action']

        if not action in [*tr_model.get_transaction_assignment_action_all()]:
           raise forms.ValidationError("Action not a valid selection")

        selections = self.request.POST.getlist('selection')

        if len(selections) > 10:
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


from django import forms
from .models import Transaction
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

        if not assign_scope in ['shares', 'savings','expenses']:
            raise forms.ValidationError("Assign Scope not a valid selection")

        return assign_scope


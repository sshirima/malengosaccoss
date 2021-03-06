from django import forms
from members.models import Member
import shares.models as share_models
from .models import Share
from authentication.models import User
from transactions.models import BankTransaction

class ShareCreateForm(forms.ModelForm):

    description = forms.CharField(required=False)
    status = forms.CharField(required=False)
    owner = forms.CharField(required=False)

    class Meta:
        fields = []
        model = Share


    def clean_reference(self):
        reference = self.cleaned_data['reference']
        bank_transaction = BankTransaction.objects.get(id=reference)
        if not bank_transaction:
            raise forms.ValidationError("Transaction reference does not exist")

        if hasattr(bank_transaction, 'transaction'):
            raise forms.ValidationError("Bank transaction already assigned")

        if not bank_transaction.type == 'credit':
            raise forms.ValidationError("Bank transaction reference type must be of type credit")
        
        return reference

    def clean_owner(self):
        id = self.cleaned_data['owner']
        if not Member.objects.filter(id=id).exists():
            raise forms.ValidationError("Owner does not exists: "+id)
        return id

class ShareUpdateForm(forms.ModelForm):
    description = forms.CharField(max_length=255,required=False)

    class Meta:
        fields = []
        model = Share

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ShareUpdateForm, self).__init__(*args, **kwargs)


class ShareAuthorizationForm(forms.Form):
    status = forms.CharField(max_length=20, required=True)

    def clean_status(self):
        status = self.cleaned_data['status']
        for stats in share_models.SHARE_STATUS:
            if status in stats:
                return status
        raise forms.ValidationError("Status not a valid format")
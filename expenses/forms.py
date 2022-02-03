from django import forms
from authentication.models import User
from expenses.models import Expense
from transactions.models import BankTransaction


class ExpenseUpdateForm(forms.ModelForm):
    description = forms.CharField(max_length=255,required=False)

    class Meta:
        fields = []
        model = Expense

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)


class ExpenseCreateForm(forms.ModelForm):

    description = forms.CharField(required=False)
    status = forms.CharField(required=False)
    owner = forms.CharField(required=False)

    class Meta:
        fields = []
        model = Expense

    def __init__(self, uuid, *args, **kwargs):
        self.uuid = uuid
        super(ExpenseCreateForm, self).__init__(*args, **kwargs)


    # def clean_owner(self):
    #     email = self.cleaned_data['owner']
    #     if not User.objects.filter(email=email).exists():
    #         raise forms.ValidationError("Owner does not exists: "+email)
    #     return email

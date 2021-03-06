from django import forms
from authentication.models import User
from members.models import Member
from savings.models import Saving
from transactions.models import BankTransaction


class SavingUpdateForm(forms.ModelForm):
    description = forms.CharField(max_length=255,required=False)

    class Meta:
        fields = []
        model = Saving

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(SavingUpdateForm, self).__init__(*args, **kwargs)


class SavingCreateForm(forms.ModelForm):

    description = forms.CharField(required=False)
    status = forms.CharField(required=False)
    owner = forms.CharField(required=False)

    class Meta:
        fields = []
        model = Saving

    def __init__(self, uuid, *args, **kwargs):
        self.uuid = uuid
        super(SavingCreateForm, self).__init__(*args, **kwargs)


    def clean_owner(self):
        id = self.cleaned_data['owner']
        if not Member.objects.filter(id=id).exists():
            raise forms.ValidationError("Owner does not exists: "+id)
        return id


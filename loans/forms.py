from django import forms
from members.models import Member

from loans.models import Loan, LoanLimits
import loans.models as l_models
from transactions.models import BankTransaction

class LoanCreateFromBankTransactionForm(forms.ModelForm):

    transaction_id = forms.CharField(max_length=50,required=True)
    member = forms.CharField(max_length=50,required=True)
    loan_type = forms.CharField(max_length=255,required=True)
    duration = forms.CharField(max_length=10,required=True)

    class Meta:
        fields = []
        model = Loan

    def clean_member(self):
        member_id = self.cleaned_data['member']
        if not Member.objects.filter(id=member_id, is_active = True).exists():
            raise forms.ValidationError("Member does not exists or is not active: "+member_id)
        return member_id


    def clean_transaction_id(self):
        transaction = self.cleaned_data['transaction_id']
        
        if not BankTransaction.objects.filter(id=transaction).exists():
            raise forms.ValidationError("BankTransaction does not exists: "+transaction)
            
        return transaction

    def clean_loan_type(self):
        loan_type = self.cleaned_data['loan_type']
        loan_types = [x[0] for x in l_models.LOAN_TYPE]

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

class LoanRepaymentMemberSelectForm(forms.Form):

    member = forms.CharField(max_length=50,required=True)

    def clean_member(self):
        member_id = self.cleaned_data['member']
        member = Member.objects.filter(id=member_id, is_active = True)

        if not member.exists():
            raise forms.ValidationError("Does not exists or is not active: "+member_id)

        if hasattr(member.first(), 'loan'):
            raise forms.ValidationError("No loan exist for member: "+member_id)

        return member_id

class LoanRepaymentCreateForm(forms.Form):

    loan = forms.CharField(max_length=50,required=True)
    transaction = forms.CharField(max_length=50,required=True)

    def clean_loan(self):
        loan_id = self.cleaned_data['loan']
        loan = Loan.objects.filter(id=loan_id)

        if not loan.exists():
            raise forms.ValidationError("Does not exists : "+loan_id)

        return loan_id
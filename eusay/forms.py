from django import forms
from eusay.models import Proposal

class ProposalForm (forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'actionDescription', 'backgroundDescription', 'beliefsDescription']
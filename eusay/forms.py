from django import forms
from eusay.models import Proposal, Comment

class ProposalForm (forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "id": "title", "maxlength": "100", "placeholder": "The title of your policy - be as descriptive as possible."}))
    actionDescription = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": "6", "id": "actionDescription", "maxlength": "2000"}))
    backgroundDescription = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": "6", "id": "backgroundDescription", "maxlength": "2000"}))
    beliefsDescription = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": "6", "id": "beliefsDescription", "maxlength": "2000"}))
    class Meta:
        model = Proposal
        fields = ['title', 'actionDescription', 'backgroundDescription', 'beliefsDescription']

class CommentForm (forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": "3", "maxlength": "499", "placeholder": "Add a comment"}))
    class Meta:
    	model = Comment
    	fields = ['text']

class HideCommentActionForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textare(attrs={"class":"form-control", "rows":"3", "maxlength":"1999", "placeholder":"Why should this comment be removed?"}))
    class Meta:
        model = HideCommentAction
        fields = ['reason']

class HideProposalActionForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textare(attrs={"class":"form-control", "rows":"3", "maxlength":"1999", "placeholder":"Why should this proposal be removed?"}))
    class Meta:
        model = HideProposalAction
        fields = ['reason']

from django import forms

from proposals.models import Proposal, Response
from core.utils import better_slugify, contains_swear_words
from tags.models import Tag

class ProposalForm (forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'text', 'tags']

    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",
                                                          "id": "title",
                                                          "maxlength": "100",
                                                          "placeholder": "Please be descriptive."}))
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control",
                                                        "maxlength": "6000",
                                                        "id": "text",
                                                        "onkeyup": "countChars(this, 6000)"}))
    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"id": "tag-list"}),
        queryset=Tag.objects.all(),
        required=False)

    def clean_title(self):
        cleaned_title = self.cleaned_data["title"]
        # don't allow swear words
        if contains_swear_words(cleaned_title):
            raise forms.ValidationError("Proposals cannot contain swear words.")
        return cleaned_title

    def clean_text(self):
        cleaned_text = self.cleaned_data["text"]
        # don't allow swear words
        if contains_swear_words(cleaned_text):
            raise forms.ValidationError("Proposals cannot contain swear words.")
        return cleaned_text

class AmendmentForm (forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",
                                                          "id": "title",
                                                          "maxlength": "100",
                                                          "placeholder": "Please be descriptive."}))
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control",
                                                        "maxlength": "6000",
                                                        "id": "text",
                                                        "onkeyup": "countChars(this, 6000)"}))

    def set_initial(self, proposal_title, proposal_text):
        self.initial['title'] = proposal_title
        self.initial['text'] = proposal_text

class ResponseForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control",
               "rows": "3",
               "placeholder": "Enter your official response to "
                              "this proposal here."}))

    class Meta:
        model = Response
        fields = ['text']

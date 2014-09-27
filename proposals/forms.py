from datetime import datetime

from django import forms

from proposals.models import Proposal, Response
from core.utils import contains_swear_words
from tags.models import Tag
from student_councils.models import StudentCouncil


class ProposalForm(forms.ModelForm):
    """
    Form for proposal submission including ``title``, ``text`` and
    ``tags`` fields.
    """

    title = forms.CharField(widget=forms.TextInput(attrs={"class":
                                                          "form-control",
                                                          "id": "title",
                                                          "maxlength": "100",
                                                          "placeholder":
                                                          "Please be"
                                                          " descriptive."}))
    text = forms.CharField(widget=forms.Textarea(attrs={"class":
                                                        "form-control",
                                                        "maxlength": "6000",
                                                        "id": "text",
                                                        "onkeyup":
                                                        "countChars"
                                                        "(this, 6000)"}))
    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"id": "tag-list"}),
        queryset=Tag.objects.all(),
        required=False)

    def clean_title(self):
        """
        Get the cleaned proposal title if it contains no swear words,
        otherwise raise an excption.

        :returns:  Cleaned ``title`` if it contains no swear words
        :rtype:    string
        :raises:   :mod:`django.forms.ValidationError`
        """
        cleaned_title = self.cleaned_data["title"]
        # don't allow swear words
        if contains_swear_words(cleaned_title):
            raise forms.ValidationError("Proposals cannot contain"
                                        " swear words.")
        return cleaned_title

    def clean_text(self):
        """
        Get the cleaned proposal text if it contains no swear words,
        otherwise raise an exception.

        :returns:  Cleaned ``title`` if it contains no swear words
        :rtype:    string
        :raises:   :mod:`django.forms.ValidationError`
        """
        cleaned_text = self.cleaned_data["text"]
        # don't allow swear words
        if contains_swear_words(cleaned_text):
            raise forms.ValidationError("Proposals cannot contain"
                                        " swear words.")
        return cleaned_text

    class Meta:
        model = Proposal
        fields = ['title', 'text', 'tags']


class AmendmentForm(forms.Form):
    """
    Form for suggesting proposal amendments including ``title`` and ``text``
    fields.
    """
    title = forms.CharField(widget=forms.TextInput(attrs={"class":
                                                          "form-control",
                                                          "id": "title",
                                                          "maxlength": "100",
                                                          "placeholder":
                                                          "Please be"
                                                          "descriptive."}))
    text = forms.CharField(widget=forms.Textarea(attrs={"class":
                                                        "form-control",
                                                        "maxlength": "6000",
                                                        "id": "text",
                                                        "onkeyup":
                                                        "countChars"
                                                        "(this, 6000)"}))

    def set_initial(self, proposal_title, proposal_text):
        """
        Set the initial value of form fields before rendering.

        :param proposal_title: Initial title in form
        :type proposal_title:  string
        :param proposal_text:  Initial text in form
        :type proposal_text:   string
        """
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


class ProposalStatusForm(forms.ModelForm):
    """
    Form for changing the status of a proposal.
    """
    status = forms.ChoiceField(choices=Proposal.PROPOSAL_STATUS_CHOICES,
                               widget=forms.Select(
                                   attrs={"class": "form-control"}))
    student_council = forms.ModelChoiceField(
        StudentCouncil.objects.filter(datetime__gt=datetime.now()),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False)

    class Meta:
        model = Proposal
        fields = ["status", "student_council"]

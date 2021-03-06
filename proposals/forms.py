from datetime import datetime

from django import forms

from core.utils import contains_swear_words
from proposals.models import Proposal, Response
from student_councils.models import StudentCouncil
from tags.models import Tag
from core.forms import SwearFilteredModelForm

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
                                                        "(this, 6000)",
                                                        "oninput":
                                                        "this.editor.update()"}))
    school_tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Tag.objects.filter(group=1),
        required=False)
    liberation_tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Tag.objects.filter(group=2),
        required=False)
    other_tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Tag.objects.filter(group=3),
        required=False)

    def clean_school_tags(self):
        """
        Get the cleaned school tags if there are no more than
        4 of them

        :returns:   Cleaned school tags of length < 4
        :raises:   :mod:`django.forms.ValidationError`
        """
        cleaned_school_tags = self.cleaned_data["school_tags"]
        if len(cleaned_school_tags) > 4:
            raise forms.ValidationError("Please add no more than "
                                        "four school tags")
        return cleaned_school_tags

    def clean_liberation_tags(self):
        """
        Get the cleaned liberation tags if there are no more than
        4 of them

        :returns:   Cleaned liberation tags of length < 4
        :raises:   :mod:`django.forms.ValidationError`
        """
        cleaned_liberation_tags = self.cleaned_data["liberation_tags"]
        if len(cleaned_liberation_tags) > 4:
            raise forms.ValidationError("Please add no more than "
                                        "four liberation group tags")
        return cleaned_liberation_tags

    def clean_other_tags(self):
        """
        Get the cleaned general tags if there are no more than
        4 of them

        :returns:   Cleaned general tags of length < 4
        :raises:   :mod:`django.forms.ValidationError`
        """
        cleaned_other_tags = self.cleaned_data["other_tags"]
        if len(cleaned_other_tags) > 4:
            raise forms.ValidationError("Please include no more than "
                                        "four general tags")
        return cleaned_other_tags

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
        fields = ['title', 'text']


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


class ResponseForm(SwearFilteredModelForm):
    text = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control",
               "rows": "3",
               "placeholder": "What does EUSA think of the proposal? What "
                              "will they do about it, or what has been done so far?"}))

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

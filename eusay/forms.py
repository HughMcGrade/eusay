import re

from django import forms
from django.conf import settings

from .models import Proposal, Comment, HideProposalAction, \
    HideCommentAction, User, CommentReport, ProposalReport, Tag
from .utils import better_slugify


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
                                                        "onkeyup": "countChars(this)"}))
    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"id": "tag-list"}),
        queryset=Tag.objects.all(),
        required=False)


class CommentForm (forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control",
                                                        "rows": "3",
                                                        "maxlength": "500"}))

    class Meta:
        model = Comment
        fields = ['text']


class HideCommentActionForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control",
                                                          "rows":"3",
                                                          "maxlength":"1999",
                                                          "placeholder":"Why should this comment be hidden?"}))

    class Meta:
        model = HideCommentAction
        fields = ['reason']


class HideProposalActionForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control",
                                                          "rows":"3",
                                                          "maxlength":"1999",
                                                          "placeholder":"Why should this proposal be hidden?"}))

    class Meta:
        model = HideProposalAction
        fields = ['reason']

class CommentReportForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control",
                                                          "rows":"3",
                                                          "maxlength":"1999",
                                                          "placeholder":"Why should this comment be hidden?"}))

    class Meta:
        model = CommentReport
        fields = ['reason']


class ProposalReportForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control",
                                                          "rows":"3",
                                                          "maxlength":"1999",
                                                          "placeholder":"Why should this proposal be hidden?"}))

    class Meta:
        model = ProposalReport
        fields = ['reason']


class UserForm(forms.ModelForm):
    # Name = CharField
    # hasProfile = BooleanField
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("current_user")
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields["name"] = forms.CharField(required=False,
                                              initial=user.name,
                                              widget=forms.TextInput(
                                              attrs={"placeholder": "New username",
                                                     "class": "form-control"}))
        has_profile_attrs={"id": "hasProfileCheckbox"}
        if user.hasProfile:
            has_profile_attrs["checked"] = ""
        self.fields['hasProfile'] = forms.BooleanField(required=False,
                                    initial=False,
                                    widget=forms.CheckboxInput(attrs=has_profile_attrs))

    class Meta:
        model = User
        fields = ["name", "hasProfile"]

    def clean_name(self):
        cleaned_name = self.cleaned_data["name"]

        # don't allow blank usernames
        if cleaned_name == "":
            raise forms.ValidationError("Username cannot be blank.")

        # don't allow usernames where the slug already exists
        slug = better_slugify(cleaned_name)
        if User.objects.filter(slug=slug).exists():
            raise forms.ValidationError("User slug already exists.")

        # don't allow swear words
        words = re.sub("[^\w]", " ", self.cleaned_data["name"]).split()
        bad_words = [w for w in words if w.lower() in settings.PROFANITIES_LIST]
        if bad_words:
            raise forms.ValidationError("Username cannot contain swear words.")

        return cleaned_name
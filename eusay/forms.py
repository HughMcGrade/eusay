from django import forms

from .models import Proposal, Comment, HideAction, User, Report, Tag
from .utils import better_slugify, contains_swear_words


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


class CommentForm (forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control",
                                                        "rows": "3",
                                                        "maxlength": "500"}))

    class Meta:
        model = Comment
        fields = ['text']

class HideActionForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control",
                                                          "rows":"3",
                                                          "maxlength":"1999",
                                                          "placeholder":"Why should this content be hidden?"}))

    class Meta:
        model = HideAction
        fields = ['reason']

class ReportForm (forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control",
                                                          "rows":"3",
                                                          "maxlength":"1999",
                                                          "placeholder":"Why should this content be hidden?"}))

    class Meta:
        model = Report
        fields = ['reason']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "hasProfile"]

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

    def clean_name(self):
        cleaned_name = self.cleaned_data["name"]

        # don't allow blank usernames
        if cleaned_name == "":
            raise forms.ValidationError("Username cannot be blank.")

        # don't allow usernames where the slug already exists
        slug = better_slugify(cleaned_name)
        if User.objects.exclude(sid=self.instance.sid).filter(slug=slug).exists():
            raise forms.ValidationError("User slug already exists.")

        # don't allow swear words
        if contains_swear_words(cleaned_name):
            raise forms.ValidationError("Username cannot contain swear words.")

        return cleaned_name

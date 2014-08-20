from django import forms

from .models import Proposal, Comment, HideAction, Report, Tag, Response, User
from .utils import better_slugify, contains_swear_words

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "hasProfile"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("current_user")
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields["username"] = \
            forms.CharField(required=False,
                            initial=user.username,
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
        # TODO: is this necessary when using django's user system?
        cleaned_name = self.cleaned_data["username"]

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

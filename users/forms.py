from slugify import slugify

from django import forms

from users.models import User
from core.utils import contains_swear_words, is_sid
from tags.models import Tag

def check_username(form, user):
    """
    This function takes a form as input, and raises an error if
    the username is blank, if the username slug already exists (and therefore
    if the username already exists), and if the username contains swear words.
    :param username: the form with the username to be checked
    :return: the same username, if it passes all checks
    """
    cleaned_username = form.cleaned_data["username"]

    # don't allow blank usernames
    if cleaned_username == "":
        raise forms.ValidationError("Username cannot be blank.")

    # don't allow usernames where the slug already exists
    slug = slugify(cleaned_username, max_length=100)
    if User.objects.exclude(sid=user.sid).filter(slug=slug)\
                                                  .exists():
        raise forms.ValidationError("User slug already exists.")

    # don't allow swear words
    if contains_swear_words(cleaned_username):
        raise forms.ValidationError("Username cannot contain swear words.")

    # don't allow SIDs as username
    if is_sid(cleaned_username):
        raise forms.ValidationError("Username cannot be a student ID.")

    return cleaned_username


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username",
                  "hasProfile",
                  "subscribed_to_notification_emails"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields["username"] = \
            forms.CharField(required=False,
                            widget=forms.TextInput(
                                attrs={"placeholder": "New username",
                                       "class": "form-control"}))

        self.fields['hasProfile'] = \
            forms.BooleanField(required=False)

        self.fields['subscribed_to_notification_emails'] = \
            forms.BooleanField(required=False)

    def clean_username(self):
        return check_username(self, self.instance)


class NewUserForm(forms.Form):

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
    username = forms.CharField(
            required=True,
            widget=forms.TextInput(attrs={"class": "form-control",
                                          "placeholder": "Please enter a username."}))

    def __init__(self, user, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_username(self):
        return check_username(self, self.user)

class UserAdminForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ["password"]

from django import forms

from users.models import User
from core.utils import better_slugify, contains_swear_words

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

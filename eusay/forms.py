from django import forms
from eusay.models import Proposal, Comment, HideProposalAction, \
    HideCommentAction, User, CommentReport, ProposalReport


class ProposalForm (forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",
                                                          "id": "title",
                                                          "maxlength": "100",
                                                          "placeholder": "The title of your policy - "
                                                                         "be descriptive."}))
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control",
                                                        "maxlength": "6000",
                                                        "id": "text",
                                                        "onkeyup": "countChars(this)"}))


    class Meta:
        model = Proposal
        fields = ['title', 'text']


class CommentForm (forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control",
                                                        "rows": "3",
                                                        "maxlength": "499",
                                                        "placeholder": "Add a comment"}))

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
        if cleaned_name == "":
            raise forms.ValidationError("Username cannot be blank.")
        if User.objects.exclude(sid=self.instance.sid).filter(name=cleaned_name).exists():
            raise forms.ValidationError("Username %s already exists." % cleaned_name)
        return cleaned_name

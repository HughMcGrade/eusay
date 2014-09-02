from django import forms

from moderation.models import HideAction, Report


class HideActionForm(forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":
                                                          "form-control",
                                                          "rows": "3",
                                                          "maxlength": "1999",
                                                          "placeholder":
                                                          "Why should this "
                                                          "content be "
                                                          "hidden?"}))

    class Meta:
        model = HideAction
        fields = ['reason']


class ReportForm(forms.ModelForm):
    reason = forms.CharField(widget=forms.Textarea(attrs={"class":
                                                          "form-control",
                                                          "rows": "3",
                                                          "maxlength": "1999",
                                                          "placeholder":
                                                          "Why should this "
                                                          "content be "
                                                          "hidden?"}))

    class Meta:
        model = Report
        fields = ['reason']

from django import forms

from comments.models import Comment
from core.forms import SwearFilteredModelForm

class CommentForm(SwearFilteredModelForm):
    text = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control",
               "rows": "3",
               "maxlength": "6000",
               "onkeyup": "countChars(this, 6000)"}))

    class Meta:
        model = Comment
        fields = ['text']

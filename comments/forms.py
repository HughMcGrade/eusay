from django import forms

from comments.models import Comment

class CommentForm (forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control",
                "rows": "3",
                "maxlength": "1000",
                "onkeyup": "countChars(this, 1000)"}))

    class Meta:
        model = Comment
        fields = ['text']


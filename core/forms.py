from django import forms

from core.utils import replace_bad_words


class SwearFilteredModelForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(SwearFilteredModelForm, self).clean()
        for field in self.fields:
            value = cleaned_data[field]
            if isinstance(value, str):
                cleaned_data[field] = replace_bad_words(value)
        return cleaned_data

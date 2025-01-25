from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published', 'created_at')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date < timezone.now():
            raise ValidationError(
                'Дата публикации не может быть раньше сегодняшней'
            )
        return pub_date

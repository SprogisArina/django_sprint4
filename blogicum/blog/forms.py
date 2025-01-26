from django import forms

from .models import Comment, Post 


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published', 'created_at')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

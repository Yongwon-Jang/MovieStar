from django import forms
from django.forms.fields import TimeField
from django.forms.widgets import TextInput
from .models import Review, Comment


class ReviewForm(forms.ModelForm):
    rank = forms.IntegerField(min_value=0, max_value=10)
    class Meta:
        model = Review
        fields = ['title', 'rank', 'content']
        # fields = '__all__'


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                # 'class': "input-group-text",
                'placeholder': '댓글을 입력해 주세요.'
            }
        )
    )
    class Meta:
        model = Comment
        exclude = ['review', 'user']

class SearchForm(forms.ModelForm):
    
    class Meta:
        model = Review
        fields = ['movie_title']

        # fields = '__all__'

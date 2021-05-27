from django import forms
from .models import LineReview,Movie


class LineReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=0, max_value=10)
    class Meta:
        model = LineReview
        fields = ['content','rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control'})
        }


# class SearchForm(forms.ModelForm):
    
#     class Meta:
#         model = Movie
#         fields = ['movie_title']

        # fields = '__all__'
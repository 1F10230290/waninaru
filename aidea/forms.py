from django import forms
from .models import DesignIdea

class DesignIdeaForm(forms.ModelForm):
    class Meta:
        model = DesignIdea
        fields = ['image', 'description']

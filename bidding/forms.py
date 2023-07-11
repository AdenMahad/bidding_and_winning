from django import forms
from .models import Category, Item, Bid

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'starting_bid', 'image', 'category']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
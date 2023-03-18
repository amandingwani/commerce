from django.forms import ModelForm

from .models import Listing

# Create the listing form class
class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['name','description','original_price','category','image']
        labels = {
            "name": "Title",
            "original_price": "Starting Bid"
        }
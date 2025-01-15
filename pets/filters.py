import django_filters
from .models import Pet, Booking
from django import forms


class PetFilter(django_filters.FilterSet):
    class Meta:
        model = Pet
        fields = {
            "name": ["icontains"],
            "pet_type": ["exact"],
            "medication_required": ["exact"],
            "owner__name": ["icontains"],
            "household__name": ["icontains"],
        }


class BookingFilter(django_filters.FilterSet):
    start_date_range = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr="gt",
        widget=forms.DateInput(attrs={'class': '', 'type': 'date'})
    )

    end_date_range = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr="lt",
        widget=forms.DateInput(attrs={'class': '', 'type': 'date'})
    )
    class Meta:
        model = Booking
        fields = {
            "owner__name": ["icontains"],
            "household__name": ["icontains"],
            "status": ["exact"],
        }
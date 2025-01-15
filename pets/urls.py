from django.urls import path
from .views import (
    HomePageView,
    BookingListView,
    BookingDetailView,
    BookingCreateView,
    BookingUpdateView,
    BookingCancelView,
    BookingUncancelView,
    BookingDeleteView,
    PetListView,
    PetDetailView,
    PetUpdateView,
    PetTemplateView,
    PetWizardView,
    PetCreateView,
    PetDeleteView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("pets/", PetListView.as_view(), name="pet_list"),
    path("pets/<uuid:pk>/", PetDetailView.as_view(), name="pet_detail"),
    path("pets/<uuid:pk>/edit", PetUpdateView.as_view(), name="pet_update"),
    path("pets/new/", PetTemplateView.as_view(), name="pet_new_base"),
    path("pets/new/create_pet", PetWizardView.as_view(), name="pet_create"),
    path(
        "pet/new/existing_client", PetCreateView.as_view(), name="pet_create_existing"
    ),
    path("pets/<uuid:pk>/delete/", PetDeleteView.as_view(), name="pet_destroy"),
    path("bookings/", BookingListView.as_view(), name="booking_list"),
    path("bookings/<uuid:pk>/", BookingDetailView.as_view(), name="booking_detail"),
    path(
        "bookings/<uuid:pk>/edit/", BookingUpdateView.as_view(), name="booking_update"
    ),
    path("bookings/new/", BookingCreateView.as_view(), name="booking_new"),
    path(
        "bookings/<uuid:pk>/cancel/", BookingCancelView.as_view(), name="booking_cancel"
    ),
    path(
        "bookings/<uuid:pk>/uncancel/",
        BookingUncancelView.as_view(),
        name="booking_uncancel",
    ),
    path(
        "bookings/<uuid:pk>/delete/",
        BookingDeleteView.as_view(),
        name="booking_destroy",
    ),
]

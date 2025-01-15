from django.urls import reverse, reverse_lazy
from django.core.files.storage import DefaultStorage
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Booking, Pet
from .filters import PetFilter, BookingFilter
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
    DeleteView,
    View,
)
from .forms import (
    CreateBookingForm,
    AddressForm,
    PetForm,
    OwnerForm,
    HouseholdForm,
    ExistingClientForm,
    UpdatePetForm,
)
from formtools.wizard.views import SessionWizardView


class HasHouseholdsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["has_households"] = user.household_set.exists()
        return context


class HasOwnersMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["has_owners"] = user.owner_set.exists()
        return context


class HasPetsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["has_pets"] = user.pet_set.exists()
        return context


class BookingBaseView(HasHouseholdsMixin, HasPetsMixin):
    def get_queryset(self):
        # Get the base queryset with select_related and prefetch_related
        queryset = Booking.objects.select_related("owner").prefetch_related(
            "owner__pets"
        )

        status_filter = self.request.GET.get("status", Booking.Status.UPCOMING)
        # Apply the appropriate filter based on the status_filter
        if status_filter:
            queryset = queryset.filter(user=self.request.user, status=status_filter)
        else:
            # If status_filter is None or empty, show all bookings
            queryset = queryset.filter(user=self.request.user)

        return queryset.order_by("status", "start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bookings = context["bookings"]

        for booking in bookings:
            booking.dates = booking.format_booking_dates()

        return context


class PetBaseView(HasHouseholdsMixin, HasOwnersMixin):
    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user)


class HomePageView(ListView, HasHouseholdsMixin, HasPetsMixin):
    model = Booking
    context_object_name = "bookings"
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # Add authenticated user context
            context["bookings"] = Booking.objects.filter(
                user=self.request.user,
                start_date__gte=date.today(),
                status=Booking.Status.UPCOMING,
            ).order_by("start_date")

            for booking in context["bookings"]:
                booking.dates = booking.format_booking_dates()

        return context


class BookingListView(LoginRequiredMixin, BookingBaseView, ListView):
    filterset_class = BookingFilter
    model = Booking
    context_object_name = "bookings"
    template_name = "bookings/booking_list.html"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()

        self.filter = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        # Add the filter instance to the context
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        context["booking_count"] = self.filter.qs.count()
        return context


class BookingDetailView(LoginRequiredMixin, BookingBaseView, DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"

    def get_context_data(self, **kwargs):
        context = {"booking": self.object}
        booking = self.object

        context.update(
            {
                "dates": booking.format_booking_dates(),
                "rates": booking.format_amount(booking.rate_per_day),
                "owners": booking.get_owner_names(),
                "pets": booking.get_pet_names(),
            }
        )

        return context


class BookingCreateView(LoginRequiredMixin, HasHouseholdsMixin, HasPetsMixin, CreateView):
    model = Booking
    template_name = "bookings/booking_new.html"
    form_class = CreateBookingForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if start_date > end_date:
            form.add_error(
                "start_date", "Start date cannot be later than the end date."
            )
            return super().form_invalid(form)

        booking = form.save(commit=False)
        booking.user = self.request.user
        household = form.cleaned_data.get("household")

        if household:
            # Assuming that household.owner is the owner of the booking
            booking.owner = household.owners.first()  # Set the owner from the household

        booking.save()

        messages.success(self.request, "Booking created successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("booking_list")


class BookingUpdateView(BookingCreateView, UpdateView):
    template_name = "bookings/booking_update.html"


class BookingCancelView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.status != Booking.Status.CANCELLED:
            booking.status = Booking.Status.CANCELLED
            booking.save()
            messages.success(request, "Booking canceled successfully!")
        else:
            messages.info(request, "This booking is already canceled.")
        return redirect("booking_list")


class BookingUncancelView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.status == Booking.Status.CANCELLED:
            booking.status = Booking.Status.UPCOMING
            booking.save()
            messages.success(request, "Booking is no longer canceled!")
        else:
            messages.info(
                request, "This booking is not cancelled, so it cannot be uncanceled."
            )
        return redirect("booking_list")


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy("booking_list")

    def form_valid(self, form):
        messages.success(self.request, "Booking deleted successfully!")
        return super().form_valid(form)


class PetListView(LoginRequiredMixin, PetBaseView, ListView):
    filterset_class = PetFilter
    model = Pet
    template_name = "pets/pet_list.html"
    paginate_by = 5

    def get_queryset(self):
        # Start with the base queryset from PetBaseView
        queryset = super().get_queryset()

        # Apply the filter logic
        self.filter = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        # Add the filter instance to the context
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        context["pet_count"] = self.filter.qs.count()

        return context


class PetDetailView(LoginRequiredMixin, PetBaseView, DetailView):
    model = Pet
    template_name = "pets/pet_detail.html"
    context_object_name = "pet"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pet = self.object
        household = pet.household

        context["owner_contact_method"] = pet.get_method_of_contact()
        context["bookings"] = Booking.objects.filter(
            household=household, status=Booking.Status.UPCOMING
        ).order_by("start_date")
        context["address"] = pet.get_owner_address

        return context


class PetTemplateView(LoginRequiredMixin, PetBaseView, TemplateView):
    model = Pet
    template_name = "pets/pet_new_base.html"


class PetWizardView(LoginRequiredMixin, PetBaseView, SessionWizardView):
    file_storage = DefaultStorage()
    template_name = "pets/pet_new_client.html"
    form_list = [OwnerForm, AddressForm, PetForm, HouseholdForm]
    success_url = reverse_lazy("pet_list")

    def done(self, form_list, **kwargs):
        owner_form = form_list[0]
        address_form = form_list[1]
        pet_form = form_list[2]
        household_form = form_list[3]

        # Save household, ensuring it's associated with the current logged-in user
        household = household_form.save(commit=False)
        if not household.name:
            household.name = pet_form.cleaned_data.get("name")
        household.user = (
            self.request.user
        )  # Associate household with the logged-in user
        household.save()

        # Save owner, ensuring it's associated with the current household and user
        owner = owner_form.save(commit=False)
        owner.household = household
        owner.user = self.request.user  # Associate owner with the logged-in user
        owner.save()

        address = address_form.save(commit=False)
        address.owner = owner
        address.save()

        # Save pet, ensuring it's associated with the current owner, household, and user
        pet = pet_form.save(commit=False)
        pet.household = household
        pet.owner = owner
        pet.user = self.request.user  # Associate pet with the logged-in user
        pet.save()

        # Redirect to the pet list after saving
        return redirect("pet_list")


class PetCreateView(LoginRequiredMixin, PetBaseView, CreateView):
    model = Pet
    form_class = ExistingClientForm
    template_name = "pets/pet_new_existing.html"
    success_url = reverse_lazy("pet_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        pet = form.save(commit=False)
        pet.user = self.request.user
        pet.save()

        messages.success(self.request, "Pet created successfully!")
        return super().form_valid(form)


class PetUpdateView(LoginRequiredMixin, UpdateView):
    model = Pet
    form_class = UpdatePetForm
    template_name = "pets/pet_update.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Pet info saved successfully!")
        return super().form_valid(form)


class PetDeleteView(LoginRequiredMixin, DeleteView):
    model = Pet
    success_url = reverse_lazy("pet_list")

    def form_valid(self, form):
        messages.success(self.request, "Pet deleted successfully!")
        return super().form_valid(form)

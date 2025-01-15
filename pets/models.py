from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
import uuid


class Household(models.Model):
    name = models.CharField(max_length=250)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"], name="unique_household_name_per_user"
            )
        ]

    def __str__(self):
        return self.name


class Owner(models.Model):
    class ContactMethod(models.IntegerChoices):
        LINE = 1, "Line"
        MESSENGER = 2, "FB Messenger"
        INSTAGRAM = 3, "Instagram"
        OTHER = 4, "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=250)
    method_of_contact = models.IntegerField(
        choices=ContactMethod.choices, default=ContactMethod.LINE
    )
    household = models.ForeignKey(
        Household,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="owners",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"], name="unique_owner_name_per_user"
            )
        ]

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name


class Address(models.Model):
    owner = models.OneToOneField(
        "Owner", on_delete=models.CASCADE, related_name="address"
    )
    postcode = models.CharField(max_length=8)
    prefecture = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    town = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.street}, \n{self.town}, \n{self.city}, \n{self.prefecture}, \n{self.postcode}"


class Pet(models.Model):
    class PetType(models.IntegerChoices):
        DOG = 1, "Dog"
        CAT = 2, "Cat"
        OTHER = 3, "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=250)
    pet_type = models.IntegerField(choices=PetType.choices, default=PetType.DOG)
    medication_required = models.BooleanField(default=False)
    owner = models.ForeignKey(
        Owner, on_delete=models.CASCADE, related_name="pets", null=False, blank=False
    )
    profile_image = models.ImageField(upload_to="profile_imgs/", blank=True)
    household = models.ForeignKey(
        Household,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="pets",
    )
    medication_instructions = models.TextField(
        max_length=1000,
        help_text="Provide instructions on the medication's dosage, frequency, and any special requirements.",
        blank=True,
        null=True,
    )
    instruction_manual = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pet_detail", args=[str(self.id)])

    def get_edit_url(self):
        return reverse("pet_update", args=[str(self.id)])

    def get_destroy_url(self):
        # Assuming you have a URL pattern named 'pet_destroy'
        return reverse("pet_destroy", args=[str(self.id)])

    def get_method_of_contact(self):
        method_of_contact = self.owner.method_of_contact
        contact_method_display = Owner.ContactMethod(method_of_contact).label
        owner_contact_method = contact_method_display
        return owner_contact_method

    def get_owner_address(self):
        return getattr(self.owner, "address", None) if self.owner else ""

    def medication_status(self):
        return "Yes" if self.medication_required else "No"


class Booking(models.Model):
    class Status(models.IntegerChoices):
        UPCOMING = 1, "Upcoming"
        ONGOING = 2, "Ongoing"
        DONE = 3, "Done"
        CANCELLED = 4, "Cancelled"

    class ServiceType(models.IntegerChoices):
        OVERNIGHT = 1, "Overnight"
        VISIT = 2, "Visit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey(
        Owner, null=True, blank=True, on_delete=models.CASCADE, related_name="bookings"
    )
    rate_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_rate = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=False, default=0
    )
    status = models.IntegerField(choices=Status.choices, default=Status.UPCOMING)
    service_type = models.IntegerField(
        choices=ServiceType.choices, default=ServiceType.OVERNIGHT
    )
    household = models.ForeignKey(
        Household,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    def __str__(self):
        return self.household.name

    def get_absolute_url(self):
        return reverse("booking_detail", args=[str(self.id)])

    def get_edit_url(self):
        return reverse("booking_update", args=[str(self.id)])

    def get_cancel_url(self):
        return reverse("booking_cancel", args=[str(self.id)])

    def get_destroy_url(self):
        return reverse("booking_destroy", args=[str(self.id)])

    def get_owner_names(self):
        """
        Returns the names of owners associated with the booking.
        """
        owner = self.household.owners.first()
        return owner.name

    def get_pet_names(self):
        """
        Returns the names of pets associated with the booking's owner.
        """
        return self.household.pets.all()

    def format_amount(self, rate):
        return f"¥{rate:,.0f}"

    def format_booking_dates(self):
        # Same day
        if self.start_date == self.end_date:
            return self.start_date.strftime("%-d %B %Y")

        # Check if start and end dates are in the same month and year
        if self.start_date.month == self.end_date.month and self.start_date.year == self.end_date.year:
            return f"{self.start_date.strftime('%-d')}-{self.end_date.strftime('%-d %B %Y')}"

        # Same year, different month
        if self.start_date.year == self.end_date.year:
            return f"{self.start_date.strftime('%-d %B')}-{self.end_date.strftime('%-d %B %Y')}"

        # Different year
        return f"{self.start_date.strftime('%-d %B %Y')}-{self.end_date.strftime('%-d %B %Y')}"


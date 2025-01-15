from django import forms
from pets.models import Booking, Owner, Pet, Household, Address
from django.core.exceptions import ValidationError
import re


class CreateBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "household",
            "status",
            "rate_per_day",
            "bonus_rate",
            "service_type",
            "start_date",
            "end_date",
        ]
        labels = {"household": "Select either pet or household name"}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Retrieve the user from kwargs
        super().__init__(*args, **kwargs)

        self.fields["household"].required = False

        if user:
            # Filter the queryset based on the logged-in user
            self.fields["household"].queryset = Household.objects.filter(
                owners__user=user
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()

        # Retrieve the values for household
        household = cleaned_data.get("household")

        # If household is empty, raise validation error
        if not household:
            raise ValidationError("Either a pet or a household name must be provided.")

        return cleaned_data


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ["name"]
        labels = {"name": "Household Name (optional)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = False


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ["name", "method_of_contact"]
        labels = {"name": "Owner Name", "method_of_contact": "Preferred Contact Method"}


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["postcode", "prefecture", "city", "town", "street"]
        labels = {
            "postcode": "Postcode (e.g. 151-0001)",
            "prefecture": "Prefecture",
            "city": "City (e.g. Setagaya-ku)",
            "town": "Town or Village (e.g. Jingumae 6-23-4)",
            "city": "Building name (e.g. My Apartment 101)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["postcode"].required = False
        self.fields["prefecture"].required = False
        self.fields["city"].required = False
        self.fields["town"].required = False


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ["name", "pet_type", "medication_required", "profile_image"]
        labels = {"name": "Pet Name", "pet_type": "Pet Type"}


class ExistingClientForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "name",
            "pet_type",
            "medication_required",
            "medication_instructions",
            "instruction_manual",
            "owner",
            "profile_image",
            "household",
        ]
        labels = {
            "name": "Pet Name",
            "pet_type": "Pet Type",
            "owner": "Owner Name",
            "instruction_manual": "Reference guide from owners",
            "household": "Household Name",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["owner"].required = False
        self.fields["household"].required = False

        if user:
            self.fields["owner"].queryset = Owner.objects.filter(
                household__owners__user=user
            ).distinct()
            self.fields["household"].queryset = Household.objects.filter(
                owners__user=user
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()

        # Retrieve the values for owner and household
        owner = cleaned_data.get("owner")
        household = cleaned_data.get("household")

        # If both are empty, raise validation error
        if not owner and not household:
            raise ValidationError(
                "Either an owner or a household name must be provided."
            )

        if owner and not household:
            household = owner.household
            cleaned_data["household"] = household

        if household and not owner:
            owners = household.owners.all()
            if owners.exists():
                cleaned_data["owner"] = owners.first()

        return cleaned_data


class UpdatePetForm(forms.ModelForm):
    owner = forms.CharField(max_length=100, required=False)
    household = forms.CharField(max_length=100, required=False)
    postcode = forms.CharField(max_length=20, required=False)
    prefecture = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=False)
    town = forms.CharField(max_length=100, required=False)
    street = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Pet
        fields = [
            "name",
            "pet_type",
            "medication_required",
            "medication_instructions",
            "profile_image",
        ]
        labels = {
            "postcode": "Postcode (e.g. 151-0001)",
            "prefecture": "Prefecture",
            "city": "City (e.g. Setagaya-ku)",
            "town": "Town or Village (e.g. Jingumae 6-23-4)",
            "street": "Building name (e.g. My Apartment 101)",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter Pet Name",
                }
            ),
            "owner": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter Owner Name",
                }
            ),
            "pet_type": forms.Select(attrs={"class": "form-input"}),
            "medication_required": forms.CheckboxInput(
                attrs={"class": "checkbox create-input"}
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={"class": "file-input create-input mt-2"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the 'owner' field with the current owner's name
        if self.instance and self.instance.owner:
            self.fields["owner"].initial = self.instance.owner.name
            address = getattr(self.instance.owner, "address", None)
            if address:
                self.fields["postcode"].initial = address.postcode
                self.fields["prefecture"].initial = address.prefecture
                self.fields["city"].initial = address.city
                self.fields["town"].initial = address.town
                self.fields["street"].initial = address.street
        if self.instance.household:
            self.fields["household"].initial = self.instance.household.name

    def clean_owner(self):
        owner_name = self.cleaned_data.get("owner")
        if owner_name:
            # Try to find the owner by name
            try:
                owner = Owner.objects.get(name=owner_name)
                # If the owner exists, return that owner
                return owner
            except Owner.DoesNotExist:
                # If the owner doesn't exist, update the name of the current owner
                if self.instance and self.instance.owner:
                    self.instance.owner.name = owner_name
                    self.instance.owner.save()
                    return self.instance.owner
                else:
                    raise forms.ValidationError("No owner exists to update.")
        return None

    def clean_household(self):
        household_name = self.cleaned_data.get("household")
        if household_name:
            # Try to find the household by name or handle creation
            try:
                household = Household.objects.get(name=household_name)
                return household  # Return the existing household if found
            except Household.DoesNotExist:
                if self.instance and self.instance.household:
                    self.instance.household.name = household_name
                    self.instance.household.save()
                    return self.instance.household
                else:
                    # Handle if there's no current household or if you want to create one
                    raise forms.ValidationError("No household exists to update.")
        return None

    def clean_postcode(self):
        """Ensure the postcode is formatted as XXX-XXXX."""
        postcode = self.cleaned_data.get("postcode", "")
        if postcode:
            # Remove any non-digit characters for validation
            cleaned_postcode = "".join(filter(str.isdigit, postcode))

            # Check if the cleaned postcode matches the exact pattern
            if re.match(r"^\d{3}-\d{4}$", postcode):
                return postcode  # Return the valid postcode in the correct format
            else:
                raise forms.ValidationError(
                    "Postcode must be in the format XXX-XXXX, e.g., 151-0001."
                )
        return postcode

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("owner"):
            instance.owner = self.cleaned_data["owner"]
        if self.cleaned_data.get("household"):
            instance.household = self.cleaned_data[
                "household"
            ]  # Set the updated household instance
        if instance.owner:
            address_data = {
                "postcode": self.cleaned_data.get("postcode"),
                "prefecture": self.cleaned_data.get("prefecture"),
                "city": self.cleaned_data.get("city"),
                "town": self.cleaned_data.get("town"),
                "street": self.cleaned_data.get("street"),
            }
            address, created = Address.objects.update_or_create(
                owner=instance.owner, defaults=address_data
            )

        if commit:
            instance.save()
        return instance
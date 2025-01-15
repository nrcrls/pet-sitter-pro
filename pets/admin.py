from django.contrib import admin
from pets.models import Pet, Booking, Owner, Household, Address


class PetInlineAdmin(admin.StackedInline):
    model = Pet
    fields = ["name", "pet_type", "medication_required", "profile_image"]
    extra = 1


class AddressInlineAdmin(admin.StackedInline):
    model = Address
    fields = ["postcode", "prefecture", "city", "town", "street"]


class HouseholdAdmin(admin.ModelAdmin):
    inlines = [PetInlineAdmin]
    list_display = ("__str__",)


class OwnerAdmin(admin.ModelAdmin):
    inlines = [AddressInlineAdmin, PetInlineAdmin]
    fields = ["name", "method_of_contact"]


class AdressAdmin(admin.ModelAdmin):
    list_display = ("owner", "postcode", "prefecture", "city", "town", "street")


class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "pet_type")


class BookingAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "status", "start_date", "end_date")


admin.site.register(Household, HouseholdAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(Address, AdressAdmin)
admin.site.register(Pet, PetAdmin)
admin.site.register(Booking, BookingAdmin)

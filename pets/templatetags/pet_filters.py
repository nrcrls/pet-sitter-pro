from django import template
from pets.models import Pet


register = template.Library()

PET_TYPE_MAP = {
    Pet.PetType.DOG.label: "primary",
    Pet.PetType.CAT.label: "error",
    Pet.PetType.OTHER.label:"success",
}

@register.filter
def pet_type_to_class(pet_type):
    """Map pet type to Tailwind CSS classes using the enum."""
    return PET_TYPE_MAP.get(pet_type)
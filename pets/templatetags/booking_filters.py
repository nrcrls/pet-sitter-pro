from django import template
from datetime import date
from pets.models import Booking


register = template.Library()

# Mapping of Booking status to Tailwind CSS classes
STATUS_CLASS_MAP = {
    Booking.Status.UPCOMING.label: "warning",  # UPCOMING
    Booking.Status.ONGOING.label: "primary",  # ONGOING
    Booking.Status.DONE.label: "success",  # DONE
    Booking.Status.CANCELLED.label: "error",  # CANCELLED
}


@register.filter
def status_to_class(status):
    """Map booking status to Tailwind CSS classes using the enum."""
    return STATUS_CLASS_MAP.get(status, "primary")


@register.filter
def status_based_on_date(booking):
    today = date.today()

    # If the booking is CANCELLED, return CANCELLED status immediately
    if booking.status == Booking.Status.CANCELLED:
        return Booking.Status.CANCELLED.label

    # Determine status based on dates
    if today > booking.end_date:
        return Booking.Status.DONE.label
    elif today >= booking.start_date:
        return Booking.Status.ONGOING.label
    return Booking.Status.UPCOMING.label
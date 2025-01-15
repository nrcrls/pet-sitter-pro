from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from .views import HomePageView
from .models import Pet, Owner, Household, Booking


class HomepageTests(SimpleTestCase):
    def setUp(self):
        url = reverse("home")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "home.html")

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, "The pet sitter's diary")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_homepage_url_resolves_homepageview(self):
        view = resolve("/")
        self.assertEqual(view.func.__name__, HomePageView.as_view().__name__)


class PetTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.household = Household.objects.create(name="Test Household")
        cls.owner = Owner.objects.create(name="Test Owner", household=cls.household)
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        cls.pet = Pet.objects.create(
            user=cls.user,
            name="Maruko",
            pet_type=Pet.PetType.DOG,
            medication_required=False,
            owner=cls.owner,
            household=cls.household,
            medication_instructions="Give one pill daily.",
            instruction_manual="link.url.com",
        )

    def setUp(self):
        self.client.login(username="testuser", password="password123")

    def test_pet_listing(self):
        self.assertEqual(self.pet.name, "Maruko")
        self.assertEqual(self.pet.pet_type, Pet.PetType.DOG)
        self.assertFalse(self.pet.medication_required)
        self.assertEqual(self.pet.owner, self.owner)
        self.assertEqual(self.pet.household, self.household)
        self.assertEqual(self.pet.medication_instructions, "Give one pill daily.")
        self.assertEqual(self.pet.instruction_manual, "link.url.com")
        self.assertIsNotNone(self.pet.id)

    def test_pet_list_view(self):
        response = self.client.get(reverse("pet_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maruko")
        self.assertTemplateUsed(response, "pets/pet_list.html")

    def test_book_detail_view(self):
        response = self.client.get(self.pet.get_absolute_url())
        no_response = self.client.get("/pets/12345/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Maruko")
        self.assertTemplateUsed(response, "pets/pet_detail.html")


class BookingModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.household = Household.objects.create(name="Test Household")
        cls.owner = Owner.objects.create(name="Test Owner", household=cls.household)
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

        cls.booking = Booking.objects.create(
            user=cls.user,
            start_date="2025-02-01",
            end_date="2025-02-05",
            owner=cls.owner,
            rate_per_day=1000.00,
            status=Booking.Status.UPCOMING,
            service_type=Booking.ServiceType.OVERNIGHT,
            household=cls.household,
        )

    def setUp(self):
        self.client.login(username="testuser", password="password123")

    def test_booking_listing(self):
        booking = self.booking
        
        self.assertEqual(booking.user.username, "testuser")
        self.assertEqual(booking.start_date, "2025-02-01")
        self.assertEqual(booking.end_date, "2025-02-05")
        self.assertEqual(booking.owner, self.owner)
        self.assertEqual(booking.rate_per_day, 1000.00)
        self.assertEqual(booking.status, Booking.Status.UPCOMING)
        self.assertEqual(booking.service_type, Booking.ServiceType.OVERNIGHT)
        self.assertEqual(booking.household, self.household)
        self.assertIsNotNone(booking.id)

    def test_booking_list_view(self):
        response = self.client.get(reverse("booking_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Household")
        self.assertTemplateUsed(response, "bookings/booking_list.html")

    def test_booking_detail_view(self):
        response = self.client.get(self.booking.get_absolute_url())
        
        invalid_response = self.client.get("/bookings/12345/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(invalid_response.status_code, 404)
        
        self.assertContains(response, "Test Household")
        self.assertContains(response, "Feb. 1 - 5, 2025")
        self.assertTemplateUsed(response, "bookings/booking_detail.html")
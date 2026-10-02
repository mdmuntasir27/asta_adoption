from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Pet, AdoptionRequest, Favorite


class PetModelAndBusinessLogicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user2 = User.objects.create_user(username='otheruser', password='password123')
        self.available_pet = Pet.objects.create(
            name='Tommy',
            animal_type='Dog',
            breed='Labrador',
            age='1 year',
            gender='Male',
            location='Dhaka',
            description='Friendly pup',
            status='Available',
            adoption_fee=Decimal('1000.00')
        )
        self.adopted_pet = Pet.objects.create(
            name='Kitty',
            animal_type='Cat',
            breed='Persian',
            age='2 years',
            gender='Female',
            location='Chittagong',
            status='Adopted',
            adoption_fee=Decimal('800.00')
        )

    def test_pet_str_and_properties(self):
        self.assertEqual(str(self.available_pet), "Tommy (Dog - Labrador)")
        self.assertTrue(self.available_pet.is_available)
        self.assertFalse(self.adopted_pet.is_available)

    def test_rule_1_only_available_pets_can_be_adopted(self):
        """Rule 1: If pet status is Adopted, new application cannot be submitted."""
        req = AdoptionRequest(
            user=self.user,
            pet=self.adopted_pet,
            phone='01700000000',
            address='Dhaka',
            reason='Love cats'
        )
        with self.assertRaises(ValidationError):
            req.clean()

    def test_rule_2_prevent_multiple_active_requests_for_same_pet(self):
        """Rule 2: One user cannot submit multiple active requests for the same pet."""
        AdoptionRequest.objects.create(
            user=self.user,
            pet=self.available_pet,
            phone='01700000000',
            address='Dhaka',
            reason='First request',
            status='Pending'
        )
        # Attempting second pending request by same user for same pet
        duplicate_req = AdoptionRequest(
            user=self.user,
            pet=self.available_pet,
            phone='01700000000',
            address='Dhaka',
            reason='Second duplicate request',
            status='Pending'
        )
        with self.assertRaises(ValidationError):
            duplicate_req.clean()

    def test_rule_3_approved_application_changes_pet_status_to_adopted(self):
        """Rule 3: When admin approves an application, Pet Status becomes Adopted."""
        req = AdoptionRequest.objects.create(
            user=self.user,
            pet=self.available_pet,
            phone='01700000000',
            address='Dhaka',
            reason='I have a great home',
            status='Pending'
        )
        self.assertEqual(self.available_pet.status, 'Available')

        # Admin approves the request
        req.status = 'Approved'
        req.save()

        # Pet status should now be updated to Adopted
        self.available_pet.refresh_from_db()
        self.assertEqual(self.available_pet.status, 'Adopted')


class TemplateViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='johndoe', password='secretpassword')
        self.pet = Pet.objects.create(
            name='Rocky',
            animal_type='Dog',
            breed='German Shepherd',
            age='3 years',
            gender='Male',
            location='Dhaka',
            description='Very alert and brave',
            status='Available',
            adoption_fee=Decimal('1500.00')
        )
        self.adopted_pet = Pet.objects.create(
            name='Mimi',
            animal_type='Cat',
            breed='Domestic',
            age='1 year',
            gender='Female',
            location='Dhaka',
            description='Friendly cat',
            status='Adopted',
            adoption_fee=Decimal('0.00')
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ASTA Adoption Center')
        self.assertContains(response, 'Rocky')

    def test_pet_list_and_filtering(self):
        response = self.client.get(reverse('pet_list'), {'animal_type': 'Dog'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rocky')

        # Search filter
        response = self.client.get(reverse('pet_list'), {'search': 'German'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rocky')

        # Filter for non-matching animal type
        response = self.client.get(reverse('pet_list'), {'animal_type': 'Rabbit'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Rocky')

    def test_pet_detail_available(self):
        response = self.client.get(reverse('pet_detail', kwargs={'pk': self.pet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rocky')
        self.assertContains(response, '৳ 1500')
        self.assertContains(response, 'BDT')

    def test_pet_detail_adopted_message(self):
        """Page 3 requirement: If pet has already been adopted, show 'This pet has already been adopted'."""
        response = self.client.get(reverse('pet_detail', kwargs={'pk': self.adopted_pet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This pet has already been adopted.')
        self.assertNotContains(response, 'Apply for Adoption')

    def test_adoption_application_submission_flow(self):
        self.client.login(username='johndoe', password='secretpassword')
        url = reverse('adoption_apply', kwargs={'pk': self.pet.pk})
        
        # GET form
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Adoption Application')

        # POST valid application
        post_data = {
            'address': 'House 1, Road 2, Dhanmondi, Dhaka',
            'phone': '01711111111',
            'reason': 'We love dogs and have time to care for Rocky',
            'previous_pet_experience': 'True',
            'message': 'Looking forward to meeting him!'
        }
        post_resp = self.client.post(url, post_data)
        self.assertRedirects(post_resp, reverse('dashboard'))
        self.assertTrue(AdoptionRequest.objects.filter(user=self.user, pet=self.pet).exists())

    def test_adoption_application_prevent_multiple_active(self):
        """Rule 2 check in web application."""
        self.client.login(username='johndoe', password='secretpassword')
        AdoptionRequest.objects.create(
            user=self.user,
            pet=self.pet,
            phone='01711111111',
            address='Dhaka',
            reason='First try',
            status='Pending'
        )
        url = reverse('adoption_apply', kwargs={'pk': self.pet.pk})
        response = self.client.get(url)
        # Should redirect to dashboard because active request already exists
        self.assertRedirects(response, reverse('dashboard'))


class RestApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apiuser', password='password123')
        self.staff_user = User.objects.create_user(username='adminstaff', password='password123', is_staff=True)
        self.token = Token.objects.create(user=self.user)
        self.staff_token = Token.objects.create(user=self.staff_user)

        self.pet = Pet.objects.create(
            name='Simba',
            animal_type='Cat',
            breed='Orange Tabby',
            age='1 year',
            gender='Male',
            location='Dhaka',
            description='Friendly ginger cat',
            status='Available',
            adoption_fee=Decimal('500.00')
        )

    def test_get_pets_list(self):
        response = self.client.get(reverse('api_pet_list_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify pagination structure and results
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Simba')

    def test_get_pet_detail(self):
        response = self.client.get(reverse('api_pet_detail', kwargs={'pk': self.pet.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Simba')
        self.assertIn('BDT', response.data['formatted_fee'])

    def test_create_pet_as_staff(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.staff_token.key)
        data = {
            'name': 'Bunny',
            'animal_type': 'Rabbit',
            'breed': 'Dutch',
            'age': '6 months',
            'gender': 'Female',
            'location': 'Sylhet',
            'description': 'Loves carrots',
            'status': 'Available',
            'adoption_fee': '300.00'
        }
        response = self.client.post(reverse('api_pet_list_create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Bunny')

    def test_create_pet_as_non_staff_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            'name': 'Unauthorized Pet',
            'animal_type': 'Dog',
            'breed': 'Mix',
            'age': '1 year',
            'gender': 'Male',
            'location': 'Dhaka',
            'description': 'test'
        }
        response = self.client.post(reverse('api_pet_list_create'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adoption_api_submission_and_scoping(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        post_data = {
            'pet': self.pet.id,
            'phone': '01912345678',
            'address': 'Gulshan-2, Dhaka',
            'reason': 'I love cats and can provide great care',
            'previous_pet_experience': False,
            'message': 'When can I meet Simba?'
        }
        create_resp = self.client.post(reverse('api_adoption_list_create'), post_data)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_resp.data['status'], 'Pending')

        # Rule 2 in API: Attempting duplicate active request should fail
        dup_resp = self.client.post(reverse('api_adoption_list_create'), post_data)
        self.assertEqual(dup_resp.status_code, status.HTTP_400_BAD_REQUEST)

        # GET /api/adoptions/ should return user's own request
        list_resp = self.client.get(reverse('api_adoption_list_create'))
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_resp.data['results']), 1)

    def test_favorites_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Add to favorites
        fav_resp = self.client.post(reverse('api_favorites'), {'pet': self.pet.id})
        self.assertEqual(fav_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(fav_resp.data['status'], 'added')

        # Toggle off
        toggle_resp = self.client.post(reverse('api_favorites'), {'pet': self.pet.id})
        self.assertEqual(toggle_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(toggle_resp.data['status'], 'removed')

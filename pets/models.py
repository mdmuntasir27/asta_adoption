from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Pet(models.Model):
    ANIMAL_TYPE_CHOICES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Rabbit', 'Rabbit'),
        ('Other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Adopted', 'Adopted'),
    ]

    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=50, choices=ANIMAL_TYPE_CHOICES, default='Dog')
    breed = models.CharField(max_length=100)
    age = models.CharField(max_length=50, help_text="e.g. 2 years, 6 months")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    location = models.CharField(max_length=100, default='Dhaka')
    description = models.TextField()
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    adoption_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Adoption / Medical care fee in BDT"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.animal_type} - {self.breed})"

    @property
    def is_available(self):
        return self.status == 'Available'


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_requests')
    phone = models.CharField(max_length=25)
    address = models.TextField()
    reason = models.TextField(help_text="Why do you want to adopt this pet?")
    previous_pet_experience = models.BooleanField(
        default=False,
        help_text="Have you owned a pet before?"
    )
    message = models.TextField(blank=True, help_text="Additional message (optional)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request by {self.user.username} for {self.pet.name} [{self.status}]"

    def clean(self):
        super().clean()
        pet = getattr(self, 'pet', None) if hasattr(self, 'pet_id') and self.pet_id else None
        user = getattr(self, 'user', None) if hasattr(self, 'user_id') and self.user_id else None

        # Rule 1: Only available pets can be adopted for new applications
        if not self.pk:
            if pet and pet.status == 'Adopted':
                raise ValidationError({
                    'pet': 'This pet has already been adopted and is no longer available for adoption.'
                })
            # Rule 2: One user cannot submit multiple active requests for the same pet
            if user and pet:
                existing_active = AdoptionRequest.objects.filter(
                    user=user,
                    pet=pet,
                    status='Pending'
                ).exists()
                if existing_active:
                    raise ValidationError(
                        'You already have an active pending adoption request for this pet.'
                    )

    def save(self, *args, **kwargs):
        # Enforce Rule 3: When admin approves an application, set pet status to Adopted
        is_approval = self.status == 'Approved'
        super().save(*args, **kwargs)
        if is_approval and self.pet.status != 'Adopted':
            self.pet.status = 'Adopted'
            self.pet.save(update_fields=['status'])


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pet')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ❤️ {self.pet.name}"

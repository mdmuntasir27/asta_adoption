from django import forms
from django.contrib.auth.models import User
from .models import AdoptionRequest, Pet


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter strong password'
        }),
        min_length=6,
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. jhon_doe'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class AdoptionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ['phone', 'address', 'reason', 'previous_pet_experience', 'message']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+880 1XXXXXXXXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House/Street, Area, City, District'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Why do you want to adopt this pet? Share your plan to care for it.'
            }),
            'previous_pet_experience': forms.Select(
                choices=[(True, 'Yes, I have owned a pet before'), (False, 'No, this is my first pet')],
                attrs={'class': 'form-select'}
            ),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any questions, preferences, or additional info for the shelter...'
            }),
        }
        labels = {
            'phone': 'Phone Number',
            'address': 'Your Residence Address',
            'reason': 'Why do you want this pet?',
            'previous_pet_experience': 'Have you owned a pet before?',
            'message': 'Additional Message (Optional)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.pet = kwargs.pop('pet', None)
        super().__init__(*args, **kwargs)
        if self.pet:
            self.instance.pet = self.pet
        if self.user:
            self.instance.user = self.user

    def clean(self):
        cleaned_data = super().clean()
        if self.pet:
            # Rule 1: Only available pets can be adopted
            if self.pet.status == 'Adopted':
                raise forms.ValidationError("This pet has already been adopted and cannot receive new applications.")
            
            # Rule 2: One user cannot submit multiple active requests for the same pet
            if self.user and self.user.is_authenticated:
                active_req = AdoptionRequest.objects.filter(
                    user=self.user,
                    pet=self.pet,
                    status='Pending'
                ).exists()
                if active_req:
                    raise forms.ValidationError("You already have an active pending adoption request for this pet.")
        return cleaned_data


class PetSearchFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, breed, location...'
        })
    )
    animal_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Species')] + Pet.ANIMAL_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'All Genders')] + Pet.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City or Location (e.g. Dhaka)'
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Pet.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

import os
import sys
import django
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asta_adoption.settings')
django.setup()

from django.contrib.auth.models import User
from pets.models import Pet, AdoptionRequest, Favorite
from rest_framework.authtoken.models import Token


def create_pet_image(filename, name, animal_type, bg_color):
    """Generate a clean visual card image for a pet."""
    os.makedirs('media/pets', exist_ok=True)
    filepath = os.path.join('media', 'pets', filename)
    
    width, height = 600, 450
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Draw soft inner frame
    draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255), width=3)

    # Big circle in center
    cx, cy, r = width // 2, height // 2 - 25, 110
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 60), outline=(255, 255, 255), width=4)

    # Draw animal icon text representation
    species_symbols = {
        'Dog': 'DOG / CANINE',
        'Cat': 'CAT / FELINE',
        'Bird': 'BIRD / AVIAN',
        'Rabbit': 'RABBIT / BUNNY',
        'Other': 'RESCUE PET'
    }
    spec_txt = species_symbols.get(animal_type, 'PET')
    
    # Text labels
    draw.text((cx, cy - 15), spec_txt, fill=(255, 255, 255), anchor="mm")
    draw.text((cx, cy + 20), "ASTA RESCUE", fill=(240, 240, 240), anchor="mm")

    # Bottom name banner
    draw.rectangle([0, height - 90, width, height], fill=(20, 25, 35))
    draw.text((width // 2, height - 55), f"{name.upper()} ({animal_type})", fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, height - 25), "ASTA Adoption Center - Bangladesh", fill=(180, 190, 205), anchor="mm")

    image.save(filepath, format='JPEG', quality=92)
    return f"pets/{filename}"


def seed_database():
    print("🌱 Starting database population for ASTA Adoption Center...")

    # 1. Superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@asta.org', 'admin123')
        admin.first_name = "System"
        admin.last_name = "Admin"
        admin.save()
        Token.objects.get_or_create(user=admin)
        print("✅ Created Superuser: admin / admin123")
    else:
        admin = User.objects.get(username='admin')
        Token.objects.get_or_create(user=admin)

    # 2. Demo Users (Rahim, Fatima, Karim)
    user_data = [
        ('rahim', 'rahim@example.com', 'password123', 'Rahim', 'Uddin'),
        ('fatima', 'fatima@example.com', 'password123', 'Fatima', 'Begum'),
        ('karim', 'karim@example.com', 'password123', 'Karim', 'Chowdhury'),
    ]
    users = {}
    for username, email, pwd, first, last in user_data:
        user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': first, 'last_name': last})
        if created:
            user.set_password(pwd)
            user.save()
        Token.objects.get_or_create(user=user)
        users[username] = user
        print(f"✅ User: {username} (pwd: {pwd})")

    # 3. Pets Seed Data (Dhaka, Chittagong, Sylhet, etc. with BDT Currency fees)
    pets_info = [
        {
            'name': 'Max',
            'animal_type': 'Dog',
            'breed': 'Golden Retriever',
            'age': '2 years',
            'gender': 'Male',
            'location': 'Dhaka',
            'status': 'Available',
            'adoption_fee': Decimal('1500.00'),
            'description': 'Max is friendly, energetic, and playful. He was rescued near Dhanmondi Lake and has received full vaccination, deworming, and leash training. Very gentle around kids and other dogs.',
            'image_file': 'max_dog.jpg',
            'bg_color': (43, 84, 126)
        },
        {
            'name': 'Luna',
            'animal_type': 'Cat',
            'breed': 'Persian Longhair',
            'age': '1.5 years',
            'gender': 'Female',
            'location': 'Chittagong',
            'status': 'Available',
            'adoption_fee': Decimal('1200.00'),
            'description': 'Luna is a calm, affectionate cat who loves sitting on laps and purring softly while being brushed. Litter box trained and spayed. Looking for a quiet, loving indoor home.',
            'image_file': 'luna_cat.jpg',
            'bg_color': (140, 68, 102)
        },
        {
            'name': 'Coco',
            'animal_type': 'Bird',
            'breed': 'Cockatiel',
            'age': '10 months',
            'gender': 'Male',
            'location': 'Dhaka',
            'status': 'Adopted',
            'adoption_fee': Decimal('800.00'),
            'description': 'Coco loves whistling tunes and sitting on shoulders. He was hand-fed and is very socialized. He has been happily adopted into his forever family!',
            'image_file': 'coco_bird.jpg',
            'bg_color': (184, 115, 51)
        },
        {
            'name': 'Bella',
            'animal_type': 'Rabbit',
            'breed': 'Holland Lop',
            'age': '8 months',
            'gender': 'Female',
            'location': 'Sylhet',
            'status': 'Available',
            'adoption_fee': Decimal('600.00'),
            'description': 'Bella is a sweet Holland Lop rabbit who enjoys fresh greens, hay, and gentle petting. She is healthy, clean, and accustomed to human interaction.',
            'image_file': 'bella_rabbit.jpg',
            'bg_color': (56, 128, 92)
        },
        {
            'name': 'Rocky',
            'animal_type': 'Dog',
            'breed': 'German Shepherd Mix',
            'age': '3 years',
            'gender': 'Male',
            'location': 'Dhaka',
            'status': 'Available',
            'adoption_fee': Decimal('2000.00'),
            'description': 'Rocky is an alert, intelligent, and loyal companion. He knows basic obedience commands (Sit, Stay, Come) and makes a wonderful guardian and active family friend.',
            'image_file': 'rocky_dog.jpg',
            'bg_color': (60, 70, 95)
        },
        {
            'name': 'Milo',
            'animal_type': 'Cat',
            'breed': 'Domestic Short Hair (Deshi)',
            'age': '6 months',
            'gender': 'Male',
            'location': 'Rajshahi',
            'status': 'Available',
            'adoption_fee': Decimal('0.00'),
            'description': 'Milo is a rescued deshi kitten full of curiosity and affection. Free adoption fee to encourage responsible care. Fully vaccinated and dewormed.',
            'image_file': 'milo_cat.jpg',
            'bg_color': (120, 90, 45)
        },
        {
            'name': 'Rio',
            'animal_type': 'Bird',
            'breed': 'Budgerigar (Budgie)',
            'age': '1 year',
            'gender': 'Female',
            'location': 'Chittagong',
            'status': 'Available',
            'adoption_fee': Decimal('400.00'),
            'description': 'Rio is a cheerful sky-blue budgie who chirps joyfully each morning. Rescued from an overcrowded market in Chittagong, now healthy and active.',
            'image_file': 'rio_bird.jpg',
            'bg_color': (45, 110, 140)
        },
        {
            'name': 'Daisy',
            'animal_type': 'Dog',
            'breed': 'Labrador Retriever',
            'age': '1 year',
            'gender': 'Female',
            'location': 'Dhaka',
            'status': 'Adopted',
            'adoption_fee': Decimal('1800.00'),
            'description': 'Daisy is a gentle water-loving yellow lab who was adopted by a loving family in Gulshan. She has found her lifelong home!',
            'image_file': 'daisy_dog.jpg',
            'bg_color': (160, 110, 70)
        },
        {
            'name': 'Snowball',
            'animal_type': 'Rabbit',
            'breed': 'Netherland Dwarf',
            'age': '1 year',
            'gender': 'Male',
            'location': 'Sylhet',
            'status': 'Available',
            'adoption_fee': Decimal('750.00'),
            'description': 'Snowball is a tiny, pure white dwarf rabbit with adorable upright ears. Calm demeanor and loves apple slices and dried alfalfa.',
            'image_file': 'snowball_rabbit.jpg',
            'bg_color': (85, 95, 120)
        }
    ]

    created_pets = {}
    for pdata in pets_info:
        img_rel_path = create_pet_image(
            pdata['image_file'],
            pdata['name'],
            pdata['animal_type'],
            pdata['bg_color']
        )
        pet, created = Pet.objects.get_or_create(
            name=pdata['name'],
            animal_type=pdata['animal_type'],
            defaults={
                'breed': pdata['breed'],
                'age': pdata['age'],
                'gender': pdata['gender'],
                'location': pdata['location'],
                'status': pdata['status'],
                'adoption_fee': pdata['adoption_fee'],
                'description': pdata['description'],
                'image': img_rel_path
            }
        )
        created_pets[pet.name] = pet
        print(f"🐾 Pet: {pet.name} [{pet.status}] - Fee: ৳{pet.adoption_fee} BDT")

    # 4. Adoption Requests matching PDF specifications (Page 4: Max Pending, Luna Rejected, Coco Approved)
    # User Rahim applies for Max (Pending)
    max_pet = created_pets.get('Max')
    if max_pet and not AdoptionRequest.objects.filter(user=users['rahim'], pet=max_pet).exists():
        AdoptionRequest.objects.create(
            user=users['rahim'],
            pet=max_pet,
            phone='+880 1711-234567',
            address='House 14, Road 7, Dhanmondi, Dhaka',
            reason='We have a spacious home with a fenced yard and our children love dogs.',
            previous_pet_experience=True,
            message='We would love to visit the shelter this weekend to meet Max.',
            status='Pending'
        )
        print("📋 Created Adoption Request: Rahim -> Max (Pending)")

    # User Rahim applies for Luna (Rejected)
    luna_pet = created_pets.get('Luna')
    if luna_pet and not AdoptionRequest.objects.filter(user=users['rahim'], pet=luna_pet).exists():
        AdoptionRequest.objects.create(
            user=users['rahim'],
            pet=luna_pet,
            phone='+880 1711-234567',
            address='House 14, Road 7, Dhanmondi, Dhaka',
            reason='Looking for an indoor companion cat.',
            previous_pet_experience=True,
            message='Please let me know if an interview is needed.',
            status='Rejected'
        )
        print("📋 Created Adoption Request: Rahim -> Luna (Rejected)")

    # User Rahim applied for Coco (Approved -> Pet became Adopted)
    coco_pet = created_pets.get('Coco')
    if coco_pet and not AdoptionRequest.objects.filter(user=users['rahim'], pet=coco_pet).exists():
        AdoptionRequest.objects.create(
            user=users['rahim'],
            pet=coco_pet,
            phone='+880 1711-234567',
            address='House 14, Road 7, Dhanmondi, Dhaka',
            reason='I have cared for cockatiels for over 5 years and have a large flight cage.',
            previous_pet_experience=True,
            message='Ready to pick up anytime.',
            status='Approved'
        )
        print("📋 Created Adoption Request: Rahim -> Coco (Approved)")

    # User Fatima applies for Bella (Pending)
    bella_pet = created_pets.get('Bella')
    if bella_pet and not AdoptionRequest.objects.filter(user=users['fatima'], pet=bella_pet).exists():
        AdoptionRequest.objects.create(
            user=users['fatima'],
            pet=bella_pet,
            phone='+880 1819-987654',
            address='Rose Garden Apartment, Zindabazar, Sylhet',
            reason='I adore rabbits and have set up an indoor bunny-proof area.',
            previous_pet_experience=False,
            message='Excited to welcome Bella!',
            status='Pending'
        )
        print("📋 Created Adoption Request: Fatima -> Bella (Pending)")

    # 5. Favorites
    if max_pet:
        Favorite.objects.get_or_create(user=users['rahim'], pet=max_pet)
    if bella_pet:
        Favorite.objects.get_or_create(user=users['rahim'], pet=bella_pet)
        Favorite.objects.get_or_create(user=users['fatima'], pet=bella_pet)
    print("❤️ Created demo favorites")

    print("\n✨ Database successfully seeded with ASTA Adoption Center demo records!")


if __name__ == '__main__':
    seed_database()

from .models import Pet, Favorite

def site_settings(request):
    favorite_pet_ids = []
    if request.user.is_authenticated:
        favorite_pet_ids = list(
            Favorite.objects.filter(user=request.user).values_list('pet_id', flat=True)
        )
    return {
        'SITE_NAME': 'ASTA Adoption Center',
        'SITE_TAGLINE': 'Find Your Loyal Companion & Rescue a Loving Friend',
        'CURRENCY': 'BDT',
        'CURRENCY_SYMBOL': '৳',
        'PET_CATEGORIES': [
            {'name': 'Dog', 'icon': 'bi-suit-heart-fill'},
            {'name': 'Cat', 'icon': 'bi-emoji-smile'},
            {'name': 'Bird', 'icon': 'bi-feather'},
            {'name': 'Rabbit', 'icon': 'bi-flower1'},
            {'name': 'Other', 'icon': 'bi-stars'},
        ],
        'user_favorite_pet_ids': favorite_pet_ids,
    }

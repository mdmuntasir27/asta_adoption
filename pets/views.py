from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse

from .models import Pet, AdoptionRequest, Favorite
from .forms import UserRegisterForm, AdoptionApplicationForm, PetSearchFilterForm


def home_view(request):
    """Landing homepage with hero, categories, stats, and featured available pets."""
    featured_pets = Pet.objects.filter(status='Available')[:6]
    total_available = Pet.objects.filter(status='Available').count()
    total_adopted = Pet.objects.filter(status='Adopted').count()
    total_rescues = Pet.objects.count()

    context = {
        'featured_pets': featured_pets,
        'total_available': total_available,
        'total_adopted': total_adopted,
        'total_rescues': total_rescues,
    }
    return render(request, 'pets/home.html', context)


def pet_list_view(request):
    """Pet browsing page with search, multi-faceted filtering, and pagination."""
    queryset = Pet.objects.all()
    form = PetSearchFilterForm(request.GET or None)

    search_query = request.GET.get('search', '').strip()
    animal_type = request.GET.get('animal_type', '').strip()
    gender = request.GET.get('gender', '').strip()
    location = request.GET.get('location', '').strip()
    status = request.GET.get('status', '').strip()

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(breed__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if animal_type:
        queryset = queryset.filter(animal_type__iexact=animal_type)

    if gender:
        queryset = queryset.filter(gender__iexact=gender)

    if location:
        queryset = queryset.filter(location__icontains=location)

    if status:
        queryset = queryset.filter(status__iexact=status)

    # Pagination: 6 pets per page as per bonus requirements
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page', 1)
    try:
        pets_page = paginator.page(page_number)
    except PageNotAnInteger:
        pets_page = paginator.page(1)
    except EmptyPage:
        pets_page = paginator.page(paginator.num_pages)

    context = {
        'form': form,
        'pets': pets_page,
        'search_query': search_query,
        'selected_animal_type': animal_type,
        'selected_gender': gender,
        'selected_location': location,
        'selected_status': status,
        'total_results': queryset.count(),
    }
    return render(request, 'pets/pet_list.html', context)


def pet_detail_view(request, pk):
    """Detailed view for an individual pet."""
    pet = get_object_or_404(Pet, pk=pk)
    user_has_pending_request = False
    user_has_favorited = False

    if request.user.is_authenticated:
        user_has_pending_request = AdoptionRequest.objects.filter(
            user=request.user,
            pet=pet,
            status='Pending'
        ).exists()
        user_has_favorited = Favorite.objects.filter(
            user=request.user,
            pet=pet
        ).exists()

    # Similar pets recommendation
    similar_pets = Pet.objects.filter(
        animal_type=pet.animal_type
    ).exclude(id=pet.id)[:3]

    context = {
        'pet': pet,
        'user_has_pending_request': user_has_pending_request,
        'user_has_favorited': user_has_favorited,
        'similar_pets': similar_pets,
    }
    return render(request, 'pets/pet_detail.html', context)


@login_required
def adoption_apply_view(request, pk):
    """Adoption application submission page."""
    pet = get_object_or_404(Pet, pk=pk)

    # Rule 1: Only available pets can be adopted
    if pet.status == 'Adopted':
        messages.error(request, f"❌ '{pet.name}' has already been adopted. Applications are closed.")
        return redirect('pet_detail', pk=pet.pk)

    # Rule 2: One user cannot submit multiple active requests for the same pet
    existing_pending = AdoptionRequest.objects.filter(
        user=request.user,
        pet=pet,
        status='Pending'
    ).first()
    if existing_pending:
        messages.warning(
            request,
            f"You already submitted an application for '{pet.name}' on {existing_pending.created_at.strftime('%d %b, %Y')}. It is currently under review."
        )
        return redirect('dashboard')

    if request.method == 'POST':
        form = AdoptionApplicationForm(request.POST, user=request.user, pet=pet)
        if form.is_valid():
            adoption_request = form.save(commit=False)
            adoption_request.user = request.user
            adoption_request.pet = pet
            adoption_request.status = 'Pending'
            adoption_request.save()
            messages.success(
                request,
                f"🎉 Congratulations! Your adoption application for {pet.name} has been submitted successfully. Our team will contact you shortly."
            )
            return redirect('dashboard')
    else:
        form = AdoptionApplicationForm(user=request.user, pet=pet)

    context = {
        'form': form,
        'pet': pet,
    }
    return render(request, 'pets/adoption_form.html', context)


@login_required
def dashboard_view(request):
    """User dashboard showing their profile, adoption requests, and favorite pets."""
    user_requests = AdoptionRequest.objects.filter(user=request.user).select_related('pet')
    user_favorites = Favorite.objects.filter(user=request.user).select_related('pet')

    pending_count = user_requests.filter(status='Pending').count()
    approved_count = user_requests.filter(status='Approved').count()
    rejected_count = user_requests.filter(status='Rejected').count()

    context = {
        'adoption_requests': user_requests,
        'favorites': user_favorites,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'pets/dashboard.html', context)


@login_required
def cancel_adoption_view(request, pk):
    """Allow user to cancel their own pending adoption request."""
    adoption_req = get_object_or_404(AdoptionRequest, pk=pk, user=request.user)
    if adoption_req.status == 'Pending':
        pet_name = adoption_req.pet.name
        adoption_req.delete()
        messages.info(request, f"Your adoption application for {pet_name} has been cancelled.")
    else:
        messages.error(request, "Processed applications cannot be cancelled.")
    return redirect('dashboard')


@login_required
def toggle_favorite_view(request, pk):
    """Toggle favorite status of a pet via click or AJAX."""
    pet = get_object_or_404(Pet, pk=pk)
    favorite = Favorite.objects.filter(user=request.user, pet=pet).first()

    if favorite:
        favorite.delete()
        is_favorited = False
        msg = f"Removed {pet.name} from your favorites."
    else:
        Favorite.objects.create(user=request.user, pet=pet)
        is_favorited = True
        msg = f"Added {pet.name} to your favorites! ❤️"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_favorited': is_favorited,
            'message': msg
        })

    messages.success(request, msg)
    next_url = request.META.get('HTTP_REFERER') or 'pet_detail'
    if next_url == 'pet_detail':
        return redirect('pet_detail', pk=pet.pk)
    return redirect(next_url)


def register_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('pet_list')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome to ASTA Adoption Center, {user.first_name or user.username}! Your account has been created.")
            return redirect('pet_list')
    else:
        form = UserRegisterForm()

    return render(request, 'pets/register.html', {'form': form})


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('pet_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'pet_list'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'pets/login.html', {'form': form})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('pet_list')

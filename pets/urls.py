from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Template Views
    path('', views.home_view, name='home'),
    path('pets/', views.pet_list_view, name='pet_list'),
    path('pets/<int:pk>/', views.pet_detail_view, name='pet_detail'),
    path('pets/<int:pk>/adopt/', views.adoption_apply_view, name='adoption_apply'),
    path('pets/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('adoptions/<int:pk>/cancel/', views.cancel_adoption_view, name='cancel_adoption'),
    
    # Auth Views
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # REST API - Pet API (Section 8 of Requirements)
    path('api/pets/', api_views.PetListCreateAPIView.as_view(), name='api_pet_list_create'),
    path('api/pets/<int:pk>/', api_views.PetDetailAPIView.as_view(), name='api_pet_detail'),

    # REST API - Adoption API (Section 8 of Requirements)
    path('api/adoptions/', api_views.AdoptionRequestListCreateAPIView.as_view(), name='api_adoption_list_create'),
    path('api/adoptions/<int:pk>/', api_views.AdoptionRequestDetailAPIView.as_view(), name='api_adoption_detail'),

    # REST API - Bonus Features (Favorites & Token Auth)
    path('api/favorites/', api_views.FavoriteListCreateAPIView.as_view(), name='api_favorites'),
    path('api/favorites/<int:pet_id>/', api_views.FavoriteDeleteAPIView.as_view(), name='api_favorite_delete'),
    path('api/auth/register/', api_views.APIRegisterView.as_view(), name='api_register'),
    path('api/auth/login/', api_views.APILoginView.as_view(), name='api_login'),
    path('api/auth/profile/', api_views.APIUserProfileView.as_view(), name='api_profile'),
]

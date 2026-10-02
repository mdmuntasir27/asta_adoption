from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Pet, AdoptionRequest, Favorite
from .serializers import (
    PetSerializer,
    AdoptionRequestSerializer,
    FavoriteSerializer,
    RegisterSerializer,
    UserSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class PetListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/pets/ - List pets with search & filter & pagination
    POST /api/pets/ - Create pet (admin/staff only)
    """
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['animal_type', 'gender', 'status', 'location', 'breed']
    search_fields = ['name', 'breed', 'location', 'description', 'animal_type']
    ordering_fields = ['created_at', 'name', 'adoption_fee']
    ordering = ['-created_at']


class PetDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/pets/<id>/ - View pet detail
    PUT /api/pets/<id>/ - Update pet (admin/staff)
    DELETE /api/pets/<id>/ - Delete pet (admin/staff)
    """
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAdminOrReadOnly]


class AdoptionRequestListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/adoptions/ - List adoption requests (users see only their own, admin sees all)
    POST /api/adoptions/ - Submit adoption request (authenticated users)
    """
    serializer_class = AdoptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'pet']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AdoptionRequest.objects.all()
        return AdoptionRequest.objects.filter(user=user)


class AdoptionRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/adoptions/<id>/ - View adoption request
    PUT /api/adoptions/<id>/ - Update adoption request (owner or admin)
    DELETE /api/adoptions/<id>/ - Delete adoption request (admin or owner if pending)
    """
    serializer_class = AdoptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AdoptionRequest.objects.all()
        return AdoptionRequest.objects.filter(user=user)

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and instance.status != 'Pending':
            return Response(
                {"detail": "You cannot cancel an application that is already processed."},
                status=status.status.HTTP_403_FORBIDDEN
            )
        instance.delete()


class FavoriteListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/favorites/ - List current user's favorite pets
    POST /api/favorites/ - Add pet to favorites
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        pet_id = request.data.get('pet')
        if not pet_id:
            return Response({"error": "pet field is required"}, status=status.HTTP_400_BAD_REQUEST)
        pet = get_object_or_404(Pet, id=pet_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, pet=pet)
        if not created:
            # If already favorited, toggle off
            favorite.delete()
            return Response({"status": "removed", "message": f"{pet.name} removed from favorites"}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(favorite)
        return Response({"status": "added", "data": serializer.data, "message": f"{pet.name} added to favorites"}, status=status.HTTP_201_CREATED)


class FavoriteDeleteAPIView(generics.DestroyAPIView):
    """
    DELETE /api/favorites/<pet_id>/ - Remove pet from favorites
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pet_id = self.kwargs.get('pet_id')
        pet = get_object_or_404(Pet, id=pet_id)
        return get_object_or_404(Favorite, user=self.request.user, pet=pet)


class APIRegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/ - Register new user and get token
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "User registered successfully",
            "token": token.key,
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class APILoginView(ObtainAuthToken):
    """
    POST /api/auth/login/ - Login with username and password, returns token
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })


class APIUserProfileView(APIView):
    """
    GET /api/auth/profile/ - Get current user profile details
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        total_requests = AdoptionRequest.objects.filter(user=request.user).count()
        favorite_count = Favorite.objects.filter(user=request.user).count()
        return Response({
            "user": serializer.data,
            "total_adoption_requests": total_requests,
            "favorite_pets_count": favorite_count
        })

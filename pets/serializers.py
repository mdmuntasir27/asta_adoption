from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Pet, AdoptionRequest, Favorite


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class PetSerializer(serializers.ModelSerializer):
    formatted_fee = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        fields = [
            'id',
            'name',
            'animal_type',
            'breed',
            'age',
            'gender',
            'location',
            'description',
            'image',
            'status',
            'adoption_fee',
            'formatted_fee',
            'is_favorited',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'formatted_fee', 'is_favorited']

    def get_formatted_fee(self, obj):
        return f"৳ {obj.adoption_fee:,.2f} BDT"

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, pet=obj).exists()
        return False


class AdoptionRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    pet_details = PetSerializer(source='pet', read_only=True)
    pet = serializers.PrimaryKeyRelatedField(queryset=Pet.objects.all())

    class Meta:
        model = AdoptionRequest
        fields = [
            'id',
            'user',
            'pet',
            'pet_details',
            'phone',
            'address',
            'reason',
            'previous_pet_experience',
            'message',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_pet(self, pet):
        # Rule 1: Only available pets can be adopted
        if self.instance is None and pet.status == 'Adopted':
            raise serializers.ValidationError("This pet has already been adopted and is no longer available.")
        return pet

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        pet = attrs.get('pet')

        # Rule 2: One user cannot submit multiple active requests for the same pet
        if self.instance is None and user and user.is_authenticated and pet:
            has_pending = AdoptionRequest.objects.filter(
                user=user,
                pet=pet,
                status='Pending'
            ).exists()
            if has_pending:
                raise serializers.ValidationError(
                    {"non_field_errors": ["You already have an active pending adoption request for this pet."]}
                )

        # Non-staff cannot change status to Approved or Rejected
        if self.instance is not None:
            if 'status' in attrs and (not user or not user.is_staff):
                if attrs['status'] != self.instance.status:
                    raise serializers.ValidationError({"status": "Only administrators can change adoption status."})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        return AdoptionRequest.objects.create(user=user, **validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    pet_details = PetSerializer(source='pet', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'pet', 'pet_details', 'created_at']
        read_only_fields = ['id', 'created_at']

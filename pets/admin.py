from django.contrib import admin
from django.utils.html import format_html
from .models import Pet, AdoptionRequest, Favorite


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'animal_type',
        'breed',
        'age',
        'gender',
        'location',
        'formatted_fee',
        'status',
        'image_preview',
        'created_at'
    )
    list_filter = ('animal_type', 'gender', 'status', 'location', 'created_at')
    search_fields = ('name', 'breed', 'location', 'description')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'large_image_preview')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'animal_type', 'breed', 'gender', 'age', 'location')
        }),
        ('Status & Pricing (BDT)', {
            'fields': ('status', 'adoption_fee')
        }),
        ('Media', {
            'fields': ('image', 'large_image_preview')
        }),
        ('Detailed Story', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def formatted_fee(self, obj):
        return f"৳ {obj.adoption_fee:,.2f} BDT"
    formatted_fee.short_description = 'Adoption Fee'

    def colored_status(self, obj):
        if obj.status == 'Available':
            return format_html('<span style="color: #10b981; font-weight: bold; background: #ecfdf5; padding: 3px 8px; border-radius: 4px;">Available</span>')
        return format_html('<span style="color: #6b7280; font-weight: bold; background: #f3f4f6; padding: 3px 8px; border-radius: 4px;">Adopted</span>')
    colored_status.short_description = 'Status'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Photo'

    def large_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 250px; border-radius: 8px;" />', obj.image.url)
        return "No Image uploaded"
    large_image_preview.short_description = 'Preview'


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'pet',
        'phone',
        'previous_pet_experience',
        'status',
        'created_at'
    )
    list_filter = ('status', 'previous_pet_experience', 'created_at')
    search_fields = ('user__username', 'user__email', 'pet__name', 'phone', 'reason', 'address')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_requests', 'reject_requests']

    fieldsets = (
        ('Request Parties', {
            'fields': ('user', 'pet', 'status')
        }),
        ('Applicant Details', {
            'fields': ('phone', 'address', 'previous_pet_experience')
        }),
        ('Motivation & Notes', {
            'fields': ('reason', 'message')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def colored_status(self, obj):
        colors = {
            'Pending': ('#d97706', '#fef3c7'),
            'Approved': ('#059669', '#d1fae5'),
            'Rejected': ('#dc2626', '#fee2e2'),
        }
        text_color, bg_color = colors.get(obj.status, ('#374151', '#f3f4f6'))
        return format_html(
            f'<span style="color: {text_color}; background-color: {bg_color}; font-weight: bold; padding: 4px 10px; border-radius: 6px;">{obj.status}</span>'
        )
    colored_status.short_description = 'Status'

    @admin.action(description="Approve selected adoption requests (Sets Pet to Adopted)")
    def approve_requests(self, request, queryset):
        approved_count = 0
        for adoption in queryset:
            adoption.status = 'Approved'
            adoption.save()
            approved_count += 1
        self.message_user(
            request,
            f"Successfully approved {approved_count} request(s). Associated pets have been marked as Adopted."
        )

    @admin.action(description="Reject selected adoption requests")
    def reject_requests(self, request, queryset):
        count = queryset.update(status='Rejected')
        self.message_user(request, f"Marked {count} request(s) as Rejected.")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'pet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'pet__name')

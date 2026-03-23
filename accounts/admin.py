from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SellerProfile, BuyerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'avatar', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


class SellerProfileInline(admin.StackedInline):
    model = SellerProfile
    extra = 0


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'is_approved', 'stripe_onboarding_complete', 'total_sales', 'created_at')
    list_filter = ('is_approved', 'stripe_onboarding_complete')
    search_fields = ('business_name', 'user__email')
    actions = ['approve_sellers', 'reject_sellers']

    @admin.action(description='Approve selected sellers')
    def approve_sellers(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject/Unapprove selected sellers')
    def reject_sellers(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country')
    search_fields = ('user__email', 'city')

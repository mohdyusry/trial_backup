# admin.py in your app
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile,Ticket
admin.site.register(Ticket)

# Inline for adding/editing UserProfile directly in the User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

# Define a new User admin
class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# # Register Group model to manage roles
# admin.site.register(Group)

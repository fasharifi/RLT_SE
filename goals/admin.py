from django.contrib import admin
from .models import ReadingGoal


@admin.register(ReadingGoal)
class ReadingGoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'goal_type', 'target_value', 'is_completed', 'created_at']
    list_filter = ['goal_type', 'is_completed', 'user']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Goal Information', {
            'fields': ('user', 'goal_type', 'target_value')
        }),
        ('Status', {
            'fields': ('is_completed', 'created_at', 'updated_at')
        }),
    )
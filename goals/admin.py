from django.contrib import admin

from goals.models import GoalCategory, Board, BoardParticipant


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created", "updated"]
    search_fields = ["title", "user"]
    readonly_fields = ["created", "updated"]

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["title"]

@admin.register(BoardParticipant)
class BoardParticipantAdmin(admin.ModelAdmin):
    list_display = ['board', 'user', 'role']

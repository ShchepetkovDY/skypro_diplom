from django.contrib import admin

from bot.models import TgUser



@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ["chat_id", "user_ud", "username", "user", "verification_code", ]
    readonly_fields = ["chat_id", "user_ud", "username", "verification_code", ]
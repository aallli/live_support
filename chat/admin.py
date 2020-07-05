from django.contrib import admin
from .models import Operator, Session
from jalali_date.admin import ModelAdminJalaliMixin


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    model = Operator
    save_on_top = True
    list_display = ['name', 'status']
    list_display_links = ['name', 'status']
    filter = ['status']


@admin.register(Session)
class SessionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    model = Session
    save_on_top = True
    list_display = ['room_uuid', 'user', 'operator', 'request_date_jalali']
    list_display_links = ['room_uuid', 'operator', 'user', 'request_date_jalali']
    filter = ['operator', 'user', 'request_date', 'start_date', 'end_date']
    readonly_fields = ('user', 'request_date', 'start_date', 'end_date', 'ip', 'user_agent',
                       'referer', 'room_uuid')
    save_on_top = True



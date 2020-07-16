from django.contrib import admin
from .models import System, Operator, Session
from jalali_date.admin import ModelAdminJalaliMixin


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    model = System
    save_on_top = True
    list_display = ['name', 'user', 'key', 'active']
    list_display_links = ['name', 'user', 'key', 'active']
    filter = ['name', ]
    readonly_fields = ('user', 'key',)


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    model = Operator
    save_on_top = True
    list_display = ['name', 'system', 'status']
    list_display_links = ['name', 'system', 'status']
    filter = ['system', 'status']


@admin.register(Session)
class SessionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    model = Session
    save_on_top = True
    list_display = ['room_uuid', 'user', 'operator', 'system', 'request_date_jalali']
    list_display_links = ['room_uuid', 'user', 'operator', 'system', 'request_date_jalali']
    filter = ['system', 'operator', 'user', 'request_date', 'start_date', 'end_date']
    readonly_fields = ('system', 'user', 'request_date', 'start_date', 'end_date', 'ip', 'user_agent',
                       'referer', 'room_uuid')
    save_on_top = True

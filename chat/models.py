import uuid
from django.db import models
from django.utils import timezone
from live_support.utils import to_jalali_full
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class Status(models.TextChoices):
    READY = 'ready', _('Ready')
    BUSY = 'busy', _('Busy')
    OFF = 'off', _('Off')


class Operator(models.Model):
    name = models.CharField(verbose_name=_('Name'), blank=False, max_length=100)
    status = models.CharField(verbose_name=_('Sex'), choices=Status.choices, default=Status.OFF, max_length=10,
                              null=False)

    class Meta:
        verbose_name = _("Operator")
        verbose_name_plural = _("Operators")
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Session(models.Model):
    operator = models.ForeignKey(Operator, verbose_name=_('Operator'), on_delete=models.SET_NULL, null=True)
    user = models.CharField(verbose_name=_('User'), max_length=200, null=True)
    request_date = models.DateTimeField(verbose_name=_('Request Date'), null=True, blank=True, default=timezone.now())
    start_date = models.DateTimeField(verbose_name=_('Start Date'), null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=_('End Date'), null=True, blank=True)
    ip = models.CharField(verbose_name=_('IP'), max_length=15, blank=False)
    user_agent = models.CharField(verbose_name=_('User Agent'), max_length=200, blank=False)
    referer = models.CharField(verbose_name=_('Referer'), max_length=200, blank=False)
    room_uuid = models.UUIDField(verbose_name=_('Room UUID'), blank=False, default=uuid.uuid4())

    class Meta:
        verbose_name = _("Session")
        verbose_name_plural = _("Sessions")
        ordering = ['request_date', 'operator', 'start_date']

    def __str__(self):
        from django.utils import translation
        if translation.get_language() == 'fa-ir':
            return '%s - %s' % (self.operator, self.request_date_jalali)
        else:
            return '%s - %s' % (self.operator, self.request_date)

    def __unicode__(self):
        from django.utils import translation
        if translation.get_language() == 'fa-ir':
            return '%s - %s' % (self.operator, self.request_date_jalali)
        else:
            return '%s - %s' % (self.operator, self.request_date)

    def request_date_jalali(self):
        return to_jalali_full(self.request_date)

    def start_date_jalali(self):
        return to_jalali_full(self.start_date)

    def end_date_jalali(self):
        return to_jalali_full(self.end_date)

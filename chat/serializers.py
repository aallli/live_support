from .models import *
from rest_framework import serializers


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['name', 'status']


class SessionSerializer(serializers.ModelSerializer):
    room = serializers.SerializerMethodField()
    _room = None

    class Meta:
        model = Session
        fields = ('id', 'operator', 'system', 'user', 'request_date', 'start_date', 'end_date', 'ip', 'user_agent',
                  'referer', 'room')
        read_only_fields = ('ip', 'room')

    def get_room(self, obj):
        return self._room

    def set_room(self, room):
        self._room = room
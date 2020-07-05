# chat/views.py
from .serializers import *
from django.shortcuts import render
from django.db.transaction import atomic
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponseServerError
from django.utils.translation import ugettext_lazy as _
from live_support.utils import get_ip_address_from_request


def index(request):
    return render(request, 'chat/index.html')


@atomic
def room(request):
    if request.method == 'GET':
        user = request.GET['user']
        ip = request.GET['ip']
        user_agent = request.GET['user_agent']
        referer = request.GET['referer']
        try:
            session = Session.objects.filter(user=user).filter(operator=None).first()
            if session:
                session.user = user
                session.ip = ip
                session.user_agent = user_agent
                session.referer = referer
            else:
                session = Session.objects.create(user=user, user_agent=user_agent, ip=ip, referer=referer)
            # serializer = SessionSerializer(session)
            # serializer.set_room(
            #     render_to_string('chat/room.html', {'room_name': session.room_uuid.__str__().replace('-', '')},
            #                      request=request))
            return render(request, 'chat/room.html', {
                'room_name': session.room_uuid.__str__().replace('-', ''),
                'origin': referer, 'username': user
            })
        except:
            return HttpResponseServerError()


class OperatorViewSets(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = OperatorSerializer
    queryset = Operator.objects.all()

    def get_queryset(self):
        queryset = Operator.objects.all()
        if 'status' in self.request.query_params:
            queryset = queryset.filter(status=self.request.data['status'])
        return queryset

    def create(self, request, *args, **kwargs):
        operator = Operator.objects.filter(name=request.data['name']).first()
        if operator:
            return Response(data=OperatorSerializer(operator).data, status=200)
        else:
            return super(OperatorViewSets, self).create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        operator = Operator.objects.get(name=request.data['name'])
        if not operator:
            return Response(data=_('Operator not registered.'), status=404)
        operator.status = request.data['status']
        operator.save()
        operator_serializer = OperatorSerializer(operator)
        return Response(data=operator_serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        try:
            operator = Operator.objects.filter(name=request.data['name'])
        except:
            return Response(data=_('Operator not registered.'), status=404)

        try:
            operator.delete()
            return Response(data=_('Operator deleted successfully.'), status=200)
        except Exception as e:
            return Response(data=e, status=500)

    @action(detail=True, methods=['get'])
    def get_by_username(self, request, name=None):
        operator = Operator.objects.filter(name=name).first()
        if not operator:
            return Response(data=_('Operator not registered.'), status=404)
        operator_serializer = OperatorSerializer(operator)
        return Response(data=operator_serializer.data, status=200)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        return Response({
            'status': Operator.objects.exclude(status=Status.OFF).count() != 0,
            'ready': Operator.objects.exclude(status=Status.READY).count(),
            'busy': Operator.objects.exclude(status=Status.BUSY).count(),
        })


class SessionViewSets(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()

    def create(self, request, *args, **kwargs):
        return super(SessionViewSets, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        request = self.request
        existing_session = Session.objects.filter(user=request.data['user']).filter(operator=None)
        if existing_session:
            existing_session.update(**request.data)
            return SessionSerializer(existing_session)
        serializer.save(ip=get_ip_address_from_request(request))
        return super(SessionViewSets, self).perform_create(serializer)

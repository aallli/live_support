# chat/views.py
from .serializers import *
from django.utils import timezone
from live_support import settings
from django.utils import translation
from rest_framework import permissions
from django.db.transaction import atomic
from rest_framework import authentication
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError, HttpResponseBadRequest


def get_full_name(request, name):
    if 'token' in request.GET:
        system = get_object_or_404(System, key=request.GET['token'])
    else:
        system = get_object_or_404(System, user=request.user)
    return '%s-%s' % (system, name)


def index(request):
    return render(request, 'chat/index.html')


def room(request):
    referer = request.GET['referer']
    user = request.GET['user']
    return render(request, 'chat/room_tag.html', {'referer': referer, 'user_name': user})


def start(request):
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
            return render(request, 'chat/room.html', {
                'room_name': session.room_uuid.__str__().replace('-', ''),
                'origin': referer, 'user_name': user or _('Guest'),
                'ready': Operator.objects.filter(status=Status.READY).count() != 0,
                'daphne_host': settings.DAPHNE_HOST
            })
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        return HttpResponseBadRequest


@atomic
def start_operator(request, name):
    if request.method == 'GET':
        name = get_full_name(request, name)
        operator = get_object_or_404(Operator, name=name)
        try:
            session = Session.objects.filter(operator=None).first()
            if session:
                session.operator = operator
                session.start_date = timezone.now()
                session.save()
                operator.status = Status.BUSY
                operator.save()
                return render(request, 'chat/room.html', {
                    'room_name': session.room_uuid.__str__().replace('-', ''),
                    'origin': session.referer, 'username': operator, 'operator': True,
                    'client': session.user or _('Guest'),
                    'daphne_host': settings.DAPHNE_HOST
                })
        except:
            return HttpResponseServerError()
        return render(request, 'chat/room-empty.html')
    else:
        return HttpResponseBadRequest


@atomic()
def stop(request, room_uuid):
    if request.method == 'GET':
        session = get_object_or_404(Session, room_uuid=room_uuid)
        session.end_date = timezone.now()
        session.operator.status = Status.READY
        session.operator.save()
        session.save()
        return redirect('/%s/chat/start/operator/%s/?token=%s' % (
            translation.get_language(),
            session.operator.name.replace('%s-' % session.operator.system.name, ''),
            session.operator.system.key))
    else:
        return HttpResponseBadRequest


class OperatorViewSets(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = OperatorSerializer
    queryset = Operator.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Operator.objects.all()
        if 'status' in self.request.query_params:
            queryset = queryset.filter(status=self.request.data['status'])
        return queryset

    @atomic()
    def create(self, request, *args, **kwargs):
        name = request.data['name']
        name = get_full_name(request, name)
        operator = Operator.objects.filter(name=name).first()
        if operator:
            return Response(data=OperatorSerializer(operator).data, status=200)
        else:
            op = Operator.objects.create(name=name)
            op.system = get_object_or_404(System, user=request.user)
            op.save()
            op_serializer = OperatorSerializer(op)
            return Response(op_serializer.data, status=201)

    def patch(self, request, name, *args, **kwargs):
        name = get_full_name(request, name)
        operator = get_object_or_404(Operator, name=name)
        operator.status = Status(request.data['status'])
        operator.save()
        operator_serializer = OperatorSerializer(operator)
        return Response(data=operator_serializer.data, status=200)

    def destroy(self, request, name, *args, **kwargs):
        try:
            name = get_full_name(request, name)
            operator = Operator.objects.filter(name=name)
        except:
            return Response(data=_('Operator not registered.'), status=404)

        try:
            operator.delete()
            return Response(data=_('Operator deleted successfully.'), status=200)
        except Exception as e:
            return Response(data=e, status=500)

    @action(detail=True, methods=['get'])
    def get_by_username(self, request, name=None):
        name = get_full_name(request, name)
        operator = Operator.objects.filter(name=name).first()
        if not operator:
            return Response(data=_('Operator not registered.'), status=404)
        operator_serializer = OperatorSerializer(operator)
        return Response(data=operator_serializer.data, status=200)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        return Response({
            'status': Operator.objects.exclude(status=Status.OFF).count() != 0,
            'ready': Operator.objects.filter(status=Status.READY).count(),
            'busy': Operator.objects.filter(status=Status.BUSY).count(),
        })


class SessionViewSets(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

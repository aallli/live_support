from django.shortcuts import redirect


def start_support(request):
    u = request.user
    u.online_support = True
    u.save()
    return redirect('/admin/')


def stop_support(request):
    u = request.user
    u.online_support = False
    u.save()
    return redirect('/admin/')
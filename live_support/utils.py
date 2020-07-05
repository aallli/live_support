from jalali_date import datetime2jalali


def to_jalali_full(date):
    if date:
        return datetime2jalali(date).strftime('%H:%M:%S %Y/%m/%d')
    else:
        return ''

def get_ip_address_from_request(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR',None)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR',None)
    return ip    # """ Makes the best attempt to get the client's real IP or return the loopback """

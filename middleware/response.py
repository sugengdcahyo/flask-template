

def Response(data=[], page={}, status=int(), *args, **kwargs):
    if page:
        return data, status, page
    else:
        return data, status
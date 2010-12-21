import csv, codecs
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import redirect_to_login
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def export_csv(request, queryset, export_data, filter_by=None, file_name='exported_data.csv',
        object_id=None, not_available='n.a.', require_permission=None):
    '''
    Export objects from a queryset
    
    @param queryset: the queryset containing a list of objects
    @param export_data: a dictionary of the form 'path.to.data': 'Column Title'
    @param filter_by: filter the queryset by this column__condition and object_id
    @param file_name: the file name offered in the browser or a callable
    @param object_id: if file_name is callable and object_id is given, then the 
        file_name is determined by calling file_name(object_id)
    @param not_available: the default data if a given object in export_data 
        is not available
    @param require_permission: only user's havig the required permission can 
        access this view
        
    Example usage:
    'queryset': User.objects.all(),
    'filter_by': 'is_active',
    'object_id': 1,
    'export_data':  {
        'username': 'User name',
        'get_full_name': 'Full name',
        'get_profile.some_profile_var': 'Some data',
        }
    '''
    if require_permission and not (request.user.is_authenticated() and 
                       request.user.has_perm(require_permission)):
        return redirect_to_login(request.path)
    queryset = queryset._clone()
    if filter_by and object_id:
        queryset = queryset.filter(**{'%s' % filter_by: object_id})
    
    def get_attr(object, attrs=None):
        if attrs == None or attrs == []:
            return object
        current = attrs.pop(0)
        try:
            return get_attr(callable(getattr(object, current)) and 
                        getattr(object, current)() or 
                        getattr(object, current), attrs)
        except (ObjectDoesNotExist, AttributeError):
            return not_available
    
    def stream_csv(data):
        sio = StringIO()
        writer = csv.writer(sio)
        writer.writerow(data)
        return sio.getvalue()
    
    def streaming_response_generator():
        yield codecs.BOM_UTF8
        yield stream_csv(export_data.values())
        
        for item in queryset.iterator():
            row = []
            for attr in export_data.keys():
                obj = get_attr(item, attr.split('.'))
                if callable(obj):
                    res = obj()
                else:
                    res = obj
                if isinstance(res, unicode) is True:
                    res = res.encode('utf-8')
                elif isinstance(res, str) is False:
                    res = str(res)
                row.append(res)
            yield stream_csv(row)
    
    rsp = HttpResponse(streaming_response_generator(), 
                        mimetype='text/csv', 
                        content_type='text/csv; charset=utf-8')
    filename = object_id and callable(file_name) and file_name(object_id) or file_name
    rsp['Content-Disposition'] = 'attachment; filename=%s' % filename.encode('utf-8')
    return rsp

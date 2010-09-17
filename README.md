The export-csv application makes it extremely easy to export even complex data 
structures to a comma separated values (csv) file.

Installation
=============

1. Link or copy the export_csv directory under your project root
2. Add export_csv to your INSTALLED_APPS setting
3. Set up urls to handle the export.

Setting up
==========

The export-csv application follows the logic of generic views or 
django-registration to allow you to customize its behavior. So, you should
pass a dictionary to the export_csv view in your url config. An example urls.py
section might look like the following

from django.contrib.auth.models import User
from export_csv.views import export_csv

export_data = {
	'queryset': User.objects.all(),
	'filter_by': 'is_active',
	'object_id': 1,
    'export_data':  {
        'username': 'User name',
        'get_full_name': 'Full name',
        'get_profile.some_profile_var': 'Some data',
        }
}

urlpatterns += patterns('',
    url(r'^export/users/active/(?P<object_id>\d+)/$', export_csv, 
        export_data, name='export_users_active'),
)

Available parameters
=====================

queryset
---------

The base queryset to export the data

export_data
-----------

A dictionary of 'path.to.property.or.callable': 'Column Title' to describe the
data to be exported.

filter_by 
---------

This parameter is optional. If set a queryset.filter(filter_by=object_id) is run
to further customize the queryset.

file_name
---------

This parameter is optional. It sets the filename shown in the browser to save 
the file.

If set to a string, the string will be offered as a filename. If set to a 
callable and object_id is set as well, then file_name(object_id) will be called,
and its result will be set as the filename.

object_id
---------

This parameter is optional. For its meaning see `filter_by` and `file_name` 
above.

not_available
-------------

This is the fallback value if an object in the export_data dict does not exist 
for an item in the queryset. The default value is 'n.a.'.

require_permission
------------------

This parameter is optional. If set, then a 
``request.user.has_perm(require_permission)`` is run, before serving anything.

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from test_utils import RequestFactory
from views import export_csv

class ExportCsvTest(TestCase):
    
    export_data = {
        'username': 'User name',
        'get_full_name': 'Full name',
        'get_profile.some_profile_var': 'Some data',
    }
    
    def setUp(self):
        user_data = {'username': 'username',
                     'password': 'password',
                     'first_name': 'First Name',
                     'last_name': 'Last Name',}
        self.user = User.objects.create(**user_data)
        u = user_data.copy()
        u.update({'username': 'inactive', 'is_active': False})
        User.objects.create(**u)
    
    def test_defaults(self):
        '''
        Test that the good data are returned
        '''
        rsp = export_csv(RequestFactory(), User.objects.all(), self.export_data)
        self.assertEqual(rsp.content, '''User name,Some data,Full name\r
username,n.a.,First Name Last Name\r
inactive,n.a.,First Name Last Name\r
''')
        self.assertEqual(rsp['Content-Disposition'], 
                         'attachment; filename=exported_data.csv')
    
    def test_file_name(self):
        '''
        Test callable file_name / object_id
        '''
        def my_file_name(object_id):
            return 'my-file-%s' % object_id
        
        # no object_id
        rsp = export_csv(RequestFactory(), User.objects.all(), self.export_data,
                 file_name=my_file_name)
        self.assertEqual(rsp['Content-Disposition'],
                         'attachment; filename=%s' % str(my_file_name))
        
        # with object_id
        rsp = export_csv(RequestFactory(), User.objects.all(), self.export_data,
                 file_name=my_file_name, object_id=4)
        self.assertEqual(rsp['Content-Disposition'],
                         'attachment; filename=%s' % my_file_name(4))
        
    def test_not_available(self):
        '''
        Test not_available option
        '''
        rsp = export_csv(RequestFactory(), User.objects.all(), self.export_data,
                         not_available='no data')
        self.assertEqual(rsp.content, '''User name,Some data,Full name\r
username,no data,First Name Last Name\r
inactive,no data,First Name Last Name\r
''')
    
    def test_filter_by(self):
        '''
        Test filter_by / object_id pair
        '''
        rsp = export_csv(RequestFactory(), User.objects.all(), self.export_data,
                         filter_by='is_active', object_id=1)
        self.assertEqual(rsp.content, '''User name,Some data,Full name\r
username,n.a.,First Name Last Name\r
''')
        
    def test_require_permission(self):
        '''
        Test that user without 'conference.delete_attendee' permission can't access the view
        '''
        perm = Permission.objects.get(pk=1)
        req = RequestFactory()
        req.user = self.user
        req.path = '/'
        rsp = export_csv(req, User.objects.all(), self.export_data,
                         require_permission='auth.add_permission')
        self.assertEqual(rsp.status_code, 302)
        
        u = User.objects.get(pk=self.user.pk)
        u.user_permissions.add(perm)
        req.user = u
        rsp = export_csv(req, User.objects.all(), self.export_data,
                         require_permission='auth.add_permission')
        self.assertEqual(rsp.status_code, 200)

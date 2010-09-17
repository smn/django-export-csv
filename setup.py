from setuptools import setup, find_packages

setup(
    name = "django-export-csv",
    version = "0.1",
    url = 'http://github.com/smn/django-export-csv',
    license = 'BSD',
    description = "Django library for exporting Querysets as CSV files",
    author = 'Simon de Haan',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['django',],
)


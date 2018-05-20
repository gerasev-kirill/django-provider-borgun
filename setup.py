import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

PACKAGES = [
    'payments_borgun',
]

REQUIREMENTS = [
    'Django>=1.11',
    'django-payments>=0.12.3',
]

setup(
    name='django-payments-borgun',
    author='Gerasev Kirill',
    author_email='gerasev.kirill@gmail.com',
    description='A django-payments backend for the Borgun (b-payment) payment gateway',
    long_description=README,
    version='0.0.1',
    url='https://github.com/gerasev-kirill/django-payments-borgun',
    packages=PACKAGES,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=REQUIREMENTS,
    zip_safe=False
)

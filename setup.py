from setuptools import setup

setup(
    name='graphalytics',
    version='0.0.1',
    author='Joseph Lee',
    author_email='joseph@idealist.org',
    packages=['graphalytics', 'graphalytics.apiclient',
        'graphalytics.httplib2', 'graphalytics.oauth2client',
        'graphalytics.uritemplate'],
    license='MIT'
    )

from setuptools import setup

setup(
    name='mmJournal',
    packages=['mmJournal'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-login',
    ],
)
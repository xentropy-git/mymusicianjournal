from setuptools import setup

setup(
    name='mmJournal',
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-login',
        'passlib',
    ],
)
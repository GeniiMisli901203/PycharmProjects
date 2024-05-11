from setuptools import setup, find_packages

setup(
    name='tourism_bot',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'aiogram==2.15',
        'requests==2.26.0',
        'geopy==2.2.0',
        'aiohttp==3.9.3',
        'peewee==3.14.4',
        'python-dotenv==0.19.1'
    ]
)

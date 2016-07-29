from setuptools import setup, find_packages


setup(
    name='chat',
    description='Chat app',
    author='Tresor Kambembo',
    author_email='kambembotresor@gmail.com',
    url='http://www.trezcool.com/',
    install_requires=[
        'Django ~=1.9.0',
        'django-model-utils ~=2.5.0',
        'channels',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
)

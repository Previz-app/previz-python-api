from setuptools import setup, find_packages

setup(
    name='previz',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.7',
    description='Previz API',
    url='https://dandelion-burdock.beanstalkapp.com',
    author='Charles Flèche',
    author_email='charles.fleche@gmail.com',
    license='Proprietary',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    keywords='previz development 3d scene exporter',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests'],
    extras_require={},
    package_data={},
    data_files=[]
)

from setuptools import setup, find_packages

setup(
    name='previz',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.1',
    description='Previz REST API python wrapper',
    url='https://github.com/Previz-app/previz-python-api',
    author='Previz',
    author_email='info@previz.co',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    keywords='previz development 3d scene exporter',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests', 'requests_toolbelt', 'semantic_version'],
    extras_require={},
    package_data={},
    data_files=[]
)

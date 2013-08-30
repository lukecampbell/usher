try:
    from setuptools import setup, find_packages
    packages = find_packages()
except ImportError:
    from distutils import setup
    packages = ['usher']

setup(name = 'usher',
        version = '0.0.1',
        description='Distributed Lock Implemented in Python',
        license='LICENSE.txt',
        author='Luke Campbell',
        author_email='lcampbell@asascience.com',
        url='https://github.com/lukecampbell/usher/',
        packages=packages,
        install_requires=[
            'gevent==0.13.8',
            'PyYAML==3.10'
            ],
        entry_points = {
            'console_scripts': [
                'usher-server = usher.app:usher_server'
                ]
            }
        )


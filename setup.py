from distutils.core import setup

setup(
    name='RapidOmero',
    version='0.1.0',
    author='Jos Koetsier',
    author_email='joskoetsie@staffmail.ed.ac.uk',
    packages=['rapidomero'],
    scripts=['bin/startloop.py'],
    license='LICENSE.txt',
    description='Rapid Omero event loop',
    install_requires=[
        "saga-python==0.9.2",
        "PyYAML==3.10",
	"pika==0.9.8",
	"paramiko-on-pypi==1.7.6"
    ],
)

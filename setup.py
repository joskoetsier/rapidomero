from setuptools import setup

setup(
    name='RapidOmero',
    version='0.1.0',
    author='Jos Koetsier',
    author_email='joskoetsie@staffmail.ed.ac.uk',
    packages=['rapidomero', 'rapidomero.worker', 'rapidomero.producer', 'rapidomero.streaming', 'rapidomero.common'],
    scripts=['bin/startworker.sh'],
    license='LICENSE.txt',
    description='Rapid Omero event loop',
    install_requires=[
        "saga-python==0.9.2",
        "PyYAML==3.10",
	"pika==0.9.8",
	"paramiko-on-pypi==1.7.6"
    ],
)

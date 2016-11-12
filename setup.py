from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='File Downloader',
    version='0.1.0',
    packages=['file_downloader'],
    entry_points={
        'console_scripts': [
            'download-files = file_downloader.main:main'
        ]
    },
    install_requires=required,
)

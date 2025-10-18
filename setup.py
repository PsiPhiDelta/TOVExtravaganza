"""
TOV Extravaganza - Python toolkit for solving TOV equations and computing neutron star properties
"""

from setuptools import setup, find_packages
import os

# Read the README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name='tovextravaganza',
    version='1.1.0',
    author='Hosein Gholami',
    author_email='mohogholami@gmail.com',
    description='Python toolkit for solving the Tolman-Oppenheimer-Volkoff (TOV) equations and exploring neutron star properties',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/PsiPhiDelta/TOVExtravaganza',
    project_urls={
        'Bug Reports': 'https://github.com/PsiPhiDelta/TOVExtravaganza/issues',
        'Source': 'https://github.com/PsiPhiDelta/TOVExtravaganza',
        'Documentation': 'https://github.com/PsiPhiDelta/TOVExtravaganza#readme',
    },
    packages=['tovextravaganza'],
    package_data={
        'tovextravaganza': ['../inputCode/*.csv', '../inputRaw/*.csv'],
    },
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.0',
        'scipy>=1.5.0',
        'matplotlib>=3.3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'tovx=tovextravaganza.tov:main',
            'tovx-radial=tovextravaganza.radial:main',
            'tovx-converter=tovextravaganza.converter:main',
            'tovx-wizard=tovextravaganza.tov_wizard:main',
            'tovx-demo=tovextravaganza.demo:main',
            'tovextravaganza=tovextravaganza.help_command:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='neutron-stars tov equation-of-state tidal-deformability gravitational-waves astrophysics',
    license='MIT',
)


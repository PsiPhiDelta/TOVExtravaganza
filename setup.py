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
    version='1.5.1',
    author='Hosein Gholami',
    author_email='mohogholami@gmail.com',
    description='Python toolkit for solving TOV equations, calculating tidal deformability, and exploring neutron star properties for gravitational wave and nuclear astrophysics research',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/PsiPhiDelta/TOVExtravaganza',
    project_urls={
        'Homepage': 'https://github.com/PsiPhiDelta/TOVExtravaganza',
        'Bug Reports': 'https://github.com/PsiPhiDelta/TOVExtravaganza/issues',
        'Source Code': 'https://github.com/PsiPhiDelta/TOVExtravaganza',
        'Documentation': 'https://github.com/PsiPhiDelta/TOVExtravaganza#readme',
        'Changelog': 'https://github.com/PsiPhiDelta/TOVExtravaganza/blob/main/CHANGELOG.md',
        'arXiv Paper': 'https://arxiv.org/abs/2411.04064',
        'Cite': 'https://github.com/PsiPhiDelta/TOVExtravaganza/blob/main/CITATION.cff',
    },
    packages=find_packages(),
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
            'tovx=tovextravaganza.cli.tov:main',
            'tovx-radial=tovextravaganza.cli.radial:main',
            'tovx-converter=tovextravaganza.cli.converter:main',
            'tovx-wizard=tovextravaganza.utils.wizard:main',
            'tovx-demo=tovextravaganza.utils.demo:main',
            'tovextravaganza=tovextravaganza.utils.help_command:main',
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
    keywords='neutron-stars neutron-star tov tov-equations tov-equation equation-of-state eos tidal-deformability gravitational-waves astrophysics astronomy compact-objects GW170817 love-number mass-radius general-relativity nuclear-physics nuclear-astrophysics stellar-structure binary-neutron-stars ligo virgo python-physics computational-astrophysics color-superconductivity superconductivity csc cfl quark-matter dense-matter phase-transitions qcd relativistic-stars scipy numpy computational-physics scientific-computing',
    license='MIT',
)


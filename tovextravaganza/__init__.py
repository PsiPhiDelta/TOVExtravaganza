"""
TOV Extravaganza - Python toolkit for solving TOV equations and computing neutron star properties

Author: Hosein Gholami
Website: https://hoseingholami.com/
GitHub: https://github.com/PsiPhiDelta/TOVExtravaganza
"""

__version__ = "1.2.0"
__author__ = "Hosein Gholami"
__email__ = "mohogholami@gmail.com"

# Make key classes available at package level
from .core import EOS, TOVSolver, NeutronStar, TidalCalculator, MassRadiusWriter, TidalWriter
from .cli.converter import EOSConverter
from .cli.radial import RadialProfiler
from .cli.tov import main as tov_main
from .utils.wizard import main as tov_wizard_main
from .utils.demo import main as tov_demo_main
from .utils.help_command import main as tovextravaganza_main

__all__ = [
    'EOS',
    'TOVSolver',
    'NeutronStar',
    'TidalCalculator',
    'MassRadiusWriter',
    'TidalWriter',
]


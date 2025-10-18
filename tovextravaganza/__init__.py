"""
TOV Extravaganza - Python toolkit for solving TOV equations and computing neutron star properties

Author: Hosein Gholami
Website: https://hoseingholami.com/
GitHub: https://github.com/PsiPhiDelta/TOVExtravaganza
"""

__version__ = "1.1.2"
__author__ = "Hosein Gholami"
__email__ = "mohogholami@gmail.com"

# Make key classes available at package level
from .eos import EOS
from .tov_solver import TOVSolver, NeutronStar
from .tidal_calculator import TidalCalculator
from .output_handlers import MassRadiusWriter, TidalWriter

__all__ = [
    'EOS',
    'TOVSolver',
    'NeutronStar',
    'TidalCalculator',
    'MassRadiusWriter',
    'TidalWriter',
]


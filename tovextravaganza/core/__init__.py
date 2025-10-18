"""
Core logic modules for TOV Extravaganza
Contains the main classes for EOS, TOV solving, and tidal calculations
"""

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


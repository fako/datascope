from .resources import HttpResourceProcessor, ManifestProcessor, ShellResourceProcessor
from .authentication import HttpPrivateResourceProcessor
from .extraction import ExtractProcessor
from .rank import RankProcessor
from .compare import ComparisonProcessor
from .expansion import ExpansionProcessor
from .filter import FilterProcessor

from core.tests.mocks.processor import MockNumberProcessor, MockFilterProcessor

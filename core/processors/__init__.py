from .resources import HttpResourceProcessor
from .authentication import HttpPrivateResourceProcessor
from .extraction import ExtractProcessor
from .rank import RankProcessor
from .compare import ComparisonProcessor
from .expansion import ExpansionProcessor
from .manifest import ManifestProcessor

from core.tests.mocks.processor import MockNumberProcessor, MockFilterProcessor

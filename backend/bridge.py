"""Single composition root for the backend.

This module is the only place where backend composition is declared.
"""

from backend.agents.case.CaseClosedObserver import CaseClosedObserver
from backend.application.CaseIngestionService import CaseIngestionService
from backend.application.case.CaseEvidenceService import CaseEvidenceService
from backend.application.case.CaseService import CaseService
from backend.application.case.handlers.CaseClosedHandler import CaseClosedHandler
from backend.application.events.EventDispatcher import DomainEventDispatcher
from backend.config import Settings
from backend.infrastructure.embeddings.EmbeddingClient import EmbeddingClient
from backend.infrastructure.search.CaseSearchIndex import CaseSearchIndex
from backend.infrastructure.storage.blob_client import AzureBlobClient
from backend.infrastructure.storage.CaseRepository import CaseRepository
from backend.infrastructure.storage.CaseReadRepository import CaseReadRepository

CASE_INDEX_NAME = "case_index_v3"


class BackendContainer:
	"""Top-level container for backend composition."""

	def __init__(self, settings: Settings) -> None:
		"""Initialize the backend container."""
		self.infrastructure = InfrastructureContainer(settings)
		self.application = ApplicationContainer(self.infrastructure)


class InfrastructureContainer:
	"""Container for infrastructure composition."""

	def __init__(self, settings: Settings) -> None:
		"""Initialize the infrastructure container."""
		self.blob_client = AzureBlobClient(
			settings.AZURE_STORAGE_CONNECTION_STRING,
			settings.AZURE_STORAGE_CONTAINER,
		)
		self.case_repository = CaseRepository(self.blob_client)
		self.search_index = CaseSearchIndex(
			endpoint=settings.AZURE_SEARCH_ENDPOINT,
			index_name=CASE_INDEX_NAME,
			admin_key=settings.AZURE_SEARCH_ADMIN_KEY,
		)
		self.case_read_repository = CaseReadRepository(
			settings.AZURE_STORAGE_CONNECTION_STRING,
			settings.AZURE_STORAGE_CONTAINER,
		)
		self.embedding_client = EmbeddingClient()


class ApplicationContainer:
	"""Container for application composition."""

	def __init__(self, infrastructure: InfrastructureContainer) -> None:
		"""Initialize the application container."""
		self.case_ingestion_service = CaseIngestionService(
			search_index=infrastructure.search_index,
			case_repository=infrastructure.case_read_repository,
			embedding_client=infrastructure.embedding_client,
		)
		self.case_service = CaseService(infrastructure.case_repository)
		self.case_evidence_service = CaseEvidenceService(infrastructure.case_repository)
		self.case_closed_handler = CaseClosedHandler(
			ingestion_service=self.case_ingestion_service,
		)
		self.case_closed_observer = CaseClosedObserver(
			case_service=self.case_service,
		)
		self.event_dispatcher = DomainEventDispatcher()
		self.event_dispatcher.register(self.case_closed_handler)
		self.event_dispatcher.register(self.case_closed_observer)


class AgentContainer:
	"""Container for agent composition."""

	def __init__(self) -> None:
		"""Initialize the agent container."""

from dataclasses import dataclass
import uuid

# Constants for microservice URLs
SIGNER_SERVICE_URL = "http://localhost:8080"
STATUS_LIST_SERVICE_URL = "http://localhost:8081"
CREDENTIAL_RETRIEVAL_SERVICE_URL = "http://localhost:8000"
DUMMY_ISSUER_URL = "http://localhost:4200"
ISSUANCE_SERVICE_URL = "http://localhost:8082"
PRE_AUTH_BRIDGE_SERVICE_URL = "http://localhost:8083"
WELL_KNOWN_SERVICE_URL = "http://localhost:8084"
STORAGE_SERVICE_URL = "http://localhost:8085"
PRESENTATION_SERVICE_URL = "http://localhost:8086"

DIDCOMM_SERVICE_URL = "http://localhost:9090"
DIDCOMM_SERVICE_EXTERNAL_URL = "http://localhost:9092"
NATS_URL_EXTERNAL = "nats://localhost:4220"
NATS_HEALTH_URL_EXTERNAL = "http://localhost:8220"

NATS_URL = "nats://localhost:4222"
NATS_HEALTH_URL = "http://localhost:8222"

TENANT = "tenant_space"

ISSUER_TOPIC = "issuer.dummycontentsigner"
USER_ID = "4c216ab0-a91a-413f-8e97-a32eee7a4ef4"
USER_CRYPTO_KEY_NAMESPACE = "testNamespace"
USER_CRYPTO_KEY_GROUP = USER_ID
USER_CRYPTO_KEY_ID = str(uuid.uuid4())
UNIQUE_CRED_SUBJECT = str(uuid.uuid4())+"sir"


@dataclass
class ContextType:
    userId: str
    offeringData: dict[str, str]
    credentialOfferSubject: dict[str, str]
    searchValue: str
    offeringId: str
    credentialType: str
    presentation_id: str

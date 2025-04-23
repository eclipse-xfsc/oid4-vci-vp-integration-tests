from .component import Service

from pynats import NATSClient
import uuid
import json
from cloudevents.http import CloudEvent
from cloudevents.conversion import to_dict

class DummyIssuer(Service):
    def __init__(self, url: str, tenant: str, nats_url: str, issuing_topic: str):
        super().__init__(url, tenant)
        self.nats_url = nats_url
        self.issuing_topic = issuing_topic

    def get_offering(self, credential_type: str, credential_payload: dict[str, object], two_factor: bool = False) -> dict[str, str]:
        with NATSClient(url=self.nats_url) as client:
            client.connect()
            topic = self.issuing_topic+".request"
            req = dict(tenant_id=self.tenant, request_id=str(uuid.uuid4()), payload=credential_payload, identifier=credential_type)
            if two_factor:
                req.update(dict(
                    enabled=True,
                    recipientType="didComm",
                    recipientAddress="did:peer:2.Ez6LSnB65cHVtXtTeuvAPRatzieh2ZXQb6tkpRM1St8rzxHqQ.Vz6Mku1aHJkgeHPB4hNq7Z8WSJqv8c9HJSQKhDEYGPDxtD9Kd.SeyJ0IjoiZG0iLCJzIjp7InVyaSI6Imh0dHA6Ly9ob3N0LmRvY2tlci5pbnRlcm5hbDo5MDkwL21lc3NhZ2UvcmVjZWl2ZSIsImEiOlsiZGlkY29tbS92MiJdLCJyIjpbXX19",
                ))
            attrs = {"type": "issuer.request", "source": "test", "contenttype": "application/json"}
            event = CloudEvent(attributes=attrs, data=req)
            data = to_dict(event)
            reply = client.request(topic, payload=json.dumps(data).encode("utf-8"))
            return json.loads(reply.payload).get("data", {})

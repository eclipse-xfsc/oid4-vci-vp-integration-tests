import asyncio
import queue
import threading
import time
from typing import Awaitable, Any

from nats.aio.client import Subscription, Client as NATS
from pynats import NATSClient, NATSMessage

def base64_padding(data: str) -> str:
    """
    Add padding to a base64 encoded string
    """
    return data + "=" * (4 - (len(data) % 4))


def cleanup_nats(nats_clients: dict[str, NATS], futures: dict[str, Awaitable], subscriptions: dict[str, Subscription], loop: asyncio.AbstractEventLoop) -> None:
    if futures:
        for future in futures.values():
            future.close()
            print("Cancelled future")

    if subscriptions:
        for sub in subscriptions.values():
            loop.run_until_complete(sub.unsubscribe())
            print(f"Unsubscribed from topic {sub.subject}")

    if nats_clients:
        for nats_client in nats_clients.values():
            if nats_client.is_connected:
                loop.run_until_complete(nats_client.close())
                print("Closed NATS connection")

    if loop:
        print("Closed event loop")
        loop.close()

def threaded_nats_subscribe(topic: str, nats_url: str) -> queue.Queue[NATSMessage]:
    message_queue: queue.Queue[Any] = queue.Queue()
    stop = threading.Event()

    # Start the subscription thread
    thread = threading.Thread(target=nats_subscribe,
                              args=(message_queue, topic, stop, nats_url))
    thread.start()

    # Give some time for the subscription to be set up
    time.sleep(2)

    stop.set()
    thread.join(2)
    return message_queue

def nats_subscribe(message_queue: queue.Queue[NATSMessage], topic: str, stop: threading.Event, nats_url: str) -> None:
        with NATSClient(url=nats_url) as client:
            client.connect()

            def callback(msg: NATSMessage):
                message_queue.put(msg)
                print(f"Topic {topic} received message: {msg}")

            sub = client.subscribe(topic, callback=callback)

            # Wait for a message or timeout after 5 seconds
            while not stop.is_set():
                client.wait(count=1)
import threading

from supabase import create_client, Client

from abf_api.config import settings

_client: Client | None = None
_lock = threading.Lock()


def get_supabase() -> Client:
    """Return a singleton Supabase admin client (service-role key).

    Thread-safe via a lock to prevent duplicate initialization
    in concurrent async handlers.
    """
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_role_key,
                )
    return _client

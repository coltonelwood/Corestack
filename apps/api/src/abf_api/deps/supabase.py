import threading

from supabase import create_client, Client

from abf_api.config import settings

_client: Client | None = None
_lock = threading.Lock()


def get_supabase() -> Client:
    """Return a singleton Supabase admin client (service-role key).

    Thread-safe via double-checked locking. Raises immediately
    if credentials are missing rather than producing a cryptic error
    on the first query.
    """
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                if not settings.supabase_url or not settings.supabase_service_role_key:
                    raise RuntimeError(
                        "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set. "
                        "See apps/api/.env.example."
                    )
                _client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_role_key,
                )
    return _client

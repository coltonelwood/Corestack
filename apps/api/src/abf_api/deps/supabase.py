from supabase import create_client, Client

from abf_api.config import settings

_client: Client | None = None


def get_supabase() -> Client:
    """Return a singleton Supabase admin client (service-role key)."""
    global _client
    if _client is None:
        _client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
    return _client

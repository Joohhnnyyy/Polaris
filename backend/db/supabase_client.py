from supabase import create_client, Client
from backend.config import settings

supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY # Use service role key to bypass RLS for administrative/agent tasks
)

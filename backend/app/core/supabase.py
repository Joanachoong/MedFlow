from supabase import create_client, Client
from app.core.config import settings

# Service role client — bypasses RLS, used only in server-side admin operations
def get_supabase_admin() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

# Anon client — used for sign-in operations that go through GoTrue
def get_supabase_anon() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

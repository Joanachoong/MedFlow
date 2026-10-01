from fastapi import APIRouter, HTTPException, Header
from app.schemas.auth import SignUpRequest, LoginRequest, AuthResponse, ProfileOut
from app.core.supabase import get_supabase_admin, get_supabase_anon

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse)
def signup(body: SignUpRequest):
    admin = get_supabase_admin()
    anon  = get_supabase_anon()

    # 1. Create the auth user via Supabase Admin API
    #    Set role in app_metadata so it is server-side trusted.
    try:
        user_resp = admin.auth.admin.create_user({
            "email": body.email,
            "password": body.password,
            "email_confirm": True,                      # skip email verification for dev
            "app_metadata": {"role": body.role},
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Auth user creation failed: {e}")

    user_id = user_resp.user.id

    # 2. Insert into profiles (trigger sets public_id automatically)
    try:
        profile_resp = admin.table("profiles").insert({
            "id":        user_id,
            "full_name": body.full_name,
            "email":     body.email,
            "role":      body.role,
            "phone":     body.phone,
        }).execute()
    except Exception as e:
        # Roll back: delete the auth user we just created
        admin.auth.admin.delete_user(user_id)
        raise HTTPException(status_code=400, detail=f"Profile creation failed: {e}")

    # 3. If role is patient, also create the patients row
    if body.role == "patient":
        try:
            admin.table("patients").insert({
                "user_id":   user_id,
                "user_role": "patient",
                "status":    "stable",
            }).execute()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Patient record creation failed: {e}")

    # 4. Sign in to get a session token to return
    try:
        session_resp = anon.auth.sign_in_with_password({
            "email":    body.email,
            "password": body.password,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sign-in after signup failed: {e}")

    profile = profile_resp.data[0]

    return AuthResponse(
        access_token=session_resp.session.access_token,
        profile=ProfileOut(
            id=profile["id"],
            full_name=profile["full_name"],
            email=profile["email"],
            role=profile["role"],
            public_id=profile.get("public_id"),
            phone=profile.get("phone"),
            created_at=str(profile["created_at"]),
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest):
    anon  = get_supabase_anon()
    admin = get_supabase_admin()

    # 1. Sign in via GoTrue
    try:
        session_resp = anon.auth.sign_in_with_password({
            "email":    body.email,
            "password": body.password,
        })
    except Exception as e:
        print(f"[login] GoTrue error for {body.email!r}: {type(e).__name__}: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {e}")

    user_id = session_resp.user.id

    # 2. Fetch the profile
    try:
        profile_resp = admin.table("profiles").select("*").eq("id", user_id).single().execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = profile_resp.data

    return AuthResponse(
        access_token=session_resp.session.access_token,
        profile=ProfileOut(
            id=profile["id"],
            full_name=profile["full_name"],
            email=profile["email"],
            role=profile["role"],
            public_id=profile.get("public_id"),
            phone=profile.get("phone"),
            created_at=str(profile["created_at"]),
        ),
    )


@router.get("/me", response_model=ProfileOut)
def get_me(authorization: str = Header(...)):
    """
    Returns the profile of the currently authenticated user.
    Pass:  Authorization: Bearer <access_token>
    """
    token = authorization.removeprefix("Bearer ").strip()
    admin = get_supabase_admin()

    # Verify the JWT and get the user
    try:
        user_resp = admin.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = user_resp.user.id

    try:
        profile_resp = admin.table("profiles").select("*").eq("id", user_id).single().execute()
    except Exception:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = profile_resp.data
    return ProfileOut(
        id=profile["id"],
        full_name=profile["full_name"],
        email=profile["email"],
        role=profile["role"],
        public_id=profile.get("public_id"),
        phone=profile.get("phone"),
        created_at=str(profile["created_at"]),
    )

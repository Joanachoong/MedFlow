# MedFlow ERD (matches `schema.sql` v3)

```mermaid
erDiagram

    AUTH_USERS {
        uuid id PK "Supabase-managed, auth.users"
        text email
        jsonb raw_app_meta_data "role set by service_role only"
        jsonb raw_user_meta_data "user editable, never trusted for role"
    }

    PROFILES {
        uuid id PK, FK "references auth.users, cascade"
        text full_name
        text email UK
        user_role role "patient, doctor, nurse, admin. immutable"
        text public_id UK "D-0001, N-0001, P-0001, A-0001. trigger generated"
        text phone
        boolean is_active "admin deactivation"
        timestamptz created_at
        timestamptz deleted_at "soft delete"
    }

    PATIENTS {
        uuid id PK
        uuid user_id FK, UK "one patient record per account"
        user_role user_role "always patient, composite FK guard"
        date date_of_birth
        text blood_type
        text allergies
        patient_status status "stable, monitoring, critical"
        timestamptz created_at
        timestamptz updated_at "trigger maintained"
        timestamptz deleted_at "soft delete"
    }

    DOCTOR_PATIENT_ASSIGNMENTS {
        uuid id PK
        uuid doctor_id FK
        user_role doctor_role "always doctor, composite FK guard"
        uuid patient_id FK
        timestamptz assigned_at
        timestamptz unassigned_at "NULL means active"
    }

    CLINICAL_NOTES {
        uuid id PK
        uuid patient_id FK
        uuid doctor_id FK
        user_role doctor_role "always doctor, composite FK guard"
        text diagnosis
        text observation
        text plan
        boolean visible_to_patient "false for internal notes"
        timestamptz created_at
        timestamptz updated_at "trigger maintained"
        timestamptz deleted_at "soft delete"
    }

    CARE_NOTES {
        uuid id PK
        uuid patient_id FK
        uuid nurse_id FK
        user_role nurse_role "always nurse, composite FK guard"
        jsonb vitals "bp, hr, temp"
        text observation
        timestamptz created_at
        timestamptz updated_at "trigger maintained"
        timestamptz deleted_at "soft delete"
    }

    AUTH_USERS ||--|| PROFILES : "has profile"
    PROFILES ||--o| PATIENTS : "patient account"

    PROFILES ||--o{ DOCTOR_PATIENT_ASSIGNMENTS : "doctor assigned"
    PATIENTS ||--o{ DOCTOR_PATIENT_ASSIGNMENTS : "assigned to"

    PROFILES ||--o{ CLINICAL_NOTES : "doctor writes"
    PATIENTS ||--o{ CLINICAL_NOTES : "has"

    PROFILES ||--o{ CARE_NOTES : "nurse writes"
    PATIENTS ||--o{ CARE_NOTES : "has"
```

## Enums

| Enum | Values |
|------|--------|
| `user_role` | `patient`, `doctor`, `nurse`, `admin` |
| `patient_status` | `stable`, `monitoring`, `critical` |

## Guardrails that the diagram cannot show

| Guardrail | Where | What it prevents |
|-----------|-------|------------------|
| `UNIQUE (id, role)` on `profiles` + composite FKs | `patients`, `doctor_patient_assignments`, `clinical_notes`, `care_notes` | A doctor FK pointing at a nurse or patient (and the reverse) |
| `public_id_matches_role` CHECK + `trg_public_id` | `profiles` | A `D-` ID on a non-doctor |
| `trg_block_role_change` | `profiles` | Changing a role after creation, so `public_id` stays truthful |
| Partial unique index `uq_active_assignment` | assignments | The same doctor assigned twice to one patient, while keeping history |
| `ON DELETE RESTRICT` | assignments, notes | Deleting an account that wipes medical records. Use `deleted_at`. |
| `ON DELETE CASCADE` | `auth.users` to `profiles` to `patients` | Orphaned profiles when a test user is removed |
| `trg_*_updated` | patients, clinical_notes, care_notes | Stale `updated_at` |
| `on_auth_user_created` | `auth.users` | Signup without a profile. Role comes from `raw_app_meta_data`, default `patient`, and patients also get a `patients` row. |

## Access summary (RLS)

| Table | Patient | Doctor | Nurse | Admin |
|-------|---------|--------|-------|-------|
| `profiles` | own row | read all | read all | read and update |
| `patients` | own row | assigned only, can update | all, can update status | all, can insert |
| `doctor_patient_assignments` | none | own rows | read | full |
| `clinical_notes` | own, if `visible_to_patient` | assigned patients, insert and update own | read | read |
| `care_notes` | own | assigned patients, read | insert and update own | read |

The FastAPI backend connects directly to Postgres and bypasses RLS, so repeat these role checks in the API.
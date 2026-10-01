-- =============================================================
-- MedFlow Seed Data — One account per role for system validation
-- Run in Supabase SQL editor (requires service_role access)
-- Passwords are all:  MedFlow2026!
-- =============================================================

-- NOTE: In Supabase, auth.users is managed by GoTrue.
-- The easiest way to seed is via the Supabase dashboard → Auth → Users,
-- or via the Admin API. The SQL below seeds the profiles table ONLY
-- (assuming you have already created the auth users via the dashboard
--  OR you run the companion seed_auth.py script).
--
-- If you want pure-SQL seeding, use the SQL editor and run as service_role.

-- =============================================================
-- Step 1: Insert into auth.users (service_role only)
-- Supabase stores bcrypt hashes. These UUIDs are fixed so the
-- profiles FK can reference them deterministically.
-- =============================================================

-- We use Supabase's built-in function to create users with known UUIDs.
-- Copy this block to the Supabase SQL editor → Run as service_role.

SELECT auth.create_user(
    '{"id":"00000000-0000-0000-0000-000000000001",
      "email":"admin@medflow.dev",
      "password":"MedFlow2026!",
      "email_confirm":true,
      "app_metadata":{"role":"admin"}}'::jsonb
) WHERE NOT EXISTS (
    SELECT 1 FROM auth.users WHERE id = '00000000-0000-0000-0000-000000000001'
);

SELECT auth.create_user(
    '{"id":"00000000-0000-0000-0000-000000000002",
      "email":"doctor@medflow.dev",
      "password":"MedFlow2026!",
      "email_confirm":true,
      "app_metadata":{"role":"doctor"}}'::jsonb
) WHERE NOT EXISTS (
    SELECT 1 FROM auth.users WHERE id = '00000000-0000-0000-0000-000000000002'
);

SELECT auth.create_user(
    '{"id":"00000000-0000-0000-0000-000000000003",
      "email":"nurse@medflow.dev",
      "password":"MedFlow2026!",
      "email_confirm":true,
      "app_metadata":{"role":"nurse"}}'::jsonb
) WHERE NOT EXISTS (
    SELECT 1 FROM auth.users WHERE id = '00000000-0000-0000-0000-000000000003'
);

SELECT auth.create_user(
    '{"id":"00000000-0000-0000-0000-000000000004",
      "email":"patient@medflow.dev",
      "password":"MedFlow2026!",
      "email_confirm":true,
      "app_metadata":{"role":"patient"}}'::jsonb
) WHERE NOT EXISTS (
    SELECT 1 FROM auth.users WHERE id = '00000000-0000-0000-0000-000000000004'
);


-- =============================================================
-- Step 2: Insert profiles
-- public_id is auto-set by trg_public_id BEFORE INSERT trigger.
-- =============================================================

INSERT INTO profiles (id, full_name, email, role, phone)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'Alice Admin',    'admin@medflow.dev',   'admin',   '+1-555-0001'),
    ('00000000-0000-0000-0000-000000000002', 'Dr. Bob Chen',   'doctor@medflow.dev',  'doctor',  '+1-555-0002'),
    ('00000000-0000-0000-0000-000000000003', 'Nurse Carol Day', 'nurse@medflow.dev',  'nurse',   '+1-555-0003'),
    ('00000000-0000-0000-0000-000000000004', 'Pat Patient',    'patient@medflow.dev', 'patient', '+1-555-0004')
ON CONFLICT (id) DO NOTHING;


-- =============================================================
-- Step 3: Insert patient record for the patient profile
-- user_role = 'patient' is the phantom column (composite FK guard)
-- =============================================================

INSERT INTO patients (user_id, user_role, date_of_birth, blood_type, allergies, status)
VALUES (
    '00000000-0000-0000-0000-000000000004',
    'patient',
    '1990-06-15',
    'O+',
    'Penicillin',
    'stable'
)
ON CONFLICT DO NOTHING;


-- =============================================================
-- Step 4: Assign Dr. Bob to Pat Patient
-- =============================================================

INSERT INTO doctor_patient_assignments (doctor_id, doctor_role, patient_id)
SELECT
    '00000000-0000-0000-0000-000000000002',
    'doctor',
    p.id
FROM patients p
WHERE p.user_id = '00000000-0000-0000-0000-000000000004'
ON CONFLICT DO NOTHING;


-- =============================================================
-- Verification query — run after seeding
-- =============================================================
SELECT p.public_id, p.full_name, p.email, p.role
FROM profiles p
ORDER BY p.role;

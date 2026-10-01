-- =============================================================
-- MedFlow Seed — profiles only (auth users already created via dashboard)
-- Run this in the Supabase SQL Editor AFTER creating the 4 auth users
-- via Authentication → Users → Add user.
-- =============================================================

-- Step 1: Insert profiles, looking up the UUID from auth.users by email
INSERT INTO profiles (id, full_name, email, role, phone)
SELECT
    u.id,
    'Alice Admin',
    u.email,
    'admin',
    '+1-555-0001'
FROM auth.users u
WHERE u.email = 'admin@medflow.dev'
ON CONFLICT (id) DO NOTHING;

INSERT INTO profiles (id, full_name, email, role, phone)
SELECT
    u.id,
    'Dr. Bob Chen',
    u.email,
    'doctor',
    '+1-555-0002'
FROM auth.users u
WHERE u.email = 'doctor@medflow.dev'
ON CONFLICT (id) DO NOTHING;

INSERT INTO profiles (id, full_name, email, role, phone)
SELECT
    u.id,
    'Nurse Carol Day',
    u.email,
    'nurse',
    '+1-555-0003'
FROM auth.users u
WHERE u.email = 'nurse@medflow.dev'
ON CONFLICT (id) DO NOTHING;

INSERT INTO profiles (id, full_name, email, role, phone)
SELECT
    u.id,
    'Pat Patient',
    u.email,
    'patient',
    '+1-555-0004'
FROM auth.users u
WHERE u.email = 'patient@medflow.dev'
ON CONFLICT (id) DO NOTHING;

-- Step 2: Create the patient record
INSERT INTO patients (user_id, user_role, date_of_birth, blood_type, allergies, status)
SELECT
    p.id,
    'patient',
    '1990-06-15',
    'O+',
    'Penicillin',
    'stable'
FROM profiles p
WHERE p.email = 'patient@medflow.dev'
ON CONFLICT DO NOTHING;

-- Step 3: Assign Dr. Bob to Pat Patient
INSERT INTO doctor_patient_assignments (doctor_id, doctor_role, patient_id)
SELECT
    doc.id,
    'doctor',
    pat.id
FROM patients pat
JOIN profiles p ON p.id = pat.user_id
JOIN profiles doc ON doc.email = 'doctor@medflow.dev'
WHERE p.email = 'patient@medflow.dev'
ON CONFLICT DO NOTHING;

-- Verify
SELECT public_id, full_name, email, role FROM profiles ORDER BY role;

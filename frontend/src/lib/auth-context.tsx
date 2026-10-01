'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export type UserRole = 'patient' | 'doctor' | 'nurse' | 'admin'

export interface Profile {
  id: string
  full_name: string
  email: string
  role: UserRole
  public_id: string | null
  phone: string | null
  created_at: string
}

interface AuthContextValue {
  profile: Profile | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<Profile>
  signup: (data: SignupData) => Promise<Profile>
  logout: () => void
}

export interface SignupData {
  email: string
  password: string
  full_name: string
  role: UserRole
  phone?: string
}

const AuthContext = createContext<AuthContextValue | null>(null)

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Rehydrate from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('mf_token')
    const storedProfile = localStorage.getItem('mf_profile')
    if (storedToken && storedProfile) {
      setToken(storedToken)
      setProfile(JSON.parse(storedProfile))
    }
    setLoading(false)
  }, [])

  async function login(email: string, password: string): Promise<Profile> {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail ?? 'Login failed')
    }
    const data = await res.json()
    localStorage.setItem('mf_token', data.access_token)
    localStorage.setItem('mf_profile', JSON.stringify(data.profile))
    setToken(data.access_token)
    setProfile(data.profile)
    return data.profile
  }

  async function signup(body: SignupData): Promise<Profile> {
    const res = await fetch(`${API}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail ?? 'Signup failed')
    }
    const data = await res.json()
    localStorage.setItem('mf_token', data.access_token)
    localStorage.setItem('mf_profile', JSON.stringify(data.profile))
    setToken(data.access_token)
    setProfile(data.profile)
    return data.profile
  }

  function logout() {
    localStorage.removeItem('mf_token')
    localStorage.removeItem('mf_profile')
    setToken(null)
    setProfile(null)
  }

  return (
    <AuthContext.Provider value={{ profile, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}

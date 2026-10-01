'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth, UserRole } from '@/lib/auth-context'

const ROLES: { value: UserRole; label: string; description: string }[] = [
  { value: 'patient', label: 'Patient', description: 'View your own records and notes' },
  { value: 'doctor', label: 'Doctor', description: 'Manage patients and write clinical notes' },
  { value: 'nurse', label: 'Nurse', description: 'Record vitals and care notes' },
  { value: 'admin', label: 'Admin', description: 'Manage users and system access' },
]

export default function SignupPage() {
  const { signup } = useAuth()
  const router = useRouter()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>('patient')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      const profile = await signup({ email, password, full_name: fullName, role, phone: phone || undefined })
      router.push(`/dashboard/${profile.role}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-950 px-4 py-10">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-3">
            <span className="text-3xl">🏥</span>
            <span className="text-2xl font-bold text-white tracking-tight">MedFlow</span>
          </div>
          <p className="text-slate-400 text-sm">Create your account</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
          <h1 className="text-xl font-semibold text-white mb-6">New account</h1>

          <form id="signup-form" onSubmit={handleSubmit} className="space-y-4">
            {/* Role selector */}
            <div>
              <label className="block text-sm text-slate-300 mb-2">Role</label>
              <div className="grid grid-cols-2 gap-2">
                {ROLES.map(r => (
                  <button
                    key={r.value}
                    type="button"
                    id={`role-${r.value}`}
                    onClick={() => setRole(r.value)}
                    className={`text-left p-3 rounded-lg border text-sm transition-all ${
                      role === r.value
                        ? 'border-blue-500 bg-blue-500/10 text-white'
                        : 'border-slate-700 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <div className="font-medium">{r.label}</div>
                    <div className="text-xs opacity-70 mt-0.5 leading-tight">{r.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="signup-name" className="block text-sm text-slate-300 mb-1.5">
                Full name
              </label>
              <input
                id="signup-name"
                type="text"
                required
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                placeholder="Jane Smith"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label htmlFor="signup-email" className="block text-sm text-slate-300 mb-1.5">
                Email
              </label>
              <input
                id="signup-email"
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label htmlFor="signup-phone" className="block text-sm text-slate-300 mb-1.5">
                Phone <span className="text-slate-500">(optional)</span>
              </label>
              <input
                id="signup-phone"
                type="tel"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder="+1-555-0000"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label htmlFor="signup-password" className="block text-sm text-slate-300 mb-1.5">
                Password <span className="text-slate-500">(min. 8 characters)</span>
              </label>
              <input
                id="signup-password"
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            {error && (
              <div id="signup-error" className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-3 py-2.5">
                {error}
              </div>
            )}

            <button
              id="signup-submit"
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors text-sm"
            >
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link href="/login" className="text-blue-400 hover:text-blue-300 transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </main>
  )
}

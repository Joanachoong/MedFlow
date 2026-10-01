'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'

export default function LoginPage() {
  const { login } = useAuth()
  const router = useRouter()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const profile = await login(email, password)
      router.push(`/dashboard/${profile.role}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  // Quick-fill buttons for seed users
  const seedUsers = [
    { label: 'Admin', email: 'admin@medflow.dev' },
    { label: 'Doctor', email: 'doctor@medflow.dev' },
    { label: 'Nurse', email: 'nurse@medflow.dev' },
    { label: 'Patient', email: 'patient@medflow.dev' },
  ]

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-md">
        {/* Logo / header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-3">
            <span className="text-3xl">🏥</span>
            <span className="text-2xl font-bold text-white tracking-tight">MedFlow</span>
          </div>
          <p className="text-slate-400 text-sm">Hospital Management System</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
          <h1 className="text-xl font-semibold text-white mb-6">Sign in to your account</h1>

          {/* Quick-fill seed users */}
          <div className="mb-6">
            <p className="text-xs text-slate-500 mb-2 uppercase tracking-wide">Quick login (seed accounts)</p>
            <div className="grid grid-cols-4 gap-2">
              {seedUsers.map(u => (
                <button
                  key={u.label}
                  type="button"
                  id={`quick-login-${u.label.toLowerCase()}`}
                  onClick={() => { setEmail(u.email); setPassword('MedFlow2026!') }}
                  className="text-xs py-1.5 px-2 rounded-lg border border-slate-700 text-slate-300 hover:border-blue-500 hover:text-blue-400 transition-colors"
                >
                  {u.label}
                </button>
              ))}
            </div>
          </div>

          <form id="login-form" onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="login-email" className="block text-sm text-slate-300 mb-1.5">
                Email
              </label>
              <input
                id="login-email"
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label htmlFor="login-password" className="block text-sm text-slate-300 mb-1.5">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            {error && (
              <div id="login-error" className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-3 py-2.5">
                {error}
              </div>
            )}

            <button
              id="login-submit"
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors text-sm"
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-slate-500">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="text-blue-400 hover:text-blue-300 transition-colors">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </main>
  )
}

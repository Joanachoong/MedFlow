'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { profile, loading, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !profile) {
      router.push('/login')
    }
  }, [profile, loading, router])

  if (loading || !profile) return null

  const roleColors: Record<string, string> = {
    admin:   'bg-purple-500/20 text-purple-300 border-purple-500/40',
    doctor:  'bg-blue-500/20   text-blue-300   border-blue-500/40',
    nurse:   'bg-teal-500/20   text-teal-300   border-teal-500/40',
    patient: 'bg-green-500/20  text-green-300  border-green-500/40',
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Top navigation */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-lg">🏥</span>
            <span className="text-white font-semibold tracking-tight">MedFlow</span>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-xs px-2.5 py-1 rounded-full border font-medium capitalize ${roleColors[profile.role]}`}>
              {profile.public_id ?? profile.role}
            </span>
            <span className="text-slate-400 text-sm hidden sm:block">{profile.full_name}</span>
            <button
              id="nav-logout"
              onClick={() => { logout(); router.push('/login') }}
              className="text-xs text-slate-500 hover:text-red-400 transition-colors ml-1"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-8">
        {children}
      </main>
    </div>
  )
}

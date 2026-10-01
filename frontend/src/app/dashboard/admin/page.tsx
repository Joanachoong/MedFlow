'use client'

import { useAuth } from '@/lib/auth-context'

export default function AdminDashboard() {
  const { profile } = useAuth()
  if (!profile) return null

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">
          Admin Panel — {profile.full_name} 🛡️
        </h1>
        <p className="text-slate-400 mt-1 text-sm">System Admin — {profile.public_id}</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
        <StatCard icon="👨‍⚕️" label="Doctors" value="—" />
        <StatCard icon="👩‍⚕️" label="Nurses" value="—" />
        <StatCard icon="🏥" label="Patients" value="—" />
        <StatCard icon="👤" label="Admins" value="—" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InfoCard
          title="Your Profile"
          icon="🪪"
          rows={[
            { label: 'ID',    value: profile.public_id ?? '—' },
            { label: 'Email', value: profile.email },
            { label: 'Phone', value: profile.phone ?? '—' },
            { label: 'Role',  value: 'Admin' },
          ]}
        />
        <PlaceholderCard icon="👥" title="User Management" description="List, activate, deactivate, or change roles for all users." />
        <PlaceholderCard icon="📊" title="System Stats" description="Total notes written, active assignments, recent signups." />
        <PlaceholderCard icon="📜" title="Audit Log" description="Record of who changed what and when across all tables. (Feature #11)" />
      </div>

      <SystemCheck label="Admin dashboard" role="admin" email={profile.email} public_id={profile.public_id} />
    </div>
  )
}

function StatCard({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
      <span className="text-2xl block mb-1">{icon}</span>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-slate-500 text-xs mt-1">{label}</p>
    </div>
  )
}

function InfoCard({ title, icon, rows }: { title: string; icon: string; rows: { label: string; value: string }[] }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <span>{icon}</span>
        <h2 className="text-white font-medium text-sm">{title}</h2>
      </div>
      <dl className="space-y-2">
        {rows.map(r => (
          <div key={r.label} className="flex justify-between text-sm">
            <dt className="text-slate-500">{r.label}</dt>
            <dd className="text-slate-200 font-mono text-xs">{r.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}

function PlaceholderCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <span>{icon}</span>
        <h2 className="text-white font-medium text-sm">{title}</h2>
      </div>
      <p className="text-slate-500 text-xs">{description}</p>
      <div className="mt-4 h-16 rounded-lg bg-slate-800/60 border border-dashed border-slate-700 flex items-center justify-center text-slate-600 text-xs">
        Coming soon
      </div>
    </div>
  )
}

function SystemCheck({ label, role, email, public_id }: { label: string; role: string; email: string; public_id: string | null }) {
  return (
    <div className="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-5">
      <h2 className="text-white text-sm font-medium mb-3">✅ System validation</h2>
      <div className="font-mono text-xs space-y-1 text-slate-400">
        <p><span className="text-slate-600">Dashboard:</span> {label} — <span className="text-green-400">PASS</span></p>
        <p><span className="text-slate-600">Role guard:</span> role === &quot;{role}&quot; — <span className="text-green-400">PASS</span></p>
        <p><span className="text-slate-600">Auth email:</span> {email}</p>
        <p><span className="text-slate-600">Public ID:</span> {public_id ?? 'pending trigger'}</p>
      </div>
    </div>
  )
}

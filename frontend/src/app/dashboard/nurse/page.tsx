'use client'

import { useAuth } from '@/lib/auth-context'

export default function NurseDashboard() {
  const { profile } = useAuth()
  if (!profile) return null

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">
          Hello, {profile.full_name} 🩹
        </h1>
        <p className="text-slate-400 mt-1 text-sm">Nurse Portal — {profile.public_id}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <StatCard icon="🛏️" label="Active Patients" value="—" note="After seeding" />
        <StatCard icon="💉" label="Care Notes Today" value="—" note="This shift" />
        <StatCard icon="⚠️" label="Critical Status" value="—" note="Needs attention" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InfoCard
          title="Your Profile"
          icon="🪪"
          rows={[
            { label: 'ID',    value: profile.public_id ?? '—' },
            { label: 'Email', value: profile.email },
            { label: 'Phone', value: profile.phone ?? '—' },
            { label: 'Role',  value: 'Nurse' },
          ]}
        />
        <PlaceholderCard icon="📋" title="Patient List" description="All patients you are responsible for will appear here." />
        <PlaceholderCard icon="❤️" title="Record Vitals" description="BP, heart rate, temperature — log a care note for a patient." />
        <PlaceholderCard icon="🔔" title="Alerts" description="Patients flagged as 'critical' or 'monitoring' will surface here." />
      </div>

      <SystemCheck label="Nurse dashboard" role="nurse" email={profile.email} public_id={profile.public_id} />
    </div>
  )
}

function StatCard({ icon, label, value, note }: { icon: string; label: string; value: string; note: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-2">
        <span>{icon}</span>
        <span className="text-slate-400 text-xs">{label}</span>
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
      <p className="text-slate-600 text-xs mt-1">{note}</p>
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

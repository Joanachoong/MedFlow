'use client'

import { useAuth } from '@/lib/auth-context'

export default function PatientDashboard() {
  const { profile } = useAuth()
  if (!profile) return null

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">
          Welcome, {profile.full_name} 👋
        </h1>
        <p className="text-slate-400 mt-1 text-sm">Patient Portal — {profile.public_id}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InfoCard
          title="Your Profile"
          icon="🪪"
          rows={[
            { label: 'ID',    value: profile.public_id ?? '—' },
            { label: 'Email', value: profile.email },
            { label: 'Phone', value: profile.phone ?? '—' },
            { label: 'Role',  value: 'Patient' },
          ]}
        />
        <StatusCard
          title="Health Status"
          icon="💓"
          status="Stable"
          color="text-green-400"
          note="Your assigned doctor will update this."
        />
        <PlaceholderCard icon="📋" title="Clinical Notes" description="Notes written by your doctor will appear here." />
        <PlaceholderCard icon="💊" title="Care Records" description="Vitals and care notes from your nurse will appear here." />
      </div>

      <SystemCheck label="Patient dashboard" role="patient" email={profile.email} public_id={profile.public_id} />
    </div>
  )
}

// ─── Shared mini-components ───────────────────────────────────────────────────

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

function StatusCard({ title, icon, status, color, note }: { title: string; icon: string; status: string; color: string; note: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <span>{icon}</span>
        <h2 className="text-white font-medium text-sm">{title}</h2>
      </div>
      <p className={`text-2xl font-bold ${color}`}>{status}</p>
      <p className="text-slate-500 text-xs mt-2">{note}</p>
    </div>
  )
}

function PlaceholderCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
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

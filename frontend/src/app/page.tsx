'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'

export default function Home() {
  const { profile, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    if (profile) {
      router.replace(`/dashboard/${profile.role}`)
    } else {
      router.replace('/login')
    }
  }, [profile, loading, router])

  return null
}

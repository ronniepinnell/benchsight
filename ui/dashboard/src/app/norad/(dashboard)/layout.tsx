// src/app/(dashboard)/layout.tsx
'use client'

import { Sidebar } from '@/components/layout/sidebar'
import { Topbar } from '@/components/layout/topbar'
import { useState } from 'react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background">
      <Sidebar 
        isMobileOpen={isMobileMenuOpen}
        onMobileClose={() => setIsMobileMenuOpen(false)}
      />
      <Topbar onMobileMenuClick={() => setIsMobileMenuOpen(true)} />
      
      {/* Main content area - responsive margins */}
      <main className={`
        mt-14 p-4 lg:p-6
        lg:ml-60
        min-h-[calc(100vh-3.5rem)]
      `}>
        {children}
      </main>
    </div>
  )
}

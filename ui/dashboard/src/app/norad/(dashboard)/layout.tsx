// src/app/(dashboard)/layout.tsx
'use client'

import { Sidebar } from '@/components/layout/sidebar'
import { Topbar } from '@/components/layout/topbar'
import { useState, useEffect } from 'react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      // Save current scroll position
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
      
      return () => {
        // Restore scroll position
        document.body.style.position = ''
        document.body.style.top = ''
        document.body.style.width = ''
        document.body.style.overflow = ''
        window.scrollTo(0, scrollY)
      }
    }
  }, [isMobileMenuOpen])

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
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
        w-full
        max-w-full
        overflow-x-hidden
      `}>
        {children}
      </main>
    </div>
  )
}

// src/app/(dashboard)/layout.tsx
import { Sidebar } from '@/components/layout/sidebar'
import { Topbar } from '@/components/layout/topbar'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <Topbar />
      
      {/* Main content area */}
      <main className="ml-60 mt-14 p-6">
        {children}
      </main>
    </div>
  )
}

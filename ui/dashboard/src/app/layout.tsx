// src/app/layout.tsx
import type { Metadata } from 'next'
import { Inter, Rajdhani, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { cn } from '@/lib/utils'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const rajdhani = Rajdhani({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-rajdhani',
})

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
})

export const metadata: Metadata = {
  title: 'BenchSight - NORAD Hockey Analytics',
  description: 'Advanced analytics for the NORAD recreational hockey league',
  icons: {
    icon: '/favicon.ico',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={cn(
          inter.variable,
          rajdhani.variable,
          jetbrains.variable,
          'font-body bg-background text-foreground antialiased'
        )}
      >
        {children}
      </body>
    </html>
  )
}

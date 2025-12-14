import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import WinterEffects from '@/components/WinterEffects'
import InstallPrompt from '@/components/InstallPrompt'
import ClientWrapper from '@/components/ClientWrapper'

const inter = Inter({ subsets: ['latin', 'cyrillic'] })

export const metadata: Metadata = {
  title: 'LibriMomsClub — Библиотека для мам-блогеров',
  description: 'Закрытая библиотека идей для Reels, постов, гайдов по блогингу и личному бренду',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'MomsClub',
  },
}

export const viewport: Viewport = {
  themeColor: '#FDF8F3',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  viewportFit: 'cover',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <head>
        <link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=2" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="theme-color" content="#FDF8F3" />
      </head>
      <body className={inter.className}>
        <WinterEffects />
        <ClientWrapper>
          {children}
        </ClientWrapper>
        <InstallPrompt />
      </body>
    </html>
  )
}

import './globals.css'
import Link from 'next/link'

export const metadata = {
  title: 'Whatcom Civic Watch',
  description: 'Civic research app for Whatcom County Council history',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <h2>Whatcom Civic Watch</h2>
            <nav>
              <Link href="/meetings">Meetings</Link>
              <Link href="/ordinances">Ordinances</Link>
              <Link href="/search">Search</Link>
              <Link href="/admin">Sources/Admin</Link>
              <Link href="/jobs">Jobs/Status</Link>
            </nav>
          </aside>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  )
}

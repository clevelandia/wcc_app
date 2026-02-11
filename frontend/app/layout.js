export const metadata = {
  title: 'Whatcom Civic Watch',
  description: 'Config-driven civic intelligence platform'
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'Arial, sans-serif', margin: 0, background: '#f5f7fb' }}>
        {children}
      </body>
    </html>
  )
}

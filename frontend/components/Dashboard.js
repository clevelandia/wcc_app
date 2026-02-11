'use client'

import { useState } from 'react'

const sectionStyle = { background: 'white', padding: 16, borderRadius: 12, boxShadow: '0 2px 6px rgba(0,0,0,.08)', marginBottom: 14 }

export default function Dashboard() {
  const [query, setQuery] = useState('ordinance housing')

  return (
    <main style={{ maxWidth: 1100, margin: '24px auto', padding: 12 }}>
      <h1>Whatcom Civic Watch</h1>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
        <section style={sectionStyle}>
          <h2>Meetings Calendar</h2>
          <ul>
            <li>County Council — Feb 12, 2026 (Agenda + attachments)</li>
            <li>Public Works Committee — Feb 14, 2026</li>
          </ul>
          <h3>Ordinance Semantic Diff</h3>
          <p>Detected moved clause §12.08 from Article II to Article IV.</p>
        </section>

        <section style={sectionStyle}>
          <h2>Search</h2>
          <input value={query} onChange={(e) => setQuery(e.target.value)} style={{ width: '100%', padding: 8 }} />
          <p style={{ fontSize: 13 }}>Searches meetings, ordinances, transcripts, and news snippets.</p>
        </section>
      </div>

      <section style={sectionStyle}>
        <h2>Document Viewer</h2>
        <p>Attachment: 2026 Budget Amendment.pdf</p>
        <p>Citation highlight: Page 3, lines 18–32.</p>
      </section>

      <section style={sectionStyle}>
        <h2>Organizer Brief Generator</h2>
        <p><strong>Evidence:</strong> County budget account 001-123 increased by 18%.</p>
        <p><strong>Interpretation:</strong> This is interpretive analysis grounded in sources.</p>
      </section>
    </main>
  )
}

'use client'
import Link from 'next/link'
import { useState } from 'react'
import { apiFetch } from '../../lib/api'

export default function SearchPage() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])

  async function run() {
    if (!q.trim()) return
    const data = await apiFetch(`/search?q=${encodeURIComponent(q)}&types=meetings,agenda_items,ordinances,documents,news`)
    setResults(data.results)
  }

  const grouped = results.reduce((acc, r) => { (acc[r.type] ||= []).push(r); return acc }, {})

  return <div>
    <h1>Search</h1>
    <div className="card row">
      <input placeholder="Search council history..." value={q} onChange={(e)=>setQ(e.target.value)} onKeyDown={(e)=> e.key === 'Enter' ? run() : null} style={{minWidth:300}}/>
      <button onClick={run}>Search</button>
    </div>
    {Object.keys(grouped).map((type)=> <div className="card" key={type}>
      <h2>{type}</h2>
      {grouped[type].map((r)=> <div key={r.id} style={{padding:'8px 0', borderBottom:'1px solid #eee'}}>
        <strong>{r.type === 'meeting' ? <Link href={`/meetings/${r.id.split(':')[1]}`}>{r.title}</Link> : r.type === 'document' ? <Link href={`/documents/${encodeURIComponent(r.id)}`}>{r.title}</Link> : r.type === 'ordinance' ? <Link href={`/ordinances/${r.id.split(':')[1]}`}>{r.title}</Link> : r.title}</strong>
        <div className="muted">{r.date ? new Date(r.date).toLocaleDateString() : ''}</div>
        <div dangerouslySetInnerHTML={{__html:r.snippet}} />
        <small>Citations: {JSON.stringify(r.citations)}</small>
      </div>)}
    </div>)}
  </div>
}

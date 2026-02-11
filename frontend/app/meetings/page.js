'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'

export default function MeetingsPage() {
  const [items, setItems] = useState([])
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [keyword, setKeyword] = useState('')

  async function load() {
    const params = new URLSearchParams()
    if (from) params.set('from', from)
    if (to) params.set('to', to)
    if (keyword) params.set('keyword', keyword)
    const data = await apiFetch(`/meetings?${params.toString()}`)
    setItems(data.items)
  }

  useEffect(() => { load() }, [])

  return <div>
    <h1>Meetings Timeline</h1>
    <div className="card row">
      <input type="date" value={from} onChange={(e)=>setFrom(e.target.value)} />
      <input type="date" value={to} onChange={(e)=>setTo(e.target.value)} />
      <input placeholder="keyword" value={keyword} onChange={(e)=>setKeyword(e.target.value)} />
      <button onClick={load}>Apply Filters</button>
    </div>
    {items.length === 0 ? <div className="card"><p>No data yet—run backfill.</p><Link href="/admin"><button>Run Backfill</button></Link></div> : null}
    <div className="list">
      {items.map((m) => <div className="card" key={m.id}>
        <Link href={`/meetings/${m.id}`}><h3>{m.title}</h3></Link>
        <p className="muted">{m.meeting_date ? new Date(m.meeting_date).toLocaleString() : 'Unknown date'} · {m.location || 'No location'}</p>
        <p>{m.status}</p>
      </div>)}
    </div>
  </div>
}

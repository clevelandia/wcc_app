'use client'
import { useState } from 'react'
import { apiFetch } from '../../lib/api'

export default function AdminPage() {
  const [mode, setMode] = useState('backfill')
  const [status, setStatus] = useState('')

  async function runIngest() {
    setStatus('Running...')
    const data = await apiFetch(`/admin/ingest?mode=${mode}&source=whatcom_legistar_api`, { method: 'POST' })
    setStatus(`Job ${data.job_id} complete: ${data.meetings} meetings`)
  }

  return <div>
    <h1>Sources / Admin</h1>
    <div className='card'>
      <div className='row'>
        <select value={mode} onChange={(e)=>setMode(e.target.value)}>
          <option value='backfill'>backfill</option>
          <option value='incremental'>incremental</option>
        </select>
        <button onClick={runIngest}>Run ingest</button>
      </div>
      <p>{status}</p>
      <p className='muted'>CLI equivalents: <code>cw ingest --source whatcom_legistar_api --mode backfill</code> and <code>cw ingest --all --mode incremental</code>.</p>
    </div>
  </div>
}

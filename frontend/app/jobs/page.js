'use client'
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'

export default function JobsPage() {
  const [jobs, setJobs] = useState([])
  useEffect(() => {
    apiFetch('/jobs').then((d) => setJobs(d.items))
  }, [])
  return <div>
    <h1>Jobs / Status</h1>
    <div className='list'>{jobs.map((j)=><div key={j.id} className='card'>
      <strong>{j.source}</strong> · {j.mode} · {j.status}
      <div className='muted'>processed {j.processed_items}/{j.total_items}, failed {j.failed_items}, retries {j.retries}</div>
    </div>)}</div>
  </div>
}

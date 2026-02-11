import Link from 'next/link'
import { apiFetch } from '../../../lib/api'

export default async function MeetingDetail({ params }) {
  const data = await apiFetch(`/meetings/${params.id}`)
  const { meeting, agenda_items, documents, votes } = data
  return <div>
    <h1>{meeting.title}</h1>
    <p className="muted">{meeting.meeting_date ? new Date(meeting.meeting_date).toLocaleString() : ''} · {meeting.location || ''}</p>
    <div className="card"><h2>Agenda</h2><ul>{agenda_items.map((a)=><li key={a.id}>{a.title}</li>)}</ul></div>
    <div className="card"><h2>Attachments</h2><ul>{documents.map((d)=><li key={d.id}><Link href={`/documents/${encodeURIComponent(d.id)}`}>{d.title}</Link> {d.file_url ? <a href={d.file_url} target="_blank">(download)</a> : null}</li>)}</ul></div>
    <div className="card"><h2>Actions / Votes</h2><ul>{votes.map((v)=><li key={v.id}>{v.person_name}: {v.vote_value}</li>)}</ul></div>
  </div>
}

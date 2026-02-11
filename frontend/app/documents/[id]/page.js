import { apiFetch } from '../../../lib/api'

export default async function DocumentDetail({ params }) {
  const id = decodeURIComponent(params.id)
  const data = await apiFetch(`/documents/${encodeURIComponent(id)}`)
  const d = data.document
  return <div>
    <h1>{d.title}</h1>
    <div className='card'>
      <p><a href={d.file_url} target='_blank'>Open original PDF</a></p>
      <pre style={{whiteSpace:'pre-wrap', maxHeight:500, overflow:'auto'}}>{d.text_content || 'No extracted text available.'}</pre>
      <p>Highlighted citations: {JSON.stringify(d.citations)}</p>
    </div>
  </div>
}

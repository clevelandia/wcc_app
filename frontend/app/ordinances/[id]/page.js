import { apiFetch } from '../../../lib/api'

export default async function OrdinanceDetail({ params }) {
  const data = await apiFetch(`/ordinances/${params.id}`)
  return <div>
    <h1>{data.ordinance.title}</h1>
    <div className='card'><h2>Versions</h2><ul>{data.versions.map((v)=><li key={v.id}>{v.title}</li>)}</ul></div>
    <div className='card'><h2>Diff view</h2><p>{data.diff || 'No diff available yet.'}</p></div>
  </div>
}

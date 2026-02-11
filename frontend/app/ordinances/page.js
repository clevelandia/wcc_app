import Link from 'next/link'
import { apiFetch } from '../../lib/api'

export default async function Ordinances() {
  const data = await apiFetch('/search?q=ordinance&types=ordinances')
  return <div><h1>Ordinances</h1><div className='list'>{data.results.map((o)=><div key={o.id} className='card'><Link href={`/ordinances/${o.id.split(':')[1]}`}>{o.title}</Link></div>)}</div></div>
}

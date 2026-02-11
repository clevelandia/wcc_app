const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, { cache: 'no-store', ...options })
  if (!res.ok) {
    throw new Error(`API failed: ${res.status}`)
  }
  return res.json()
}

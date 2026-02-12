const SERVER_API_ENV = 'API_URL_SERVER'
const PUBLIC_API_ENV = 'NEXT_PUBLIC_API_URL'

function normalizeBaseUrl(base) {
  return base.replace(/\/$/, '')
}

export function getApiBase() {
  const publicApi = process.env[PUBLIC_API_ENV]
  const serverApi = process.env[SERVER_API_ENV]

  if (typeof window === 'undefined') {
    if (serverApi) {
      return normalizeBaseUrl(serverApi)
    }
    if (publicApi) {
      console.warn(`${SERVER_API_ENV} is not set during SSR. Falling back to ${PUBLIC_API_ENV}.`)
      return normalizeBaseUrl(publicApi)
    }
    throw new Error(`Missing API base URL for server runtime. Set ${SERVER_API_ENV} (preferred) or ${PUBLIC_API_ENV}.`)
  }

  if (publicApi) {
    return normalizeBaseUrl(publicApi)
  }

  return '/api'
}

export function buildApiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${getApiBase()}${normalizedPath}`
}

export async function apiFetch(path, options = {}) {
  const method = options.method || 'GET'
  const url = buildApiUrl(path)

  let res
  try {
    res = await fetch(url, { cache: 'no-store', ...options })
  } catch (error) {
    throw new Error(`API request failed (${method} ${url}): ${error.message}`, { cause: error })
  }

  if (!res.ok) {
    throw new Error(`API request failed (${method} ${url}): ${res.status} ${res.statusText}`)
  }
  return res.json()
}

import test from 'node:test'
import assert from 'node:assert/strict'

const ORIGINAL_ENV = { ...process.env }
const ORIGINAL_WINDOW = globalThis.window
const ORIGINAL_FETCH = globalThis.fetch

function resetRuntime() {
  process.env = { ...ORIGINAL_ENV }
  if (ORIGINAL_WINDOW === undefined) {
    delete globalThis.window
  } else {
    globalThis.window = ORIGINAL_WINDOW
  }
  if (ORIGINAL_FETCH === undefined) {
    delete globalThis.fetch
  } else {
    globalThis.fetch = ORIGINAL_FETCH
  }
}

test.afterEach(async () => {
  resetRuntime()
})

test('SSR uses API_URL_SERVER when set', async () => {
  delete globalThis.window
  process.env.API_URL_SERVER = 'http://backend:8000/api/'
  process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api'

  const { getApiBase } = await import(`../lib/api.js?case=${Date.now()}`)
  assert.equal(getApiBase(), 'http://backend:8000/api')
})

test('Browser uses NEXT_PUBLIC_API_URL', async () => {
  globalThis.window = {}
  process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api/'

  const { getApiBase } = await import(`../lib/api.js?case=${Date.now()}`)
  assert.equal(getApiBase(), 'http://localhost:8000/api')
})

test('SSR missing environment variables throws a helpful error', async () => {
  delete globalThis.window
  delete process.env.API_URL_SERVER
  delete process.env.NEXT_PUBLIC_API_URL

  const { getApiBase } = await import(`../lib/api.js?case=${Date.now()}`)
  assert.throws(
    () => getApiBase(),
    /Missing API base URL for server runtime. Set API_URL_SERVER \(preferred\) or NEXT_PUBLIC_API_URL\./,
  )
})

test('apiFetch builds URL and wraps network errors with method + URL', async () => {
  delete globalThis.window
  process.env.API_URL_SERVER = 'http://backend:8000/api'
  const { apiFetch } = await import(`../lib/api.js?case=${Date.now()}`)

  globalThis.fetch = async () => {
    throw new Error('connect ECONNREFUSED')
  }

  await assert.rejects(
    apiFetch('/meetings', { method: 'POST' }),
    /API request failed \(POST http:\/\/backend:8000\/api\/meetings\): connect ECONNREFUSED/,
  )
})

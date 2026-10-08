const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '')
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS', 'TRACE'])

function getErrorMessage(data) {
  if (data && typeof data === 'object') {
    const messages = Object.entries(data).flatMap(([field, errors]) => {
      const values = Array.isArray(errors) ? errors : [errors]
      return values.map((error) => {
        if (error && typeof error === 'object') return `${field}: ${getErrorMessage(error)}`
        return field === 'detail' ? String(error) : `${field}: ${error}`
      })
    })
    if (messages.length) return messages.join(' ')
  }
  return 'The request could not be completed. Please try again.'
}

export async function apiRequest(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const headers = { ...options.headers }
  if (!SAFE_METHODS.has(method)) {
    const csrfResponse = await fetch(`${API_BASE_URL}/auth/csrf/`, {
      credentials: 'include',
      headers: { Accept: 'application/json' },
    }).catch(() => null)
    if (!csrfResponse?.ok) {
      throw new Error('Could not prepare a secure request. Check that Django is running and try again.')
    }
    const csrfData = await csrfResponse.json().catch(() => ({}))
    if (!csrfData.csrfToken) throw new Error('The server did not provide a security token. Please try again.')
    headers['X-CSRFToken'] = csrfData.csrfToken
  }

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      method,
      credentials: 'include',
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...headers,
      },
    })
  } catch {
    throw new Error('Could not reach the server. Check that Django is running and try again.')
  }

  if (response.status === 204) return null
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    if (response.status === 401) window.dispatchEvent(new Event('auth:unauthorized'))
    const message = getErrorMessage(data)
    const error = new Error(message === 'The request could not be completed. Please try again.'
      ? `The server returned an error (HTTP ${response.status}). Please try again.`
      : message)
    error.status = response.status
    throw error
  }
  return data
}

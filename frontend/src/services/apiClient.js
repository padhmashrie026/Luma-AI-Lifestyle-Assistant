const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

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
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    })
  } catch {
    throw new Error('Could not reach the server. Check that Django is running and try again.')
  }

  if (response.status === 204) return null
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(getErrorMessage(data))
  return data
}

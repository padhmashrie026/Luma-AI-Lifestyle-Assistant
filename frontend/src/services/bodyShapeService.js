const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export async function calculateBodyShape(measurements) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}/body-shape/calculate/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(measurements),
    })
  } catch {
    throw new Error('Could not reach the server. Check that Django is running and try again.')
  }

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const messages = Object.entries(data)
      .flatMap(([field, errors]) => (Array.isArray(errors) ? errors : [errors]).map((error) => `${field}: ${error}`))
    throw new Error(messages.join(' ') || 'The server could not calculate these measurements.')
  }

  return data
}

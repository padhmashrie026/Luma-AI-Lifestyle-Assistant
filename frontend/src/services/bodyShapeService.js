import { apiRequest } from './apiClient.js'

export async function calculateBodyShape(measurements) {
  return apiRequest('/body-shape/calculate/', {
    method: 'POST',
    body: JSON.stringify(measurements),
  })
}

export function getBodyMeasurements() {
  return apiRequest('/body-shape/measurements/')
}

export function saveBodyMeasurements(measurements) {
  return apiRequest('/body-shape/measurements/', {
    method: 'POST',
    body: JSON.stringify(measurements),
  })
}

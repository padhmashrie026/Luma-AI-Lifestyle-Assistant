import { apiRequest } from './apiClient.js'

export function getCurrentAccount() {
  return apiRequest('/auth/me/')
}

export function registerAccount(fields) {
  return apiRequest('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(fields),
  })
}

export function loginAccount(fields) {
  return apiRequest('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(fields),
  })
}

export function logoutAccount() {
  return apiRequest('/auth/logout/', { method: 'POST' })
}

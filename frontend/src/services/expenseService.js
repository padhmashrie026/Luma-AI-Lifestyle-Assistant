import { apiRequest } from './apiClient.js'

const EXPENSES_PATH = '/expenses/'

export function getExpenses(filters = {}) {
  const query = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== undefined && value !== null) query.set(key, value)
  })
  const suffix = query.toString()
  return apiRequest(`${EXPENSES_PATH}${suffix ? `?${suffix}` : ''}`)
}

export function getExpense(id) {
  return apiRequest(`${EXPENSES_PATH}${id}/`)
}

export function getExpenseSummary(month) {
  const query = new URLSearchParams({ month })
  return apiRequest(`${EXPENSES_PATH}summary/?${query}`)
}

export function getBudgetCategories() {
  return apiRequest(`${EXPENSES_PATH}categories/`)
}

export function createBudgetCategory(category) {
  return apiRequest(`${EXPENSES_PATH}categories/`, {
    method: 'POST',
    body: JSON.stringify(category),
  })
}

export function createExpense(expense) {
  return apiRequest(EXPENSES_PATH, { method: 'POST', body: JSON.stringify(expense) })
}

export function updateExpense(id, expense) {
  return apiRequest(`${EXPENSES_PATH}${id}/`, { method: 'PATCH', body: JSON.stringify(expense) })
}

export function deleteExpense(id) {
  return apiRequest(`${EXPENSES_PATH}${id}/`, { method: 'DELETE' })
}

import { useCallback, useEffect, useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { isValidISODate, localDateString } from '../utils/date.js'
import { createExpense, deleteExpense, getExpense, getExpenseSummary, getExpenses, updateExpense } from '../services/expenseService.js'

const today = localDateString()
const monthNow = today.slice(0, 7)
const blankForm = { profile: '', category: '', daily_plan: '', description: '', amount: '', spent_on: today, notes: '' }
const money = (value, currency) => {
  const amount = Number(value)
  if (!Number.isFinite(amount)) return '-'
  if (!currency) return amount.toFixed(2)
  try { return new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(amount) }
  catch { return `${currency} ${amount.toFixed(2)}` }
}

function ExpensesPage() {
  const [profileId, setProfileId] = useState('')
  const [expenses, setExpenses] = useState([])
  const [summary, setSummary] = useState(null)
  const [categories, setCategories] = useState([])
  const [month, setMonth] = useState(monthNow)
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')
  const [notice, setNotice] = useState('')
  const [formOpen, setFormOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(blankForm)
  const [saving, setSaving] = useState(false)

  const loadData = useCallback(async () => {
    if (!profileId) {
      setExpenses([]); setSummary(null); setCategories([]); setError(''); setLoading(false)
      return
    }
    setLoading(true); setError('')
    try {
      const filters = { profile_id: profileId }
      if (categoryFilter) filters.category_id = categoryFilter
      if (search.trim()) filters.q = search.trim()
      if (dateFrom) filters.start_date = dateFrom
      if (dateTo) filters.end_date = dateTo
      const [listData, summaryData] = await Promise.all([
        getExpenses(filters), getExpenseSummary(profileId, month),
      ])
      if (!Array.isArray(listData) || !summaryData || !Array.isArray(summaryData.spending_by_category)
        || typeof summaryData.total_spending !== 'string' || typeof summaryData.monthly_spending !== 'string') {
        throw new Error('The server returned unexpected expense data. Please try again.')
      }
      setExpenses(listData)
      setSummary(summaryData)
      setCategories(summaryData.spending_by_category)
    } catch (requestError) {
      setError(requestError.message)
    } finally { setLoading(false) }
  }, [profileId, month, search, categoryFilter, dateFrom, dateTo])

  useEffect(() => { loadData() }, [loadData])

  const closeForm = () => { setFormOpen(false); setEditingId(null); setForm(blankForm); setFormError('') }
  const openCreate = () => {
    setNotice(''); setFormError('')
    setForm({ ...blankForm, profile: profileId, category: '', spent_on: `${month}-01` })
    setEditingId(null); setFormOpen(true)
  }
  const openEdit = async (id) => {
    setNotice(''); setFormError('')
    try {
      const item = await getExpense(id)
      setEditingId(id)
      setForm({ profile: String(item.profile), category: String(item.category), daily_plan: item.daily_plan ? String(item.daily_plan) : '', description: item.description, amount: String(item.amount), spent_on: item.spent_on, notes: item.notes || '' })
      setProfileId(String(item.profile)); setFormOpen(true)
    } catch (requestError) { setError(requestError.message) }
  }
  const handleSave = async (event) => {
    event.preventDefault(); setFormError('')
    if (!form.profile || !/^\d+$/.test(form.profile) || !Number.isSafeInteger(Number(form.profile)) || Number(form.profile) < 1) return setFormError('Enter a valid positive profile ID.')
    if (!form.category) return setFormError('Choose a category from this profile.')
    if (!form.description.trim()) return setFormError('Description is required.')
    if (!Number.isFinite(Number(form.amount)) || Number(form.amount) <= 0 || Number(form.amount) > 9999999999.99 || !/^\d+(\.\d{1,2})?$/.test(form.amount)) return setFormError('Enter an amount from 0.01 to 9,999,999,999.99 with up to two decimal places.')
    if (!isValidISODate(form.spent_on)) return setFormError('Enter a valid expense date.')
    const payload = { profile: Number(form.profile), category: Number(form.category), daily_plan: form.daily_plan ? Number(form.daily_plan) : null, description: form.description.trim(), amount: Number(form.amount).toFixed(2), spent_on: form.spent_on, notes: form.notes.trim() }
    setSaving(true)
    try {
      if (editingId) { await updateExpense(editingId, payload); setNotice('Expense updated.') }
      else { await createExpense(payload); setNotice('Expense added.') }
      closeForm(); await loadData()
    } catch (requestError) { setFormError(requestError.message) }
    finally { setSaving(false) }
  }
  const handleDelete = async (item) => {
    if (!window.confirm(`Delete "${item.description}"? This cannot be undone.`)) return
    setNotice('')
    try { await deleteExpense(item.id); setNotice('Expense deleted.'); await loadData() }
    catch (requestError) { setError(requestError.message) }
  }
  const updateField = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const categoryName = (id) => categories.find((category) => category.category_id === id)?.category || `Category ${id}`
  const currency = summary?.currency_code

  return <div className="expenses-page">
    <section className="dashboard-welcome wardrobe-welcome"><div><p className="eyebrow">Your money, clearly organized</p><h2 className="welcome-title">Expense Manager</h2><p className="welcome-copy">Track spending and review the budget figures returned for your profile.</p></div><Button className="primary-button" onClick={openCreate} disabled={!profileId || !categories.length}> Add expense</Button></section>
    {notice && <p className="expense-notice" role="status">{notice}</p>}
    <Card className="expense-scope-card"><div className="expense-scope"><div><label htmlFor="expense-profile">Profile ID</label><input id="expense-profile" type="number" min="1" step="1" value={profileId} onChange={(event) => setProfileId(event.target.value)} placeholder="Enter an existing profile ID" /><small>Required for profile totals, categories, budget status, and adding expenses.</small></div><div><label htmlFor="expense-month">Summary month</label><input id="expense-month" type="month" value={month} onChange={(event) => setMonth(event.target.value)} /></div></div></Card>
    {summary && <section className="expense-summary-grid" aria-label="Expense overview">
      <Card className="expense-stat"><span>Total spending</span><strong>{money(summary.total_spending, currency)}</strong><small>All recorded expenses for this profile</small></Card>
      <Card className="expense-stat"><span>Monthly spending</span><strong>{money(summary.monthly_spending, currency)}</strong><small>{summary.month}</small></Card>
      <Card className="expense-stat"><span>Monthly budget</span><strong>{summary.monthly_budget?.available ? money(summary.monthly_budget.monthly_limit, currency) : 'Not set'}</strong><small>{summary.monthly_budget?.status?.replaceAll('_', ' ') || 'No budget data'}</small></Card>
      {summary.monthly_budget?.available && <Card className="expense-stat"><span>Remaining this month</span><strong>{money(summary.monthly_budget.remaining, currency)}</strong><small>As reported by the expense summary</small></Card>}
    </section>}
    {summary && <Card className="expense-category-card"><SectionHeader title="Monthly category breakdown" description={`Spending and limits returned by the API for ${summary.month}.`} />{categories.length ? <div className="expense-category-list">{categories.map((row) => <div className="expense-category-row" key={row.category_id}><div><strong>{row.category}</strong><small>{row.budget_status.replaceAll('_', ' ')}{row.is_active ? '' : '  -  inactive'}</small></div><div><strong>{money(row.spent, currency)}</strong><small>of {money(row.monthly_limit, currency)}</small></div><div className="expense-meter" aria-label={`${row.category} spending ${row.budget_status}`}><span style={{ width: `${Math.min(100, row.monthly_limit > 0 ? Number(row.spent) / Number(row.monthly_limit) * 100 : Number(row.spent) > 0 ? 100 : 0)}%` }} /></div></div>)}</div> : <p className="expense-muted">No categories were returned for this profile.</p>}</Card>}
    {formOpen && <Card className="expense-form-card"><SectionHeader title={editingId ? 'Edit expense' : 'Add an expense'} description="Enter the fields accepted by the expense API." /><form onSubmit={handleSave} noValidate><div className="expense-form-grid">
      <div><label htmlFor="expense-form-profile">Profile ID <span>Required</span></label><input id="expense-form-profile" name="profile" type="number" min="1" step="1" value={form.profile} onChange={updateField} required /></div>
      <div><label htmlFor="expense-form-category">Budget category <span>Required</span></label><select id="expense-form-category" name="category" value={form.category} onChange={updateField} required><option value="">Choose a category</option>{categories.map((item) => <option key={item.category_id} value={item.category_id}>{item.category}</option>)}</select></div>
      <div><label htmlFor="expense-description">Description <span>Required</span></label><input id="expense-description" name="description" maxLength="160" value={form.description} onChange={updateField} required /></div>
      <div><label htmlFor="expense-amount">Amount <span>Required</span></label><input id="expense-amount" name="amount" type="number" min="0.01" step="0.01" value={form.amount} onChange={updateField} required /></div>
      <div><label htmlFor="expense-date">Date spent <span>Required</span></label><input id="expense-date" name="spent_on" type="date" value={form.spent_on} onChange={updateField} required /></div>
      <div><label htmlFor="expense-daily-plan">Daily plan ID <span>Optional</span></label><input id="expense-daily-plan" name="daily_plan" type="number" min="1" step="1" value={form.daily_plan} onChange={updateField} /></div>
      <div className="expense-notes-field"><label htmlFor="expense-notes">Notes <span>Optional</span></label><textarea id="expense-notes" name="notes" maxLength="240" rows="3" value={form.notes} onChange={updateField} /></div>
    </div>{formError && <p className="expense-error" role="alert">{formError}</p>}<div className="form-actions"><Button type="submit" className="primary-button" disabled={saving}>{saving ? 'Saving...' : editingId ? 'Save changes' : 'Add expense'}</Button><Button type="button" className="secondary-button" onClick={() => { setForm(blankForm); setFormError('') }} disabled={saving}>Reset</Button><Button type="button" className="secondary-button" onClick={closeForm} disabled={saving}>Cancel</Button></div></form></Card>}
    <Card className="expense-filter-card"><form className="expense-filters" onSubmit={(event) => event.preventDefault()}><div><label htmlFor="expense-search">Search description or notes</label><input id="expense-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search expenses" /></div><div><label htmlFor="expense-category-filter">Category</label><select id="expense-category-filter" value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)}><option value="">All categories</option>{categories.map((item) => <option key={item.category_id} value={item.category_id}>{item.category}</option>)}</select></div><div><label htmlFor="expense-from">From</label><input id="expense-from" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} /></div><div><label htmlFor="expense-to">To</label><input id="expense-to" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} /></div></form></Card>
    <section className="expense-list-section"><SectionHeader title="Expenses" description={loading ? 'Loading expenses...' : `${expenses.length} ${expenses.length === 1 ? 'expense' : 'expenses'}`} />
      {error && <div className="expense-error-box" role="alert"><span>{error}</span><Button className="secondary-button" onClick={loadData}>Try again</Button></div>}
      {loading ? <Card className="expense-empty"><p>Loading expenses...</p></Card> : !error && expenses.length === 0 ? <Card className="expense-empty"><h3>{profileId ? 'No expenses found' : 'Choose a profile to begin'}</h3><p>{profileId ? 'No records match the current filters, or this profile has no expenses yet.' : 'Enter an existing profile ID above to load its expenses, category summary, and budget status.'}</p>{profileId && <Button className="primary-button" onClick={openCreate}>Add your first expense</Button>}</Card> : !error && <div className="expense-table-wrap"><table className="expense-table"><thead><tr><th scope="col">Description</th><th scope="col">Category</th><th scope="col">Date</th><th scope="col">Amount</th><th scope="col">Notes</th><th scope="col"><span className="visually-hidden">Actions</span></th></tr></thead><tbody>{expenses.map((item) => <tr key={item.id}><td data-label="Description"><strong>{item.description}</strong></td><td data-label="Category">{categoryName(item.category)}</td><td data-label="Date">{item.spent_on}</td><td data-label="Amount" className="expense-amount">{money(item.amount, currency)}</td><td data-label="Notes">{item.notes || '-'}</td><td data-label="Actions"><div className="expense-row-actions"><Button className="item-edit-button" onClick={() => openEdit(item.id)}>Edit</Button><Button className="item-delete-button" onClick={() => handleDelete(item)}>Delete</Button></div></td></tr>)}</tbody></table></div>}
    </section>
  </div>
}

export default ExpensesPage

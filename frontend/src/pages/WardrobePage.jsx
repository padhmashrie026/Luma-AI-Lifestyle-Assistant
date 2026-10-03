import { useCallback, useEffect, useMemo, useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import {
  createWardrobeItem,
  deleteWardrobeItem,
  getWardrobeItem,
  getWardrobeItems,
  updateWardrobeItem,
} from '../services/wardrobeService.js'

const categories = [
  ['top', 'Top'], ['bottom', 'Bottom'], ['dress', 'Dress or one-piece'],
  ['outerwear', 'Outerwear'], ['shoes', 'Shoes'], ['accessory', 'Accessory'], ['other', 'Other'],
]
const statuses = [
  ['available', 'Available'], ['laundry', 'In laundry'], ['repair', 'Needs repair'], ['archived', 'Archived'],
]
const emptyForm = { profile: '', name: '', category: '', color: '', brand: '', size_label: '', status: 'available', notes: '' }

function WardrobePage() {
  const [items, setItems] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [listError, setListError] = useState('')
  const [formOpen, setFormOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [formErrors, setFormErrors] = useState({})
  const [isSaving, setIsSaving] = useState(false)
  const [notice, setNotice] = useState('')
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({ category: '', color: '', status: '' })
  const [appliedFilters, setAppliedFilters] = useState({})

  const loadItems = useCallback(async (activeFilters = {}) => {
    setIsLoading(true)
    setListError('')
    try {
      const data = await getWardrobeItems(activeFilters)
      setItems(Array.isArray(data) ? data : [])
    } catch (error) {
      setListError(error.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { loadItems(appliedFilters) }, [loadItems, appliedFilters])

  const visibleItems = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return items
    return items.filter((item) => [item.name, item.color, item.brand, item.category, item.size_label]
      .some((value) => value?.toLowerCase().includes(term)))
  }, [items, search])

  const openCreateForm = () => {
    setEditingId(null)
    setForm(emptyForm)
    setFormErrors({})
    setFormOpen(true)
    setNotice('')
  }

  const openEditForm = async (id) => {
    setNotice('')
    setFormErrors({})
    try {
      const item = await getWardrobeItem(id)
      setEditingId(id)
      setForm({
        profile: String(item.profile), name: item.name, category: item.category,
        color: item.color || '', brand: item.brand || '', size_label: item.size_label || '',
        status: item.status, notes: item.notes || '',
      })
      setFormOpen(true)
    } catch (error) {
      setListError(error.message)
    }
  }

  const closeForm = () => {
    setFormOpen(false)
    setEditingId(null)
    setForm(emptyForm)
    setFormErrors({})
  }

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setFormErrors((current) => ({ ...current, [name]: undefined }))
  }

  const validateForm = () => {
    const errors = {}
    if (!form.profile.trim()) errors.profile = 'Profile ID is required.'
    else if (!/^\d+$/.test(form.profile.trim()) || Number(form.profile) < 1) errors.profile = 'Enter a valid positive profile ID.'
    if (!form.name.trim()) errors.name = 'Item name is required.'
    if (!form.category) errors.category = 'Choose a category.'
    return errors
  }

  const handleSave = async (event) => {
    event.preventDefault()
    const errors = validateForm()
    setFormErrors(errors)
    if (Object.keys(errors).length) return
    const payload = { ...form, profile: Number(form.profile), name: form.name.trim() }
    setIsSaving(true)
    setNotice('')
    try {
      if (editingId) {
        await updateWardrobeItem(editingId, payload)
        setNotice('Wardrobe item updated.')
      } else {
        await createWardrobeItem(payload)
        setNotice('Wardrobe item added.')
      }
      closeForm()
      await loadItems(appliedFilters)
    } catch (error) {
      setFormErrors((current) => ({ ...current, api: error.message }))
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async (item) => {
    if (!window.confirm(`Delete “${item.name}” from your wardrobe? This cannot be undone.`)) return
    setNotice('')
    try {
      await deleteWardrobeItem(item.id)
      setNotice('Wardrobe item deleted.')
      await loadItems(appliedFilters)
    } catch (error) {
      setListError(error.message)
    }
  }

  const applyFilters = (event) => {
    event.preventDefault()
    setAppliedFilters({ ...filters })
  }

  const clearFilters = () => {
    setFilters({ category: '', color: '', status: '' })
    setSearch('')
    setAppliedFilters({})
  }

  return <div className="wardrobe-page">
    <section className="dashboard-welcome wardrobe-welcome">
      <div><p className="eyebrow">Your closet, organized</p><h2 className="welcome-title">Smart Wardrobe</h2><p className="welcome-copy">Keep track of the pieces you own and their everyday details.</p></div>
      <Button className="primary-button wardrobe-add-button" onClick={openCreateForm}>＋ Add item</Button>
    </section>

    {notice && <p className="wardrobe-notice" role="status">{notice}</p>}

    {formOpen && <Card className="wardrobe-form-card">
      <SectionHeader title={editingId ? 'Edit wardrobe item' : 'Add a wardrobe item'} description="Fields marked required are needed to save an item." />
      <form onSubmit={handleSave} noValidate>
        <div className="wardrobe-form-grid">
          <div className="wardrobe-field"><label htmlFor="wardrobe-profile">Profile ID <span>Required</span></label><input id="wardrobe-profile" name="profile" type="number" min="1" step="1" value={form.profile} onChange={handleFieldChange} aria-invalid={Boolean(formErrors.profile)} aria-describedby={formErrors.profile ? 'wardrobe-profile-error' : 'wardrobe-profile-help'} />{formErrors.profile ? <small className="wardrobe-field-error" id="wardrobe-profile-error">{formErrors.profile}</small> : <small className="wardrobe-field-help" id="wardrobe-profile-help">Use an existing profile ID.</small>}</div>
          <div className="wardrobe-field"><label htmlFor="wardrobe-name">Item name <span>Required</span></label><input id="wardrobe-name" name="name" type="text" maxLength="100" value={form.name} onChange={handleFieldChange} aria-invalid={Boolean(formErrors.name)} aria-describedby={formErrors.name ? 'wardrobe-name-error' : undefined} />{formErrors.name && <small className="wardrobe-field-error" id="wardrobe-name-error">{formErrors.name}</small>}</div>
          <div className="wardrobe-field"><label htmlFor="wardrobe-category">Category <span>Required</span></label><select id="wardrobe-category" name="category" value={form.category} onChange={handleFieldChange} aria-invalid={Boolean(formErrors.category)} aria-describedby={formErrors.category ? 'wardrobe-category-error' : undefined}><option value="">Choose a category</option>{categories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select>{formErrors.category && <small className="wardrobe-field-error" id="wardrobe-category-error">{formErrors.category}</small>}</div>
          <div className="wardrobe-field"><label htmlFor="wardrobe-color">Color</label><input id="wardrobe-color" name="color" type="text" maxLength="40" value={form.color} onChange={handleFieldChange} /></div>
          <div className="wardrobe-field"><label htmlFor="wardrobe-brand">Brand</label><input id="wardrobe-brand" name="brand" type="text" maxLength="80" value={form.brand} onChange={handleFieldChange} /></div>
          <div className="wardrobe-field"><label htmlFor="wardrobe-size">Size label</label><input id="wardrobe-size" name="size_label" type="text" maxLength="30" value={form.size_label} onChange={handleFieldChange} /></div>
          <div className="wardrobe-field"><label htmlFor="wardrobe-status">Status</label><select id="wardrobe-status" name="status" value={form.status} onChange={handleFieldChange}>{statuses.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
          <div className="wardrobe-field wardrobe-notes-field"><label htmlFor="wardrobe-notes">Notes</label><textarea id="wardrobe-notes" name="notes" maxLength="240" rows="3" value={form.notes} onChange={handleFieldChange} /></div>
        </div>
        {formErrors.api && <p className="wardrobe-api-error" role="alert">{formErrors.api}</p>}
        <div className="form-actions"><Button type="submit" className="primary-button" disabled={isSaving}>{isSaving ? 'Saving…' : editingId ? 'Save changes' : 'Add item'}</Button><Button type="button" className="secondary-button" onClick={() => { setForm(emptyForm); setFormErrors({}) }} disabled={isSaving}>Reset</Button><Button type="button" className="secondary-button" onClick={closeForm} disabled={isSaving}>Cancel</Button></div>
      </form>
    </Card>}

    <Card className="wardrobe-filter-card">
      <form className="wardrobe-filter-form" onSubmit={applyFilters}>
        <div className="wardrobe-search-field"><label htmlFor="wardrobe-search">Search wardrobe</label><input id="wardrobe-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name, brand, color…" /></div>
        <div className="wardrobe-filter-field"><label htmlFor="filter-category">Category</label><select id="filter-category" value={filters.category} onChange={(event) => setFilters((current) => ({ ...current, category: event.target.value }))}><option value="">All categories</option>{categories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
        <div className="wardrobe-filter-field"><label htmlFor="filter-color">Color</label><input id="filter-color" type="search" value={filters.color} onChange={(event) => setFilters((current) => ({ ...current, color: event.target.value }))} placeholder="Any color" /></div>
        <div className="wardrobe-filter-field"><label htmlFor="filter-status">Status</label><select id="filter-status" value={filters.status} onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))}><option value="">All statuses</option>{statuses.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
        <div className="wardrobe-filter-actions"><Button type="submit" className="secondary-button">Apply filters</Button><Button type="button" className="filter-clear-button" onClick={clearFilters}>Clear</Button></div>
      </form>
    </Card>

    <section className="wardrobe-list-section" aria-labelledby="wardrobe-list-title">
      <SectionHeader id="wardrobe-list-title" title="Wardrobe items" description={isLoading ? 'Loading items…' : `${visibleItems.length} ${visibleItems.length === 1 ? 'item' : 'items'}`} />
      {listError && <div className="wardrobe-list-error" role="alert"><p>{listError}</p><Button className="secondary-button" onClick={() => loadItems(appliedFilters)}>Try again</Button></div>}
      {isLoading ? <Card className="wardrobe-empty-state"><p>Loading your wardrobe…</p></Card> : !listError && visibleItems.length === 0 ? <Card className="wardrobe-empty-state"><span className="wardrobe-empty-icon" aria-hidden="true">⌑</span><h3>{items.length ? 'No items match these filters' : 'Your wardrobe is ready for its first item'}</h3><p>{items.length ? 'Try changing your search or clearing the filters.' : 'Add an item you own to start keeping its details in one place.'}</p>{items.length ? <Button className="secondary-button" onClick={clearFilters}>Clear filters</Button> : <Button className="primary-button" onClick={openCreateForm}>Add your first item</Button>}</Card> : !listError && <div className="wardrobe-items-grid">{visibleItems.map((item) => <Card className="wardrobe-item-card" key={item.id}>
        <div className="wardrobe-item-top"><span className="wardrobe-category-tag">{categories.find(([value]) => value === item.category)?.[1] || item.category}</span><span className={`wardrobe-status-tag status-${item.status}`}>{statuses.find(([value]) => value === item.status)?.[1] || item.status}</span></div>
        <h3>{item.name}</h3>
        <p className="wardrobe-item-color">{item.color || 'Color not specified'}</p>
        <dl className="wardrobe-item-details">{item.brand && <div><dt>Brand</dt><dd>{item.brand}</dd></div>}{item.size_label && <div><dt>Size</dt><dd>{item.size_label}</dd></div>}{item.notes && <div className="wardrobe-item-notes"><dt>Notes</dt><dd>{item.notes}</dd></div>}</dl>
        <div className="wardrobe-item-actions"><Button className="item-edit-button" onClick={() => openEditForm(item.id)}>Edit</Button><Button className="item-delete-button" onClick={() => handleDelete(item)}>Delete</Button></div>
      </Card>)}</div>}
    </section>
  </div>
}

export default WardrobePage

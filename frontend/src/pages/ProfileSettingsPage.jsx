import { useEffect, useRef, useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { getProfile, getSettings, updateProfile, updateSettings } from '../services/profileService.js'
const blank = { username: '', first_name: '', last_name: '', email: '', display_name: '' }
function ProfileSettingsPage({ mode = 'profile' }) {
  const settings = mode === 'settings'
  const [record, setRecord] = useState(null)
  const [form, setForm] = useState(blank)
  const [currency, setCurrency] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [fieldError, setFieldError] = useState('')
  const emailRef = useRef(null)
  const applyData = (data) => {
    setRecord(data)
    if (settings) setCurrency(data.currency_code || '')
    else setForm({ username: data.username || '', first_name: data.first_name || '', last_name: data.last_name || '', email: data.email || '', display_name: data.display_name || '' })
  }
  useEffect(() => {
    let active = true
    ;(settings ? getSettings() : getProfile()).then((data) => { if (active) applyData(data) }).catch((e) => { if (active) setError(e.message) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [settings])
  const saveProfile = async (event) => {
    event.preventDefault(); setError(''); setFieldError(''); setNotice('')
    if (!emailRef.current.validity.valid) { setFieldError('Enter a valid email address, or leave it blank.'); return }
    setSaving(true)
    try { applyData(await updateProfile({ first_name: form.first_name, last_name: form.last_name, email: form.email, display_name: form.display_name })); setNotice('Profile changes saved.') }
    catch (e) { setError(e.message) } finally { setSaving(false) }
  }
  const saveSettings = async (event) => {
    event.preventDefault(); setError(''); setFieldError(''); setNotice('')
    if (!/^[a-zA-Z]{3}$/.test(currency.trim())) { setFieldError('Enter a three-letter currency code.'); return }
    setSaving(true)
    try { applyData(await updateSettings({ currency_code: currency.trim() })); setNotice('Settings saved.') }
    catch (e) { setError(e.message) } finally { setSaving(false) }
  }
  const reset = () => {
    setError(''); setFieldError(''); setNotice('')
    if (settings) setCurrency(record.currency_code || '')
    else setForm({ username: record.username || '', first_name: record.first_name || '', last_name: record.last_name || '', email: record.email || '', display_name: record.display_name || '' })
  }
  const change = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const title = settings ? 'Settings' : 'Profile'
  return <div className="account-page">
    <section className="dashboard-welcome account-welcome"><div><p className="eyebrow">Your account details</p><h2 className="welcome-title">{title}</h2><p className="welcome-copy">{settings ? 'Manage your account preference.' : 'Review and update the profile details stored for your account.'}</p></div></section>
    {notice && <p className="account-notice" role="status">{notice}</p>}{error && <p className="account-error" role="alert">{error}</p>}
    {loading && <Card className="account-state" aria-live="polite">Loading {title.toLowerCase()}…</Card>}
    {!loading && !record && !error && <Card className="account-state"><h3>{title} unavailable</h3><p>We couldn’t find the signed-in account’s {title.toLowerCase()}. Try refreshing the page.</p></Card>}
    {!loading && record && !settings && <Card className="account-form-card"><SectionHeader title="Profile information" description="Fields are saved to your signed-in account." />
      <form onSubmit={saveProfile} noValidate><div className="account-form-grid">
        <div><label htmlFor="profile-username">Username</label><input id="profile-username" value={form.username} readOnly aria-readonly="true" /><small>Username is read-only here.</small></div>
        <div><label htmlFor="profile-display-name">Display name</label><input id="profile-display-name" name="display_name" maxLength="80" value={form.display_name} onChange={change} /></div>
        <div><label htmlFor="profile-first-name">First name</label><input id="profile-first-name" name="first_name" maxLength="150" value={form.first_name} onChange={change} /></div>
        <div><label htmlFor="profile-last-name">Last name</label><input id="profile-last-name" name="last_name" maxLength="150" value={form.last_name} onChange={change} /></div>
        <div className="account-email-field"><label htmlFor="profile-email">Email</label><input ref={emailRef} id="profile-email" type="email" maxLength="254" value={form.email} onChange={change} autoComplete="email" /></div>
      </div>{fieldError && <p className="account-field-error" role="alert">{fieldError}</p>}<div className="form-actions"><Button type="submit" className="primary-button" disabled={saving}>{saving ? 'Saving…' : 'Save changes'}</Button><Button type="button" className="secondary-button" onClick={reset} disabled={saving}>Reset</Button></div></form>
      <p className="account-timestamp">Last updated: {record.updated_at ? new Date(record.updated_at).toLocaleString() : 'Not provided'}</p></Card>}
    {!loading && record && settings && <Card className="account-form-card"><SectionHeader title="Application preference" description="This is the only settings preference currently stored by the backend." />
      <form onSubmit={saveSettings} noValidate><div className="account-form-grid account-settings-grid"><div><label htmlFor="settings-currency">Currency code</label><input id="settings-currency" maxLength="3" pattern="[A-Za-z]{3}" value={currency} onChange={(e) => setCurrency(e.target.value)} /><small>Enter a three-letter code.</small></div></div>
      {fieldError && <p className="account-field-error" role="alert">{fieldError}</p>}<div className="form-actions"><Button type="submit" className="primary-button" disabled={saving}>{saving ? 'Saving…' : 'Save settings'}</Button><Button type="button" className="secondary-button" onClick={reset} disabled={saving}>Reset</Button></div></form></Card>}
  </div>
}
export function ProfilePage() { return <ProfileSettingsPage mode="profile" /> }
export function SettingsPage() { return <ProfileSettingsPage mode="settings" /> }

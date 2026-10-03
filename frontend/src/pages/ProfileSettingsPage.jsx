import { useRef, useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { getProfile, getSettings, updateProfile, updateSettings } from '../services/profileService.js'

const SESSION_PROFILE_KEY = 'luma-development-profile-id'
const blankProfile = { username: '', first_name: '', last_name: '', email: '', display_name: '' }

function getSavedProfileId() {
  try { return window.sessionStorage.getItem(SESSION_PROFILE_KEY) || '' }
  catch { return '' }
}

function ProfileSettingsPage({ mode = 'profile' }) {
  const isSettings = mode === 'settings'
  const [profileId, setProfileId] = useState(getSavedProfileId)
  const [record, setRecord] = useState(null)
  const [profileForm, setProfileForm] = useState(blankProfile)
  const [currencyCode, setCurrencyCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [fieldError, setFieldError] = useState('')
  const [notice, setNotice] = useState('')
  const emailRef = useRef(null)
  const title = isSettings ? 'Settings' : 'Profile'

  const loadRecord = async (event) => {
    event?.preventDefault()
    setError(''); setFieldError(''); setNotice('')
    if (!/^\d+$/.test(profileId) || Number(profileId) < 1) {
      setError('Enter a valid positive profile ID to continue.')
      return
    }
    setLoading(true)
    try {
      const data = isSettings ? await getSettings(profileId) : await getProfile(profileId)
      setRecord(data)
      if (isSettings) setCurrencyCode(data.currency_code || '')
      else setProfileForm({
        username: data.username || '', first_name: data.first_name || '',
        last_name: data.last_name || '', email: data.email || '',
        display_name: data.display_name || '',
      })
      try { window.sessionStorage.setItem(SESSION_PROFILE_KEY, profileId) } catch { /* Session storage is optional. */ }
    } catch (requestError) {
      setRecord(null); setError(requestError.message)
    } finally { setLoading(false) }
  }

  const saveProfile = async (event) => {
    event.preventDefault(); setError(''); setFieldError(''); setNotice('')
    if (emailRef.current && !emailRef.current.validity.valid) {
      setFieldError('Enter a valid email address, or leave the field blank.')
      emailRef.current.focus()
      return
    }
    setSaving(true)
    try {
      const data = await updateProfile(profileId, {
        first_name: profileForm.first_name,
        last_name: profileForm.last_name,
        email: profileForm.email,
        display_name: profileForm.display_name,
      })
      setRecord(data)
      setProfileForm({
        username: data.username || '', first_name: data.first_name || '',
        last_name: data.last_name || '', email: data.email || '',
        display_name: data.display_name || '',
      })
      setNotice('Profile changes saved.')
    } catch (requestError) { setError(requestError.message) }
    finally { setSaving(false) }
  }

  const saveSettings = async (event) => {
    event.preventDefault(); setError(''); setFieldError(''); setNotice('')
    if (!/^[a-zA-Z]{3}$/.test(currencyCode.trim())) {
      setFieldError('Enter a three-letter currency code.')
      return
    }
    setSaving(true)
    try {
      const data = await updateSettings(profileId, { currency_code: currencyCode.trim() })
      setRecord(data); setCurrencyCode(data.currency_code || '')
      setNotice('Settings saved.')
    } catch (requestError) { setError(requestError.message) }
    finally { setSaving(false) }
  }

  const resetForm = () => {
    setFieldError(''); setError(''); setNotice('')
    if (isSettings) setCurrencyCode(record?.currency_code || '')
    else setProfileForm({
      username: record?.username || '', first_name: record?.first_name || '',
      last_name: record?.last_name || '', email: record?.email || '',
      display_name: record?.display_name || '',
    })
  }
  const changeProfileField = (event) => setProfileForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const changeProfileId = (event) => {
    setProfileId(event.target.value)
    setRecord(null); setError(''); setFieldError(''); setNotice('')
  }

  return <div className="account-page">
    <section className="dashboard-welcome account-welcome">
      <div><p className="eyebrow">Your account details</p><h2 className="welcome-title">{title}</h2><p className="welcome-copy">{isSettings ? 'Manage the preference available in your current account settings.' : 'Review and update the profile details stored for your account.'}</p></div>
    </section>

    <Card className="account-scope-card">
      <form className="account-scope-form" onSubmit={loadRecord}>
        <div><label htmlFor={`${mode}-profile-id`}>Profile ID</label><input id={`${mode}-profile-id`} type="number" min="1" step="1" value={profileId} onChange={changeProfileId} disabled={loading} placeholder="Enter an existing profile ID" /><small>The development API requires an explicit profile ID. These endpoints do not sign you in or identify a current user.</small></div>
        <Button type="submit" className="secondary-button" disabled={loading}>{loading ? 'Loading…' : `Load ${isSettings ? 'settings' : 'profile'}`}</Button>
      </form>
    </Card>

    {notice && <p className="account-notice" role="status">{notice}</p>}
    {error && <p className="account-error" role="alert">{error}</p>}
    {loading && <Card className="account-state" aria-live="polite">Loading {isSettings ? 'settings' : 'profile'}…</Card>}

    {!loading && record && !isSettings && <Card className="account-form-card">
      <SectionHeader title="Profile information" description="Fields are saved to the existing Django user and profile record." />
      <form onSubmit={saveProfile} noValidate>
        <div className="account-form-grid">
          <div><label htmlFor="profile-username">Username</label><input id="profile-username" value={profileForm.username} readOnly aria-readonly="true" /><small>Username is provided by Django and is read-only here.</small></div>
          <div><label htmlFor="profile-display-name">Display name</label><input id="profile-display-name" name="display_name" maxLength="80" value={profileForm.display_name} onChange={changeProfileField} /></div>
          <div><label htmlFor="profile-first-name">First name</label><input id="profile-first-name" name="first_name" maxLength="150" value={profileForm.first_name} onChange={changeProfileField} /></div>
          <div><label htmlFor="profile-last-name">Last name</label><input id="profile-last-name" name="last_name" maxLength="150" value={profileForm.last_name} onChange={changeProfileField} /></div>
          <div className="account-email-field"><label htmlFor="profile-email">Email</label><input ref={emailRef} id="profile-email" name="email" type="email" maxLength="254" value={profileForm.email} onChange={changeProfileField} autoComplete="email" /></div>
        </div>
        {fieldError && <p className="account-field-error" role="alert">{fieldError}</p>}
        <div className="form-actions"><Button type="submit" className="primary-button" disabled={saving}>{saving ? 'Saving…' : 'Save changes'}</Button><Button type="button" className="secondary-button" onClick={resetForm} disabled={saving}>Reset</Button></div>
      </form>
      <p className="account-timestamp">Last updated: {record.updated_at ? new Date(record.updated_at).toLocaleString() : 'Not provided'}</p>
    </Card>}

    {!loading && record && isSettings && <Card className="account-form-card">
      <SectionHeader title="Application preference" description="This is the only settings preference currently stored by the backend." />
      <form onSubmit={saveSettings} noValidate>
        <div className="account-form-grid account-settings-grid"><div>
          <label htmlFor="settings-currency">Currency code</label>
          <input id="settings-currency" name="currency_code" type="text" inputMode="text" autoCapitalize="characters" maxLength="3" pattern="[A-Za-z]{3}" value={currencyCode} onChange={(event) => setCurrencyCode(event.target.value)} aria-describedby="settings-currency-help" />
          <small id="settings-currency-help">Enter a three-letter code. The backend does not define a fixed list of currency choices.</small>
        </div></div>
        {fieldError && <p className="account-field-error" role="alert">{fieldError}</p>}
        <div className="form-actions"><Button type="submit" className="primary-button" disabled={saving}>{saving ? 'Saving…' : 'Save settings'}</Button><Button type="button" className="secondary-button" onClick={resetForm} disabled={saving}>Reset</Button></div>
      </form>
    </Card>}

    {!loading && !record && !error && <Card className="account-state"><h3>Load your {isSettings ? 'settings' : 'profile'}</h3><p>Enter an existing profile ID above to retrieve the values stored by the backend.</p></Card>}
  </div>
}

export function ProfilePage() { return <ProfileSettingsPage mode="profile" /> }
export function SettingsPage() { return <ProfileSettingsPage mode="settings" /> }

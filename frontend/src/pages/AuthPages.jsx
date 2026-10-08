import { useState } from 'react'
import { useAuth } from '../auth/AuthContext.jsx'
import Button from '../components/Button.jsx'
import Icon from '../components/Icon.jsx'

function AuthPage({ mode, onNavigate, onAuthenticated }) {
  const isRegister = mode === 'register'
  const { signIn, signUp } = useAuth()
  const [fields, setFields] = useState({ username: '', email: '', password: '', confirmPassword: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const updateField = (event) => {
    setFields((current) => ({ ...current, [event.target.name]: event.target.value }))
    setError('')
  }

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    const username = fields.username.trim()
    if (!username) return setError('Enter your username.')
    if (!fields.password) return setError('Enter your password.')
    if (isRegister) {
      if (!fields.email.trim()) return setError('Enter your email address.')
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fields.email.trim())) return setError('Enter a valid email address.')
      if (fields.password !== fields.confirmPassword) return setError('The passwords do not match.')
    }

    setSubmitting(true)
    try {
      if (isRegister) {
        await signUp({
          username,
          email: fields.email.trim(),
          password: fields.password,
          password_confirmation: fields.confirmPassword,
        })
      } else {
        await signIn({ username, password: fields.password })
      }
      onAuthenticated()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return <main className="auth-page">
    <section className="auth-panel" aria-labelledby="auth-title">
      <a className="auth-brand" href="/login" onClick={(event) => { event.preventDefault(); onNavigate('/login') }}>
        <span className="brand-mark"><Icon name="sparkle" size={19} strokeWidth={1.8} /></span>
        <span className="brand-name">Luma<span className="brand-caption">Lifestyle, in balance</span></span>
      </a>
      <div className="auth-intro">
        <p className="eyebrow">Your everyday, thoughtfully planned</p>
        <h1 id="auth-title">{isRegister ? 'Create your account' : 'Welcome back'}</h1>
        <p>{isRegister ? 'Start building a lifestyle that feels like yours.' : 'Sign in to continue to your lifestyle workspace.'}</p>
      </div>

      <form className="auth-form" onSubmit={submit} noValidate>
        <div className="auth-field">
          <label htmlFor="auth-username">Username</label>
          <input id="auth-username" name="username" value={fields.username} onChange={updateField} autoComplete="username" maxLength={150} required autoFocus />
        </div>
        {isRegister && <div className="auth-field">
          <label htmlFor="auth-email">Email</label>
          <input id="auth-email" name="email" type="email" value={fields.email} onChange={updateField} autoComplete="email" maxLength={254} required />
        </div>}
        <div className="auth-field">
          <label htmlFor="auth-password">Password</label>
          <input id="auth-password" name="password" type="password" value={fields.password} onChange={updateField} autoComplete={isRegister ? 'new-password' : 'current-password'} required />
        </div>
        {isRegister && <div className="auth-field">
          <label htmlFor="auth-confirm-password">Confirm password</label>
          <input id="auth-confirm-password" name="confirmPassword" type="password" value={fields.confirmPassword} onChange={updateField} autoComplete="new-password" required />
        </div>}
        {error && <p className="auth-error" role="alert">{error}</p>}
        <Button type="submit" className="primary-button auth-submit" disabled={submitting}>
          {submitting ? (isRegister ? 'Creating account…' : 'Signing in…') : (isRegister ? 'Create account' : 'Sign in')}
        </Button>
      </form>

      <p className="auth-switch">
        {isRegister ? 'Already have an account?' : 'New to Luma?'}{' '}
        <a href={isRegister ? '/login' : '/register'} onClick={(event) => {
          event.preventDefault()
          onNavigate(isRegister ? '/login' : '/register')
        }}>{isRegister ? 'Sign in' : 'Create an account'}</a>
      </p>
    </section>
  </main>
}

export function LoginPage({ onNavigate, onAuthenticated }) {
  return <AuthPage mode="login" onNavigate={onNavigate} onAuthenticated={onAuthenticated} />
}

export function RegisterPage({ onNavigate, onAuthenticated }) {
  return <AuthPage mode="register" onNavigate={onNavigate} onAuthenticated={onAuthenticated} />
}

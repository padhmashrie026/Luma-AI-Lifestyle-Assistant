import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { getCurrentAccount, loginAccount, logoutAccount, registerAccount } from '../services/authService.js'

const AuthContext = createContext(null)

function isAuthenticationFailure(error) {
  // DRF with SessionAuthentication can return 403 for an anonymous request.
  return error.status === 401 || error.status === 403
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState('loading')
  const [loadError, setLoadError] = useState('')

  const refreshAccount = useCallback(async () => {
    setStatus('loading')
    setLoadError('')
    try {
      const account = await getCurrentAccount()
      setUser(account)
      setStatus('authenticated')
    } catch (error) {
      if (isAuthenticationFailure(error)) {
        setUser(null)
        setStatus('unauthenticated')
      } else {
        setLoadError(error.message)
        setStatus('error')
      }
    }
  }, [])

  useEffect(() => { refreshAccount() }, [refreshAccount])

  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null)
      setStatus('unauthenticated')
    }
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [])

  const signIn = useCallback(async (fields) => {
    const account = await loginAccount(fields)
    setUser(account)
    setStatus('authenticated')
    return account
  }, [])

  const signUp = useCallback(async (fields) => {
    await registerAccount(fields)
    // Registration creates the account; login establishes its session.
    const account = await loginAccount({ username: fields.username, password: fields.password })
    setUser(account)
    setStatus('authenticated')
    return account
  }, [])

  const signOut = useCallback(async () => {
    await logoutAccount()
    setUser(null)
    setStatus('unauthenticated')
  }, [])

  const value = useMemo(() => ({
    user, status, loadError, signIn, signUp, signOut, refreshAccount,
  }), [user, status, loadError, signIn, signUp, signOut, refreshAccount])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider.')
  return context
}

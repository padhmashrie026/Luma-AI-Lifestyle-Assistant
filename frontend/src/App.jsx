import { useEffect, useState } from 'react'
import { useAuth } from './auth/AuthContext.jsx'
import AppLayout from './components/AppLayout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import PlaceholderPage from './pages/PlaceholderPage.jsx'
import BodyShapePage from './pages/BodyShapePage.jsx'
import WardrobePage from './pages/WardrobePage.jsx'
import OutfitRecommendationPage from './pages/OutfitRecommendationPage.jsx'
import DietPlannerPage from './pages/DietPlannerPage.jsx'
import ExpensesPage from './pages/ExpensesPage.jsx'
import DailyPlanPage from './pages/DailyPlanPage.jsx'
import { ProfilePage, SettingsPage } from './pages/ProfileSettingsPage.jsx'
import { LoginPage, RegisterPage } from './pages/AuthPages.jsx'
import Button from './components/Button.jsx'
import './App.css'

const pages = {
  '/dashboard': { title: 'Dashboard', component: <Dashboard /> },
  '/body-shape': { title: 'Body Shape Calculator', component: <BodyShapePage /> },
  '/wardrobe': { title: 'Wardrobe', component: <WardrobePage /> },
  '/outfits': { title: 'Outfit Recommendation', component: <OutfitRecommendationPage /> },
  '/diet': { title: 'Diet Planner', component: <DietPlannerPage /> },
  '/expenses': { title: 'Expenses', component: <ExpensesPage /> },
  '/daily-plan': { title: 'Daily Plan', component: <DailyPlanPage /> },
  '/insights': { title: 'Insights', component: <PlaceholderPage title="Insights" /> },
  '/profile': { title: 'Profile', component: <ProfilePage /> },
  '/settings': { title: 'Settings', component: <SettingsPage /> },
}

function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname)
  const [returnPath, setReturnPath] = useState(null)
  const [logoutError, setLogoutError] = useState('')
  const { user, status, loadError, signOut, refreshAccount } = useAuth()

  useEffect(() => {
    const updatePath = () => setCurrentPath(window.location.pathname)
    window.addEventListener('popstate', updatePath)
    return () => window.removeEventListener('popstate', updatePath)
  }, [])

  const navigate = (path, replace = false) => {
    if (path === currentPath) return
    if (replace) window.history.replaceState({}, '', path)
    else window.history.pushState({}, '', path)
    setCurrentPath(path)
    window.scrollTo(0, 0)
  }

  const isAuthPage = currentPath === '/login' || currentPath === '/register'

  useEffect(() => {
    if (status === 'loading' || status === 'error') return
    if (status === 'authenticated' && isAuthPage) {
      navigate('/dashboard', true)
    } else if (status === 'unauthenticated' && !isAuthPage) {
      setReturnPath(currentPath)
      navigate('/login', true)
    }
  }, [status, user, currentPath, isAuthPage])

  const handleLogout = async () => {
    setLogoutError('')
    try {
      await signOut()
      navigate('/login', true)
    } catch (error) {
      setLogoutError(error.message)
    }
  }

  if (status === 'loading') return <main className="auth-status"><p>Checking your account…</p></main>
  if (status === 'error') return <main className="auth-status"><section className="auth-status-card">
    <h1>We couldn’t check your account</h1><p>{loadError}</p>
    <Button className="primary-button" onClick={refreshAccount}>Try again</Button>
  </section></main>

  if (status === 'authenticated' && (currentPath === '/login' || currentPath === '/register')) {
    return <main className="auth-status"><p>Opening your workspace…</p></main>
  }

  if (status === 'unauthenticated') {
    if (currentPath !== '/login' && currentPath !== '/register') return null
    const AuthRoute = currentPath === '/register' ? RegisterPage : LoginPage
    return <AuthRoute onNavigate={navigate} onAuthenticated={() => {
      const destination = returnPath || '/dashboard'
      setReturnPath(null)
      navigate(destination, true)
    }} />
  }

  const page = pages[currentPath] ?? pages['/dashboard']
  const content = page === pages['/dashboard'] ? <Dashboard onNavigate={navigate} /> : page.component
  return <AppLayout title={page.title} currentPath={currentPath} onNavigate={navigate} user={user} onLogout={handleLogout}>
    {logoutError && <p className="auth-error" role="alert">{logoutError}</p>}
    {content}
  </AppLayout>
}

export default App

import { useEffect, useState } from 'react'
import AppLayout from './components/AppLayout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import PlaceholderPage from './pages/PlaceholderPage.jsx'
import './App.css'

const pages = {
  '/dashboard': { title: 'Dashboard', component: <Dashboard /> },
  '/wardrobe': { title: 'Wardrobe', component: <PlaceholderPage title="Wardrobe" /> },
  '/diet': { title: 'Diet Planner', component: <PlaceholderPage title="Diet Planner" /> },
  '/expenses': { title: 'Expenses', component: <PlaceholderPage title="Expenses" /> },
  '/daily-plan': { title: 'Daily Plan', component: <PlaceholderPage title="Daily Plan" /> },
  '/insights': { title: 'Insights', component: <PlaceholderPage title="Insights" /> },
  '/profile': { title: 'Profile', component: <PlaceholderPage title="Profile" /> },
  '/settings': { title: 'Settings', component: <PlaceholderPage title="Settings" /> },
}

function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname)

  useEffect(() => {
    const updatePath = () => setCurrentPath(window.location.pathname)
    window.addEventListener('popstate', updatePath)
    return () => window.removeEventListener('popstate', updatePath)
  }, [])

  const navigate = (path) => {
    if (path === currentPath) return
    window.history.pushState({}, '', path)
    setCurrentPath(path)
    window.scrollTo(0, 0)
  }

  const page = pages[currentPath] ?? pages['/dashboard']
  return <AppLayout title={page.title} currentPath={currentPath} onNavigate={navigate}>{page.component}</AppLayout>
}

export default App

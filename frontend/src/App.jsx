import { useEffect, useState } from 'react'
import AppLayout from './components/AppLayout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import PlaceholderPage from './pages/PlaceholderPage.jsx'
import BodyShapePage from './pages/BodyShapePage.jsx'
import WardrobePage from './pages/WardrobePage.jsx'
import OutfitRecommendationPage from './pages/OutfitRecommendationPage.jsx'
import DietPlannerPage from './pages/DietPlannerPage.jsx'
import ExpensesPage from './pages/ExpensesPage.jsx'
import './App.css'

const pages = {
  '/dashboard': { title: 'Dashboard', component: <Dashboard /> },
  '/body-shape': { title: 'Body Shape Calculator', component: <BodyShapePage /> },
  '/wardrobe': { title: 'Wardrobe', component: <WardrobePage /> },
  '/outfits': { title: 'Outfit Recommendation', component: <OutfitRecommendationPage /> },
  '/diet': { title: 'Diet Planner', component: <DietPlannerPage /> },
  '/expenses': { title: 'Expenses', component: <ExpensesPage /> },
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

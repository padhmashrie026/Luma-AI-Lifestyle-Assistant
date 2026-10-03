import { useEffect, useState } from 'react'
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
  const content = page === pages['/dashboard'] ? <Dashboard onNavigate={navigate} /> : page.component
  return <AppLayout title={page.title} currentPath={currentPath} onNavigate={navigate}>{content}</AppLayout>
}

export default App

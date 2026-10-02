import { useEffect, useState } from 'react'
import Header from './Header.jsx'
import Sidebar from './Sidebar.jsx'

function AppLayout({ title, currentPath, onNavigate, children }) {
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    if (!menuOpen) return undefined
    const closeOnEscape = (event) => {
      if (event.key === 'Escape') setMenuOpen(false)
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [menuOpen])

  return <div className="app-shell"><Sidebar currentPath={currentPath} onNavigate={onNavigate} isOpen={menuOpen} onClose={() => setMenuOpen(false)} /><div className="app-main"><Header title={title} onMenuToggle={() => setMenuOpen((open) => !open)} /><main className="page-content">{children}</main></div></div>
}

export default AppLayout

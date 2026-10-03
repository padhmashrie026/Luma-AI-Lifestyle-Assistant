import Icon from './Icon.jsx'

const primaryLinks = [
  { label: 'Dashboard', path: '/dashboard', icon: 'grid' },
  { label: 'Body Shape', path: '/body-shape', icon: 'user' },
  { label: 'Wardrobe', path: '/wardrobe', icon: 'clothes' },
  { label: 'Outfit ideas', path: '/outfits', icon: 'sparkle' },
  { label: 'Diet Planner', path: '/diet', icon: 'leaf' },
  { label: 'Expenses', path: '/expenses', icon: 'wallet' },
  { label: 'Daily Plan', path: '/daily-plan', icon: 'calendar' },
  { label: 'Insights', path: '/insights', icon: 'chart' },
]
const accountLinks = [
  { label: 'Profile', path: '/profile', icon: 'user' },
  { label: 'Settings', path: '/settings', icon: 'settings' },
]

function Sidebar({ currentPath, onNavigate, isOpen, onClose }) {
  const renderLink = ({ label, path, icon }) => <a key={path} href={path} className="nav-link" aria-current={currentPath === path ? 'page' : undefined} onClick={(event) => {
    event.preventDefault()
    onNavigate(path)
    onClose()
  }}><Icon name={icon} size={17} />{label}</a>

  return <>
    <button className={`sidebar-backdrop ${isOpen ? 'is-visible' : ''}`} type="button" aria-label="Close navigation menu" onClick={onClose} />
    <aside className={`sidebar ${isOpen ? 'is-open' : ''}`} aria-label="Main navigation">
      <a className="brand" href="/dashboard" onClick={(event) => { event.preventDefault(); onNavigate('/dashboard'); onClose() }}><span className="brand-mark"><Icon name="sparkle" size={19} strokeWidth={1.8} /></span><span className="brand-name">Luma<span className="brand-caption">Lifestyle, in balance</span></span></a>
      <nav aria-label="Primary"><p className="nav-label">Workspace</p><div className="nav-list">{primaryLinks.map(renderLink)}</div></nav>
      <div className="sidebar-bottom"><p className="nav-label">Account</p><div className="nav-list">{accountLinks.map(renderLink)}</div><p className="sidebar-note">A thoughtful space for your everyday routines.</p></div>
    </aside>
  </>
}

export default Sidebar

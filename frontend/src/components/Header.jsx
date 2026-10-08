import Icon from './Icon.jsx'
import Button from './Button.jsx'

function Header({ title, onMenuToggle, onNavigate, user, onLogout }) {
  return <header className="topbar">
    <div className="topbar-left"><Button className="mobile-menu icon-button" aria-label="Open navigation menu" onClick={onMenuToggle}><Icon name="menu" size={19} /></Button><h1 className="topbar-title">{title}</h1></div>
    <div className="topbar-actions">
      <Button className="profile-trigger" aria-label="Open profile" onClick={() => onNavigate('/profile')}><span className="avatar" aria-hidden="true"><Icon name="user" size={16} /></span><span className="profile-name-wrap"><span className="profile-name">{user?.profile?.display_name || user?.username || 'Profile'}</span><span className="profile-role">Profile and settings</span></span></Button>
      <Button className="secondary-button auth-logout" onClick={onLogout}>Log out</Button>
    </div>
  </header>
}

export default Header

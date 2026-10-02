import Icon from './Icon.jsx'
import Button from './Button.jsx'

function Header({ title, onMenuToggle }) {
  return <header className="topbar">
    <div className="topbar-left"><Button className="mobile-menu icon-button" aria-label="Open navigation menu" onClick={onMenuToggle}><Icon name="menu" size={19} /></Button><h1 className="topbar-title">{title}</h1></div>
    <div className="topbar-actions">
      <label className="search-box"><Icon name="search" size={16} /><span className="visually-hidden">Search</span><input type="search" placeholder="Search" aria-label="Search" /><kbd className="search-shortcut">⌘ K</kbd></label>
      <Button className="icon-button" aria-label="Notifications"><Icon name="bell" size={17} /><span className="notification-dot" /></Button>
      <Button className="profile-trigger" aria-label="Open profile"><span className="avatar" aria-hidden="true">JD</span><span className="profile-name-wrap"><span className="profile-name">Jamie Doe</span><span className="profile-role">Personal space</span></span></Button>
    </div>
  </header>
}

export default Header

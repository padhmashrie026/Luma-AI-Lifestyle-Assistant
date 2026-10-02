function Button({ children, className = '', type = 'button', ...props }) {
  return <button className={`button ${className}`} type={type} {...props}>{children}</button>
}

export default Button

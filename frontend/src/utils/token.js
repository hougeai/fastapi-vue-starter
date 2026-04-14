export function getToken() {
  return localStorage.getItem('access_token')
}

export function setToken(token) {
  localStorage.setItem('access_token', token)
}

export function removeToken() {
  window.localStorage.removeItem('access_token')
}

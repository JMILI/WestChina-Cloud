import Cookies from '~../../js-cookie'

const TokenKey = 'Admin-Token'

const ExpiresInKey = 'Admin-Expires-In'

export function getToken() {
  return Cookies.get(TokenKey)
}

const cookieOpts = { path: '/' }

export function setToken(token) {
  return Cookies.set(TokenKey, token, cookieOpts)
}

export function removeToken() {
  return Cookies.remove(TokenKey, cookieOpts)
}

export function getExpiresIn() {
  return Cookies.get(ExpiresInKey) || -1
}

export function setExpiresIn(time) {
  return Cookies.set(ExpiresInKey, time, cookieOpts)
}

export function removeExpiresIn() {
  return Cookies.remove(ExpiresInKey, cookieOpts)
}

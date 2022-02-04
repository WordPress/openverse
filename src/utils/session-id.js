import { v4 as uuidv4 } from 'uuid'
import Cookie from 'js-cookie'

const COOKIE_EXPIRY_DAYS = 7
const COOKIE_PREFIX = 'openverse_'

const generateSessionId = () => uuidv4()

/**
 * Store a session in in a cookie for usage analytics. By default
 * it expires when a user closes the browser. If hasExpirationDate is set to
 * true, the cookie will last for 7 days, which is determined by
 * `COOKIE_EXPIRY_DAYS`.
 * @param {string} cookieName - The name of the cookie
 * @param {string} sessionId - randomly generated uuid
 * @param {boolean} hasExpirationDate - Whether the cookie should expire when user closes the browser
 */
const saveSessionIdInCookie = (cookieName, sessionId, hasExpirationDate) => {
  if (hasExpirationDate) {
    Cookie.set(`${COOKIE_PREFIX}${cookieName}`, sessionId, {
      expires: COOKIE_EXPIRY_DAYS,
      secure: true,
      sameSite: 'None',
    })
  } else {
    Cookie.set(cookieName, sessionId)
  }
}

/**
 * Retrieves saved session Id or creates a new one.
 * @param {string} cookieName - The name of the cookie
 * @param {boolean} [hasExpirationDate=false] Whether the cookie should expire when user closes the browser
 */
const SessionId = (cookieName, hasExpirationDate = false) => {
  let sessionId = Cookie.get(`${COOKIE_PREFIX}${cookieName}`)

  if (!sessionId) {
    sessionId = generateSessionId()
    saveSessionIdInCookie(cookieName, sessionId, hasExpirationDate)
  }

  return sessionId
}

export default SessionId

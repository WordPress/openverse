import { v4 as uuid } from 'uuid'
import Cookie from 'js-cookie'

const COOKIE_NAME = 'SESSION_ID'
const COOKIE_EXPIRY_DAYS = 7

const generateSessionId = () => uuid()

/**
 * Store a session in in a cookie, to determine which version of an a/b test a user recieves.
 * The cookie (and therefore the a/b test version), will last for a number of days
 * determined by `COOKIE_EXPIRY_DAYS`.
 */
const saveSessionIdInCookie = (sessionId) =>
  Cookie.set(COOKIE_NAME, sessionId, { expires: COOKIE_EXPIRY_DAYS })

const SessionId = () => {
  let sessionId = Cookie.get(COOKIE_NAME)

  if (!sessionId) {
    sessionId = generateSessionId()
    saveSessionIdInCookie(sessionId)
  }

  return sessionId
}

export default SessionId

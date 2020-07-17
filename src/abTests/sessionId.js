import uuid from 'uuid/v4'
import Cookie from 'js-cookie'

const COOKIE_NAME = 'SESSION_ID'
const COOKIE_EXPIRY_DAYS = 7

const generateSessionId = () => uuid()

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

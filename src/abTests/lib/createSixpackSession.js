import sixpack from 'sixpack-client'
import SessionId from './sessionId'

const createSixpackSession = (existingSessionId) => {
  const baseUrl = process.env.apiUrl.replace('/v1/', '')
  const SIXPACK_URL = `${baseUrl}/sixpack`

  const sessionId = existingSessionId || SessionId()
  const session = new sixpack.Session({
    client_id: sessionId,
    base_url: SIXPACK_URL,
    timeout: 1000,
  })

  return session
}

export default createSixpackSession

import SessionId from '~/utils/sessionId'

const state = {
  abSessionId: SessionId('abSessionId', true),
  usageSessionId: SessionId('usageSessionId'),
}

export default {
  state,
}

import SessionId from '~/utils/session-id'

const state = {
  abSessionId: SessionId('abSessionId', true),
  usageSessionId: SessionId('usageSessionId'),
}

export default {
  state,
}

import SessionId from '~/utils/session-id'

export const state = () => ({
  abSessionId: SessionId('abSessionId', true),
  usageSessionId: SessionId('usageSessionId'),
})

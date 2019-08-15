import sixpack from 'sixpack-client';
import SessionId from './sessionId';

const SIXPACK_URL = `${process.env.API_URL}/sixpack`;

const createSixpackSession = (existingSessionId) => {
  const sessionId = existingSessionId || SessionId();
  const session = new sixpack.Session({
    client_id: sessionId,
    base_url: SIXPACK_URL,
    timeout: 1000,
  });

  return session;
};

export default createSixpackSession;

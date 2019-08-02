import sixpack from 'sixpack-client';
import SessionId from './sessionId';

const SIXPACK_URL = process.env.SIXPACK_URL;

const createSixpackSession = () => {
  const sessionId = SessionId();
  const session = new sixpack.Session({
    client_id: sessionId,
    base_url: SIXPACK_URL,
  });

  return session;
};

export default createSixpackSession;

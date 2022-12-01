import { isProd } from '~/utils/node-env'

import type { CookieSerializeOptions } from 'cookie'

export const cookieOptions: CookieSerializeOptions = {
  path: '/',
  sameSite: 'strict',
  maxAge: 60 * 60 * 24 * 60, // 60 days
  secure: isProd,
}

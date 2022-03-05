import useragent from 'express-useragent'

export default function (context, inject) {
  let userAgent

  if (typeof context.req !== 'undefined') {
    userAgent = context.req.headers['user-agent']
  } else if (typeof navigator !== 'undefined') {
    userAgent = navigator.userAgent
  }
  let ua
  if (userAgent !== null || userAgent !== undefined) {
    ua = useragent.parse(userAgent)
  } else {
    ua = null
  }

  context.$ua = ua
  inject('ua', ua)
}

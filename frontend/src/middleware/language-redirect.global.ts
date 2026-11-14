import {
  defineNuxtRouteMiddleware,
  navigateTo,
  useCookie,
  useNuxtApp,
} from '#app'

export default defineNuxtRouteMiddleware((to) => {
  const { $i18n } = useNuxtApp()
  const availableLocales = $i18n.availableLocales as string[]

  const segments = to.path.split('/').filter(Boolean)
  if (!segments.length) return

  const locale = segments[0]

  // Only act on two-letter language codes
  if (locale.length !== 2) return

  // Supported locale → do nothing
  if (availableLocales.includes(locale)) return

  // Store unsupported locale to show banner
  const bannerCookie = useCookie<string>('unsupported_language_code')
  bannerCookie.value = locale

  // Redirect to English path (strip the locale)
  const newPath = '/' + segments.slice(1).join('/')
  return navigateTo(newPath || '/', { redirectCode: 302 })
})

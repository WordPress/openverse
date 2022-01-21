import { useContext } from '@nuxtjs/composition-api'

export const useBrowserDetection = () => {
  const { app } = useContext()
  return app.$ua
}

export const useBrowserIsBlink = () => {
  const browser = useBrowserDetection()
  return browser.isChrome || browser.isEdge || browser.isOpera
}

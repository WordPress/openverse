import { useContext } from "@nuxtjs/composition-api"

export const useBrowserDetection = () => {
  const { app } = useContext()
  return app.$ua
}

export const useBrowserIsMobile = (): boolean => {
  const browser = useBrowserDetection()
  if (browser === null) {
    return false
  } else {
    return browser.isMobile
  }
}

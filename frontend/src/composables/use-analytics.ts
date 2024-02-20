import { useContext } from "@nuxtjs/composition-api"

export const useAnalytics = () => {
  const { $sendCustomEvent } = useContext()

  return { sendCustomEvent: $sendCustomEvent }
}

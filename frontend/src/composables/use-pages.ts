import { computed } from "vue"
import { useContext, useRoute } from "@nuxtjs/composition-api"

export default function usePages() {
  const { app } = useContext()

  const pages = [
    {
      id: "about",
      name: "navigation.about",
      link: app.localePath("/about"),
    },
    {
      id: "licenses",
      name: "navigation.licenses",
      link: "https://creativecommons.org/about/cclicenses/",
    },
    {
      id: "sources",
      name: "navigation.sources",
      link: app.localePath("/sources"),
    },
    {
      id: "search-help",
      name: "navigation.searchHelp",
      link: app.localePath("/search-help"),
    },
    {
      id: "get-involved",
      name: "navigation.getInvolved",
      link: "https://make.wordpress.org/openverse/handbook/",
    },
    {
      id: "api",
      name: "navigation.api",
      link: "https://api.openverse.org/v1/",
    },
    {
      id: "terms",
      name: "navigation.terms",
      link: "https://docs.openverse.org/terms_of_service.html",
    },
    {
      id: "privacy",
      name: "navigation.privacy",
      link: app.localePath("/privacy"),
    },
    {
      id: "feedback",
      name: "navigation.feedback",
      link: app.localePath("/feedback"),
    },
  ]

  const route = useRoute()
  /**
   * The route name of the current page is localized, so it looks like `index__en`.
   * We need to remove the locale suffix to match the page id.
   */
  const currentPageId = computed<string>(
    () => route.value?.name?.split("__")[0] ?? ""
  )

  return { all: pages, current: currentPageId }
}

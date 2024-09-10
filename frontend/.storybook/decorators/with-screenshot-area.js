import { h } from "vue"

export const WithScreenshotArea = (story) => {
  return {
    components: { story },
    setup() {
      return () =>
        h(
          "div",
          {
            class: "screenshot-area",
            style: "display: inline-block; padding: 2rem;",
          },
          [h(story())]
        )
    },
  }
}

import { Suspense } from "vue"

export const WithSuspense = (story) => {
  return {
    template: `
      <Suspense>
        <story />
      </Suspense>`,
    components: { story, Suspense },
  }
}

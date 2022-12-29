export const WithScreenshotArea = (story) => {
  return {
    template: `
      <div
        class="screenshot-area"
        :style="{ display: 'inline-block', padding: '2rem' }"
      >
        <story />
      </div>`,
    components: { story },
  }
}

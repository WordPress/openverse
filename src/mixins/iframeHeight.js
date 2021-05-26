import debounce from 'lodash.debounce'

/**
 * When the app is in embedded mode, it passes the full height
 * of its content to the parent window so that the parent window
 * sets the correct iframe height to avoid double scrollbars
 */
export default {
  data: () => ({ height: 0, observer: null }),
  mounted() {
    if (this.$store.state.isEmbedded) {
      this.notifyOuterWindow(document.documentElement.scrollHeight)
      this.observer = this.createResizeObserver()
      this.observer.observe(document.documentElement)
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.notifyOuterWindow)
    this.observer.disconnect()
  },
  methods: {
    createResizeObserver() {
      return new ResizeObserver(
        debounce((entries) => {
          for (let entry of entries) {
            if (entry.contentBoxSize) {
              if (entry.contentBoxSize[0]) {
                this.height = Math.ceil(entry.contentBoxSize[0].blockSize)
              } else {
                this.height = Math.ceil(entry.contentBoxSize.blockSize)
              }
            }
          }
        }, 1)
      )
    },
    notifyOuterWindow(height) {
      // TODO: set correct targetOrigin of the parent window
      window.parent.postMessage({ height }, '*')
    },
  },
  watch: {
    height: function (newHeight) {
      this.notifyOuterWindow(newHeight)
    },
  },
}

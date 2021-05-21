import debounce from 'lodash.debounce'

export default {
  mounted() {
    if (this.$store.state.isEmbedded) {
      this.notifyOuterWindow()
      window.addEventListener(
        'resize',
        debounce(this.notifyOuterWindow, 100),
        false
      )
    }
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.notifyOuterWindow)
  },
  data: () => ({
    windowHeight: 0,
  }),
  methods: {
    /**
     * When the app is in embedded mode, it passes the full height
     * of its content to the parent window so that the parent window
     * sets the correct iframe height to avoid double scrollbars
     */
    notifyOuterWindow() {
      this.windowHeight = document.documentElement.scrollHeight
      // TODO: set correct targetOrigin of the parent window
      window.parent.postMessage(this.windowHeight, '*')
    },
  },
}

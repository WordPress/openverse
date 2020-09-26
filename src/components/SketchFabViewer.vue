<template>
  <div class="sketchfab-viewer image is-16by9">
    <!-- <div v-if="loading">Loading...</div> -->
    <iframe
      src=""
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
      title="Sketchfab iframe"
      id="sketchfab-iframe"
      ref="sketchfabIframe"
      allow="autoplay; fullscreen; vr"
      :autoplay="true"
      class="has-ratio"
    />
  </div>
</template>

<script>
import loadScript from '@/utils/loadScript'

const sketchfabUrl =
  'https://static.sketchfab.com/api/sketchfab-viewer-1.8.2.js'

export default {
  props: {
    uid: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      client: null,
      clientConfig: {
        success: (api) => {
          api.addEventListener('viewerready', () => {
            this.loading = false
            console.log('LOADED!')
          })
        },
        error: () => {
          console.log('Viewer error')
        },
      },
      loading: true,
    }
  },
  mounted() {
    this.initSketchfab()
      .then(this.initViewer)
      .catch((error) => console.error(error))
  },
  methods: {
    /**
     * Load the SketchFab script and initialize a client
     */
    initSketchfab() {
      return loadScript(sketchfabUrl).then(() => {
        this.client = new window.Sketchfab(this.$refs.sketchfabIframe)
      })
    },
    initViewer() {
      if (!this.client) return
      this.client.init(this.uid, this.clientConfig)
    },
  },
}
</script>

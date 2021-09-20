<template>
  <div class="sketchfab-viewer image is-sketchfab-viewer">
    <!-- <div v-if="loading">Loading...</div> -->
    <iframe
      id="sketchfab-iframe"
      ref="sketchfabIframe"
      src=""
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
      title="Sketchfab iframe"
      allow="autoplay; fullscreen; vr"
      :autoplay="true"
      class="has-ratio"
    />
  </div>
</template>

<script>
import loadScript from '~/utils/load-script'

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
      .catch((error) => {
        console.error(error)
        this.$emit('failure')
      })
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
<style lang="scss" scoped>
.image {
  display: block;
}
.is-sketchfab-viewer {
  padding-top: 56.25%;
}
.has-ratio {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  height: 100%;
  width: 100%;
}
</style>

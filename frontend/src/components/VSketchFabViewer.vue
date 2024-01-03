<template>
  <div class="block aspect-[2/1] max-h-[500px] max-w-[1000px]">
    <iframe
      id="sketchfab-iframe"
      ref="node"
      src=""
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
      :title="label"
      :aria-label="label"
      allow="autoplay; fullscreen; vr"
      :autoplay="true"
      class="h-full w-full"
    />
  </div>
</template>

<script lang="ts">
import { useNuxtApp } from "#imports"

import { defineComponent, ref, onMounted } from "vue"

import { useNuxtI18n } from "~/composables/use-i18n"
import { loadScript } from "~/utils/load-script"

const sketchfabUrl =
  "https://static.sketchfab.com/api/sketchfab-viewer-1.10.1.js"

interface SketchfabConfig {
  error(e: unknown): void
}

declare global {
  interface Window {
    Sketchfab?: new (node: Element) => {
      init(uid: string, config: SketchfabConfig): void
    }
  }
}

export default defineComponent({
  props: {
    uid: {
      type: String,
      required: true,
    },
  },
  emits: ["failure"],
  setup(props, { emit }) {
    const i18n = useNuxtI18n()
    const label = i18n
      .t("sketchfabIframeTitle", { sketchfab: "Sketchfab" })
      .toString()
    const node = ref<Element | undefined>()
    const { $sentry } = useNuxtApp()

    const initSketchfab = async () => {
      await loadScript(sketchfabUrl)
      if (typeof window.Sketchfab === "undefined") {
        $sentry.captureMessage("Unable to find window.Sketchfab after loading")
        return
      }

      if (!node.value) {
        // This is impossible as far as I can tell as the
        // function is only called in `onMounted`
        return
      }

      const sf = new window.Sketchfab(node.value)
      sf.init(props.uid, {
        error: (e: unknown) => {
          $sentry.captureException(e)
          emit("failure")
        },
      })
    }

    onMounted(() => {
      initSketchfab()
    })

    return { node, label }
  },
})
</script>

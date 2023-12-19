<template>
  <!-- eslint-disable vue/use-v-on-exact -->
  <Component
    :is="isComposite ? 'VLink' : 'div'"
    v-bind="containerAttributes"
    class="audio-track group block overflow-hidden rounded-sm ring-pink hover:no-underline"
    :aria-label="ariaLabel"
    :role="isComposite ? 'application' : undefined"
    @keydown.native.shift.tab.exact="$emit('shift-tab', $event)"
    @keydown="handleKeydown"
    @blur="handleBlur"
    @mousedown="handleMousedown"
    @focus="handleFocus"
  >
    <Component
      :is="layoutComponent"
      :audio="audio"
      :size="layoutSize"
      :status="status"
      :current-time="currentTime"
    >
      <template #controller="waveformProps">
        <VWaveform
          ref="waveformRef"
          v-bind="waveformProps"
          :is-parent-seeking="isSeeking"
          :peaks="audio.peaks"
          :audio-id="audio.id"
          :current-time="currentTime"
          :duration="duration"
          :message="message"
          @seeked="handleSeeked"
          @toggle-playback="handleToggle"
          @blur="handleWaveformBlur"
          @focus="handleWaveformFocus"
        />
      </template>

      <template #audio-control="audioControlProps">
        <VAudioControl
          ref="audioControlRef"
          :status="status"
          v-bind="audioControlProps"
          @toggle="handleToggle"
        />
      </template>
    </Component>
  </Component>
</template>

<script lang="ts">
import { useI18n, useNuxtApp, useRoute } from "#imports"

import {
  computed,
  defineComponent,
  onUnmounted,
  PropType,
  ref,
  watch,
} from "vue"

import { useActiveAudio } from "~/composables/use-active-audio"
import { defaultRef } from "~/composables/default-ref"
import { useSeekable } from "~/composables/use-seekable"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"
import {
  useMatchSearchRoutes,
  useMatchSingleResultRoutes,
} from "~/composables/use-match-routes"

import { useActiveMediaStore } from "~/stores/active-media"
import { useMediaStore } from "~/stores/media"

import { AUDIO } from "~/constants/media"
import {
  activeAudioStatus,
  AudioLayout,
  AudioSize,
  AudioStatus,
  layoutMappings,
} from "~/constants/audio"

import type { AudioInteraction, AudioInteractionData } from "~/types/analytics"
import type { AudioDetail } from "~/types/media"

import { defineEvent } from "~/types/emits"

import type { AudioTrackClickEvent } from "~/types/events"

import VAudioControl from "~/components/VAudioTrack/VAudioControl.vue"
import VWaveform from "~/components/VAudioTrack/VWaveform.vue"
import VFullLayout from "~/components/VAudioTrack/layouts/VFullLayout.vue"
import VRowLayout from "~/components/VAudioTrack/layouts/VRowLayout.vue"
import VBoxLayout from "~/components/VAudioTrack/layouts/VBoxLayout.vue"
import VGlobalLayout from "~/components/VAudioTrack/layouts/VGlobalLayout.vue"
import VLink from "~/components/VLink.vue"

/**
 * Displays the waveform and basic information about the track, along with
 * controls to play, pause or seek to a point on the track.
 */
export default defineComponent({
  name: "VAudioTrack",
  components: {
    VAudioControl,
    VWaveform,
    VLink,

    // Layouts
    VFullLayout,
    VRowLayout,
    VBoxLayout,
    VGlobalLayout,
  },
  props: {
    /**
     * the information about the track, typically from a track's detail endpoint
     */
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
    /**
     * the arrangement of the contents on the canvas; This determines the
     * overall L&F of the audio component.
     */
    layout: {
      type: String as PropType<AudioLayout>,
      required: true,
    },
    /**
     * the size of the component; Both 'box' and 'row' layouts offer multiple
     * sizes to choose from.
     */
    size: {
      type: String as PropType<AudioSize>,
    },
    /**
     * the search term that was used to find this track; This is used
     * in the link to the track's detail page.
     */
    searchTerm: {
      type: String,
    },
  },
  emits: {
    "shift-tab": defineEvent<[KeyboardEvent]>(),
    interacted: defineEvent<[Omit<AudioInteractionData, "component">]>(),
    mousedown: defineEvent<[AudioTrackClickEvent]>(),
    focus: defineEvent<[FocusEvent]>(),
  },
  setup(props, { emit }) {
    const i18n = useI18n()
    const { $sentry } = useNuxtApp()

    const activeMediaStore = useActiveMediaStore()
    const route = useRoute()

    const activeAudio = useActiveAudio()

    const status = ref<AudioStatus>("paused")
    const currentTime = ref(0)

    const initLocalAudio = () => {
      // Preserve existing local audio if we plucked it from the global active audio
      if (!localAudio) {
        localAudio = new Audio(props.audio.url)
      }

      Object.entries(eventMap).forEach(([name, fn]) =>
        /**
         * This cast is safe, it just filters `undefined` that is still present on the
         * `localAudio`'s type despite the check above to create it if it doesn't exist.
         */
        (localAudio as HTMLAudioElement).addEventListener(name, fn)
      )

      /**
       * Similar to the behavior in the global audio track,
       * if the local audio was set to an already existing and
       * matching active global track, then we'll need to initialize
       * the status based on the `paused` and `ended` booleans
       * on the audio object.
       *
       * For newly initialized audio objects, this is harmless,
       * but it is essential for making sure page transitions
       * preserve the existing, already manipulated audio
       * object's state.
       *
       * Unlike the global audio track, however, this will not
       * always result in a status of `playing` in practice,
       * as the state of the active global track could be any
       * of the three statuses we track when the page transition
       * happens. For example, the audio track on the result page
       * could have been played through (and thus `ended`), or it
       * could be paused mid-way (and thus `paused`), or neither
       * and thus would be playing.
       */
      if (localAudio.paused) {
        if (localAudio.ended) {
          setPlayed()
        } else {
          setPaused()
        }
      } else {
        setPlaying()
      }

      currentTime.value = localAudio.currentTime
    }

    /**
     * We can only create the local audio object on the client,
     * so the initialization of this variable is hidden inside
     * the `initLocalAudio` function which is only called when
     * playback is first requested or when the track is first seeked.
     *
     * However, when navigating to an audio result page, if
     * the globally active audio already matches the result
     * that was clicked on, hijack that object instead and
     * treat it as the local audio for this instance.
     */
    let localAudio =
      activeAudio.obj.value?.src === props.audio.url
        ? activeAudio.obj.value
        : undefined

    const updateTimeLoop = () => {
      if (localAudio) {
        if (activeAudioStatus.includes(status.value)) {
          currentTime.value = localAudio.currentTime
          window.requestAnimationFrame(updateTimeLoop)
        } else {
          currentTime.value = localAudio.currentTime
        }
      }
    }

    const mediaStore = useMediaStore()
    const setLoaded = () => {
      mediaStore.setMediaProperties("audio", props.audio.id, {
        hasLoaded: true,
      })
      status.value = "playing"
    }
    const setWaiting = () => {
      status.value = "loading"
    }
    const setPlaying = () => {
      if (props.audio.hasLoaded) {
        status.value = "playing"
      } else {
        status.value = "loading"
      }
      activeAudio.obj.value = localAudio
      activeMediaStore.setActiveMediaItem({
        type: "audio",
        id: props.audio.id,
      })
      activeMediaStore.setMessage({ message: null })
      updateTimeLoop()
    }
    const setPaused = () => {
      status.value = "paused"
      activeMediaStore.pauseActiveMediaItem()
    }
    const setPlayed = () => (status.value = "played")
    const setTimeWhenPaused = () => {
      if (status.value !== "playing" && localAudio) {
        currentTime.value = localAudio.currentTime
        if (status.value === "played") {
          // Set to pause to remove replay icon
          status.value = "paused"
        }
      }
    }
    const duration = defaultRef(() => {
      if (localAudio) {
        return localAudio.duration
      }
      if (typeof props.audio?.duration === "number") {
        return props.audio.duration / 1e3
      }
      return 0
    })
    const setDuration = () => {
      if (localAudio) {
        duration.value = localAudio.duration
      }
    }

    const eventMap = {
      play: setPlaying,
      pause: setPaused,
      ended: setPlayed,
      timeupdate: setTimeWhenPaused,
      durationchange: setDuration,
      waiting: setWaiting,
      playing: setLoaded,
    } as const

    /**
     * If we're transforming the globally active audio
     * into our local audio, then we need to initialize
     * the local state syncing from the audio object
     * to our local refs.
     *
     * This lives here instead of closer to where `localAudio`
     * is defined because `initLocalAudio` and several of
     * the functions it depends on also all depend on the
     * `localAudio` variable. This is the earliest in
     * `setup` that this can be called.
     */
    if (localAudio) {
      initLocalAudio()
    }

    onUnmounted(() => {
      if (!localAudio) {
        return
      }

      Object.entries(eventMap).forEach(([name, fn]) =>
        localAudio?.removeEventListener(name, fn)
      )

      const { matches: isSearchRoute } = useMatchSearchRoutes()
      const { matches: isSingleResultRoute } = useMatchSingleResultRoutes()

      if (
        (isSingleResultRoute.value && route.params.id === props.audio.id) ||
        (isSearchRoute.value && mediaStore.getItemById(AUDIO, props.audio.id))
      ) {
        /**
         * If switching to any route other than the single result
         * route for this track, pause it. Otherwise, let it keep
         * playing to introduce a "seamless" feeling between the
         * search results page and the single result page.
         *
         * This handles going from the search page to the single
         * result page for a different track than is currently playing.
         * It also handles the same interaction for related audio.
         * Also for related audio, it will handle pausing any related
         * audio when navigating back from the single result page
         * to the search results page.
         *
         * Also, if the currently playing audio is present in the
         * existing list of search results, then also let it keep
         * playing.
         */
        return
      }

      localAudio.pause()
    })

    const play = () => {
      // Delay initializing the local audio element until playback is requested
      if (!localAudio) {
        initLocalAudio()
      }

      const playPromise = localAudio?.play()
      // Check if the audio can be played successfully
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          let message: string
          switch (err.name) {
            case "NotAllowedError": {
              message = "err_unallowed"
              break
            }
            case "NotSupportedError": {
              message = "err_unsupported"
              break
            }
            case "AbortError": {
              message = "err_aborted"
              break
            }
            default: {
              message = "err_unknown"
              if ($sentry) {
                $sentry.captureException(err)
              } else {
                console.log("Sentry not available to capture exception", err)
              }
            }
          }
          activeMediaStore.setMessage({ message })
          localAudio?.pause()
        })
      }
    }
    const pause = () => localAudio?.pause()

    watch(
      activeAudio.obj,
      (audio) => {
        if (
          audio !== localAudio &&
          (status.value === "playing" || status.value === "loading")
        ) {
          localAudio?.pause()
        }
      },
      { immediate: true }
    )

    /* Timekeeping */

    const message = computed(() =>
      activeMediaStore.message
        ? i18n.t(`audioTrack.messages.${activeMediaStore.message}`)
        : ""
    )

    /* Interface with VAudioControl */

    /**
     * This function can safely ignore the `loading` status because
     * that status is never toggled _to_.
     */
    const handleToggle = (state?: Exclude<AudioStatus, "loading">) => {
      let event: AudioInteraction | undefined = undefined
      if (!state) {
        switch (status.value) {
          case "playing": {
            state = "paused"
            break
          }
          case "paused":
          case "played": {
            state = "playing"
            break
          }
        }
      }

      switch (state) {
        case "playing": {
          play()
          event = "play"
          break
        }
        case "paused": {
          pause()
          event = "pause"
          break
        }
      }
      emitInteracted(event)
    }

    const emitInteracted = (event?: AudioInteraction) => {
      if (!event) {
        return
      }
      snackbar.dismiss()
      emit("interacted", {
        event,
        id: props.audio.id,
        provider: props.audio.provider,
      })
    }

    /* Interface with VWaveform */

    const handleSeeked = (frac: number) => {
      if (!localAudio) {
        initLocalAudio()
      }
      /**
       * Calling initLocalAudio will guarantee localAudio
       * to be an HTMLAudioElement, but we can't prove that
       * to TypeScript without jumping through some tricky
       * hoops (using `assert`) or adding unnecessary
       * runtime checks.
       */
      if (localAudio) {
        localAudio.currentTime = frac * duration.value
      }
      emitInteracted("seek")
    }

    /* Layout */
    const layoutComponent = computed(() => layoutMappings[props.layout])

    /**
     * Sets default size if not provided.
     */
    const layoutSize = computed(() => {
      if (props.layout === "box" && !props.size) {
        return undefined
      }
      return props.size ?? "m"
    })

    /**
     * A ref used on the play/pause button,
     * so we can capture clicks and skip
     * sending an event to the boxed layout.
     */
    const audioControlRef = ref<{ $el: HTMLElement } | null>(null)

    /**
     * A ref used on the waveform, so we can capture mousedown on the
     * audio track outside it as it will open a detail page.
     */
    const waveformRef = ref<{ $el: HTMLElement } | null>(null)

    const handleMousedown = (event: MouseEvent) => {
      const inWaveform =
        waveformRef.value?.$el.contains(event.target as Node) ?? false
      snackbar.handleMouseDown()
      emit("mousedown", { event, inWaveform })
    }

    /**
     * These layout-conditional props and listeners allow us
     * to set properties on the parent element depending on
     * the layout in use.
     */
    const isComposite = computed(() => ["box", "row"].includes(props.layout))
    const layoutBasedProps = computed(() =>
      isComposite.value
        ? {
            href: `/audio/${props.audio.id}/${
              props.searchTerm ? "?q=" + props.searchTerm : ""
            }`,
            class: [
              "cursor-pointer",
              {
                "focus-bold-filled": props.layout === "box",
                "focus-slim-tx": props.layout === "row",
              },
            ],
          }
        : {}
    )
    const ariaLabel = computed(() =>
      isComposite.value
        ? i18n.t("audioTrack.ariaLabelInteractiveSeekable", {
            title: props.audio.title,
          })
        : i18n.t("audioTrack.ariaLabel", { title: props.audio.title })
    )

    const togglePlayback = () => {
      status.value = activeAudioStatus.includes(status.value)
        ? "paused"
        : "playing"
      handleToggle(status.value)
    }

    const { isSeeking, ...seekable } = useSeekable({
      duration,
      currentTime,
      isReady: ref(true),
      isSeekable: computed(() => props.layout !== "box"),
      onSeek: handleSeeked,
      onTogglePlayback: togglePlayback,
    })
    const handleKeydown = (event: KeyboardEvent) => {
      seekable.listeners.keydown(event)
    }

    const containerAttributes = computed(() => ({
      // ARIA slider attributes are only added when interactive
      ...(isComposite.value ? seekable.attributes.value : {}),
      ...layoutBasedProps.value,
    }))

    const snackbar = useAudioSnackbar()

    const handleFocus = (event: FocusEvent) => {
      snackbar.show()
      emit("focus", event)
    }

    const handleBlur = () => {
      snackbar.hide()
      seekable.listeners.blur()
    }

    const handleWaveformFocus = (event: FocusEvent) => {
      if (!isComposite.value) {
        handleFocus(event)
      }
    }
    const handleWaveformBlur = () => {
      if (!isComposite.value) {
        handleBlur()
      }
    }

    return {
      status,
      message,
      ariaLabel,
      handleToggle,
      handleSeeked,
      handleKeydown,
      handleBlur,
      handleMousedown,
      handleFocus,
      handleWaveformBlur,
      handleWaveformFocus,

      isSeeking,

      currentTime,
      duration,

      layoutComponent,
      layoutSize,

      isComposite,
      containerAttributes,

      audioControlRef,
      waveformRef,
    }
  },
})
</script>

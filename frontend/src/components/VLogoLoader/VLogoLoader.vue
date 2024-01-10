<template>
  <svg
    viewBox="0 0 34 32"
    xmlns="http://www.w3.org/2000/svg"
    :class="{
      loading: status === 'loading' && !prefersReducedMotion,
      'h-10 w-10': autoResize,
      'h-12 w-12': !autoResize,
    }"
    aria-hidden="true"
    :data-prefers-reduced-motion="prefersReducedMotion"
    data-testid="logo-loader"
    class="inline-flex items-center justify-center rounded p-3 md:h-12 md:w-12"
    fill="currentColor"
  >
    <path
      data-logo-part-1
      d="M0 6.962c0 3.831 3.09 6.962 6.916 6.962V0C3.09 0 0 3.111 0 6.962Z"
    />
    <path
      data-logo-part-2
      d="M10.084 6.962c0 3.831 3.091 6.962 6.916 6.962V0c-3.806 0-6.916 3.111-6.916 6.962Z"
    />
    <path
      data-logo-part-3
      d="M27.084 13.924c3.82 0 6.916-3.117 6.916-6.962C34 3.117 30.904 0 27.084 0c-3.82 0-6.916 3.117-6.916 6.962 0 3.845 3.097 6.962 6.916 6.962Z"
    />
    <path
      data-logo-part-4
      d="M0 24.153c0 3.85 3.09 6.962 6.916 6.962V17.21C3.09 17.21 0 20.322 0 24.153Z"
    />
    <path
      data-logo-part-5
      d="M10.084 24.095c0 3.83 3.091 6.962 6.916 6.962V17.152c-3.806 0-6.916 3.112-6.916 6.943Z"
    />
    <path
      data-logo-part-6
      d="M27.084 31.057c3.82 0 6.916-3.117 6.916-6.962 0-3.845-3.096-6.962-6.916-6.962-3.82 0-6.916 3.117-6.916 6.962 0 3.845 3.097 6.962 6.916 6.962Z"
    />
  </svg>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import { useReducedMotion } from "~/composables/use-reduced-motion"

export default defineComponent({
  name: "VLogoLoader",
  props: {
    status: {
      type: String as PropType<"loading" | "idle">,
      default: "idle",
    },
    autoResize: {
      type: Boolean,
      default: true,
    },
  },
  setup() {
    const prefersReducedMotion = useReducedMotion()

    return { prefersReducedMotion }
  },
})
</script>

<style scoped>
/**
  Openverse Logo Loader

  ┌───┐ ┌───┐ ┌──────┐
  │ 1 │ │ 2 │ │   3  │
  └───┘ └───┘ └──────┘
  ┌───┐ ┌───┐ ┌──────┐
  │ 4 │ │ 5 │ │   6  │
  └───┘ └───┘ └──────┘

  The logo, in goofy ascii!

  The loader keyframe animation steps (the defined percentage blocks within each animation)
  are tightly coupled to the cubic bezier easing curve of the full circles (parts 3 and 6),
  as they move from right to left and back to their starting positions.

  This easing curve determines at which point in the animation timeline the sphere will be
  in a particular position. Changing it or the keyframe step percentages will break the animation.

  Things you *can* change are:

  1. The duration of the animation
  2. The easing of parts 1,2,4, and 5 (this is the animation of the half circles shifting in from
  the right after the circles 'sweep' by)
  3. The size of the logo (has no bearing on the animation despite the 'magic' pixel values in our
  CSS vars)

  Things you can't change, without making several additional changes:

  1. The --halfcircle-shift and --circle-shift variable values
  2. The easing curve of the end-shift animation on parts 3 and 6
  3. The keyframe percentage steps (think of these as points on a timeline of the animation, with 0%
  being the start and 100% being the end)
*/

.loading {
  --halfcircle-shift: 7px;
  --circle-shift: -20.1px;
}

.loading > [data-logo-part-1],
.loading > [data-logo-part-4] {
  animation: start-shift 2s infinite ease-in-out;
}

.loading > [data-logo-part-2],
.loading > [data-logo-part-5] {
  animation: middle-shift 2s infinite ease-in-out;
}

.loading > [data-logo-part-3],
.loading > [data-logo-part-6] {
  /**
    Changing this cubic-bezier will break the animation and require changes to the
    start-shift and middle-shift keyframe steps.
  */
  animation: end-shift 2s infinite cubic-bezier(0.79, 0.14, 0.15, 0.86);
}

/* Stagger the second row so it animates slightly after the first */
.loading > [data-logo-part-4],
.loading > [data-logo-part-5],
.loading > [data-logo-part-6] {
  animation-delay: 0.35s;
}

@keyframes start-shift {
  0% {
    visibility: visible;
    transform: translateX(0);
  }
  50% {
    visibility: hidden;
    transform: translateX(0);
  }
  73% {
    visibility: hidden;
    transform: translateX(var(--halfcircle-shift));
  }
  79% {
    visibility: visible;
    transform: translateX(0);
  }
}

@keyframes middle-shift {
  0% {
    visibility: visible;
    transform: translateX(0);
  }
  30% {
    visibility: hidden;
    transform: translateX(0);
  }
  78.6% {
    visibility: hidden;
    transform: translateX(var(--halfcircle-shift));
  }
  86% {
    visibility: visible;
    transform: translateX(0);
  }
}

/**
  The stops at 20% and 40% here are used to simulate a 'pause' whenever the spheres
  reach the start or end of the logo. CSS's built in animation-delay property only
  works on the first cycle of an animation, not between subsequent runs.
 */
@keyframes end-shift {
  0%,
  20% {
    transform: translateX(0);
  }
  40%,
  50% {
    transform: translateX(var(--circle-shift));
  }
}
</style>

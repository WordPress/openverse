import { ref, watch, Ref, ToRefs } from '@nuxtjs/composition-api'
import {
  createPopper,
  detectOverflow,
  Instance,
  Placement,
  PositioningStrategy,
} from '@popperjs/core'

import { useWindowSize } from '~/composables/use-window-size'

export type PopoverContentProps = {
  visible: boolean
  hide: () => void
  hideOnEsc: boolean
  hideOnClickOutside: boolean
  autoFocusOnShow: boolean
  autoFocusOnHide: boolean
  triggerElement: HTMLElement
  placement: Placement
  strategy: PositioningStrategy
  zIndex: number
}

type Props = {
  popoverRef: Ref<HTMLElement>
  popoverPropsRefs: ToRefs<PopoverContentProps>
}

// A constant offset to ensure there's a gap between
// the popover and the window border.
const PopperOffset = 20

export function usePopper({ popoverRef, popoverPropsRefs }: Props) {
  const popperInstanceRef = ref<Instance | undefined>()
  const maxHeightRef = ref<number | null>(null)

  watch(
    [
      popoverPropsRefs.triggerElement,
      popoverPropsRefs.placement,
      popoverPropsRefs.strategy,
      popoverPropsRefs.visible,
      popoverRef,
    ] as const,
    (
      [triggerElement, placement, strategy, visible, popover],
      _,
      onInvalidate
    ) => {
      if (!(triggerElement && popover)) return

      popperInstanceRef.value = createPopper(triggerElement, popover, {
        placement,
        strategy,
        modifiers: [
          {
            name: 'eventListeners',
            enabled: visible,
          },
          {
            name: 'arrow',
            enabled: false,
          },
          {
            name: 'offset',
            options: {
              offset: [0, 8],
            },
          },
        ],
      })

      onInvalidate(() => {
        if (popperInstanceRef.value) {
          popperInstanceRef.value.destroy()
          popperInstanceRef.value = undefined
        }
      })
    },
    { immediate: true }
  )

  /**
   * Detects if the popover is overflowing the viewport,
   * and sets the max-height of the popover accordingly.
   * If there is no overflow, the max-height is set to null.
   **/
  const detectMaxHeight = (popper: Instance) => {
    popper.forceUpdate() // make sure that `rects` are set

    const overflow = detectOverflow(popper.state)
    const verticalOverflow = Math.max(
      -PopperOffset,
      Math.max(overflow.bottom, overflow.top)
    )

    return verticalOverflow + PopperOffset > 0
      ? popper.state.rects.popper.height - verticalOverflow - PopperOffset
      : null
  }
  const { height: windowHeight } = useWindowSize()
  // We only use `windowHeight` to call update the popper max height when it changes, we don't need the actual value
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  watch([popperInstanceRef, windowHeight] as const, ([popper, _]) => {
    if (!popper) return
    maxHeightRef.value = detectMaxHeight(popper)
  })

  return { maxHeightRef }
}

import { ref, watch, Ref, ToRefs } from "vue"
import {
  autoUpdate,
  computePosition,
  detectOverflow,
  flip,
  limitShift,
  MiddlewareState,
  offset,
  Placement,
  shift,
  Strategy,
} from "@floating-ui/dom"

export type PopoverContentProps = {
  visible: boolean
  hide: () => void
  hideOnEsc: boolean
  hideOnClickOutside: boolean
  autoFocusOnShow: boolean
  autoFocusOnHide: boolean
  triggerElement: HTMLElement | null
  placement: Placement
  strategy: Strategy
  clippable: boolean
  trapFocus: boolean
  zIndex: number | string
}

type Props = {
  floatingElRef: Ref<HTMLElement | null>
  floatingPropsRefs: ToRefs<PopoverContentProps>
}

// A constant offset to ensure there's a gap between
// the floating element and the window border.
const FloatingOffset = 20

export function useFloatingUi({ floatingElRef, floatingPropsRefs }: Props) {
  const maxHeightRef = ref<number | null>(null)
  const style = ref<Record<string, string> | null>(null)
  const cleanup = ref<null | (() => void)>(null)

  const buildAutoUpdate = (
    triggerElement: HTMLElement,
    floatingElement: HTMLElement
  ) => {
    return autoUpdate(triggerElement, floatingElement, () => {
      computePosition(triggerElement, floatingElement, {
        placement: floatingPropsRefs.placement.value,
        middleware: [
          offset(8),
          flip(),
          shift({ limiter: limitShift() }),
          detectMaxHeight,
        ],
      }).then(({ x, y }) => {
        style.value = {
          left: `${x}px`, // floating-ui is handling RTL, so `left` is set correctly here.
          top: `${y}px`,
        }
      })
    })
  }

  watch(
    [
      floatingElRef,
      floatingPropsRefs.triggerElement,
      floatingPropsRefs.visible,
    ] as const,
    ([floatingElement, triggerElement, visible], _, onInvalidate) => {
      if (!triggerElement || !floatingElement) {
        cleanup.value?.()
        return
      }
      if (!visible) {
        return
      }

      cleanup.value = buildAutoUpdate(triggerElement, floatingElement)

      onInvalidate(() => {
        cleanup.value?.()
      })
    }
  )

  /**
   * Detects if the popover is overflowing the viewport,
   * and sets the max-height of the popover accordingly.
   * If there is no overflow, the max-height is set to null.
   **/
  const detectMaxHeight = {
    name: "detectMaxHeight",
    async fn(state: MiddlewareState) {
      if (!floatingPropsRefs.clippable.value) {
        return {}
      }
      const overflow = await detectOverflow(state, { padding: FloatingOffset })
      const verticalOverflow = Math.max(overflow.top, overflow.bottom)

      if (verticalOverflow > 0) {
        maxHeightRef.value = state.rects.floating.height - verticalOverflow
      } else if (maxHeightRef.value) {
        const p = floatingElRef.value as HTMLElement
        const isScrollable = p.scrollHeight > p.clientHeight
        if (!isScrollable) {
          maxHeightRef.value = null
        } else if (maxHeightRef.value > p.clientHeight) {
          maxHeightRef.value += Math.max(overflow.top, overflow.bottom)
        }
      }
      return {}
    },
  }

  return { style, maxHeightRef }
}

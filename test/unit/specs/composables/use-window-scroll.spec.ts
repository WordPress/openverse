import Vue from "vue"
import { ref } from "@nuxtjs/composition-api"
import { render } from "@testing-library/vue"

import { useWindowScroll } from "~/composables/use-window-scroll"

const getMockWindow = <T>(props: T) =>
  ({
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    ...props,
  } as unknown as typeof window)

const UseWindowScrollTestContainer = Vue.component(
  "UseWindowScrollTestContainer",
  {
    props: ["initX", "initY", "throttleMs"],
    setup(props) {
      return useWindowScroll({
        window: getMockWindow({
          scrollX: props.initX,
          scrollY: props.initY,
        }),
        throttleMs: props.throttleMs as number | undefined,
      })
    },
    template: "<div>x={{x}} y={{y}} isScrolled={{isScrolled}}</div>",
  }
)

describe("useWindowScroll", () => {
  it("should return [0, 0] and false when no window", () => {
    expect(useWindowScroll({})).toMatchObject({
      x: ref(0),
      y: ref(0),
      isScrolled: ref(false),
    })
  })

  it("should return the window's scroll position and not scrolled when y == 0", () => {
    const { container } = render(UseWindowScrollTestContainer, {
      props: {
        initX: 10,
        initY: 0,
      },
    })

    expect(container.firstChild?.textContent).toEqual(
      "x=10 y=0 isScrolled=false"
    )
  })

  it("should return the window's scroll position and scrolled when y != 0", () => {
    const { container } = render(UseWindowScrollTestContainer, {
      props: {
        initX: 31,
        initY: 1,
      },
    })

    expect(container.firstChild?.textContent).toEqual(
      "x=31 y=1 isScrolled=true"
    )
  })
})

import Vue, { ref, computed } from "vue"
import { screen } from "@testing-library/vue"
import userEvent from "@testing-library/user-event"

import { render } from "~~/test/unit/test-utils/render"

import VModal from "~/components/VModal/VModal.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"
import VButton from "~/components/VButton.vue"

const TestWrapper = Vue.component("TestWrapper", {
  components: { VModal, VButton, VModalTarget },
  props: ["useCustomInitialFocus"],
  setup(props) {
    const initialFocusElement = ref()

    const resolvedInitialFocusElement = computed(() =>
      props.useCustomInitialFocus ? initialFocusElement.value : undefined
    )

    return { initialFocusElement, resolvedInitialFocusElement }
  },
  template: `
    <div>
      <VModal label="modal label" :initial-focus-element="resolvedInitialFocusElement">
        <template #trigger="{ a11yProps, visible }">
          <VButton variant="filled-white" size="medium" v-bind="a11yProps">{{ visible }}</VButton>
        </template>

        <div>Code is Poetry</div>

        <button ref="initialFocusElement" type="button">Custom initial focus</button>
      </VModal>
      <VModalTarget />
    </div>
  `,
})

const nextTick = async () =>
  await new Promise((resolve) => setTimeout(resolve, 1))

const getCloseButton = () => screen.getByRole("button", { name: /close/i })
const getDialog = () => screen.getByRole("dialog")
const queryDialog = () => screen.queryByRole("dialog")
const getTrigger = () => screen.getByRole("button")
const doOpen = async () => {
  await userEvent.click(getTrigger())
  await nextTick()
}

// `useDialogContent` functionality is already tested by `VPopover` tests.
// Eventually we'll want to abstract those tests out but for now it's not worth
// the work.
describe("VModal", () => {
  let options
  let _scrollTo
  beforeAll(() => {
    _scrollTo = window.scrollTo
    window.scrollTo = jest.fn()
  })
  afterAll(() => {
    window.scrollTo = _scrollTo
  })

  beforeEach(() => {
    options = {
      props: { useCustomInitialFocus: false },
    }
    jest.resetAllMocks()
  })

  it("should render a close button that hides the modal", async () => {
    render(TestWrapper, options)
    await doOpen()

    expect(getDialog()).toBeVisible()

    await userEvent.click(getCloseButton())
    await nextTick()

    expect(queryDialog()).toBe(null)
  })

  it("should scroll lock the body when modal opens and unlock when modal closes", async () => {
    const { container } = render(TestWrapper, options)
    const scrollY = 10
    window.scrollY = scrollY
    await doOpen()

    expect(getDialog()).toBeVisible()
    expect(container.ownerDocument.body.style.position).toBe("fixed")
    expect(container.ownerDocument.body.style.top).toBe(`-${scrollY}px`)

    await userEvent.click(getCloseButton())
    await nextTick()

    expect(window.scrollTo).toHaveBeenCalledWith(0, scrollY)
    expect(container.ownerDocument.body.style.position).not.toBe("fixed")
  })

  it("should focus the close button by default", async () => {
    render(TestWrapper, options)
    await doOpen()

    expect(getDialog()).toBeVisible()
    expect(getCloseButton()).toHaveFocus()
  })

  it("should focus the explicit initial focus element when specified", async () => {
    options.props = { useCustomInitialFocus: true }
    render(TestWrapper, options)
    await doOpen()

    expect(getDialog()).toBeVisible()
    expect(screen.getByText(/custom initial focus/i)).toHaveFocus()
  })

  it("should hide the modal on escape", async () => {
    render(TestWrapper, options)
    await doOpen()

    expect(getDialog()).toBeVisible()

    await userEvent.keyboard("{Escape}")
    await nextTick()

    expect(queryDialog()).toBe(null)
  })
})

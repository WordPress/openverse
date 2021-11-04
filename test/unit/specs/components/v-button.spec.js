import { render, screen } from '@testing-library/vue'

import VButton from '~/components/VButton.vue'

/**
 * Throughout this suite we use the `screen.findBy*` functions to asynchronously
 * wait for the component to re-render. There might be some kind of performance
 * problem with the component's implementation, but if we don't "wait" for it
 * to settle, then all the props that are changed after `onMounted` completes
 * won't be rendered.
 */
describe('VButton', () => {
  let warn
  beforeAll(() => {
    warn = console.warn
    console.warn = jest.fn()
  })
  beforeEach(() => {
    console.warn.mockReset()
  })
  afterAll(() => {
    console.warn = warn
  })

  it('should render a `button` by default with type="button" and no tabindex', async () => {
    render(VButton, {
      slots: { default: 'Code is Poetry' },
    })

    const element = await screen.findByRole('button')

    expect(element.tagName).toBe('BUTTON')
    expect(element).toHaveAttribute('type', 'button')
    expect(element).not.toHaveAttribute('tabindex')
  })

  it('should allow passing an explicit type', async () => {
    render(VButton, {
      props: { type: 'submit' },
      slots: { default: 'Code is Poetry' },
    })

    const element = await screen.findByRole('button')

    expect(element).toHaveAttribute('type', 'submit')
  })

  // @todo(sarayourfriend) fix this failing test!
  it.skip('should render an anchor with no type attribute', async () => {
    render(VButton, {
      props: { as: 'a' },
      slots: { default: 'Code is Poetry' },
    })

    const element = await screen.findByText(/code is poetry/i)

    screen.debug(element)

    expect(element.tagName).toBe('A')
    expect(element).not.toHaveAttribute('type')
  })

  it('should render the disabled attribute on a button when the element is explicitly unfocusableWhenDisabled and is disabled', async () => {
    render(VButton, {
      props: { disabled: true, focusableWhenDisabled: false },
      slots: { default: 'Code is Poetry' },
    })

    const element = await screen.findByRole('button')

    // Vue renders the disabled attribute having a `true` value as `[disabled="disabled"]`
    expect(element).toHaveAttribute('disabled', 'disabled')
  })

  it('should not render the disabled attribute if the element is focusableWhenDisabled', async () => {
    render(VButton, {
      props: { disabled: true, focusableWhenDisabled: true },
      slots: { default: 'Code is Poetry' },
    })

    const element = await screen.findByRole('button')

    expect(element).not.toHaveAttribute('disabled')
    expect(element).toHaveAttribute('aria-disabled', 'true')
  })

  it('should not render the disabled attribute on elements that do not support it', async () => {
    render(VButton, {
      props: {
        as: 'a',
        disabled: true,
        focusableWhenDisabled: true,
        href: 'https://wordpress.org',
      },
      slots: { default: 'Code is Poetry' },
    })

    const element = await screen.findByText(/code is poetry/i)

    expect(element).not.toHaveAttribute('disabled')
    expect(element).toHaveAttribute('aria-disabled', 'true')
  })

  it.each([undefined, '', null, '#'])(
    'should warn if an anchor is used without a valid href: %s',
    async (href) => {
      render(VButton, {
        props: { as: 'a', href },
        slots: { default: 'Code is Poetry' },
      })

      await screen.findByText(/code is poetry/i)

      expect(console.warn).toHaveBeenCalledTimes(1)
      expect(console.warn).toHaveBeenCalledWith(
        'Do not use anchor elements without a valid `href` attribute. Use a `button` instead.'
      )
    }
  )
})

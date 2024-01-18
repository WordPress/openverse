// Copied from https://github.com/nuxt/test-utils/blob/bc86d23b2cf92aa3c3f19d52944452e4e5c27d63/src/runtime-utils/render.ts
// Fixes the issue when values returned from setup are not available in template when using renderSuspended
// Line 154: replaced `render(renderContext, ...args)` with `render(_ctx, ...args)`

import {
  type DefineComponent,
  type SetupContext,
  defineComponent,
  Suspense,
  h,
  nextTick,
} from "vue"

import { defu } from "defu"

import type { RenderOptions as TestingLibraryRenderOptions } from "@testing-library/vue"
import type { RouteLocationRaw } from "vue-router"

export const RouterLink = defineComponent({
  functional: true,
  props: {
    to: {
      type: [String, Object],
      required: true,
    },
    custom: Boolean,
    replace: Boolean,
    // Not implemented
    activeClass: String,
    exactActiveClass: String,
    ariaCurrentValue: String,
  },
  setup: (props, { slots }) => {
    const navigate = () => {}
    return () => {
      const route = useRouter().resolve(props.to)

      return props.custom
        ? slots.default?.({ href: route.href, navigate, route })
        : h(
            "a",
            {
              href: route.href,
              onClick: (e: MouseEvent) => {
                e.preventDefault()
                return navigate()
              },
            },
            slots
          )
    }
  },
})

// @ts-expect-error virtual file
import NuxtRoot from "#build/root-component.mjs"

import { useRouter } from "#imports"

export type RenderOptions = TestingLibraryRenderOptions & {
  route?: RouteLocationRaw
}

export const WRAPPER_EL_ID = "test-wrapper"

/**
 * `renderSuspended` allows you to mount any vue component within the Nuxt environment, allowing async setup and access to injections from your Nuxt plugins.
 *
 * This is a wrapper around the `render` function from @testing-libary/vue, and should be used together with
 * utilities from that package.
 *
 * ```ts
 * // tests/components/SomeComponents.nuxt.spec.ts
 * import { renderSuspended } from '@nuxt/test-utils/runtime'
 *
 * it('can render some component', async () => {
 * const { html } = await renderSuspended(SomeComponent)
 * expect(html()).toMatchInlineSnapshot(
 * 'This is an auto-imported component'
 * )
 *
 * })
 *
 * // tests/App.nuxt.spec.ts
 * import { renderSuspended } from '@nuxt/test-utils/runtime'
 * import { screen } from '@testing-library/vue'
 *
 * it('can also mount an app', async () => {
 * const { html } = await renderSuspended(App, { route: '/test' })
 * expect(screen.getByRole('link', { name: 'Test Link' })).toBeVisible()
 * })
 * ```
 * @param component the component to be tested
 * @param options optional options to set up your component
 */
export async function renderSuspended<T>(
  component: T,
  options?: RenderOptions
) {
  const {
    props = {},
    attrs = {},
    slots = {},
    route = "/",
    ..._options
  } = options || {}

  const { render: renderFromTestingLibrary } = await import(
    "@testing-library/vue"
  )

  // @ts-expect-error untyped global __unctx__
  const { vueApp } = globalThis.__unctx__.get("nuxt-app").tryUse()
  const { render, setup } = component as DefineComponent<any, any>

  // cleanup previously mounted test wrappers
  document.querySelector(`#${WRAPPER_EL_ID}`)?.remove()

  let setupContext: SetupContext

  return new Promise<ReturnType<typeof renderFromTestingLibrary>>((resolve) => {
    const utils = renderFromTestingLibrary(
      {
        // eslint-disable-next-line @typescript-eslint/no-shadow
        setup: (props: any, ctx: any) => {
          setupContext = ctx

          return NuxtRoot.setup(props, {
            ...ctx,
            expose: () => {},
          })
        },
        render: (renderContext: any) =>
          // See discussions in https://github.com/testing-library/vue-testing-library/issues/230
          // we add this additional root element because otherwise testing-library breaks
          // because there's no root element while Suspense is resolving
          h(
            "div",
            { id: WRAPPER_EL_ID },
            h(
              Suspense,
              { onResolve: () => nextTick().then(() => resolve(utils)) },
              {
                default: () =>
                  h({
                    async setup() {
                      const router = useRouter()
                      await router.replace(route)

                      // Proxy top-level setup/render context so test wrapper resolves child component
                      const clonedComponent = {
                        ...component,

                        // TODO: Should it be render({{ ...ctx, ...renderContext }}) instead?
                        render: render
                          ? (_ctx: any, ...args: any[]) => render(_ctx, ...args)
                          : undefined,
                        setup: setup
                          ? // eslint-disable-next-line @typescript-eslint/no-shadow
                            (props: Record<string, any>) =>
                              setup(props, setupContext)
                          : undefined,
                      }

                      return () =>
                        h(clonedComponent, { ...props, ...attrs }, slots)
                    },
                  }),
              }
            )
          ),
      },
      defu(_options, {
        slots,
        global: {
          config: {
            globalProperties: vueApp.config.globalProperties,
          },
          provide: vueApp._context.provides,
          components: { RouterLink },
        },
      })
    )
  })
}

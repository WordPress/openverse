import { test, expect, Expect } from "@playwright/test"

import { VIEWPORTS } from "~/constants/screens"
import type { Breakpoint } from "~/constants/screens"

type ScreenshotAble = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  screenshot(...args: any[]): Promise<Buffer>
}

type ExpectSnapshot = <T extends ScreenshotAble>(
  name: string,
  s: T,
  options?: Parameters<T["screenshot"]>[0],
  snapshotOptions?: Parameters<ReturnType<Expect>["toMatchSnapshot"]>[0]
) => Promise<Buffer | void>

type BreakpointBlock = (options: {
  getConfigValues: (name: string) => {
    name: `${typeof name}-${Breakpoint}.png`
  }
  breakpoint: Breakpoint
  expectSnapshot: ExpectSnapshot
}) => void

export const desktopBreakpoints = ["2xl", "xl", "lg"] as const
export const mobileBreakpoints = ["md", "sm", "xs"] as const

export const isMobileBreakpoint = (
  bp: Breakpoint
): bp is (typeof mobileBreakpoints)[number] =>
  (mobileBreakpoints as unknown as string[]).includes(bp)

// For desktop UA use the default
const desktopUa = undefined
const mobileUa =
  "Mozilla/5.0 (Android 7.0; Mobile; rv:54.0) Gecko/54.0 Firefox/54.0"

const mockUaStrings: Readonly<Record<Breakpoint, string | undefined>> =
  Object.freeze(
    Object.fromEntries([
      ...desktopBreakpoints.map((b) => [b, desktopUa]),
      ...mobileBreakpoints.map((b) => [b, mobileUa]),
    ])
  )

interface Options {
  /**
   * Whether to mock the UA for mobile browsers.
   *
   * @defaultValue true
   */
  uaMocking?: boolean
}

const defaultOptions = Object.freeze({
  uaMocking: true,
})

const makeBreakpointDescribe =
  (breakpoint: Breakpoint, screenWidth: number) =>
  <T extends BreakpointBlock | Options>(
    blockOrOptions: T,
    block?: T extends Record<string, unknown> ? BreakpointBlock : undefined
  ) => {
    test.describe(`screen at breakpoint ${breakpoint} with width ${screenWidth}`, () => {
      const _block = (
        typeof blockOrOptions === "function" ? blockOrOptions : block
      ) as BreakpointBlock
      const options =
        typeof blockOrOptions !== "function"
          ? { ...defaultOptions, ...blockOrOptions }
          : defaultOptions

      test.use({
        viewport: { width: screenWidth, height: 700 },
        userAgent: options.uaMocking ? mockUaStrings[breakpoint] : undefined,
      })

      const getConfigValues = (name: string) => ({
        name: `${name}-${breakpoint}.png` as const,
      })

      const expectSnapshot = async <T extends ScreenshotAble>(
        name: string,
        screenshotAble: T,
        options?: Parameters<T["screenshot"]>[0],
        snapshotOptions?: Parameters<ReturnType<Expect>["toMatchSnapshot"]>[0]
      ) => {
        const { name: snapshotName } = getConfigValues(name)
        return expect(await screenshotAble.screenshot(options)).toMatchSnapshot(
          {
            name: snapshotName,
            ...snapshotOptions,
          }
        )
      }

      _block({ breakpoint, getConfigValues, expectSnapshot })
    })
  }

const capitalize = (s: string): Capitalize<typeof s> =>
  `${s[0].toUpperCase()}${s.slice(1)}` as Capitalize<typeof s>

const breakpointTests = Array.from(Object.entries(VIEWPORTS)).reduce(
  (
    tests,
    [
      breakpoint,
      {
        styles: { width },
      },
    ]
  ) =>
    Object.assign(tests, {
      [`describe${capitalize(breakpoint as Breakpoint)}`]:
        makeBreakpointDescribe(
          breakpoint as Breakpoint,
          parseFloat(width.replace("px", ""))
        ),
    }),
  {} as Record<
    `describe${Capitalize<Breakpoint>}`,
    ReturnType<typeof makeBreakpointDescribe>
  >
)

const describeEachBreakpoint =
  (breakpoints: readonly Breakpoint[]) =>
  <T extends BreakpointBlock | Options>(
    blockOrOptions: T,
    block?: T extends Record<string, unknown> ? BreakpointBlock : undefined
  ) => {
    Object.entries(breakpointTests).forEach(([bp, describe]) => {
      if (
        breakpoints.includes(
          bp.replace("describe", "").toLowerCase() as Breakpoint
        )
      )
        describe(blockOrOptions, block)
    })
  }

const describeEvery = describeEachBreakpoint(
  Object.keys(VIEWPORTS) as Breakpoint[]
)
const describeEachDesktopWithMd = describeEachBreakpoint([
  ...desktopBreakpoints,
  "md",
])
const describeEachDesktop = describeEachBreakpoint(desktopBreakpoints)
const describeEachMobile = describeEachBreakpoint(mobileBreakpoints)
const describeEachMobileWithoutMd = describeEachBreakpoint(
  mobileBreakpoints.filter((b) => b !== "md")
)
const describeMobileAndDesktop = describeEachBreakpoint(["sm", "xl"])
const describeMobileXsAndDesktop = describeEachBreakpoint(["xs", "xl"])

export default {
  ...breakpointTests,
  describeEachBreakpoint,
  describeEvery,
  describeEachDesktop,
  describeEachMobile,
  // For `old_header` layout, the mobile layout ends at `md` breakpoint
  describeEachMobileWithoutMd,
  describeEachDesktopWithMd,
  // For testing functionality in e2e tests, we need to test mobile and desktop screens.
  // Having two breakpoints should be enough and should save testing time.
  describeMobileAndDesktop,
  // All tests
  describeMobileXsAndDesktop,
}

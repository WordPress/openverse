/**
 * `RealBreakpoints` excludes 'xs' because it's not defined in
 * Tailwind (being mobile-first) but is used in JavaScript to refer to mobile
 * screens that are narrower than 640px ('sm').
 */
export type Breakpoint = "2xl" | "xl" | "lg" | "md" | "sm" | "xs"
export type RealBreakpoint = Exclude<Breakpoint, "xs">
export type Viewport = {
  name: string
  styles: { width: string; height: string }
}

/**
 * Mapping of breakpoint names to the lower-bound of their screen width range.
 */
export const SCREEN_SIZES = Object.freeze({
  "2xl": 1536,
  xl: 1280,
  lg: 1024,
  md: 768,
  sm: 640,
} as const)

/**
 * The same as SCREEN_SIZES but with the 'xs' breakpoint added for use in JS.
 */
export const ALL_SCREEN_SIZES = Object.freeze({
  ...SCREEN_SIZES,
  xs: 0,
} as const)

/**
 * Mapping of breakpoint names to the lower-bound of their screen width range,
 * with the 'px' suffix attached. This is used by Tailwind.
 */
export const SCREENS = Object.fromEntries(
  Object.entries(SCREEN_SIZES)
    .map(([key, val]) => [key, `${val}px`])
    .reverse()
) as Record<RealBreakpoint, string>

/**
 * Mapping of breakpoint names to viewport specifications. This is used by
 * the viewports plugin of Storybook.
 */
export const VIEWPORTS = Object.fromEntries(
  (Object.entries(SCREEN_SIZES) as [Breakpoint, number][])
    .concat([["xs", 340]])
    .map(([key, val]) => [
      key,
      {
        name: `${key} (${val}px)`,
        styles: { width: `${val}px`, height: "768px" },
      },
    ])
) as Record<Breakpoint, Viewport>

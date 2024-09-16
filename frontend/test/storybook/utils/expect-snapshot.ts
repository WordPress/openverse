import {
  Expect,
  expect,
  Locator,
  LocatorScreenshotOptions,
  Page,
  PageScreenshotOptions,
} from "@playwright/test"

export type ExpectSnapshotOptions = {
  screenshotOptions: LocatorScreenshotOptions | PageScreenshotOptions
  snapshotOptions: Parameters<ReturnType<Expect>["toMatchSnapshot"]>[0]
}

export const expectSnapshot = async (
  name: string,
  locator: Locator | Page,
  options?: ExpectSnapshotOptions
) => {
  const snapshotName = `${name}-light.png`
  return expect(
    await locator.screenshot(options?.screenshotOptions)
  ).toMatchSnapshot(snapshotName, options?.snapshotOptions)
}

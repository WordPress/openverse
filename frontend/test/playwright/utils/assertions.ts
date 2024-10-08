import { expect, type Page } from "@playwright/test"

export const expectCheckboxState = async (
  page: Page,
  name: string,
  checked: boolean | undefined
) => {
  const checkbox = page.getByRole("checkbox", { name, checked }).first()
  await expect(checkbox).toBeEnabled()
  if (checked) {
    await expect(checkbox).toBeChecked()
  } else {
    await expect(checkbox).not.toBeChecked()
  }
}

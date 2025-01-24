import { h } from "vue"

import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

import VLanguageSelect from "~/components/VLanguageSelect/VLanguageSelect.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VLanguageSelect",
  component: VLanguageSelect,
  decorators: [WithScreenshotArea],
} satisfies Meta<typeof VLanguageSelect>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VLanguageSelect },
    setup() {
      return () => h(VLanguageSelect, args)
    },
  }),
  name: "Default",
}
import React from "react";
import { useTranslation } from "react-i18next";
import supportedLocales from "../../config/localization";

const LanguageSelector = () => {
  const { i18n } = useTranslation();

  const handleLanguageChange = (event) => {
    const selectedLanguage = event.target.value;
    i18n.changeLanguage(selectedLanguage);
  };

  return (
    <select onChange={handleLanguageChange} defaultValue={i18n.language}>
      {Object.entries(supportedLocales).map(([locale, label]) => (
        <option key={locale} value={locale}>
          {label}
        </option>
      ))}
    </select>
  );
};

export default LanguageSelector;

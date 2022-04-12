export default () => {
  return {
    fallbackLocale: 'en',
    silentFallbackWarn: true,
    pluralizationRules: {
      /**
       * @param choice - a choice index given by the input to $tc: `$tc('path.to.rule', choiceIndex)`
       * @param choicesLength - an overall amount of available choices
       * @returns a final choice index to select plural word by
       */
      ru: function (choice: number, choicesLength: number) {
        if (choice === 0) {
          return 0
        }

        const teen = choice > 10 && choice < 20
        const endsWithOne = choice % 10 === 1

        if (choicesLength < 4) {
          return !teen && endsWithOne ? 1 : 2
        }
        if (!teen && endsWithOne) {
          return 1
        }
        if (!teen && choice % 10 >= 2 && choice % 10 <= 4) {
          return 2
        }

        return choicesLength < 4 ? 2 : 3
      },
    },
  }
}

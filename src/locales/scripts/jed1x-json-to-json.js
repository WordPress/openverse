const { setToValue } = require('./utils')

/**
 * Convert a Jed1x-Translate object to a nested JSON object.
 *
 * Create a nested JSON object, clean up keys from jed1x context with special
 * character, remove keys without values, convert values from array to string,
 * if strings are for plural forms, join them with the pipe character.
 * Go from this:
 * {
 *  "browse-page.load\u0004Load more results": [
 *     "Загрузить ещё результаты"
 *   ],
 *   "browse-page.all-result-count-more\u0004Over ###localeCount### results": [
 *     "Более ###localeCount### результата",
 *     "Более ###localeCount### результатов",
 *     "Более ###localeCount### результатов"
 *   ]
 *  "browse-page.search-form.button\u0004Search": [],
 * }
 * To:
 * {
 *  "browse-page: {
 *   "load": "Загрузить ещё результаты"
 *   "all-result-count-more": "Более ###localeCount### результата|Более ###localeCount### результатов|Более ###localeCount### результатов",
 * }
 *
 */

// special character, context delimiter in jed format:
// https://github.com/messageformat/Jed/blob/351c47d5c57c5c81e418414c53ca84075c518edb/jed.js#L117
const SPLIT_CHAR = String.fromCharCode(4)

function jed1xJsonToJson(jed1xObject) {
  const result = {}
  Object.entries(jed1xObject?.locale_data?.messages).forEach(([key, value]) => {
    const cleanedKey = key.slice(0, key.indexOf(SPLIT_CHAR))
    if (value.length > 0) {
      const cleanedValue = value.length === 1 ? value[0] : value.join('|')
      return setToValue(result, cleanedKey, cleanedValue)
    }
  })
  return result
}

// test
// node jed1x-json-to-json.js
// console.log(
//   JSON.stringify(
//     jed1xJsonToJson({
//       locale_data: {
//         messages: {
//           'browse-page.load\u0004Load more results': [
//             'Загрузить ещё результаты',
//           ],
//           'browse-page.all-result-count-more\u0004Over ###localeCount### results':
//             [
//               'Более ###localeCount### результата',
//               'Более ###localeCount### результатов',
//               'Более ###localeCount### результатов',
//             ],
//           'browse-page.search-form.button\u0004Search': [],
//         },
//       },
//     })
//   )
// )

module.exports = jed1xJsonToJson

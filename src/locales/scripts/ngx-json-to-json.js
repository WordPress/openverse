const { setToValue } = require('./utils')

/**
 * Convert an NGX-Translate object to a nested JSON object
 *
 * Go from this:
 * {
 *   "photo-details.aria.share.pinterest": "compartir en pinterest",
 *   "photo-details.aria.share.twitter": "compartir en twitter",
 *   "photo-details.aria.share.facebook": "compartir en facebook",
 * }
 * To:
 * {
 *  "photo-details": {
 *      "aria": {
 *        "share": {
 *          "twitter": "compartir en pinterest",
 *          "facebook": "compartir en twitter",
 *          "pinterest": "compartir en facebook",
 *        }
 *      }
 *   }
 * }
 *
 */
function ngxJsonToJson(ngxObject) {
  const result = {}
  Object.entries(ngxObject).forEach(
    ([key, value]) => value && setToValue(result, key, value)
  )
  return result
}

// test
// node ngx-json-to-json.js
// console.log(
//   JSON.stringify(
//     ngxJsonToJson({
//       'wow.okay.cool': null,
//       'photo-details.aria.share.pinterest': 'compartir en pinterest',
//       'photo-details.aria.share.twitter': 'compartir en twitter',
//       'photo-details.aria.share.facebook': 'compartir en facebook',
//     })
//   )
// )

module.exports = ngxJsonToJson

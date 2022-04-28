/**
 * Mutates an object at the path with the value. If the path
 * does not exist, it is created by nesting objects along the
 * path segments.
 *
 * @see {@link https://stackoverflow.com/a/20240290|Stack Overflow}
 *
 * @param {any} obj - The object to mutate.
 * @param {string} path - The dot delimited path on the object to mutate.
 * @param {unknown} value - The value to set at the path.
 */
exports.setToValue = function setValue(obj, path, value) {
  var a = path.split('.')
  var o = obj
  while (a.length - 1) {
    var n = a.shift()
    if (!(n in o)) o[n] = {}
    o = o[n]
  }
  o[a[0]] = value
}

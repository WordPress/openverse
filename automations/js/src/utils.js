const compose = (...fns) =>
  fns.reduce(
    (f, g) =>
      (...args) =>
        f(g(...args))
  )
const map = (fn) => (arr) => arr.map(fn)
const fmap = (fn) => (arr) => arr.flatMap(fn)
const tap = (fn) => (value) => {
  fn(value)
  return value
}
const filter = (fn) => (arr) => arr.filter(fn)
const tapLog = tap(console.log)
const prop = (prop) => (obj) => obj[prop]
const fromPairs = (pairs) =>
  pairs.reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {})
const zip = (a) => (b) => a.map((a, i) => [a, b[i]])
const zipObj = (a) => compose(fromPairs, zip(a))
const mapAwait = (fn) => (data) => Promise.all(map(fn)(data))
const gt = (test) => (value) => value > test
const gte = (test) => (value) => value >= test
const entries = (obj) => Object.entries(obj)
const branch =
  (left, right) =>
  ([a, b]) => {
    left(a)
    right(b)
  }

module.exports = {
  compose,
  map,
  fmap,
  tap,
  tapLog,
  prop,
  fromPairs,
  zip,
  zipObj,
  mapAwait,
  gt,
  gte,
  filter,
  entries,
  branch,
}

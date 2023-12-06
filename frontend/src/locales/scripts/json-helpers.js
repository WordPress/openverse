// Copied from these two libraries:
// https://github.com/coderaiser/all-object-keys
// https://github.com/coderaiser/jessy
const isObject = (a) => typeof a === "object"
const isEmptyObject = (a) => !Object.keys(a).length
const isSimple = (a) => !a || !isObject(a) || isEmptyObject(a)
const pop = (a) => a.pop() || []

function getAllPaths(obj) {
  const result = []
  const [currentResult, stack] = readPaths(obj)
  result.push(...currentResult)
  let [key, current] = pop(stack)
  while (current) {
    const [currentResult, currentStack] = readPaths(current, key)
    result.push(...currentResult)
    stack.push(...currentStack)
    // [key, current] = pop(stack) - doesn't work, cannot create property '[object Object]'
    const values = pop(stack)
    key = values[0]
    current = values[1]
  }
  return result
}

const { entries } = Object

function readPaths(obj, path = "") {
  const divider = "."
  const result = []
  const stack = []
  for (const [key, value] of entries(obj)) {
    const fullPath = !path ? key : `${path}${divider}${key}`
    if (isSimple(value)) {
      result.push(fullPath)
      continue
    }
    if (value === obj) {
      continue
    }
    stack.push([fullPath, value])
  }
  return [result, stack]
}
const getKeyValue = (key, value) => {
  const selects = key.split(".")
  selects.some((name, i) => {
    const nestedName = selects.slice(i).join(".")
    if (typeof value[nestedName] !== "undefined") {
      value = value[nestedName]
      return true
    }
    if (!value[name]) {
      value = undefined
      return true
    }
    value = value[name]

    return !value
  })

  return value
}
module.exports = { getAllPaths, getKeyValue }

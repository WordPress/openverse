export default function loadScript(url = '') {
  return new Promise((resolve, reject) => {
    if (typeof document === 'undefined') {
      reject()
    }

    const el = document.createElement('script')
    el.src = url
    el.defer = true
    el.addEventListener('load', () => {
      resolve()
    })
    document.head.appendChild(el)
  })
}

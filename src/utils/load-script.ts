/**
 * Dynamically injects a `<script>` tag into the page with the given `src`
 * attribute.
 *
 * @param url - the URL of the script to load
 * @returns the `load` event emitted by the script tag upon successful load
 */
export const loadScript = (url = ''): Promise<Event> => {
  return new Promise((resolve, reject) => {
    if (typeof document === 'undefined') {
      reject()
    }

    const el = document.createElement('script')
    el.src = url
    el.defer = true
    el.addEventListener('load', resolve)
    el.addEventListener('error', reject)
    document.head.appendChild(el)
  })
}

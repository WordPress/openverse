const fs = require('fs')
const path = require('path')
const express = require('express')
const microcache = require('route-cache')
const { createBundleRenderer } = require('vue-server-renderer')
const bundle = require('./dist/server-bundle.json')

const server = express()
const resolve = (file) => path.resolve(__dirname, file)
const templatePath = resolve('./index-server.html')
const template = fs.readFileSync(templatePath, 'utf-8')
const clientManifest = require('./dist/vue-ssr-client-manifest.json')

function createRenderer(bundle, options) {
  // https://github.com/vuejs/vue/blob/dev/packages/vue-server-renderer/README.md#why-use-bundlerenderer
  return createBundleRenderer(
    bundle,
    Object.assign(options, {
      // this property means that the bundle code will run in the same global context with the server
      // process and recommended for performance.
      runInNewContext: false,
    })
  )
}

const renderer = createRenderer(bundle, {
  template,
  clientManifest,
})

const serve = (path) =>
  express.static(resolve(path), {
    maxAge: 1000 * 60 * 60, // 1h static assets cache
  })

server.use('/static', serve('./dist/static'))

function render(req, res) {
  const handleError = (err) => {
    if (err.url) {
      res.redirect(err.url)
    } else if (err.code === 404) {
      res.status(404).send('404 | Page Not Found')
    } else {
      // Render Error Page or Redirect
      res.status(500).send('500 | Internal Server Error')
      console.error(`error during render : ${req.url}`)
      console.error(err.stack)
    }
  }

  const context = {
    url: req.url,
  }
  renderer.renderToString(context, (err, html) => {
    if (err) {
      return handleError(err)
    }
    res.send(html)
  })
}

function healthcheck(req, res) {
  res.send('healthy')
}

// since this app has no user-specific content, every page is micro-cacheable.
// if your app involves user-specific content, you need to implement custom
// logic to determine whether a request is cacheable based on its url and
// headers.
// 30-second url response microcache.
// https://www.nginx.com/blog/benefits-of-microcaching-nginx/
server.use(microcache.cacheSeconds(30, (req) => req.originalUrl))

server.get('/healthcheck', healthcheck)
server.get('*', render)

const port = process.env.PORT || 8080
server.listen(port, () => {
  console.log(`server started at > http://localhost:${port}`)
})

const fs = require('fs')
const path = require('path')
const express = require('express')
const { createBundleRenderer } = require('vue-server-renderer')
const bundle = require('./dist/server-bundle.json');

const server = express();
const resolve = file => path.resolve(__dirname, file);
const templatePath = resolve('./index.html');
const template = fs.readFileSync(templatePath, 'utf-8');

function createRenderer (bundle, options) {
  // https://github.com/vuejs/vue/blob/dev/packages/vue-server-renderer/README.md#why-use-bundlerenderer
  return createBundleRenderer(bundle, Object.assign(options, {
    // recommended for performance
    // runInNewContext: false,
  }));
}

const renderer = createRenderer(bundle, {
  template,
});

const serve = path => express.static(resolve(path), {
  maxAge: 1000 * 60 * 60 * 24 * 30
})

server.use('/static', serve('./dist/static', true));

function render (req, res) {
  const s = Date.now()

  res.setHeader("Content-Type", "text/html")

  const handleError = err => {
    if (err.url) {
      res.redirect(err.url);
    }
    else if(err.code === 404) {
      res.status(404).send('404 | Page Not Found');
    }
    else {
      // Render Error Page or Redirect
      res.status(500).send('500 | Internal Server Error');
      console.error(`error during render : ${req.url}`);
      console.error(err.stack);
    }
  }

  const context = {
    title: 'Vue HN 2.0', // default title
    url: req.url,
  };
  renderer.renderToString(context, (err, html) => {
    if (err) {
      return handleError(err);
    }
    res.send(html);
    if (!isProd) {
      console.log(`whole request: ${Date.now() - s}ms`);
    }
  });
}

server.get('*', render);

const port = process.env.PORT || 8080
server.listen(port, () => {
  console.log(`server started at localhost:${port}`);
});

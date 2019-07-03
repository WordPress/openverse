import express from 'express';
import vueServerRenderer from 'vue-server-renderer';
import bundle from '../../dist/server-bundle.json';

const server = express();
const renderer = vueServerRenderer.createBundleRenderer(bundle);

server.get('*', (req, res) => {
  renderer.renderToString({}, (err, html) => {
    if (err) {
      res.status(500).end('Internal Server Error');
      console.log(err);
      return;
    }
    res.end(`
      <!DOCTYPE html>
      <html lang="en">
        <head><title>Hello</title></head>
        <body>${html}</body>
      </html>
    `);
  });
});

server.listen(8080);
console.log('Server started. Your application is running at http://localhost:8080');

import Vue from 'vue';
import express from 'express';
import vueServerRenderer from 'vue-server-renderer';

const server = express();
const renderer = vueServerRenderer.createRenderer();

server.get('*', (req, res) => {
  const app = new Vue({
    data: {
      url: req.url,
    },
    template: '<div>The visited URL is: {{ url }}</div>',
  });

  renderer.renderToString(app, (err, html) => {
    if (err) {
      res.status(500).end('Internal Server Error');
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

export default function healthcheck(req, res) {
  res.setHeader('Content-Type', 'text/plain')
  res.end('OK')
}

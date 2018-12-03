const config = require('./config.json');
const express = require('express');
const https = require('https');
const path = require('path');

const app = express();
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

const www = path.join(__dirname, config.path);
app.use(express.static(www));

const apiRouter = express.Router();
// List available api
apiRouter.get('/', (req, res) => {
  console.log('api', apiRouter.stack);
  res.json({
    links: apiRouter.stack.filter(layer => layer.route).map(layer => layer.route.path)
      .filter(path => path.startsWith('/') && path.length > 1)
      .map(endpoint => path.join(req.originalUrl, endpoint))
  });
});

apiRouter.get('/topics', (req, res) => {
  const topics = [
    '#UMKC',
    'Chiefs',
    'Kansas City',
    'CS5590',
    '#Sports!!',
    'Finals Week',
    'Basketball',
    'Snow Day',
    '#ForkKnife',
    '#Fortnite'
  ];
  const words = topics.map(topic => ({
    text: topic,
    value: 10 + Math.random() * 90,
    sentiment: 1 - Math.random() * 2
  }));
  res.send(words);
});

apiRouter.get('/weather', (req, res) => {
  const {apiKey, cityId} = config.openWeatherMap;
  const url = `https://api.openweathermap.org/data/2.5/weather?id=${cityId}&APPID=${apiKey}`;
  https.get(url, (resp) => {
    let body = '';
    resp.on('data', data => body += data);
    resp.on('end', () => res.json(JSON.parse(body)));
  }).on("error", err => res.status(500).json(err));
});

apiRouter.use('*', (req, res) => {
  res.status(404)
    .json({status: 404, title: 'Not Found', description: `No resource at specified url '${req.originalUrl}'.`});
});

app.use('/api', apiRouter);

app.get('*', (req, res) => {
  res.sendFile(path.join(www, 'index.html'));
});

const port = process.env.PORT || config.port;
app.listen(port, () => console.info("Listening on port", port));

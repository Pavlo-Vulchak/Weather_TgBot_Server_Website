const express = require('express');
const mqtt = require('mqtt');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');
const exphbs = require('express-handlebars');
// Завантажуємо змінні середовища з файлу .env
require('dotenv').config();


// Отримуємо змінні з середовища
const mqtt_username = process.env.WEATHER_MQTT_USERNAME;
const mqtt_password = process.env.WEATHER_MQTT_PASSWORD;
const mqtt_address_port = process.env.WEATHER_MQTT_BROKER_URL_PORT;

const app = express();
const port = 80;

// Setup HTTP server
const server = http.createServer(app);

// Setup WebSocket server
const wss = new WebSocket.Server({ server });

// Setup MQTT client
const client = mqtt.connect(mqtt_address_port, {
  username: mqtt_username,
  password: mqtt_password
});

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Setup Handlebars as the view engine
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

// Initialize variable to store MQTT message data
let mqttData = 'No data yet';

// Define a middleware function for rendering the index page
const renderIndex = (res) => {
  res.render('index', { data: mqttData });
};

// Define a route to render the index page
app.get('/', (req, res) => {
  renderIndex(res);
});

// WebSocket connection handling
wss.on('connection', (socket) => {
  console.log('WebSocket connected');

  // Send MQTT data to the connected WebSocket client
  socket.send(JSON.stringify(mqttData));
});

// Listen to MQTT messages
client.on('connect', () => {
  console.log('Connected to MQTT server');
  client.subscribe('measurements/WeatherWebSite');

  // Handle incoming MQTT messages
  client.on('message', (topic, message) => {
    // Update the variable with MQTT message data
    mqttData = JSON.parse(message.toString());
    console.log('Received message:', message.toString());

    // Broadcast the updated data to all WebSocket clients
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(mqttData));
      }
    });
  });
});

// Start the server
server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

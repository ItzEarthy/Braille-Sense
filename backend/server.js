const express = require('express');
const app = express();
const port = process.env.PORT || 5000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Backend' });
});

// bind explicitly to 0.0.0.0 so the service is reachable from other hosts/containers
app.listen(port, '0.0.0.0', () => {
  console.log(`Backend listening on port ${port}`);
});

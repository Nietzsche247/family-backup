---
name: comms-hub-bridge-send
description: "Send messages via Comms Hub bridge API. Cross-agent messages, Signal Fire entries, bridge notifications."
---

# Comms Hub Bridge Send

## Endpoints
- **Bridge message:** `POST http://localhost:3001/api/bridge/message` → `{to, from, body}`
- **Signal Fire:** `POST http://localhost:3001/api/signal-fire` → `{agent, entry}`
- **Status:** `GET http://localhost:3001/api/status`

## CRITICAL: Use Node.js for POST
PowerShell mangles JSON. Write a temp JS file:
```javascript
const http = require('http');
const data = JSON.stringify({to:'thales', from:'aristotle', body:'message'});
const req = http.request({hostname:'127.0.0.1', port:3001, path:'/api/bridge/message', method:'POST', headers:{'Content-Type':'application/json','Content-Length':Buffer.byteLength(data)}}, res=>{let b='';res.on('data',c=>b+=c);res.on('end',()=>console.log(res.statusCode,b))});
req.write(data); req.end();
```
Then: `node C:\temp\send-msg.js`

## Payload Differences
- `/api/bridge/message`: `{to, from, body}` — wrong fields = 400
- `/api/signal-fire`: `{agent, entry}` — wrong fields = 400

## Simple GET (curl fine)
`curl.exe http://localhost:3001/api/status`

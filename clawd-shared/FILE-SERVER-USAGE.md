# Shared File Server — Usage Guide

**Base URL:** `https://hub.stigmergy.space`  
**Local URL:** `http://localhost:3001`  
**Auth header:** `Authorization: Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27`

All `/files/*` endpoints require the auth header. Requests without it return `401`.

---

## Browse / Read Files

### Directory listing (HTML, browsable)
```bash
curl -H "Authorization: Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27" \
  "https://hub.stigmergy.space/files/"
```

### Fetch a specific file
```bash
curl -H "Authorization: Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27" \
  "https://hub.stigmergy.space/files/governed-objects/DEF-TB-001-FIX-BRIEF.md"
```

### From PowerShell
```powershell
$h = @{ Authorization = 'Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27' }
Invoke-WebRequest -Uri 'https://hub.stigmergy.space/files/governed-objects/DEF-TB-001-FIX-BRIEF.md' -Headers $h -UseBasicParsing
```

---

## Upload / Write Files

**Endpoint:** `POST /files/upload`  
**Form fields:**
- `file` — the file binary (multipart)
- `path` — relative destination path under `C:\Users\aaron\clawd-shared\`
  - Example: `governed-objects/notes/update.md`
  - If path ends with `/`, the server appends the uploaded filename automatically.

### Upload with curl
```bash
curl -X POST \
  -H "Authorization: Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27" \
  -F "file=@./my-report.md" \
  -F "path=reports/my-report.md" \
  "https://hub.stigmergy.space/files/upload"
```

### Upload from PowerShell (write text file)
```powershell
$content = [System.Text.Encoding]::ASCII.GetBytes("file content here")
$boundary = "----FormBoundary$(New-Guid)"
$body = "--$boundary`r`n" +
        "Content-Disposition: form-data; name=`"path`"`r`n`r`n" +
        "reports/output.md`r`n" +
        "--$boundary`r`n" +
        "Content-Disposition: form-data; name=`"file`"; filename=`"output.md`"`r`n" +
        "Content-Type: text/plain`r`n`r`n" +
        "file content here`r`n" +
        "--$boundary--`r`n"
$bodyBytes = [System.Text.Encoding]::ASCII.GetBytes($body)
Invoke-WebRequest -Uri 'https://hub.stigmergy.space/files/upload' `
  -Method POST `
  -Headers @{ Authorization = 'Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27' } `
  -ContentType "multipart/form-data; boundary=$boundary" `
  -Body $bodyBytes -UseBasicParsing
```

---

## Security Notes
- Path traversal (`../`, `%2e%2e`, etc.) → **400 Bad Request**
- No auth header → **401 Unauthorized**
- Paths outside `C:\Users\aaron\clawd-shared\` are rejected
- **No delete endpoint** — read and upload only
- Max file size: **50 MB**

---

## Files Root
`C:\Users\aaron\clawd-shared\` on AlienWare2025

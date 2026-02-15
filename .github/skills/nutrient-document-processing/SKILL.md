---
name: nutrient-document-processing
description: |
  Nutrient Document Web Services (DWS) REST API for document processing. Convert between formats (DOCX/XLSX/PPTX ↔ PDF ↔ images), extract text/tables/key-value pairs, apply OCR to scanned documents, redact sensitive information with pattern matching or AI, add digital signatures and watermarks, and fill PDF forms. Language-agnostic REST API. Triggers: "convert to PDF", "PDF to Word", "extract text from PDF", "OCR", "redact PII", "redact SSN", "watermark PDF", "sign PDF", "document processing", "Nutrient".
---

# Nutrient Document Web Services (DWS) API

Full PDF lifecycle processing: convert, extract, OCR, redact, sign, and watermark documents via REST API.

## API Endpoint

```
https://api.nutrient.io
```

## Environment Variables

```bash
NUTRIENT_API_KEY=<your-api-key>
```

Get an API key at [nutrient.io/api](https://www.nutrient.io/api/)

## Authentication

All requests use Bearer token authentication:

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{ ... }' \
  -F document=@input.pdf \
  -o output.pdf
```

## API Structure

The API uses a single `/build` endpoint with an `instructions` JSON payload. The `parts` array defines the processing pipeline.

```json
{
  "parts": [
    {
      "file": "document"
    }
  ],
  "actions": [
    {
      "type": "<action-type>",
      ...action-specific-options
    }
  ]
}
```

## Core Workflows

### 1. Convert DOCX/XLSX/PPTX to PDF

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{ "parts": [{ "file": "document" }] }' \
  -F document=@report.docx \
  -o report.pdf
```

### 2. Convert PDF to Images (PNG/JPEG/WebP)

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{
      "type": "renderPages",
      "outputFormat": { "type": "png", "dpi": 150 },
      "pages": { "start": 0, "end": 0 }
    }]
  }' \
  -F document=@input.pdf \
  -o page.png
```

### 3. Convert PDF to Office (DOCX/XLSX/PPTX)

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{ "type": "office", "format": "docx" }]
  }' \
  -F document=@input.pdf \
  -o output.docx
```

### 4. Extract Text

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{ "type": "text", "outputFormat": "plain" }]
  }' \
  -F document=@input.pdf \
  -o extracted.txt
```

### 5. Extract Tables

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{ "type": "tables" }]
  }' \
  -F document=@input.pdf \
  -o tables.json
```

### 6. OCR Scanned Documents

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{
      "type": "ocr",
      "language": "english"
    }]
  }' \
  -F document=@scanned.pdf \
  -o searchable.pdf
```

### 7. Redact with Pattern Matching

Preset patterns: `credit-card-number`, `date`, `email-address`, `international-phone-number`, `ipv4`, `ipv6`, `mac-address`, `north-american-phone-number`, `social-security-number`, `time`, `url`, `us-zip-code`, `vin`.

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{
      "type": "redact",
      "strategy": "preset",
      "preset": "social-security-number"
    }]
  }' \
  -F document=@input.pdf \
  -o redacted.pdf
```

**Custom regex redaction:**

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{
      "type": "redact",
      "strategy": "regex",
      "regex": "\\b[A-Z]{2}\\d{6}\\b"
    }]
  }' \
  -F document=@input.pdf \
  -o redacted.pdf
```

### 8. AI-Powered Redaction

Natural language criteria for detecting and redacting sensitive information:

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{
      "type": "aiRedact",
      "criteria": "All personally identifiable information"
    }]
  }' \
  -F document=@input.pdf \
  -o redacted.pdf
```

### 9. Add Watermark

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{
      "type": "watermark",
      "watermarkType": "text",
      "text": "CONFIDENTIAL",
      "fontSize": 48,
      "fontColor": "#FF0000",
      "opacity": 0.3,
      "rotation": 45,
      "width": "50%",
      "height": "50%"
    }]
  }' \
  -F document=@input.pdf \
  -o watermarked.pdf
```

### 10. Digital Signature

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F instructions='{
    "parts": [{ "file": "document" }],
    "actions": [{
      "type": "sign",
      "signatureType": "cms",
      "signerName": "Jane Smith",
      "reason": "Document approval",
      "location": "New York"
    }]
  }' \
  -F document=@contract.pdf \
  -o signed.pdf
```

## Action Types Reference

| Action | Description |
|--------|-------------|
| `renderPages` | Convert PDF pages to PNG, JPEG, or WebP images |
| `office` | Convert PDF to DOCX, XLSX, or PPTX |
| `text` | Extract plain text from documents |
| `tables` | Extract tabular data as JSON |
| `keyValues` | Extract key-value pairs (phone numbers, emails, dates) |
| `ocr` | Apply OCR to scanned PDFs or images |
| `redact` | Redact content via preset patterns, regex, or exact text |
| `aiRedact` | AI-powered PII detection and redaction |
| `watermark` | Add text or image watermarks |
| `sign` | Add CMS or CAdES digital signatures |
| `flatten` | Flatten annotations and form fields |

## Supported Input Formats

| Format | Extensions |
|--------|------------|
| PDF | `.pdf` |
| Microsoft Office | `.docx`, `.xlsx`, `.pptx` |
| Images | `.jpg`, `.png`, `.gif`, `.webp`, `.tiff` |
| HTML | `.html` |

## MCP Server Integration

Nutrient provides an MCP server for direct agent integration:

```json
{
  "mcpServers": {
    "nutrient": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/nutrient-mcp-server"],
      "env": {
        "NUTRIENT_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

## Best Practices

1. **Chain actions** — Multiple actions execute sequentially in one request (e.g., OCR then redact)
2. **Use preset redaction patterns** for standard PII types — more reliable than regex for known formats
3. **Use AI redaction** for complex or context-dependent PII that presets can't cover
4. **Set DPI appropriately** — 150 DPI for screen, 300 DPI for print when rendering pages
5. **Check credit usage** — Each API call consumes credits based on document size and action type

## Reference Links

| Resource | URL |
|----------|-----|
| API Documentation | https://www.nutrient.io/guides/document-engine/api/api-reference/ |
| Getting Started | https://www.nutrient.io/getting-started/web-services/ |
| npm MCP Server | https://www.npmjs.com/package/@anthropic-ai/nutrient-mcp-server |
| OpenClaw Plugin | https://www.npmjs.com/package/@nutrient-sdk/nutrient-openclaw |
| GitHub | https://github.com/nicegoodthings/nutrient-dws-examples |

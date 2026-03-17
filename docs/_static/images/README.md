<!--
   Copyright 2026 IBM Corporation

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->
# Static Images

This directory contains static images for the documentation.

## Required Files

### Logo
- **ibm_data_intelligence_logo.svg** - Main logo displayed in the documentation header
  - Recommended size: 200x50 pixels
  - Format: SVG (vector) for best quality at all sizes
  - Should contain IBM branding elements

### Favicon
- **favicon.ico** - Browser tab icon
  - Size: 16x16, 32x32, 48x48 pixels (multi-resolution ICO file)
  - Should be recognizable at small sizes

## Adding Images

1. Create or obtain the IBM watsonx.data intelligence SDK logo in SVG format
2. Create a favicon.ico file with appropriate sizes
3. Place both files in this directory
4. The documentation build will automatically use them

## Temporary Placeholders

Until official branding assets are available, you can:

1. Use a simple text-based SVG logo
2. Generate a basic favicon from the logo
3. Replace with official assets when available

## Creating Placeholder Logo (SVG)

Create `ibm_data_intelligence_logo.svg` with content like:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50" viewBox="0 0 200 50">
  <rect width="200" height="50" fill="#0f62fe"/>
  <text x="10" y="32" font-family="Arial, sans-serif" font-size="18" fill="white" font-weight="bold">
    IBM watsonx.data intelligence SDK
  </text>
</svg>
```

## Creating Placeholder Favicon

You can use online tools to convert the logo to a favicon:
- https://favicon.io/
- https://realfavicongenerator.net/

Or use ImageMagick:
```bash
convert ibm_data_intelligence_logo.svg -resize 32x32 favicon.ico
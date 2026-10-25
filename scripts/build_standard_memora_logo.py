import os
import subprocess
import time
from PIL import Image

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# 1. Pure Vector Transparent Emblem (viewBox 0 0 256 256)
EMBLEM_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="100%" height="100%" fill="none">
  <defs>
    <!-- Back Card Gradient: Deep Navy & Slate -->
    <linearGradient id="memora-card-back" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4B6382"/>
      <stop offset="45%" stop-color="#122D5C"/>
      <stop offset="100%" stop-color="#071739"/>
    </linearGradient>

    <!-- Front Card Gradient: Frosted Glass with Warm Sandstone Tint -->
    <linearGradient id="memora-card-front" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="30%" stop-color="#F7F5EE" stop-opacity="0.90"/>
      <stop offset="70%" stop-color="#E3C39D" stop-opacity="0.80"/>
      <stop offset="100%" stop-color="#A68868" stop-opacity="0.85"/>
    </linearGradient>

    <!-- Golden Orbital Arc Gradient -->
    <linearGradient id="memora-orbit-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF5E6"/>
      <stop offset="30%" stop-color="#E3C39D"/>
      <stop offset="65%" stop-color="#A68868"/>
      <stop offset="100%" stop-color="#4B6382" stop-opacity="0.4"/>
    </linearGradient>

    <!-- Subtle Ambient Dropshadows -->
    <filter id="memora-shadow-back" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-2" dy="8" stdDeviation="8" flood-color="#071739" flood-opacity="0.30"/>
    </filter>
    <filter id="memora-shadow-front" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-1" dy="6" stdDeviation="7" flood-color="#071739" flood-opacity="0.25"/>
    </filter>
    <filter id="memora-star-glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.5" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Orbital Ring: Back Arc (behind the cards) -->
  <path d="M 46,130 C 32,102 58,70 106,52 C 148,36 198,40 220,62 C 226,68 227,74 223,81" 
        stroke="url(#memora-orbit-grad)" 
        stroke-width="3" 
        stroke-linecap="round" 
        opacity="0.55"/>

  <!-- Back Card: Deep Slate Vault Card (Tilted Left) -->
  <g transform="translate(142, 126) rotate(-14) translate(-48, -66)" filter="url(#memora-shadow-back)">
    <rect x="0" y="0" width="84" height="118" rx="18" fill="url(#memora-card-back)"/>
    <rect x="0.75" y="0.75" width="82.5" height="116.5" rx="17.25" stroke="#A4B5C4" stroke-width="1.5" stroke-opacity="0.5"/>
    <!-- Minimalist Data Accent Lines -->
    <rect x="14" y="24" width="34" height="5" rx="2.5" fill="#A4B5C4" opacity="0.65"/>
    <rect x="14" y="37" width="56" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
    <rect x="14" y="47" width="44" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
  </g>

  <!-- Front Card: Frosted Warm Glassmorphic Card (Tilted Right) -->
  <g transform="translate(108, 140) rotate(11) translate(-48, -66)" filter="url(#memora-shadow-front)">
    <rect x="0" y="0" width="86" height="120" rx="18" fill="url(#memora-card-front)"/>
    <rect x="0.75" y="0.75" width="84.5" height="118.5" rx="17.25" stroke="#FFFFFF" stroke-width="1.75" stroke-opacity="0.9"/>
    <!-- Chip / Icon -->
    <rect x="14" y="20" width="22" height="22" rx="7" fill="#071739" fill-opacity="0.20"/>
    <circle cx="25" cy="31" r="5" fill="#071739" fill-opacity="0.6"/>
    <!-- Knowledge Structure Lines -->
    <rect x="14" y="52" width="58" height="4.5" rx="2.25" fill="#071739" fill-opacity="0.55"/>
    <rect x="14" y="63" width="46" height="3.5" rx="1.75" fill="#071739" fill-opacity="0.35"/>
    <rect x="14" y="73" width="36" height="3.5" rx="1.75" fill="#071739" fill-opacity="0.25"/>
  </g>

  <!-- Orbital Ring: Front Sweeping Arc (in front of cards) -->
  <path d="M 44,134 C 54,166 98,194 150,188 C 182,184 206,170 216,150 C 223,136 218,118 202,102" 
        stroke="url(#memora-orbit-grad)" 
        stroke-width="3.5" 
        stroke-linecap="round"
        filter="url(#memora-star-glow)"/>

  <!-- Orbital Sphere / Pearl Node -->
  <circle cx="202" cy="104" r="7" fill="#E3C39D" filter="url(#memora-star-glow)"/>
  <circle cx="200" cy="102" r="2.5" fill="#FFFFFF"/>

  <!-- Brilliant 4-Point Radiant Intelligence Star (Memory Spark) -->
  <g transform="translate(196, 46)" filter="url(#memora-star-glow)">
    <path d="M 0,-18 Q 0,0 18,0 Q 0,0 0,18 Q 0,0 -18,0 Q 0,0 0,-18 Z" fill="#FFFFFF"/>
    <path d="M 0,-12 Q 0,0 12,0 Q 0,0 0,12 Q 0,0 -12,0 Q 0,0 0,-12 Z" fill="#E3C39D"/>
    <circle cx="0" cy="0" r="3" fill="#FFFFFF"/>
  </g>
</svg>
'''

# 2. App Icon with Squircle Background (for PWA, Desktop Shortcut, Favicon)
APP_ICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="100%" height="100%" fill="none">
  <defs>
    <!-- Dark Deep Midnight Background with Subtle Indigo Depth -->
    <linearGradient id="app-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0E244B"/>
      <stop offset="50%" stop-color="#071739"/>
      <stop offset="100%" stop-color="#040D21"/>
    </linearGradient>

    <!-- Radial Glow behind the emblem -->
    <radialGradient id="app-glow" cx="50%" cy="48%" r="48%">
      <stop offset="0%" stop-color="#4B6382" stop-opacity="0.35"/>
      <stop offset="60%" stop-color="#122D5C" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#071739" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="memora-card-back" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4B6382"/>
      <stop offset="45%" stop-color="#122D5C"/>
      <stop offset="100%" stop-color="#071739"/>
    </linearGradient>

    <linearGradient id="memora-card-front" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="30%" stop-color="#F7F5EE" stop-opacity="0.90"/>
      <stop offset="70%" stop-color="#E3C39D" stop-opacity="0.80"/>
      <stop offset="100%" stop-color="#A68868" stop-opacity="0.85"/>
    </linearGradient>

    <linearGradient id="memora-orbit-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF5E6"/>
      <stop offset="30%" stop-color="#E3C39D"/>
      <stop offset="65%" stop-color="#A68868"/>
      <stop offset="100%" stop-color="#4B6382" stop-opacity="0.4"/>
    </linearGradient>

    <filter id="memora-shadow-back" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-2" dy="8" stdDeviation="8" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
    <filter id="memora-shadow-front" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-1" dy="6" stdDeviation="7" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
    <filter id="memora-star-glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.5" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Squircle Base -->
  <rect x="0" y="0" width="256" height="256" rx="58" fill="url(#app-bg)"/>
  <rect x="1" y="1" width="254" height="254" rx="57" stroke="#244983" stroke-width="2" stroke-opacity="0.5"/>
  <circle cx="128" cy="128" r="110" fill="url(#app-glow)"/>

  <!-- Orbital Ring: Back Arc -->
  <path d="M 46,130 C 32,102 58,70 106,52 C 148,36 198,40 220,62 C 226,68 227,74 223,81" 
        stroke="url(#memora-orbit-grad)" 
        stroke-width="3" 
        stroke-linecap="round" 
        opacity="0.6"/>

  <!-- Back Card -->
  <g transform="translate(142, 126) rotate(-14) translate(-48, -66)" filter="url(#memora-shadow-back)">
    <rect x="0" y="0" width="84" height="118" rx="18" fill="url(#memora-card-back)"/>
    <rect x="0.75" y="0.75" width="82.5" height="116.5" rx="17.25" stroke="#A4B5C4" stroke-width="1.5" stroke-opacity="0.5"/>
    <rect x="14" y="24" width="34" height="5" rx="2.5" fill="#A4B5C4" opacity="0.65"/>
    <rect x="14" y="37" width="56" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
    <rect x="14" y="47" width="44" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
  </g>

  <!-- Front Card -->
  <g transform="translate(108, 140) rotate(11) translate(-48, -66)" filter="url(#memora-shadow-front)">
    <rect x="0" y="0" width="86" height="120" rx="18" fill="url(#memora-card-front)"/>
    <rect x="0.75" y="0.75" width="84.5" height="118.5" rx="17.25" stroke="#FFFFFF" stroke-width="1.75" stroke-opacity="0.9"/>
    <rect x="14" y="20" width="22" height="22" rx="7" fill="#071739" fill-opacity="0.20"/>
    <circle cx="25" cy="31" r="5" fill="#071739" fill-opacity="0.6"/>
    <rect x="14" y="52" width="58" height="4.5" rx="2.25" fill="#071739" fill-opacity="0.55"/>
    <rect x="14" y="63" width="46" height="3.5" rx="1.75" fill="#071739" fill-opacity="0.35"/>
    <rect x="14" y="73" width="36" height="3.5" rx="1.75" fill="#071739" fill-opacity="0.25"/>
  </g>

  <!-- Orbital Ring: Front Sweeping Arc -->
  <path d="M 44,134 C 54,166 98,194 150,188 C 182,184 206,170 216,150 C 223,136 218,118 202,102" 
        stroke="url(#memora-orbit-grad)" 
        stroke-width="3.5" 
        stroke-linecap="round"
        filter="url(#memora-star-glow)"/>

  <!-- Orbital Sphere -->
  <circle cx="202" cy="104" r="7" fill="#E3C39D" filter="url(#memora-star-glow)"/>
  <circle cx="200" cy="102" r="2.5" fill="#FFFFFF"/>

  <!-- Star -->
  <g transform="translate(196, 46)" filter="url(#memora-star-glow)">
    <path d="M 0,-18 Q 0,0 18,0 Q 0,0 0,18 Q 0,0 -18,0 Q 0,0 0,-18 Z" fill="#FFFFFF"/>
    <path d="M 0,-12 Q 0,0 12,0 Q 0,0 0,12 Q 0,0 -12,0 Q 0,0 0,-12 Z" fill="#E3C39D"/>
    <circle cx="0" cy="0" r="3" fill="#FFFFFF"/>
  </g>
</svg>
'''

# 3. Full Brand Lockup (Banner)
FULL_BRAND_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 180" width="100%" height="100%" fill="none">
  <defs>
    <linearGradient id="memora-card-back" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4B6382"/>
      <stop offset="45%" stop-color="#122D5C"/>
      <stop offset="100%" stop-color="#071739"/>
    </linearGradient>

    <linearGradient id="memora-card-front" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="30%" stop-color="#F7F5EE" stop-opacity="0.90"/>
      <stop offset="70%" stop-color="#E3C39D" stop-opacity="0.80"/>
      <stop offset="100%" stop-color="#A68868" stop-opacity="0.85"/>
    </linearGradient>

    <linearGradient id="memora-orbit-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF5E6"/>
      <stop offset="30%" stop-color="#E3C39D"/>
      <stop offset="65%" stop-color="#A68868"/>
      <stop offset="100%" stop-color="#4B6382" stop-opacity="0.4"/>
    </linearGradient>

    <linearGradient id="wordmark-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#071739"/>
      <stop offset="55%" stop-color="#193B74"/>
      <stop offset="100%" stop-color="#4B6382"/>
    </linearGradient>

    <filter id="memora-shadow-back" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-2" dy="6" stdDeviation="6" flood-color="#071739" flood-opacity="0.25"/>
    </filter>
    <filter id="memora-shadow-front" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="-1" dy="5" stdDeviation="5" flood-color="#071739" flood-opacity="0.2"/>
    </filter>
  </defs>

  <!-- Left: Emblem Scaled to 140x140 at (20, 20) -->
  <g transform="translate(10, 10) scale(0.625)">
    <!-- Back Arc -->
    <path d="M 46,130 C 32,102 58,70 106,52 C 148,36 198,40 220,62 C 226,68 227,74 223,81" 
          stroke="url(#memora-orbit-grad)" stroke-width="3" stroke-linecap="round" opacity="0.55"/>

    <!-- Back Card -->
    <g transform="translate(142, 126) rotate(-14) translate(-48, -66)" filter="url(#memora-shadow-back)">
      <rect x="0" y="0" width="84" height="118" rx="18" fill="url(#memora-card-back)"/>
      <rect x="0.75" y="0.75" width="82.5" height="116.5" rx="17.25" stroke="#A4B5C4" stroke-width="1.5" stroke-opacity="0.5"/>
      <rect x="14" y="24" width="34" height="5" rx="2.5" fill="#A4B5C4" opacity="0.65"/>
      <rect x="14" y="37" width="56" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
      <rect x="14" y="47" width="44" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
    </g>

    <!-- Front Card -->
    <g transform="translate(108, 140) rotate(11) translate(-48, -66)" filter="url(#memora-shadow-front)">
      <rect x="0" y="0" width="86" height="120" rx="18" fill="url(#memora-card-front)"/>
      <rect x="0.75" y="0.75" width="84.5" height="118.5" rx="17.25" stroke="#FFFFFF" stroke-width="1.75" stroke-opacity="0.9"/>
      <rect x="14" y="20" width="22" height="22" rx="7" fill="#071739" fill-opacity="0.20"/>
      <circle cx="25" cy="31" r="5" fill="#071739" fill-opacity="0.6"/>
      <rect x="14" y="52" width="58" height="4.5" rx="2.25" fill="#071739" fill-opacity="0.55"/>
      <rect x="14" y="63" width="46" height="3.5" rx="1.75" fill="#071739" fill-opacity="0.35"/>
      <rect x="14" y="73" width="36" height="3.5" rx="1.75" fill="#071739" fill-opacity="0.25"/>
    </g>

    <!-- Front Sweeping Arc -->
    <path d="M 44,134 C 54,166 98,194 150,188 C 182,184 206,170 216,150 C 223,136 218,118 202,102" 
          stroke="url(#memora-orbit-grad)" stroke-width="3.5" stroke-linecap="round"/>

    <circle cx="202" cy="104" r="7" fill="#E3C39D"/>
    <circle cx="200" cy="102" r="2.5" fill="#FFFFFF"/>

    <!-- Star -->
    <g transform="translate(196, 46)">
      <path d="M 0,-18 Q 0,0 18,0 Q 0,0 0,18 Q 0,0 -18,0 Q 0,0 0,-18 Z" fill="#FFFFFF"/>
      <path d="M 0,-12 Q 0,0 12,0 Q 0,0 0,12 Q 0,0 -12,0 Q 0,0 0,-12 Z" fill="#E3C39D"/>
      <circle cx="0" cy="0" r="3" fill="#FFFFFF"/>
    </g>
  </g>

  <!-- Right: Pristine Typography Lockup -->
  <g transform="translate(190, 0)">
    <text x="0" y="98" 
          font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif" 
          font-size="62" 
          font-weight="800" 
          letter-spacing="0.14em" 
          fill="url(#wordmark-grad)">MEMORA</text>
    
    <text x="3" y="130" 
          font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif" 
          font-size="14.5" 
          font-weight="700" 
          letter-spacing="0.26em" 
          fill="#A68868">SAVE ANYTHING. FIND IT ANYTIME.</text>
  </g>
</svg>
'''

# Write SVGs
os.makedirs('public', exist_ok=True)
os.makedirs('src/assets', exist_ok=True)

with open('public/memora-emblem.svg', 'w', encoding='utf-8') as f:
    f.write(EMBLEM_SVG)
with open('public/memora-app-icon.svg', 'w', encoding='utf-8') as f:
    f.write(APP_ICON_SVG)
with open('public/memora-full.svg', 'w', encoding='utf-8') as f:
    f.write(FULL_BRAND_SVG)
with open('public/favicon.svg', 'w', encoding='utf-8') as f:
    f.write(APP_ICON_SVG)
with open('public/icon-192.svg', 'w', encoding='utf-8') as f:
    f.write(APP_ICON_SVG)
with open('public/icon-512.svg', 'w', encoding='utf-8') as f:
    f.write(APP_ICON_SVG)

print("Saved vector SVG assets.")

# Function to render SVG to PNG using Headless Edge
def render_svg_to_png(svg_path, output_png_path, width, height, transparent=True):
    abs_svg = os.path.abspath(svg_path).replace('\\', '/')
    abs_png = os.path.abspath(output_png_path)
    
    bg_style = "background: transparent;" if transparent else "background: #071739;"
    html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    {bg_style}
  }}
  img {{
    width: {width}px;
    height: {height}px;
    display: block;
  }}
</style>
</head>
<body>
  <img src="file:///{abs_svg}" />
</body>
</html>'''

    temp_html = os.path.abspath(f"temp_render_{width}x{height}.html")
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={abs_png}",
        f"file:///{temp_html.replace(chr(92), '/')}"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(temp_html):
        os.remove(temp_html)
    print(f"Rendered {output_png_path} ({width}x{height})")

# Render standard suite of PNGs
render_svg_to_png('public/memora-emblem.svg', 'public/memora-emblem-transparent.png', 512, 512, transparent=True)
render_svg_to_png('public/memora-app-icon.svg', 'public/memora-emblem.png', 512, 512, transparent=False)
render_svg_to_png('public/memora-app-icon.svg', 'public/icon-512.png', 512, 512, transparent=False)
render_svg_to_png('public/memora-app-icon.svg', 'public/icon-192.png', 192, 192, transparent=False)
render_svg_to_png('public/memora-full.svg', 'public/memora-full.png', 1020, 270, transparent=True)

# Generate favicons from 512 icon
im = Image.open('public/icon-512.png')
im.resize((64, 64), Image.Resampling.LANCZOS).save('public/favicon-64.png')
im.resize((32, 32), Image.Resampling.LANCZOS).save('public/favicon.png')

# Copy to src/assets
for name in ['memora-emblem-transparent.png', 'memora-emblem.png', 'memora-full.png']:
    src_file = os.path.join('public', name)
    dst_file = os.path.join('src/assets', name)
    with open(src_file, 'rb') as f_in, open(dst_file, 'wb') as f_out:
        f_out.write(f_in.read())

print("All standard Memora logo assets generated successfully!")

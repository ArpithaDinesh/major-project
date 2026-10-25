with open('src/index.css', 'r', encoding='utf-8') as f:
    css = f.read()

dark_extensions = """
  /* Selects & Options */
  html.light select,
  html:not(.dark) select {
    background-color: #FFFFFF !important;
    border: 1px solid #CDD5DB !important;
    color: #071739 !important;
    font-weight: 500 !important;
  }
  html.light select option,
  html:not(.dark) select option {
    background-color: #FFFFFF !important;
    color: #071739 !important;
  }
  html.dark select {
    background-color: #091F4A !important;
    border-color: #244983 !important;
    color: #FFFFFF !important;
  }
  html.dark select option {
    background-color: #0E244B !important;
    color: #FFFFFF !important;
  }

  /* Date / Datetime inputs picker indicator */
  html.light input[type="datetime-local"]::-webkit-calendar-picker-indicator,
  html:not(.dark) input[type="datetime-local"]::-webkit-calendar-picker-indicator,
  html.light input[type="date"]::-webkit-calendar-picker-indicator,
  html:not(.dark) input[type="date"]::-webkit-calendar-picker-indicator {
    filter: invert(8%) sepia(20%) saturate(4000%) hue-rotate(185deg) brightness(30%);
    cursor: pointer;
  }
  html.dark input[type="datetime-local"]::-webkit-calendar-picker-indicator,
  html.dark input[type="date"]::-webkit-calendar-picker-indicator {
    filter: invert(100%);
    cursor: pointer;
  }

  /* Dark theme text-palette mapping */
  html.dark .text-palette-navy {
    color: #FFFFFF !important;
  }
  html.dark .text-palette-slate {
    color: #CDD5DB !important;
  }
  html.dark .text-palette-mist {
    color: #A4B5C4 !important;
  }
  html.dark .text-palette-pale {
    color: #CDD5DB !important;
  }
  html.dark .border-palette-border,
  html.dark .border-palette-pale {
    border-color: #244983 !important;
  }
  html.dark .bg-palette-cream {
    background-color: #091F4A !important;
  }
  html.dark .bg-palette-surface {
    background-color: #0E244B !important;
  }

  /* Icon high-contrast rules */
  html.dark svg.text-palette-slate {
    color: #A4B5C4 !important;
  }
  html.dark svg.text-palette-navy {
    color: #FFFFFF !important;
  }
  html.dark svg.text-app-muted {
    color: #CDD5DB !important;
  }
  html.dark svg.text-app-subtle {
    color: #A4B5C4 !important;
  }

  /* Light theme card heading contrast */
  html.light .bg-white h1,
  html.light .bg-white h2,
  html.light .bg-white h3,
  html.light .bg-white h4,
  html.light .bg-dark-card h1,
  html.light .bg-dark-card h2,
  html.light .bg-dark-card h3,
  html.light .bg-dark-card h4,
  html.light .glass-card h1,
  html.light .glass-card h2,
  html.light .glass-card h3,
  html.light .glass-card h4,
  html:not(.dark) .bg-white h1,
  html:not(.dark) .bg-white h2,
  html:not(.dark) .bg-white h3,
  html:not(.dark) .bg-white h4,
  html:not(.dark) .bg-dark-card h1,
  html:not(.dark) .bg-dark-card h2,
  html:not(.dark) .bg-dark-card h3,
  html:not(.dark) .bg-dark-card h4,
  html:not(.dark) .glass-card h1,
  html:not(.dark) .glass-card h2,
  html:not(.dark) .glass-card h3,
  html:not(.dark) .glass-card h4 {
    color: #071739;
  }
"""

if "/* Selects & Options */" not in css:
    # insert before the final closing brace of @layer utilities
    last_brace_index = css.rfind('}')
    if last_brace_index != -1:
        css = css[:last_brace_index] + dark_extensions + css[last_brace_index:]
        with open('src/index.css', 'w', encoding='utf-8') as f:
            f.write(css)
        print("Updated src/index.css with dark extensions.")
    else:
        print("Could not find closing brace in src/index.css")
else:
    print("src/index.css already contains select & option rules.")

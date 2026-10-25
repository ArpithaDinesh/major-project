with open('src/index.css', 'r', encoding='utf-8') as f:
    c = f.read()

bad_svg = """  /* Icon high-contrast rules */
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
  }"""

clean_svg = """  /* Icon high-contrast rules */
  html.dark .text-palette-slate > svg,
  html.dark svg[class*="text-palette-slate"] {
    color: #A4B5C4 !important;
  }
  html.dark .text-palette-navy > svg,
  html.dark svg[class*="text-palette-navy"] {
    color: #FFFFFF !important;
  }"""

c = c.replace(bad_svg.replace('\r\n', '\n'), clean_svg.replace('\r\n', '\n'))
c = c.replace(bad_svg.replace('\n', '\r\n'), clean_svg.replace('\n', '\r\n'))

with open('src/index.css', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.css svg selectors cleanly.')

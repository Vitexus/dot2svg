#!/usr/bin/python2.4
import subprocess
import optparse
import os
import re
import math

regfloat = r"[+-]?[0-9]*\.?[0-9]+(?:[Ee][+-]?[0-9]+)?"

def RemoveWhiteBackground(text):
  """Remove the empty white background that causes some issues with blur."""

  re_white = re.compile(r'<polygon style="fill:white;stroke:white;".*?>\s*')
  return re_white.sub('', text)

def FixFont(text):
  """ Replace font-size:14.0 with font-size:12px for example """
  
  re_fontsize = re.compile(r'font-size:([\d\.]+?);')
  args = re_fontsize.search(text)
  if not args:
    #raise "Didn't find font-size:..."
    return text
  fontsize = float(args.group(1)) - 2
  text = re_fontsize.sub(r'font-size:%dpx;' % (fontsize), text)
  return text

def IsClose(x1, x2, x3=None):
  if abs(x1 - x2) > 0.1:
    return False
  if x3 == None:
    return True
  if abs(x1 - x3) > 0.1:
    return False
  if abs(x2 - x3) > 0.1:
    return False
  return True


def StrToTuple(str_tuple):
  if type(str_tuple) == type(()):
    return str_tuple
  if not str_tuple:
    return None
  str_tuple = str_tuple.replace('(', '').replace(')', '')
  return tuple([float(x) for x in str_tuple.split(',')])


def PolygonToRect(text, rounded='(5, 5)'):
  """ Replace <polygon ... points="232,14 138,14 138,50 232,50 232,14"
  with <rect x="229" y="96" width="94" height="36"/>
  Add rx="5" ry="5" if desired for rounded corners.
  """
  rounded = StrToTuple(rounded)
  def RepFun(match):
    stuff = match.group(1)
    (x1, y1, x2, y2, x3, y3, x4, y4, x5, y5) = [round(float(x)) for x in match.groups()[1:]]
    xs = [x1, x2, x3, x4, x5]
    ys = [y1, y2, y3, y4, y5]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    x = min(xs)
    y = min(ys)
    
    # If it is not a rect, do nothing
    if (not IsClose(x1, x4, x5) or not IsClose(x2, x3) or 
        not IsClose(y1, y2, y5) or not IsClose(y3, y4)):
      ret = r'<polygon %s points="%s,%s %s,%s %s,%s %s,%s %s,%s"' % match.groups()[0:]
      return ret
    
    ret = '<rect %s x="%d" y="%d" width="%d" height="%d"' % \
    (stuff, x, y, w, h)
    if rounded != None:
      ret += ' rx="%d" ry="%d"' % (rounded[0], rounded[1])

    return ret
      
  re_polygon = re.compile(r'<polygon (.*?) points="' \
    '(%(rf)s),(%(rf)s) (%(rf)s),(%(rf)s) (%(rf)s),(%(rf)s) (%(rf)s),(%(rf)s) (%(rf)s),(%(rf)s)"' % {
	'rf' : regfloat})
  text= re_polygon.sub(RepFun, text)
  return text

def AddHeader(text):
  re_svg = re.compile(r'(<svg [^>]+>)', re.DOTALL)
  new_text = ('\n'
      '  <defs>\n'
      '    <filter\n'
      '      id="filterBlur">\n'
      '      <feGaussianBlur\n'
      '      stdDeviation="0.69"\n'
      '      id="feGaussianBlurBlur" />\n'
      '    </filter>\n'
      '  </defs>\n')
  text = re_svg.sub(r'\1' + new_text, text)
  return text

def AddShadows(text, shadow='(2, 2)'):
  """  Get something that looks like
    <ellipse|rect|polygon .*/>
    and prepend it with another the same (without a style), except translated 
    and fill with gray.
  """
  shadow = StrToTuple(shadow)
  if shadow == None:
    return text
  text = AddHeader(text)
  def RepFun(match):
    tagname, params = match.groups()
    clean_params = re.sub(r'style=".*?"', '', params)
    ret = ('<%s fill="#999999" stroke="#999999" stroke-width="1" '
           'transform="translate(%d, %d)" '
           'style="opacity:0.75;filter:url(#filterBlur)" '
           '%s/>\n') % (tagname, shadow[0], shadow[1], clean_params)
    ret += '<%s %s/>' % (tagname, params)
    return ret

  re_ellipse = re.compile(r'<(ellipse|rect|polygon) (.*?)/>')
  text = re_ellipse.sub(RepFun, text)
  return text

def AddArrowShadows(text, shadow='(2, 2)'):
  """ 
  Get something that looks like
  <path .*/>
  and prepend it with another the same (without a style), except translated
  and draw in gray.
  """
  shadow = StrToTuple(shadow)
  if shadow == None:
    return text
  
  def RepFun(match):
    (params,) = match.groups()
    m = re.match(r'style=".*?(stroke-dasharray:.*?);',params)
    if m:
      style = "style=\"%s\"" % (m.group(1))
    else:
      style = ""
    clean_params = re.sub(r'style=".*?"', '', params)
    ret = '<path fill="none" stroke="#999999" stroke-width="1" '\
        'transform="translate(%d, %d)" %s %s/>\n' % \
        (shadow[0], shadow[1], style, clean_params)
    ret += '<path %s/>' % (params)
    return ret

  re_ellipse = re.compile(r'<path (.*?)/>')
  text= re_ellipse.sub(RepFun, text)
  return text

def PreserveWhitespace(text):
  """ 
  Get something that looks like
  <text .*>
  and add xml:space='preserve' to it
  """
  
  def RepFun(match):
    (params,) = match.groups()
    ret = '<text %s xml:space=\"preserve\">' % (params)
    return ret

  re_ellipse = re.compile(r'<text (.*?)>')
  text= re_ellipse.sub(RepFun, text)
  return text

def CleanupOuput(text, shadow, rounded):
  """ Unfortunately the output made by graphiz isn't perfect, let's clean it up.
  """
  text = RemoveWhiteBackground(text)
  text = FixFont(text)
  text = PolygonToRect(text, rounded)
  text = AddShadows(text, shadow)
  text = AddArrowShadows(text)
  text = PreserveWhitespace(text)
  
  return text
  
def ConvertDot2Svg(filename, shadow, rounded):
  """ Given a DOT filename create an SVG file from it.
  
  Args:
    filename: Filename, must end in .dot, full path not required
  """
  if not filename.endswith('.dot'):
    raise "Filename must end with .dot (%s)" % (filename)
  
  dotCmd = subprocess.Popen(['dot',
    '-Tsvg', # Output as SVG
    filename], stdout=subprocess.PIPE)
  output = dotCmd.communicate()[0]
  svg_file = filename.replace('.dot', '.svg')
  output = CleanupOuput(output, shadow, rounded)
  open(svg_file, "w").write(output)
  return svg_file
  
def ConvertSvg2Png(filename):
  """ Given an SVG file, convert it to PNG using batik and java.
  """
  if not filename.endswith('.svg'):
    raise "Filename must end with .svg (%s)" % (filename)
  
  dotCmd = subprocess.Popen(['java', '-Xmx512m', '-jar',
    os.path.join(os.path.split(__file__)[0], 
                 'batik', 'batik-rasterizer.jar'),
    filename])
  output = dotCmd.communicate()[0]
  png_file = filename.replace('.svg', '.png')
  return png_file

def parse_command_line():
  import optparse
  
  parser = optparse.OptionParser()
  parser.add_option('-p', '--png', action='store_true', dest='png',
                    help='Create a png file as well')
  parser.add_option('-r', '--rounded', action='store', dest='rounded', 
                    default='(5, 5)')
  parser.add_option('-s', '--shadow', action='store', dest='shadow', 
                    default='(2, 2)')
  (options, args) = parser.parse_args()
  
  if len(args) == 0:
    import glob
    files = glob.glob('*.dot')
    for file in files:
      print "ConvertDot2Svg2Png %s" % (file)
      new_file = ConvertDot2Svg(file, options.shadow, options.rounded)
      if options.png:
        ConvertSvg2Png(new_file)
  else:
    for arg in args:
      print "ConvertDot2Svg2Png %s" % (arg)
      new_file = ConvertDot2Svg(arg, options.shadow, options.rounded)
      if options.png:
        ConvertSvg2Png(new_file)

if __name__ == '__main__':
  parse_command_line()

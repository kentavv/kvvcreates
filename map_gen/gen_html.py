#!/usr/bin/env python3


def g(fn, nm):
  f = open(fn)
  b = list(map(lambda x: x.strip(), f))
  a = '''<div id="''' + nm + '''" style="width: 1000px; height: 450px;"></div>
<div style="width: 1000px; font-size: 70%; padding: 5px 0; text-align: center; background-color: #535364; margin-top: 1px; color: #B4B4B7;"><a href="https://www.amcharts.com/visited_countries/" style="color: #B4B4B7;">Create your own visited countries map</a> or check out the <a href="https://www.amcharts.com/" style="color: #B4B4B7;">JavaScript Charts</a>.</div>
<script type="text/javascript">
var map''' + nm + ''' = AmCharts.makeChart("''' + nm + '''",{
type: "map",
theme: "dark",
projection: "eckert3",
panEventsEnabled : true,
backgroundColor : "#535364",
backgroundAlpha : 1,
zoomControl: {
zoomControlEnabled : true
},
dataProvider : {
map : "worldHigh",
getAreasFromMap : true,
areas :
[
'''

  def h(x):
    return '''{{
          "id": "{0:s}",
          "showAsSelected": true
      }}'''.format(x)
  a += ','.join(map(h, b))

  a += '''
]
},
areasSettings : {
autoZoom : true,
color : "#B4B4B7",
colorSolid : "#84ADE9",
selectedColor : "#84ADE9",
outlineColor : "#666666",
rollOverColor : "#9EC2F7",
rollOverOutlineColor : "#000000"
}
});
</script>'''
  return a


def main():
  channel = 'Kvv Creates'
  print('''<!DOCTYPE html>
<html>
<head>
<title>''' + channel + ''' Subscriber Countries Map</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="white">
<meta name="viewport" content="width=device-width, minimum-scale=1, initial-scale=1, user-scalable=yes, minimal-ui">
</head>
<body>
<script src="https://www.amcharts.com/lib/3/ammap.js" type="text/javascript"></script>
<script src="https://www.amcharts.com/lib/3/maps/js/worldHigh.js" type="text/javascript"></script>
<script src="https://www.amcharts.com/lib/3/themes/dark.js" type="text/javascript"></script>''')
  print('''<h2>''' + channel + ''' Subscribers</h2>''')
  print(g('subscribers', 'subs'))
  print('''<br><br>''')
  print('''<h2>''' + channel + ''' Viewers</h2>''')
  print(g('viewers', 'viewers'))
  print('</body></html>')

if __name__ == "__main__":
  main()

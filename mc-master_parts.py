#!/usr/bin/python

import subprocess
import sys

# 1. Copy cmd_base from the website and update cmd_base_pn with the part number used in cmd_base
# 2. Populate txt variable with desired part numbers and target filenames
#    Watchout for invalid filename characters
# 3. Execute
# 4. Don't abuse McMaster's service

cmd_base_pn = '93365A150'
cmd_base = "/usr/bin/curl 'http://www.mcmaster.com/mvA/library/20121029/93365A150.SLDPRT'"

txt = """
93365A102	ultrasert ii 0-80 short - 93365A102.SLDPRT
93365A110	ultrasert ii 2-56 short - 93365A110.SLDPRT
93365A112	ultrasert ii 2-56 long - 93365A112.SLDPRT
93365A120	ultrasert ii 4-40 short - 93365A120.SLDPRT
93365A122	ultrasert ii 4-40 long - 93365A122.SLDPRT
93365A130	ultrasert ii 6-32 short - 93365A130.SLDPRT
93365A132	ultrasert ii 6-32 long - 93365A132.SLDPRT
93365A140	ultrasert ii 8-32 short - 93365A140.SLDPRT
93365A142	ultrasert ii 8-32 long - 93365A142.SLDPRT
93365A150	ultrasert ii 10-24 short - 93365A150.SLDPRT
93365A152	ultrasert ii 10-24 long - 93365A152.SLDPRT
93365A154	ultrasert ii 10-32 short - 93365A154.SLDPRT
93365A156	ultrasert ii 10-32 long - 93365A156.SLDPRT
93365A160	ultrasert ii 1_4-20 short - 93365A160.SLDPRT
93365A162	ultrasert ii 1_4-20 long - 93365A162.SLDPRT
94180A307	ultrasert ii M2-0.4 short - 94180A307.SLDPRT
94180A312	ultrasert ii M2-0.4 long - 94180A312.SLDPRT
94180A321	ultrasert ii M2.5-0.45 short - 94180A321.SLDPRT
94180A323	ultrasert ii M2.5-0.45 long - 94180A323.SLDPRT
94180A331	ultrasert ii M3-0.5 short - 94180A331.SLDPRT
94180A333	ultrasert ii M3-0.5 long - 94180A333.SLDPRT
94180A351	ultrasert ii M4-0.7 short - 94180A351.SLDPRT
94180A353	ultrasert ii M4-0.7 long - 94180A353.SLDPRT
94180A361	ultrasert ii M5-0.8 short - 94180A361.SLDPRT
94180A363	ultrasert ii M5-0.8 long - 94180A363.SLDPRT
94180A371	ultrasert ii M6-1 short - 94180A371.SLDPRT
94180A373	ultrasert ii M6-1 long - 94180A373.SLDPRT
94180A386	ultrasert ii M8-1.25 long - 94180A386.SLDPRT
"""

report = []

for ln in txt.split('\n'):
  ln = ln.strip()
  if ln == '':
    continue

  try: 
    pn, fn = ln.split(None, 1)
  except:
    print 'Unable to parse:', ln
    continue

  cmd = cmd_base.replace(cmd_base_pn, pn)
  cmd += " -o '{0:s}'".format(fn)

  mesg = ''

  try:
    rv = subprocess.call(cmd, shell=True)
    if rv != 0:
      mesg = 'error=' + str(rv)
    else:
      mesg = 'success'
  except OSError as e:
    mesg = 'exception=' + str(e)

  report += [[mesg, pn, fn]]

print '\n'

for ln in report:
  print '\t'.join(ln)


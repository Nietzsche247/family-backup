import os, re, email
from email import policy

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
kw = [b'cease', b'desist', b'no longer']
out = []
def log(*a): out.append(' '.join(str(x) for x in a))

rx_cease = re.compile(r'cease\W{0,6}desist', re.I)
rx_nol = re.compile(r'no longer', re.I)
rx_tom = re.compile(r'\b(tom|delaney)\b', re.I)
rx_wil = re.compile(r'wilson|davidwilson0@yahoo', re.I)
rx_atty = re.compile(r'thomae|thomaelaw', re.I)

scanned = pf = 0
for fld in folders:
    d = os.path.join(ROOT, fld)
    if not os.path.isdir(d): continue
    for fn in os.listdir(d):
        if not fn.endswith('.eml'): continue
        p = os.path.join(d, fn); scanned += 1
        try:
            with open(p, 'rb') as f: head = f.read(1048576)
        except: continue
        if not any(k in head.lower() for k in kw): continue
        pf += 1
        try:
            msg = email.message_from_bytes(open(p, 'rb').read(), policy=policy.default)
        except: continue
        subj = str(msg.get('subject', '') or ''); frm = str(msg.get('from', '') or '')
        to = str(msg.get('to', '') or ''); cc = str(msg.get('cc', '') or ''); date = str(msg.get('date', '') or '')
        body = ''
        try:
            for part in msg.walk():
                if part.get_content_type() in ('text/plain', 'text/html'):
                    try: body += (part.get_content() or '')[:60000]
                    except: pass
        except: pass
        hay = subj + '\n' + body; rcpts = to + ' ' + cc + ' ' + frm
        atty = ' [ATTY-INVOLVED: privilege-check]' if rx_atty.search(rcpts) else ''
        tag = fld + '/' + fn
        if rx_cease.search(hay):
            log('[CEASE] %s | %s | FROM %s | TO %s | CC %s | SUBJ %s%s' % (tag, date, frm[:45], to[:75], cc[:45], subj[:65], atty))
        if rx_nol.search(hay) and rx_tom.search(hay):
            w = 'WILSON IN RECIPIENTS' if rx_wil.search(rcpts) else 'wilson NOT in recipients'
            log('[NOLONGER+TOM] %s | %s | FROM %s | TO %s | CC %s | SUBJ %s | %s%s' % (tag, date, frm[:40], to[:85], cc[:55], subj[:55], w, atty))

log('\nscanned=%d passed_prefilter=%d hits=%d' % (scanned, pf, len(out)))
open(r'C:\Users\aaron\clawd-shared\_mail_search.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done scanned', scanned, 'prefilter', pf)

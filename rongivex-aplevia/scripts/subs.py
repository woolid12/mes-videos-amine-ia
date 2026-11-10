import json,re
from PIL import Image,ImageDraw,ImageFont
S='/tmp/claude-0/-home-user-mes-videos-amine-ia/f8b084f5-d612-5ae8-a97a-c3e86d2bb2c9/scratchpad'
plan=json.load(open(S+'/plan.json'));words=plan['words']
ft=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf',42)
MAXW=585
def tw(s): return ft.getlength(s)
# fix display text: apostrophes typographic already; join ':' '?' attached
CAPS=["Vous avez des souris|ou des rats chez vous ?","Voici comment|les éloigner,","sans poison|et sans piège.",
"Je vous présente les|nouveaux sachets","anti-rongeurs|RongiVex, d’Aplevia.","Une nouvelle formule|à base d’huiles essentielles",
"et d’ingrédients naturels,","pensée pour éloigner|les rats et les souris","de votre maison.",
"Chaque sachet contient|4 ingrédients naturels :","du bois de cèdre,","de l’huile de ricin,","de la menthe poivrée","et de la cannelle.",
"Leur odeur intense est|très désagréable","pour les rongeurs :","elle les pousse à|quitter leur cachette","et à aller|voir ailleurs.",
"Posez simplement|un sachet","aux endroits|où ils passent :","placards, garage,|cave, grenier.","L’odeur se diffuse|et protège la pièce.",
"Pas d’appâts|empoisonnés,","pas de pièges|dangereux,","juste 4 ingrédients|naturels","et plus de sécurité|pour vos enfants","et vos animaux.",
"Essayez les sachets|anti-rongeurs d’Aplevia","pendant 30 jours :","satisfait ou remboursé."]
out=[];wi=0;groups=[]
for c in CAPS:
    n=len(c.replace('|',' ').split());g=words[wi:wi+n];wi+=n
    a=' '.join(x['w'] for x in g).replace('quatre','4');b=c.replace('|',' ')
    assert a==b,(a,b);groups.append((g,c.split('|')))
assert wi==len(words)
for k,(c,ls) in enumerate(groups):
    t0=c[0]['o0']-0.05;nxt=groups[k+1][0][0]['o0']-0.05 if k+1<len(groups) else None
    t1=c[-1]['o1']+0.35
    if nxt is not None and (nxt-t1)<0.5: t1=nxt
    if nxt is not None: t1=min(t1,nxt)
    for l in ls: assert tw(l)<=640,l
    out.append(dict(t0=round(t0,3),t1=round(t1,3),lines=ls))
def render(lines,path):
    PADX,BOXH,PITCH,RAD=19,60,54,9
    img=Image.new('RGBA',(720,BOXH+PITCH*(len(lines)-1)+4),(0,0,0,0));d=ImageDraw.Draw(img)
    for i,l in enumerate(lines):
        w=tw(l);x0=360-w/2-PADX;y0=i*PITCH
        d.rounded_rectangle((x0,y0,360+w/2+PADX,y0+BOXH),radius=RAD,fill=(255,255,255,255))
    for i,l in enumerate(lines):
        w=tw(l);d.text((360-w/2,i*PITCH+BOXH/2),l,font=ft,fill=(0,0,0,255),anchor='lm')
    img.save(path)
for i,c in enumerate(out):
    c['png']=f'{S}/subs/c{i:02d}.png';render(c['lines'],c['png'])
json.dump(out,open(S+'/subs/caps.json','w'),ensure_ascii=False,indent=1)
for c in out: print(f"{c['t0']:6.2f}-{c['t1']:6.2f}  "+' / '.join(c['lines']))

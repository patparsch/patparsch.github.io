"""Build the public-facing CV from assets/files/CV_Parschan.md. Requires reportlab.

Run with the bundled Codex Python runtime; output: assets/files/CV_Parschan.pdf.
The Markdown file is the sole content source. Private address, birth date, personal email and referee details are omitted.
"""
from pathlib import Path
import re
from html import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Flowable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'files' / 'CV_Parschan.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
FONTDIR = Path('C:/Windows/Fonts')
for name,file in [('Body','calibri.ttf'),('BodyBold','calibrib.ttf'),('BodyItalic','calibrii.ttf'),('BodyBoldItalic','calibriz.ttf'),('Display','georgia.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBoldItalic')

INK=colors.HexColor('#24343B')
TEAL=colors.HexColor('#12636B')
MUTED=colors.HexColor('#566970')
PALE=colors.HexColor('#EDF4F4')
LINE=colors.HexColor('#D5E2E3')
W,H=A4
M=38
WIDTH=W-2*M-12
PHOTO=ROOT/'assets'/'img'/'patrick.jpg'
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=9,leading=10.4,textColor=INK,spaceAfter=2.5),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.4,leading=9.6,textColor=MUTED,spaceAfter=3),
 'h2':ParagraphStyle('h2',fontName='BodyBold',fontSize=13.5,leading=16,textColor=TEAL,spaceBefore=12,spaceAfter=6,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='BodyBold',fontSize=10,leading=12,textColor=INK,spaceBefore=6,spaceAfter=3,keepWithNext=True),
 'date':ParagraphStyle('date',fontName='BodyBold',fontSize=8.6,leading=10.8,textColor=TEAL,alignment=TA_RIGHT),
 'term':ParagraphStyle('term',fontName='BodyBold',fontSize=8.7,leading=10.7,textColor=TEAL),
 'cite':ParagraphStyle('cite',fontName='Body',fontSize=8.8,leading=10.1,textColor=INK,spaceAfter=0),
 'number':ParagraphStyle('number',fontName='BodyBold',fontSize=9,leading=11.4,textColor=TEAL,alignment=TA_RIGHT),
 'contact':ParagraphStyle('contact',fontName='Body',fontSize=8.2,leading=9.8,textColor=MUTED,spaceAfter=2),
}

def markup(s):
    s=s.replace('\u2013', '-').replace('\u2014', '-').replace('\u2011', '-')
    s=escape(s)
    s=s.replace('&lt;u&gt;', '<u>').replace('&lt;/u&gt;', '</u>')
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:f'<link href="{m[2]}" color="#12636B">{m[1]}</link>',s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    return s.replace('\n','<br/>')

def p(s,style='body'):
    return Paragraph(markup(s),styles[style])

def row(cells,widths,pad=0,bottom=3):
    t=Table([cells],colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),bottom)]))
    return t

class CircularPortrait(Flowable):
    def __init__(self,path,size=76):
        super().__init__()
        self.path=path
        self.width=size
        self.height=size
    def draw(self):
        c=self.canv
        c.saveState()
        inset=1.2
        diameter=self.width-2*inset
        clip=c.beginPath()
        clip.circle(self.width/2,self.height/2,diameter/2)
        c.clipPath(clip,stroke=0,fill=0)
        c.drawImage(str(self.path),inset,inset,width=diameter,height=diameter,preserveAspectRatio=True,anchor='c',mask='auto')
        c.restoreState()
        c.setStrokeColor(TEAL)
        c.setLineWidth(1.2)
        c.circle(self.width/2,self.height/2,diameter/2,stroke=1,fill=0)

class PageCanvas(canvas.Canvas):
    def __init__(self,*args,**kwargs):
        canvas.Canvas.__init__(self,*args,**kwargs)
        self.states=[]
    def showPage(self):
        self.states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        total=len(self.states)
        for state in self.states:
            self.__dict__.update(state)
            self.setFillColor(TEAL)
            self.rect(M,H-20,30,2.5,fill=1,stroke=0)
            if self._pageNumber>1:
                self.setFont('BodyBold',8)
                self.setFillColor(MUTED)
                self.drawString(M,H-33,'PATRICK PARSCHAN')
                self.setFont('Body',8)
                self.drawRightString(W-M,H-33,'Wissenschaftlicher Lebenslauf')
            self.setStrokeColor(LINE)
            self.setLineWidth(.45)
            self.line(M,32,W-M,32)
            self.setFont('Body',8)
            self.setFillColor(MUTED)
            self.drawString(M,20,'Patrick Parschan  ·  Oktober 2026')
            self.drawRightString(W-M,20,f'{self._pageNumber} / {total}')
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

source=(ROOT/'assets'/'files'/'CV_Parschan.md').read_text(encoding='utf-8')
sections=re.split(r'^## ',source,flags=re.M)[1:]
parsed={s.split('\n',1)[0]:s.split('\n',1)[1].strip() for s in sections}
story=[]
contact=parsed['Kontaktdaten'].split('\n\n')
identity=contact[0].splitlines()
institution=identity[0].strip()
links={}
for line in contact[1].splitlines():
    match=re.match(r'- ([^:]+): \[([^\]]+)\]\(([^)]+)\)',line.strip())
    if match:
        links[match.group(1)]=(match.group(2),match.group(3))
eyebrow=Paragraph('WISSENSCHAFTLICHER LEBENSLAUF',ParagraphStyle('eyebrow',fontName='BodyBold',fontSize=8.3,leading=11,textColor=TEAL,spaceAfter=5))
name=Paragraph('Patrick Parschan',ParagraphStyle('name',fontName='Display',fontSize=29,leading=33,textColor=INK,spaceAfter=2))
left=[eyebrow,name,p('formerly Patrick Schwabl · M. A.','small'),p(institution,'small')]
left_table=Table([[item] for item in left],colWidths=[WIDTH-88],hAlign='LEFT')
left_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
header=Table([[left_table,CircularPortrait(PHOTO,76)]],colWidths=[WIDTH-88,88],hAlign='LEFT')
header.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('ALIGN',(1,0),(1,0),'RIGHT'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
story.append(header)
email_parts=[]
for label in ('Dienstlich',):
    if label in links:
        display,url=links[label]
        email_parts.append(f'<b>{label}</b>: <link href="{url}" color="#12636B">{escape(display)}</link>')
story.append(Paragraph(' &nbsp; · &nbsp; '.join(email_parts),styles['contact']))
badges={'Website':('WWW','#12636B'),'GitHub':('GH','#24343B'),'Google Scholar':('GS','#4285F4'),'Bluesky':('b','#0085FF'),'LinkedIn':('in','#0A66C2')}
profile_parts=[]
for label,(badge,color) in badges.items():
    if label in links:
        display,url=links[label]
        profile_parts.append(f'<font color="{color}"><b>{badge}</b></font>&nbsp;<link href="{url}" color="#12636B">{escape(display)}</link>')
story.append(Paragraph(' &nbsp; · &nbsp; '.join(profile_parts),styles['contact']))
story.append(Spacer(1,2))

def blocks(content):
    return [s.strip() for s in re.split(r'\n\s*\n',content) if s.strip()]

def body_block(block,width=WIDTH):
    if block.startswith('|'):
        rows=[x for x in block.splitlines() if not re.match(r'^\|[ :|-]+\|$',x)]
        data=[[p(x.strip(),'small' if n==0 else 'body') for x in line.strip('|').split('|')] for n,line in enumerate(rows)]
        t=Table(data,colWidths=[WIDTH*.47,WIDTH*.2,WIDTH*.12,WIDTH*.21],repeatRows=1)
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),('LINEBELOW',(0,0),(-1,0),.7,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,LINE),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
        return [t,Spacer(1,3)]
    result=[]
    for line in block.splitlines() if block.startswith('- ') else [block]:
        m=re.match(r'- \*\*(\d+)\.\*\* (.*)',line)
        if m:
            t=row([p(m[1]+'.','number'),p(m[2],'cite')],[23,width-23],bottom=4)
            t.setStyle(TableStyle([('RIGHTPADDING',(0,0),(0,0),7)]))
            result.append(t)
        elif line.startswith('- '):
            result.append(row([p('•','small'),p(line[2:])],[10,width-10],bottom=0.8))
        elif line.startswith('  - '):
            result.append(row([p('•','small'),p(line[4:])],[18,width-18],bottom=0.8))
        elif line.startswith('  > '):
            note=row(['',p(line[4:],'small')],[10,width-10],bottom=3)
            note.setStyle(TableStyle([
                ('LINEBEFORE',(1,0),(1,0),0.8,TEAL),
                ('LEFTPADDING',(1,0),(1,0),7),
                ('TOPPADDING',(1,0),(1,0),2),
            ]))
            result.append(note)
        elif line.startswith('**') and line.endswith('**'):
            result.append(p(line,'h3'))
        elif line.startswith(('Die Nachnamen','SWS =')):
            note=p(line,'small')
            note.keepWithNext=True
            result.append(note)
        else:
            paragraph=p(line)
            if line.startswith('Gesamtumfang:'): paragraph.keepWithNext=True
            result.append(paragraph)
    return result

for section,content in parsed.items():
    if section in ('Kontaktdaten','Referenzen'): continue
    story.append(p(section,'h2'))
    if section=='Lehre':
        groups=re.split(r'^### ',content,flags=re.M)
        story+=body_block(groups[0].strip())
        for group in groups[1:]:
            title,body=group.split('\n',1)
            term=title.replace('Sommersemester','Sommersemester<br/>').replace('Wintersemester','Wintersemester<br/>')
            lp=Paragraph(term,styles['term'])
            rp=[]
            for b in blocks(body):rp+=body_block(b,WIDTH-92)
            story.append(row([lp,rp],[92,WIDTH-92],bottom=5))
        continue
    if section=='Referenzen':
        bs=blocks(content)
        refs=[x[2:] for x in bs[0].splitlines()]
        cells=[]
        for ref in refs:
            name,rest=ref.split('**, ',1)
            place,link=rest.split(': ',1)
            cells.append([p(name+'**','h3'),p(place,'small'),p(link,'body')])
        for i in range(0,4,2):story.append(row([cells[i],cells[i+1]],[WIDTH/2,WIDTH/2],bottom=5))
        story.append(Spacer(1,9))
        story.append(p(bs[1],'small'))
        continue
    bs=blocks(content)
    for i,block in enumerate(bs):
        if block.startswith('### '):
            title=block[4:]
            if ' · ' in title:
                date,title=title.split(' · ',1)
                h=row([p(title,'h3'),p(date,'date')],[WIDTH-107,107],bottom=3)
                h.keepWithNext=True
                story.append(Spacer(1,4))
                story.append(h)
            else:story.append(p(title,'h3'))
        else:
            items=body_block(block)
            if section=='Konferenzbeiträge mit Peer-Review' and any(x=='### Konferenzposter mit Peer-Review' for x in bs[:i]):
                if i<len(bs)-1:
                    for item in items:item.keepWithNext=True
            if section=='Weitere Lehrerfahrung' and any(x=='### Hochschuldidaktische Weiterbildung' for x in bs[:i]):
                for item in items[:-1]:item.keepWithNext=True
            story+=items

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=47,bottomMargin=43,title='Lebenslauf | Patrick Parschan',author='Patrick Parschan',subject='Academic Curriculum Vitae',allowSplitting=1)
doc.build(story,canvasmaker=PageCanvas)
print(OUT)

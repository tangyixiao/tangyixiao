"""GitHub-native profile cards; public data collection lives in generate_articles."""
from datetime import date, timedelta
from html import escape
import json
import math
from pathlib import Path
import re

PROJECTS = json.loads(Path(__file__).with_name('projects.json').read_text(encoding='utf-8'))
CSS = '''text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}.frame{fill:#fff;stroke:#d1d9e0}.heading{font-size:20px;font-weight:600;fill:#0969da}.meta{font-size:14px;fill:#59636e}.body{font-size:16px;fill:#1f2328}.summary{font-size:16px;fill:#1f2328}.top{stroke:#c5d3c9;stroke-width:.5;stroke-linejoin:round}.left,.right{stroke-width:.35;stroke-linejoin:round}.l0{--top:#e3e9e6;--left:#c5d0ca;--right:#d2dbd6}.l1{--top:#9be9a8;--left:#60ad75;--right:#7bc38b}.l2{--top:#40c463;--left:#258741;--right:#31a34f}.l3{--top:#30a14e;--left:#1a6f34;--right:#23843f}.l4{--top:#216e39;--left:#124b26;--right:#195b30}.top{fill:var(--top)}.left{fill:var(--left);stroke:var(--left)}.right{fill:var(--right);stroke:var(--right)}@media(prefers-color-scheme:dark){.frame{fill:#0d1117;stroke:#30363d}.heading{fill:#58a6ff}.meta{fill:#a4acb5}.body,.summary{fill:#e6edf3}.top{stroke:#424d49}.l0{--top:#2b3431;--left:#1d2521;--right:#222c27}.l1{--top:#287843;--left:#17492b;--right:#1e5c34}.l2{--top:#38a257;--left:#21673a;--right:#2b8146}.l3{--top:#56d378;--left:#2d8747;--right:#3fab5b}.l4{--top:#9be9a8;--left:#55a76a;--right:#73c587}}'''


def svg(width, height, title, body, mode=None, frame_height=None):
    css = CSS
    if mode == 'light':
        css = css.split('@media')[0]
    elif mode == 'dark':
        css = css.replace('@media(prefers-color-scheme:dark){', '').rstrip('}') + '}'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title><style>{css}</style><rect class="frame" x=".5" y=".5" width="{width-1}" height="{height-1 if frame_height is None else frame_height}" rx="6"/>{body}</svg>'


def text(cls, x, y, value, extra=''):
    return f'<text class="{cls}" x="{x}" y="{y}" {extra}>{escape(str(value))}</text>'


def calendar_days(calendar):
    days = sorted(calendar, key=lambda d: d['date'])
    if not 360 <= len(days) <= 367:
        raise ValueError('Expected a full contribution year')
    levels = ['NONE', 'FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE']
    normalized = []
    for i, day in enumerate(days):
        current = date.fromisoformat(day['date'])
        if i and current != date.fromisoformat(days[i-1]['date']) + timedelta(days=1):
            raise ValueError('Incomplete or duplicate contribution dates')
        count = day['contributionCount']
        if not isinstance(count, int) or count < 0:
            raise ValueError('Invalid contribution count')
        level = levels.index(day['contributionLevel'])
        if (count == 0) != (level == 0):
            raise ValueError('Contribution count/level mismatch')
        normalized.append((current, count, level))
    return normalized


def polygon(cls, points):
    return '<polygon class="'+cls+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+'"/>'


def column(x, y, dx, dy, depth, height, level, label):
    return (f'<g class="l{level}"><title>{escape(label)}</title>'
            +polygon('left',[(x,y-height),(x+dx,y-height),(x+dx,y+dy),(x,y+dy)])
            +polygon('right',[(x+dx,y-height),(x+dx+depth,y-height-dy),(x+dx+depth,y),(x+dx,y+dy)])
            +polygon('top',[(x,y-height),(x+depth,y-height-dy),(x+dx+depth,y-height-dy),(x+dx,y-height)])+'</g>')


def render_calendar(calendar, landscape=False, mobile=False, stats=None, mode=None):
    days = calendar_days(calendar)
    start = days[0][0] - timedelta(days=(days[0][0].weekday()+1)%7)
    weeks = (days[-1][0]-start).days//7+1
    split = (weeks+1)//2
    width,height = ((420,460) if mobile else (960,340)) if landscape else ((420,350) if mobile else (800,240))
    title = '3D contribution landscape' if landscape else 'Contributions calendar'
    body = text('heading',24,33,title)
    if landscape:
        body += text('meta',24,57,f'{days[0][0]} — {days[-1][0]}')
    maximum = max(n for _,n,_ in days)
    logmax = math.log10(maximum/20+1)*144+3
    for current,count,level in days:
        week,day = divmod((current-start).days,7)
        if landscape and mobile:
            x,y=48+(week%split)*12.1-day*4.2,132+day*8.5+(178 if week>=split else 0)
            dx,dy,depth=10.5,7,3.6
            h=3 if maximum == 0 else (math.log10(count/20+1)*144+3)/logmax*87
        elif landscape:
            x,y=91+week*(800/max(52,weeks-1))-day*7,179+day*13+week*.18
            dx,dy,depth=13.7,10.3,6.1
            h=3 if maximum == 0 else (math.log10(count/20+1)*144+3)/logmax*137
        elif mobile:
            x,y=43+(week%split)*13-day*4,96+day*8+(122 if week>=split else 0)
            dx,dy,depth,h=11,6,3,count/max(1,maximum)*42
        else:
            x,y=64+week*(676/max(52,weeks-1))-day*5,106+day*9
            dx,dy,depth,h=11,7,4,count/max(1,maximum)*49
        body += column(x,y,dx,dy,depth,h,level,f'{current}: {count} contributions')
    if landscape:
        if stats is None:
            raise ValueError('Missing public repository totals')
        total=sum(n for _,n,_ in days)
        if mobile:
            boundary=start+timedelta(weeks=split)
            body += text('meta',24,208,f'{days[0][0]:%Y.%m} — {boundary:%Y.%m}')
            body += text('meta',24,386,f'{boundary:%Y.%m} — {days[-1][0]:%Y.%m}')
            body += text('summary',24,421,f'{total:,} contributions')+text('meta',24,444,f'{stats["stars"]:,} stars · {stats["forks"]:,} forks')
        else:
            for i in range(0,weeks,8):
                label=(start+timedelta(weeks=i)).strftime('%Y.%m' if i==0 else '%m')
                body += text('meta',54+i*(800/max(52,weeks-1)),292,label)
            body += text('summary',24,321,f'{total:,} contributions')+text('meta',242,321,f'{stats["stars"]:,} stars · {stats["forks"]:,} forks')
    else:
        current=best=0
        for _,count,_ in days:
            current=current+1 if count else 0
            best=max(best,current)
        # Today can still receive contributions; keep yesterday's live streak.
        if not days[-1][1] and len(days)>1:
            current=0
            for _,count,_ in reversed(days[:-1]):
                if not count: break
                current+=1
        labels=[f'Current streak {current} days',f'Best streak {best} days',f'Highest in a day {maximum}']
        positions=[(22,306),(230,306),(22,330)] if mobile else [(24,213),(282,213),(542,213)]
        body += ''.join(text('meta',x,y,label) for (x,y),label in zip(positions,labels))
    return svg(width,height,title,body,mode)


def language_contributions(entries):
    totals={}
    for item in entries:
        repo=item['repository']
        if repo['isPrivate']:
            raise ValueError('Non-public repository in contribution data')
        lang=repo['primaryLanguage']
        count=item['contributions']['totalCount']
        if count < 0: raise ValueError('Negative language contribution count')
        if not lang or not count: continue
        name=lang['name']
        color=lang['color'] or '#8b949e'
        if name.lower() in ('other','others','其他') or not re.fullmatch(r'#[0-9a-fA-F]{6}',color):
            raise ValueError('Invalid concrete language')
        old=totals.get(name,(0,color))
        totals[name]=(old[0]+count,color)
    return [(name,count,color) for name,(count,color) in sorted(totals.items(),key=lambda x:(-x[1][0],x[0]))]


def render_details(collection, mobile=False):
    languages=language_contributions(collection['commitContributionsByRepository'])
    width=420 if mobile else 900
    legend_height=max(196,len(languages)*25+35)
    radar_y=legend_height+230 if mobile else max(190,legend_height/2)
    height=radar_y+190 if mobile else max(360,legend_height+70)
    body=text('heading',22,33,'Commit contributions by language')
    total=sum(n for _,n,_ in languages)
    cx,cy,r=100,134,70
    angle=-math.pi/2
    for i,(name,count,color) in enumerate(languages):
        sweep=count/total*2*math.pi
        if sweep>2*math.pi-1e-8:
            body+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="32"/>'
        else:
            x1,y1=cx+r*math.cos(angle),cy+r*math.sin(angle)
            end=angle+sweep
            x2,y2=cx+r*math.cos(end),cy+r*math.sin(end)
            body+=f'<path d="M{x1:.3f},{y1:.3f} A{r},{r} 0 {int(sweep>math.pi)} 1 {x2:.3f},{y2:.3f}" fill="none" stroke="{color}" stroke-width="32"/>'
        angle+=sweep
        y=69+i*25
        body+=f'<rect x="201" y="{y-12}" width="12" height="12" fill="{color}"/>'+text('meta',221,y,f'{name} {count/total:.1%}')
    if not languages: body+=text('meta',24,90,'No named public repository languages')
    rx=210 if mobile else 680
    body+=text('heading',rx-115,radar_y-155,'Contribution types')
    keys=[('totalCommitContributions','Commits'),('totalIssueContributions','Issues'),('totalPullRequestContributions','PRs'),('totalPullRequestReviewContributions','Reviews'),('totalRepositoryContributions','Repos')]
    values=[collection[k] for k,_ in keys]
    ceiling=max(1,max(values))
    coords=[]
    for i,(key,label) in enumerate(keys):
        a=-math.pi/2+i*2*math.pi/5
        ratio=math.log10(collection[key]+1)/math.log10(ceiling+1)
        coords.append((rx+math.cos(a)*108*ratio,radar_y+math.sin(a)*108*ratio))
        body+=text('meta',round(rx+math.cos(a)*134),round(radar_y+math.sin(a)*134),f'{label}: {collection[key]}','text-anchor="middle"')
    for ratio in (.25,.5,.75,1):
        points=[(rx+math.cos(-math.pi/2+i*2*math.pi/5)*108*ratio,radar_y+math.sin(-math.pi/2+i*2*math.pi/5)*108*ratio) for i in range(5)]
        body+='<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+'" fill="none" stroke="#8b949e" stroke-opacity=".45"/>'
    body+='<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)+'" fill="#58a6ff" fill-opacity=".3" stroke="#58a6ff" stroke-width="2"/>'
    return svg(width,height,'Languages and contribution types',body)


def render_project(definition, info, release, language):
    title=definition['title']
    body=text('heading',42,36,title,'style="font-size:19px"')
    body+='<path d="M22 23h11v14H22zM24 34h7M24 27h4" fill="none" stroke="#8b949e" stroke-width="1.5"/>'
    lines=definition[language]
    body+=''.join(text('body',22,73+i*24,line) for i,line in enumerate(lines))
    name=info['language'] or 'Source'
    colors={'TypeScript':'#3178c6','JavaScript':'#f1e05a','Kotlin':'#a97bff','Python':'#3572a5','HTML':'#e34c26','Rust':'#dea584','C++':'#f34b7d'}
    body+=f'<circle cx="27" cy="132" r="5" fill="{colors.get(name,"#8b949e")}"/>'+text('meta',40,137,name)+text('meta',188,137,f'☆ {info["stargazers_count"]}')
    if release:
        if release.get('draft') or not release.get('published_at'):
            raise ValueError('Unpublished release')
        tag=release['tag_name']
        if len(tag)>28: raise ValueError('Unexpected release tag length')
        published=date.fromisoformat(release['published_at'][:10])
        body+=text('meta',22,169,f'{tag} · {published}')
    # Transparent trailing space separates wrapped cards in GitHub's sanitized HTML.
    return svg(450,202,title,body,frame_height=189)


def generate_visuals(output, calendar, collection, stats, projects):
    for mobile in (False,True):
        (output/('isometric-mobile.svg' if mobile else 'isometric.svg')).write_text(render_calendar(calendar,mobile=mobile),encoding='utf-8')
    for mode in ('light','dark'):
        (output/f'contribution-3d-{mode}.svg').write_text(render_calendar(calendar,landscape=True,stats=stats,mode=mode),encoding='utf-8')
    (output/'contribution-3d-mobile.svg').write_text(render_calendar(calendar,landscape=True,mobile=True,stats=stats),encoding='utf-8')
    for mobile in (False,True):
        (output/('contribution-details-mobile.svg' if mobile else 'contribution-details.svg')).write_text(render_details(collection,mobile),encoding='utf-8')
    for definition,(info,release) in zip(PROJECTS,projects):
        if info['private'] or info['name'].lower()!=definition['slug'].lower():
            raise ValueError('Unexpected project identity')
        for language in ('zh','en'):
            (output/f'project-{definition["slug"]}-{language}.svg').write_text(render_project(definition,info,release,language),encoding='utf-8')

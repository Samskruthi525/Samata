#!/usr/bin/env python3
"""Capture README screenshots from prototype/ambedkar_kiosk.html with headless Chromium.

    pip install playwright && python -m playwright install chromium
    python scripts/capture_screenshots.py
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parents[1]
OUT = str(ROOT / 'docs' / 'screenshots') + '/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':1280,'height':800})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto((ROOT / 'prototype' / 'ambedkar_kiosk.html').as_uri()); await pg.wait_for_timeout(1500)
        async def s(name,js=None,wait=700):
            if js: await pg.evaluate(js)
            await pg.wait_for_timeout(wait); await pg.screenshot(path=OUT+name+'.png')
        await pg.add_style_tag(content='#toasts{display:none!important}')
        await s('01_attract')
        await s('02_home',"go('home')")
        await s('03_explore',"go('explore')")
        await s('04_viewer',"openViewer('WS-001',1,'WS001-P-b')")
        await s('05_timeline',"go('timeline')")
        await s('06_ask_answer',"go('ask');document.querySelector('#ask-input').value='What did Ambedkar say about constitutional morality?';askArchive()",wait=2500)
        await s('07_ask_abstain',"document.querySelector('#ask-input').value='What was his favourite cricket team?';askArchive()",wait=2500)
        await s('08_stories',"go('story')")
        await s('09_map',"go('map')")
        await s('10_media',"openMedia('AV-001')")
        await s('11_offline',"stopMedia();go('home');setOnline(false)")
        await s('12_hindi',"setOnline(true);setLang('hi')")
        await s('13_idle',"setLang('en');go('home');warnIdle()")
        await s('14_curator',"hideOverlays();clearInterval(S.idle.tick);S.idle.warned=false;openCurator()")
        await s('15_tests',"hideOverlays();go('tests')")
        await s('16_stats',"go('stats')")
        await s('17_device_console',"go('home');document.querySelector('#dev').classList.add('open')")
        if errs:
            print('page errors:', errs)
        await b.close()
asyncio.run(main())

# -*- coding: utf-8 -*-

import regex as re
import requests
from bs4 import BeautifulSoup

def unicode_replace(text):
    text = text.replace("…","...")
    text = re.sub(r"“|”|''", '"', text)
    text = re.sub(r"‘|’", "'", text)
    text = text.replace("–","-")
    text = text.replace("·","-")
    return text

def google_search(query, noOfPages=1):
    pages = noOfPages
    start = 0
    results = []
    for i in range(pages):
        search_term = query
        req = requests.get("http://www.google.com/search?q=" + search_term +"&start=" + str(start), allow_redirects=True)

        html = req.text.replace(u'\xa0',u' ')
        html = re.sub("[\r\n\t]+", "", html)
        html = re.sub(" {2,}", " ", html)

        html = re.sub("<script[^>]*>(.*?)</script>", "", html)
        html = re.sub("<script>(.*?)</script>", "", html)

        html = re.sub("<style(.*?)>(.*?)</style>", "", html)
        html = re.sub("<input [^>]*>", "", html)
        html = re.sub("<link [^>]*>", "", html)
        html = re.sub("<noscript(.*?)>(.*?)</noscript>", "", html)

        html = re.sub("<!--(.*?)-->","",html)
        html = re.sub(" onclick='[^']*'", "", html)
        html = re.sub(" onclick=\"[^\"]*\"", "", html)

        html = re.sub(" style='[^']*'", "", html)
        html = re.sub(" style=\"[^\"]*\"", "", html)
        
        html = re.sub(" src='data:image[^']*'", "", html)
        html = re.sub(" src=\"data:image[^\"]*\"", "", html)

        html = re.sub(" href=\"javascript\:[^\"]*", "", html)
        html = re.sub(" href='javascript\:[^']*", "", html)
        
        html = re.sub(" on[A-Za-z]+=\"[^\"]*", "", html)
        html = re.sub(" on[A-Za-z]='[^']*", "", html)
        
        html = re.sub("<body[^>]+>", "<body>", html)

        html = re.sub(" {2,}"," ",html)

        try:
            soup = BeautifulSoup(html, "lxml")
            divs = soup.select("#main > div > div > div")
            length_of_results = len(divs)
            if start == 0:
                start = length_of_results + 1
            else:
                start = start + length_of_results + 1

            for el in divs:
                if not el.parent:
                    continue

                h3 = el.select_one('h3')
                if not h3:
                    continue

                atag = el.select_one('a')
                if not atag:
                    continue

                m = re.search('url\?q=(.*)&sa=', atag['href'])
                if not bool(m):
                    continue

                for e in el.find_next_sibling('div').select('span'):
                    e.decompose()
                title = h3.text.strip()
                title = re.sub("^([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]\\.)+[a-zA-Z]{2,}$"," ", title)
                url = m.group(1)
                excerpt = el.find_next_sibling('div').text.strip()
                results.append({
                    'title' : title,
                    'url' : url,
                    'excerpt' : excerpt
                })

        except:
            return {
                'error':'Có lỗi trong quá trình lấy dữ liệu'
            }

    for i in range(len(results)):
        title = results[i]['title']
        if '-' in title:
            tmp = title.split('-')
            title = "-".join(tmp[0:-1])
        if '–' in title:
            tmp = title.split('–')
            title = "-".join(tmp[0:-1])
        if '·' in title:
            tmp = title.split('·')
            title = "-".join(tmp[0:-1])

        if '|' in title:
            tmp = title.split('|')
            if len(tmp[0]) < len(tmp[1]):
                title = '|'.join(tmp[1:])
        title = title.strip()
        if len(title) > 0:
            results[i]['title'] = unicode_replace(title)

        results[i]['excerpt'] = unicode_replace(results[i]['excerpt'])

    return results

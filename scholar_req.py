import helium
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

_IMPLICIT_WAIT=12

class ScholarRequests:
    """gestisce le richieste a semantic scholar"""
    
    def __init__(self):
        op = Options()
        #op.add_argument('--disable-gpu')
        op.add_argument('--no-sandbox')
        op.add_argument('disable-infobars')
        op.add_argument("--disable-extensions")
        try:
            self._chrm=helium.start_chrome(headless=False, options=op)
        except Exception:
            path=ChromeDriverManager.install()
            op.binary_location=path
            self._chrm=helium.start_chrome(headless=False, options=op)

    def search_single_pub(self, query):
        """restituisce il primo paper dalla ricerca"""
        
        url = 'https://www.semanticscholar.org/search?q={}&sort=relevance'.format(query)
        helium.go_to(url)
        self._wait('.result-page')

        title=self._chrm.find_element_by_class_name('cl-paper-title').text
        author=self._chrm.find_element_by_class_name('cl-paper-authors').text
        year=self._chrm.find_element_by_class_name('cl-paper-pubdates').text[-4:]
        link=self._chrm.find_element_by_css_selector('.cl-paper-row > a').get_attribute('href')

        abs_l=self._chrm.find_element_by_class_name('cl-paper-row').find_elements_by_css_selector('.cl-paper-abstract span span')
        abstract=""
        if len(abs_l)>0:
            abstract=abs_l[0].text

        pub={'title': title,
             'author': author,
             'pub_year': year,
             'venue': 'venue',
             'abstract': abstract,
             'link':link}
        return pub

    def cited_by(self, pub):
        pubs=[]
        helium.go_to(pub['link'])
        #self._wait('.card-container')

        page=1
        while page<5:
            papers=self._chrm.find_elements_by_css_selector('#citing-papers .cl-paper-row.citation-list__paper-row')
            for p in papers:
                title=p.find_elements_by_css_selector('.cl-paper-title')
                author=p.find_elements_by_css_selector('.cl-paper-authors')
                year=p.find_elements_by_css_selector('.cl-paper-pubdates')
                link=p.find_elements_by_css_selector('.cl-paper-row > a')

                if len(title)>0:
                    title=title[0].text
                else:
                    continue

                if len(author)>0:
                    author=author[0].text
                else:
                    continue

                if len(year)>0:
                    year=year[0].text
                else:
                    continue

                if len(link)>0:
                    link=link[0].get_attribute('href')
                else:
                    continue

                pubs.append({'title': title,
                    'author': author,
                    'pub_year': year,
                    'venue': 'venue',
                    'abstract': "",
                    'link':link})

            #test next page
            l=self._chrm.find_elements_by_css_selector('#citing-papers .cl-pager.cl-pager--has-next-enabled')
            if len(l)==0:
                break;
            #click next page
            elm=self._chrm.find_element_by_css_selector('.cl-pager__button.cl-pager__next')
            self._chrm.execute_script("arguments[0].click();", elm)
            page+=1
            self._wait(f'#citing-papers .cl-pager[data-curr-page-num="{page}"]')
            
        return pubs

    def references(self, pub):
        pubs=[]
        helium.go_to(pub['link'])
        #self._wait('.card-container')

        page=1
        while page<5:
            papers=self._chrm.find_elements_by_css_selector('#references .cl-paper-row.citation-list__paper-row')
            for p in papers:
                title=p.find_elements_by_css_selector('.cl-paper-title')
                author=p.find_elements_by_css_selector('.cl-paper-authors')
                year=p.find_elements_by_css_selector('.cl-paper-pubdates')
                link=p.find_elements_by_css_selector('.cl-paper-row > a')

                if len(title)>0:
                    title=title[0].text
                else:
                    continue

                if len(author)>0:
                    author=author[0].text
                else:
                    continue

                if len(year)>0:
                    year=year[0].text
                else:
                    continue

                if len(link)>0:
                    link=link[0].get_attribute('href')
                else:
                    continue

                pubs.append({'title': title,
                    'author': author,
                    'pub_year': year,
                    'venue': 'venue',
                    'abstract': "",
                    'link':link})

            #test next page
            l=self._chrm.find_elements_by_css_selector('#references .cl-pager.cl-pager--has-next-enabled')
            if len(l)==0:
                break;
            #click next page
            elm=self._chrm.find_element_by_css_selector('.cl-pager__button.cl-pager__next')
            self._chrm.execute_script("arguments[0].click();", elm)
            page+=1
            self._wait(f'#references .cl-pager[data-curr-page-num="{page}"]')
            
        return pubs

    def _wait(self, css_query):
        self._chrm.implicitly_wait(_IMPLICIT_WAIT)
        l=self._chrm.find_elements_by_css_selector(css_query)
        self._chrm.implicitly_wait(0)
        return l;

    def _nextPage(self):
        #test next page
        l=self.chrm.find_elements_by_css_selector('.cl-pager.cl-pager--has-next-enabled')

        #click next page
        elm=self.chrm.find_element_by_css_selector('.cl-pager__button.cl-pager__next')
        self.chrm.execute_script("arguments[0].click();", elm)

    def exit(self):
        helium.kill_browser()

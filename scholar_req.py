import helium
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

_IMPLICIT_WAIT=12

class ScholarRequests:
    """gestisce le richieste a semantic scholar"""
    
    def __init__(self):
        try:
            self._chrm=helium.start_chrome(headless=True)
        except Exception:
            path=ChromeDriverManager.install()
            op = Options()
            op.binary_location=path
            self._chrm=helium.start_chrome(headless=True, options=op)
            
        self._chrm.implicitly_wait(_IMPLICIT_WAIT)

    def search_single_pub(self, query):
        """restituisce il primo paper dalla ricerca"""
        
        url = 'https://www.semanticscholar.org/search?q={}&sort=relevance'.format(query)
        helium.go_to(url)

        title=self._chrm.find_element_by_class_name('cl-paper-title').text
        author=self._chrm.find_element_by_class_name('cl-paper-authors').text#.find_elements_by_class_name('cl-paper-authors__author-link')
        year=self._chrm.find_element_by_class_name('cl-paper-pubdates').text[-4:]
        link=self._chrm.find_element_by_css_selector('.cl-paper-row > a').get_attribute('href')

        self._chrm.implicitly_wait(0)
        abs_l=self._chrm.find_element_by_class_name('cl-paper-row').find_elements_by_css_selector('.cl-paper-abstract span span')
        abstract=""
        if len(abs_l)>0:
            abstract=abs_l[0].text
        self._chrm.implicitly_wait(_IMPLICIT_WAIT)

        pub={'title': title,
             'author': author,
             'pub_year': year,
             'venue': 'venue',
             'abstract': abstract,
             'link':link}
        return pub

    def cited_by(self, pub):
        helium.go_to(pub['link'])
        
        titles=self._chrm.find_elements_by_css_selector('#citing-papers .cl-paper-title')
        authors=self._chrm.find_elements_by_css_selector('#citing-papers .cl-paper-authors')
        years=self._chrm.find_elements_by_css_selector('#citing-papers .cl-paper-pubdates')
        links=self._chrm.find_elements_by_css_selector('#citing-papers .cl-paper-row > a')
        
        titles=[t.text for t in titles]
        authors=[a.text for a in authors]
        years=[y.text for y in years]
        links=[l.get_attribute('href') for l in links]

        pubs=[]
        for i,_ in enumerate(titles):
            pubs.append({'title': titles[i],
                'author': authors[i],
                'pub_year': years[i],
                'venue': 'venue',
                'abstract': "",
                'link':links[i]})
        return pubs

    def references(self, pub):
        helium.go_to(pub['link'])
        
        titles=self._chrm.find_elements_by_css_selector('#references .cl-paper-title')
        authors=self._chrm.find_elements_by_css_selector('#references .cl-paper-authors')
        years=self._chrm.find_elements_by_css_selector('#references .cl-paper-pubdates')
        links=self._chrm.find_elements_by_css_selector('#references .cl-paper-row > a')
        
        titles=[t.text for t in titles]
        authors=[a.text for a in authors]
        years=[y.text for y in years]
        links=[l.get_attribute('href') for l in links]

        pubs=[]
        for i,_ in enumerate(titles):
            pubs.append({'title': titles[i],
                'author': authors[i],
                'pub_year': years[i],
                'venue': 'venue',
                'abstract': "",
                'link':links[i]})
        return pubs

    def exit(self):
        helium.kill_browser()

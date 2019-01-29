from functools import wraps
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class SakaiBrowser:
    def __init__(self):
        opts = Options()
        opts.set_headless()

        browser = webdriver.Firefox(options=opts)
        browser.get('https://sakai.rutgers.edu/portal')
        self.browser = browser
        self.logged_in = False

    def login(self, netid, password, retry=False):
        if not retry:
            self.find_element_by_id('loginLink1').click()
        self.find_element_by_id('username').send_keys(netid)
        self.find_element_by_id('password').send_keys(password)
        self.find_elements_by_class_name('btn-submit')[0].click()

    def prompt_for_login(self):
        if self.logged_in:
            return
        netid = input("Enter your netid > ")
        password = getpass("Enter your password > ")
        self.login(netid, password)
        while self.browser.current_url.startswith('https://cas.rutgers.edu'):
            print(browser.find_element_by_css_selector('#status.errors').text)
            netid = input("Enter your netid > ")
            password = getpass("Enter your password > ")
            self.login(netid, password, True)
        self.logged_in = True

    def __getattr__(self, name):
        return getattr(self.browser, name)

def ensure_logged_in(f):
    @wraps(f)
    def log_in_then_f(browser, *args):
        browser.prompt_for_login()
        return f(browser, *args)
    return log_in_then_f

@ensure_logged_in
def list_courses(browser):
    return list((page.get_attribute('href'), page.get_attribute('title'))\
            for page in browser.find_elements_by_css_selector('li.Mrphs-sitesNav__menuitem a'))

@ensure_logged_in
def find_assignments(browser, class_href):
    def is_asst_tab(tab):
        return tab.find_elements_by_css_selector('span.Mrphs-toolsNav__menuitem--title')[0].text == 'Assignments'

    try:
        browser.get(class_href)
        asst_tab = next(filter(is_asst_tab, browser.find_elements_by_css_selector('a.Mrphs-toolsNav__menuitem--link')))
        asst_tab.click()
    except StopIteration:
        return []

    return list((n.text, d.text) for n, d in zip(browser.find_elements_by_css_selector('a[name="asnActionLink"]'), browser.find_elements_by_css_selector('td[headers="dueDate"] span')))

if __name__ == "__main__":
    b = SakaiBrowser()
    for i in list_courses(b):
        for a in find_assignments(b, i[0]):
            print(i[1], a)
    b.close()

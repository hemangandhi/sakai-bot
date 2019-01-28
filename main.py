from functools import wraps
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def mk_browser():
    opts = Options()
    opts.set_headless()

    browser = webdriver.Firefox(options=opts)
    browser.get('https://sakai.rutgers.edu/portal')
    return browser

def login(browser, netid, password):
    browser.find_element_by_id('loginlink1').click()
    browser.find_element_by_id('username').send_keys(netid)
    browser.find_element_by_id('password').send_keys(password)
    browser.find_element_by_class('btn-submit').click()

def prompt_for_login(browser):
    netid = input("Enter your netid > ")
    password = getpass("Enter your password > ")
    login(browser, netid, password)
    while browser.current_url.startswith('https://cas.rutgers.edu'):
        print(browser.find_element_by_css_selector('#status.errors').text)
        netid = input("Enter your netid > ")
        password = getpass("Enter your password > ")
        login(browser, netid, password)

def ensure_logged_in(f):
    @wraps(f)
    def log_in_then_f(browser):
        prompt_for_login(browser)
        return f(browser)

@ensure_logged_in
def list_courses(browser):
    for page in browser.find_elements_by_css_selector('li.Mrphs-sitesNav__menuitem a span'):
        yield page.text

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.set_headless()

browser = webdriver.Firefox(options=opts)
browser.get('http://www.google.com')

assert 'Google' in browser.title

import os
import shutil
import argparse
import textwrap
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def get_path(file_):
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if name == file_:
                return os.path.abspath(os.path.join(root, name))


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    fromfile_prefix_chars='@',
    description=textwrap.dedent(""" todo fix this"""))

parser.add_argument(
    '-b', '--browser',
    help=textwrap.dedent("""Specify the browser to be used to show the subjects.
    This script supports Chrome, Edge, and Firefox on recent Windows and
     Mac operating systems. Other browsers can be used with a slight modification
     """))

args = parser.parse_args()
browser_name = args.browser
os.environ['WDM_LOCAL'] = '1'
browser = ''
if browser_name.lower() == 'chrome':
    browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager(path=r".").install()))
    if os.path.isfile('chromedriver.exe'):
        os.remove('chromedriver.exe')
    shutil.copy(get_path('chromedriver.exe'), r'.')
elif browser_name.lower() == 'edge':
    browser = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager(path=r".").install()))
    if os.path.isfile('msedgedriver.exe'):
        os.remove('msedgedriver.exe')
    shutil.copy(get_path('msedgedriver.exe'), r'.')
elif browser_name.lower() == 'firefox':
    opts = Options()
    opts.log.level = "fatal"
    browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager(path=r'.').install()), options=opts)
    if os.path.isfile('geckodriver.exe'):
        os.remove('geckodriver.exe')
    shutil.copy(get_path('geckodriver.exe'), r'.')

else:
    print('The browser specified in parameters_', browser_name, 'is not in the list of supported browsers:')
    print('Supported browsers: Chrome, Edge, Firefox')
    quit()

browser.get('https://www.google.com/')

browser.quit()
if 'geckodriver.log':
    os.remove('geckodriver.log')

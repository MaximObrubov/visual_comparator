import unittest
import configparser
import shutil
from os import path, makedirs, rmdir
from time import sleep
from PIL import Image, ImageOps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class CheckScreenshots(unittest.TestCase):

    def setUp(self):
        options = Options()
        # NOTE: uncomment to run in a background
        options.add_argument("--headless")
        options.add_argument("window-size=1400,600")
        self.driver = webdriver.Chrome(options=options, executable_path=r'./chromedriver')
        self.cleanup()
        
            
    def cleanup(self):
        current_dir = path.dirname(path.abspath(__file__))
        results_path = path.join(current_dir, 'screenshots', 'results')
        targets_path = path.join(current_dir, 'screenshots', 'targets')
        
        if path.exists(results_path):
            shutil.rmtree(path.join(current_dir, 'screenshots', 'targets'))
        if path.exists(results_path):
            shutil.rmtree(path.join(current_dir, 'screenshots', 'results'))

    def test_screenshots(self):
        breakpoints = configparser.ConfigParser()
        pages = configparser.ConfigParser()
        driver = self.driver
        
        with open('breakpoints.ini') as bps:
            breakpoints.read_file(bps)
        with open('pages.ini') as ps:
            pages.read_file(ps)
        
        for (page, url) in pages.items("Pages"):
        
            print(page, url)
        
            for section in breakpoints.sections():
                params = breakpoints._sections[section]
                w = params["width"]
                taragetpath = self.imagepath('targets', page, w)
                etalonpath = self.imagepath('etalons', page, w)
                
                try:
                    with Image.open(etalonpath) as etalon:
                        width, height = etalon.size
                except Exception as e:
                    width = w
                    height = params["height"]
                
                driver.get(url)
                driver.set_window_size(width, height)
                sleep(1.4)
                
                element = driver.find_element_by_css_selector('body')
                self.save_screenshot_from_element(taragetpath, element)
                result = self.compare_images(taragetpath, etalonpath)
                
                if result:
                    result.save(self.imagepath('results', page, w))
            
    
    def imagepath(self, type, page, breakpoint):
        current_dir = path.dirname(path.abspath(__file__))
        imagepath = path.join(current_dir, 'screenshots', type,
                              page, '{}.png'.format(breakpoint))
        if not path.exists(path.dirname(imagepath)):
            makedirs(path.dirname(imagepath))
        return imagepath

    
    def save_screenshot_from_element(self, savepath, element):
        with open(savepath, 'w+b') as screenshot:
            screenshot.write(element.screenshot_as_png)
            
    def compare_images(self, im_1, im_2):
        with Image.open(im_1) as etalon:
            with Image.open(im_2) as target:
                target.convert('RGB')
                target = ImageOps.invert(target.convert('RGB'))
                target = target.convert('RGBA')
                
                if etalon.size.height > target.size.height:
                    target = target.resize(etalon.size)
                else:
                    etalon = etalon.resize(target.size)
                target.putalpha(128)
                etalon.putalpha(150)
                result = Image.alpha_composite(etalon, target)
            return result
        return None
        

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
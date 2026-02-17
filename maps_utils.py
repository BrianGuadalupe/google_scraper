from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-blink-features=AutomationControlled')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def aceptar_cookies(driver):
    wait = WebDriverWait(driver, 10)
    try:
        try:
            WebDriverWait(driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe"))
            )
        except TimeoutException:
            pass

        # Método 1: botón con aria-label directo
        try:
            boton = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@aria-label="Aceptar todo"]')
            ))
            driver.execute_script("arguments[0].scrollIntoView(true);", boton)
            time.sleep(0.5)
            boton.click()
            driver.switch_to.default_content()
            return
        except TimeoutException:
            pass

        # Método 2: botón con span aria-hidden
        try:
            boton = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[.//span[@aria-hidden="true" and contains(text(), "Aceptar todo")]]')
            ))
            driver.execute_script("arguments[0].scrollIntoView(true);", boton)
            time.sleep(0.5)
            boton.click()
            driver.switch_to.default_content()
            return
        except TimeoutException:
            pass

        driver.switch_to.default_content()
    except Exception:
        driver.switch_to.default_content()

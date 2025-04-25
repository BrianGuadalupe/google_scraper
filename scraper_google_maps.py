from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def init_driver():
    print("Arrancando el navegador...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-blink-features=AutomationControlled')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def aceptar_cookies(driver):
    wait = WebDriverWait(driver, 10)
    try:
        # Cambiar a iframe si lo hay
        try:
            WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe")))
            print("Cambiado al iframe de consentimiento.")
        except:
            print("No hay iframe visible, seguimos sin cambiar.")

        # Método 1: botón con aria-label
        try:
            boton = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Aceptar todo"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", boton)
            time.sleep(0.5)
            boton.click()
            print("Cookies aceptadas con aria-label.")
            driver.switch_to.default_content()
            return
        except:
            pass

        # Método 2: botón con span oculto
        try:
            boton = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[.//span[@aria-hidden="true" and contains(text(), "Aceptar todo")]]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", boton)
            time.sleep(0.5)
            boton.click()
            print("Cookies aceptadas por span aria-hidden.")
            driver.switch_to.default_content()
            return
        except:
            pass

        print("No se ha podido aceptar el consentimiento.")
        driver.switch_to.default_content()

    except Exception as e:
        print("Error aceptando cookies:", e)
        driver.switch_to.default_content()

def buscar_en_maps(driver, consulta):
    driver.get("https://www.google.com/maps")
    time.sleep(3)
    aceptar_cookies(driver)
    time.sleep(3)

    wait = WebDriverWait(driver, 10)
    try:
        input_busqueda = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        input_busqueda.clear()
        input_busqueda.send_keys(consulta)
        input_busqueda.send_keys(Keys.ENTER)
        print(f"🔍 Buscando: {consulta}")
        time.sleep(5)
    except Exception as e:
        print(f"No se ha podido escribir en la barra de búsqueda para: {consulta}")
        driver.save_screenshot("error_busqueda.png")
        return False
    return True

def scroll_y_extraer(driver):
    wait = WebDriverWait(driver, 10)
    resultados = []

    try:
        scroll_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
    except:
        print("No se ha encontrado el panel de resultados.")
        return resultados

    # Hacemos scroll unas cuantas veces para que se cargue todo
    for _ in range(30):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(2)

    elementos = driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]')
    print(f"Se han cargado {len(elementos)} lugares.")

    for i, item in enumerate(elementos):
        try:
            item.click()
            time.sleep(4)

            nombre = driver.find_element(By.XPATH, '//h1[contains(@class, "DUwDvf")]').get_attribute("innerText").strip()
        except:
            nombre = "No disponible"

        try:
            telefono = driver.find_element(By.XPATH, '//button[contains(@aria-label,"Teléfono") or contains(@data-tooltip,"Teléfono")]').text
        except:
            telefono = "No disponible"

        try:
            direccion = driver.find_element(By.XPATH, '//button[contains(@aria-label,"Dirección") or contains(@data-tooltip,"Dirección")]').text
        except:
            direccion = "No disponible"

        print(f" {nombre} | {telefono} | {direccion}")
        resultados.append({
            "Nombre": nombre,
            "Teléfono": telefono,
            "Dirección": direccion
        })

    return resultados

def main():
    print("🚀 Empezamos con la búsqueda")
    driver = init_driver()
    consulta = "Fisioterapia en Madrid"

    try:
        if buscar_en_maps(driver, consulta):
            datos = scroll_y_extraer(driver)
            df = pd.DataFrame(datos)
            df.to_csv("fisioterapia_en_madrid.csv", index=False, encoding="utf-8")
            print("\n Archivo guardado: fisioterapia_en_madrid.csv")
        else:
            print(" La búsqueda no ha funcionado correctamente.")
    except Exception as e:
        print(" Error general en el proceso:", e)
    finally:
        input("\n Pulsa ENTER para cerrar el navegador...")
        driver.quit()
        print("¡Todo listo!")

if __name__ == "__main__":
    main()

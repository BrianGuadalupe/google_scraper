from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
from maps_utils import init_driver, aceptar_cookies
import time
import pandas as pd


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
        print(f"Buscando: {consulta}")
        time.sleep(5)
    except TimeoutException:
        print(f"No se ha podido escribir en la barra de búsqueda para: {consulta}")
        driver.save_screenshot("error_busqueda.png")
        return False
    return True


def scroll_y_extraer(driver):
    wait = WebDriverWait(driver, 10)
    resultados = []

    try:
        scroll_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
    except TimeoutException:
        print("No se ha encontrado el panel de resultados.")
        return resultados

    # Scroll adaptativo: para cuando no cargan nuevos resultados
    MAX_SCROLLS = 30
    SCROLL_PAUSE = 2
    prev_count = 0

    for _ in range(MAX_SCROLLS):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(SCROLL_PAUSE)
        current_count = len(driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]'))
        if current_count == prev_count:
            break
        prev_count = current_count

    elementos = driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]')
    print(f"Se han cargado {len(elementos)} lugares.")

    for item in elementos:
        nombre = "No disponible"
        try:
            item.click()
            # WebDriverWait en lugar de sleep fijo: espera hasta que el título cargue
            nombre_el = wait.until(
                EC.presence_of_element_located((By.XPATH, '//h1[contains(@class, "DUwDvf")]'))
            )
            nombre = nombre_el.get_attribute("innerText").strip()
        except (TimeoutException, NoSuchElementException,
                StaleElementReferenceException, ElementClickInterceptedException):
            pass

        # Descartar resultados sin nombre: evita filas vacías en el CSV
        if nombre == "No disponible":
            continue

        try:
            telefono = driver.find_element(
                By.XPATH, '//button[contains(@aria-label,"Teléfono") or contains(@data-tooltip,"Teléfono")]'
            ).text
        except NoSuchElementException:
            telefono = "No disponible"

        try:
            direccion = driver.find_element(
                By.XPATH, '//button[contains(@aria-label,"Dirección") or contains(@data-tooltip,"Dirección")]'
            ).text
        except NoSuchElementException:
            direccion = "No disponible"

        print(f"{nombre} | {telefono} | {direccion}")
        resultados.append({
            "Nombre": nombre,
            "Teléfono": telefono,
            "Dirección": direccion
        })

    return resultados


def main():
    print("Empezamos con la búsqueda")
    driver = init_driver()
    consulta = "Fisioterapia en Madrid"

    try:
        if buscar_en_maps(driver, consulta):
            datos = scroll_y_extraer(driver)
            df = pd.DataFrame(datos)
            df.to_csv("fisioterapia_en_madrid.csv", index=False, encoding="utf-8")
            print(f"\nArchivo guardado: fisioterapia_en_madrid.csv ({len(datos)} resultados)")
        else:
            print("La búsqueda no ha funcionado correctamente.")
    except Exception as e:
        print("Error general en el proceso:", e)
    finally:
        input("\nPulsa ENTER para cerrar el navegador...")
        driver.quit()
        print("¡Todo listo!")


if __name__ == "__main__":
    main()

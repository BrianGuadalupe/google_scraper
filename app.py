import streamlit as st
import pandas as pd
import time
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

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Buscador de negocios en Google Maps", layout="centered")

# === ESTILO VISUAL PERSONALIZADO (tipo Airbnb) ===
st.markdown("""
    <style>
    .tarjeta {
        background-color: #f8f8f8;
        padding: 16px;
        margin-bottom: 12px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    .titulo {
        font-size: 20px;
        font-weight: 600;
        color: #2c2c2c;
        margin-bottom: 8px;
    }
    .detalle {
        font-size: 16px;
        color: #555;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# === FUNCIONES DE SCRAPING ===

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
        time.sleep(5)
    except TimeoutException:
        driver.save_screenshot("error_busqueda.png")
        return False
    return True


def scroll_y_extraer(driver):
    wait = WebDriverWait(driver, 10)
    resultados = []

    try:
        scroll_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
    except TimeoutException:
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

        try:
            enlace_web = driver.find_element(
                By.XPATH, '//a[contains(@class, "CsEnBe") and contains(@href, "http")]'
            )
            web = enlace_web.get_attribute("href")
        except NoSuchElementException:
            web = "No disponible"

        resultados.append({
            "Nombre": nombre,
            "Teléfono": telefono,
            "Dirección": direccion,
            "Web": web
        })

    return resultados


def ejecutar_scraping(consulta):
    st.info(f"Iniciando búsqueda: {consulta}")
    driver = init_driver()
    try:
        if buscar_en_maps(driver, consulta):
            with st.spinner("Extrayendo datos, por favor espere..."):
                datos = scroll_y_extraer(driver)
            if datos:
                st.success(f"Se han extraído {len(datos)} resultados.")
            else:
                st.warning("No se encontraron resultados.")
            return pd.DataFrame(datos)
        else:
            st.error("Error al buscar en Google Maps.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error inesperado: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()


# === INTERFAZ DE USUARIO ===

st.title("Buscador visual en Google Maps")

consulta = st.text_input("¿Qué deseas buscar? (Ejemplo: 'Fisioterapia en Madrid')")

if st.button("Buscar"):
    if consulta.strip():
        df = ejecutar_scraping(consulta)

        if not df.empty:
            for _, row in df.iterrows():
                st.markdown(f"""
                    <div class="tarjeta">
                        <div class="titulo">{row['Nombre']}</div>
                        <div class="detalle">📍 {row['Dirección']}</div>
                        <div class="detalle">📞 {row['Teléfono']}</div>
                        <div class="detalle">🌐 <a href="{row['Web']}" target="_blank">{row['Web']}</a></div>
                    </div>
                """, unsafe_allow_html=True)

            st.download_button(
                label="Descargar resultados en CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="resultados_google_maps.csv",
                mime="text/csv"
            )
        else:
            st.warning("No se han podido extraer resultados.")
    else:
        st.warning("Introduce una búsqueda antes de pulsar el botón.")

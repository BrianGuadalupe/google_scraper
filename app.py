import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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
            WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe")))
        except:
            pass

        try:
            boton = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Aceptar todo"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", boton)
            time.sleep(0.5)
            boton.click()
            driver.switch_to.default_content()
            return
        except:
            pass

        try:
            boton = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[.//span[@aria-hidden="true" and contains(text(), "Aceptar todo")]]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", boton)
            time.sleep(0.5)
            boton.click()
            driver.switch_to.default_content()
            return
        except:
            pass

        driver.switch_to.default_content()
    except:
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
        time.sleep(5)
    except:
        driver.save_screenshot("error_busqueda.png")
        return False
    return True

def scroll_y_extraer(driver):
    wait = WebDriverWait(driver, 10)
    resultados = []

    try:
        scroll_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
    except:
        return resultados

    for _ in range(30):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(2)

    elementos = driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]')

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

        try:
            enlace_web = driver.find_element(By.XPATH, '//a[contains(@class, "CsEnBe") and contains(@href, "http")]')
            web = enlace_web.get_attribute("href")
        except:
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

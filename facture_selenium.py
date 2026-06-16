import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

class FactureSelenium:
    def __init__(self, headless=False):
        self.base_url = Config.FACTURE_URL
        self.username = Config.USERNAME
        self.password = Config.PASSWORD
        self.download_dir = Config.DOWNLOAD_DIR
        
        # Crear directorio de descargas
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Configurar Chrome
        chrome_options = Options()
        
        # Configurar descargas automáticas
        prefs = {
            "download.default_directory": os.path.abspath(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        self.factura_uuid = None

    def login(self):
        """Iniciar sesión en Facture App"""
        try:
            print("🔐 Iniciando sesión...")
            self.driver.get(f"{self.base_url}/ws/login.jsp")
            time.sleep(3)
            
            # Completar formulario
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(self.username)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)
            
            # Hacer click en login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(5)
            
            # Verificar login exitoso
            if "login" not in self.driver.current_url.lower():
                print("✅ Login exitoso")
                return True
            else:
                print("❌ Login fallido")
                return False
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False

    def navigate_to_facturas(self):
        """Navegar a la sección de facturas"""
        try:
            print("🧭 Navegando a facturas...")
            time.sleep(3)
            
            # Buscar el menú de facturación - Opción 1
            try:
                facturacion_menu = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Facturación')]"))
                )
                facturacion_menu.click()
                time.sleep(2)
            except:
                # Opción 2: Menú desplegable
                menu_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'menu') or contains(@data-toggle, 'dropdown')]")
                menu_btn.click()
                time.sleep(1)
                
                facturacion_menu = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Facturación') or contains(text(), 'Facturas')]"))
                )
                facturacion_menu.click()
                time.sleep(2)
            
            # Buscar submenú "Facturas"
            try:
                facturas_link = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Facturas') or contains(text(), 'Listado')]"))
                )
                facturas_link.click()
                time.sleep(4)
            except:
                # Si ya estamos en la página de facturas
                pass
            
            print("✅ Navegación exitosa")
            return True
            
        except Exception as e:
            print(f"❌ Error navegando: {e}")
            return False

    def search_and_download_pdf(self, uuid):
        """Buscar factura por UUID y descargar PDF"""
        try:
            self.factura_uuid = uuid
            print(f"🔍 Buscando factura con UUID: {uuid}")
            
            # Esperar que cargue la tabla
            time.sleep(3)
            
            # Buscar el input de búsqueda
            try:
                # Opción 1: Input de búsqueda
                search_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Buscar...' or contains(@class, 'search')]"))
                )
                search_input.clear()
                search_input.send_keys(uuid[:8])  # Buscar por primeros 8 caracteres
                time.sleep(3)
            except:
                print("ℹ️ No se encontró campo de búsqueda, buscando en la tabla...")
            
            # Buscar la fila de la factura
            factura_row = None
            
            # Opción 1: Buscar por UUID parcial
            try:
                factura_row = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//tr[contains(., '{uuid[:8]}')]"))
                )
            except:
                # Opción 2: Buscar por el UUID completo
                try:
                    factura_row = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, f"//tr[contains(., '{uuid}')]"))
                    )
                except:
                    # Opción 3: Buscar en todas las filas
                    rows = self.driver.find_elements(By.XPATH, "//tbody/tr")
                    for row in rows:
                        if uuid[:8] in row.text:
                            factura_row = row
                            break
            
            if not factura_row:
                print("❌ No se encontró la factura en la tabla")
                self.take_screenshot("factura_no_encontrada.png")
                return None
            
            print("✅ Factura encontrada en la tabla")
            
            # Buscar el botón de descarga PDF
            try:
                # Buscar dentro de la fila encontrada
                pdf_button = factura_row.find_element(By.XPATH, ".//button[contains(@title, 'PDF') or contains(., 'PDF') or contains(@class, 'pdf')]")
                pdf_button.click()
            except:
                # Si no está en la fila, buscar en toda la página
                try:
                    pdf_button = self.driver.find_element(By.XPATH, "//button[contains(@title, 'PDF') or contains(., 'PDF') or contains(@class, 'pdf')]")
                    pdf_button.click()
                except:
                    print("❌ No se encontró el botón de descarga PDF")
                    return None
            
            # Esperar descarga
            print("📥 Descargando PDF...")
            time.sleep(8)
            
            # Verificar archivo descargado
            downloaded_files = os.listdir(self.download_dir)
            pdf_files = [f for f in downloaded_files if f.endswith('.pdf')]
            
            if pdf_files:
                # Tomar el archivo más reciente
                pdf_path = os.path.join(self.download_dir, pdf_files[-1])
                print(f"✅ PDF descargado: {pdf_path}")
                return pdf_path
            else:
                print("❌ No se encontró el PDF descargado")
                return None
                
        except Exception as e:
            print(f"❌ Error buscando/descargando PDF: {e}")
            self.take_screenshot("error_busqueda.png")
            return None

    def take_screenshot(self, filename):
        """Tomar captura de pantalla"""
        screenshot_path = os.path.join(self.download_dir, filename)
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot: {screenshot_path}")

    def close(self):
        """Cerrar el navegador"""
        self.driver.quit()
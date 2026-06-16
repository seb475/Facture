import time
from facture_api import FactureAPI
from facture_selenium import FactureSelenium

def main():
    print("=" * 60)
    print("🚀 INTEGRACIÓN FACTURE - API + SELENIUM")
    print("=" * 60)
    
    api = FactureAPI()
    factura_info = None
    
    try:
        # ============================================
        # PARTE 1: CREAR FACTURA CON API
        # ============================================
        print("\n📌 PARTE 1: CREAR FACTURA CON API")
        print("-" * 50)
        
        # 1. Obtener token
        print("\n1. Obteniendo token...")
        api.get_token()
        
        # 2. Obtener emisor
        print("\n2. Obteniendo emisor...")
        emisor = api.get_emisor()
        if not emisor:
            print("❌ No se pudo obtener emisor. Saliendo...")
            return
        emisor_id = emisor['id']
        
        # 3. Obtener sucursal
        print("\n3. Obteniendo sucursal...")
        sucursal = api.get_sucursal(emisor_id)
        if not sucursal:
            print("❌ No se pudo obtener sucursal. Saliendo...")
            return
        sucursal_id = sucursal['id']
        
        # 4. Obtener serie (opcional)
        print("\n4. Obteniendo serie...")
        serie = api.get_serie()
        serie_id = serie['id'] if serie else None
        
        # 5. Crear factura
        print("\n5. Creando factura en entorno de pruebas...")
        resultado = api.create_factura(emisor_id, sucursal_id, serie_id)
        
        if not resultado.get('succeed'):
            print(f"❌ Error creando factura: {resultado.get('message')}")
            return
        
        factura_info = resultado.get('entity', {}).get('data', {})
        uuid = factura_info.get('uuid')
        factura_id = factura_info.get('id')
        
        print("\n✅ Factura creada exitosamente:")
        print(f"   ID: {factura_id}")
        print(f"   UUID: {uuid}")
        print(f"   Folio: {factura_info.get('folio')}")
        print(f"   Total: ${factura_info.get('total')}")
        
        # ============================================
        # PARTE 2: DESCARGAR PDF CON SELENIUM
        # ============================================
        print("\n📌 PARTE 2: DESCARGAR PDF CON SELENIUM")
        print("-" * 50)
        
        selenium = FactureSelenium()
        
        try:
            # 1. Login
            print("\n1. Iniciando sesión...")
            if not selenium.login():
                print("❌ No se pudo iniciar sesión")
                return
            
            # 2. Navegar a facturas
            print("\n2. Navegando a sección de facturas...")
            if not selenium.navigate_to_facturas():
                print("❌ No se pudo navegar a facturas")
                return
            
            # 3. Buscar y descargar PDF
            print("\n3. Buscando y descargando PDF...")
            pdf_path = selenium.search_and_download_pdf(uuid)
            
            # 4. Resultado
            print("\n" + "=" * 60)
            print("📊 RESULTADO FINAL")
            print("=" * 60)
            
            if pdf_path:
                print("✅ ¡INTEGRACIÓN COMPLETA!")
                print(f"   📋 UUID: {uuid}")
                print(f"   📋 Folio: {factura_info.get('folio')}")
                print(f"   📄 PDF: {pdf_path}")
            else:
                print("⚠️ Factura creada pero no se descargó el PDF")
                print(f"   📋 UUID: {uuid}")
                print("   📸 Revisa capturas de pantalla en carpeta downloads/")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error en Selenium: {e}")
            selenium.take_screenshot("error_selenium.png")
        finally:
            selenium.close()
            
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
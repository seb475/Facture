import requests
from config import Config

class FactureAPI:
    def __init__(self):
        self.base_url = Config.FACTURE_URL
        self.client_id = Config.CLIENT_ID
        self.client_secret = Config.CLIENT_SECRET
        self.username = Config.USERNAME
        self.password = Config.PASSWORD
        self.access_token = None

    def get_token(self):
        """Obtener access token"""
        url = f"{self.base_url}/api/authorize"
        
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "scope": "emisor facturacion timbrado",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        print("🔑 Obteniendo token...")
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            response.raise_for_status()
        
        result = response.json()
        self.access_token = result.get('access_token')
        print(f"✅ Token obtenido: {self.access_token[:20]}...")
        return result

    def get_emisor(self):
        """Obtener el primer emisor disponible"""
        self._ensure_token()
        
        url = f"{self.base_url}/api/emisor/find"
        headers = self._get_headers()
        
        print("🏢 Consultando emisor...")
        response = requests.get(url, params={"offset": 0, "size": 10}, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get('succeed'):
            items = result.get('pagination', {}).get('items', [])
            if items:
                emisor = items[0]
                print(f"✅ Emisor: {emisor['nombre']} (ID: {emisor['id']})")
                return emisor
        print("❌ No se encontraron emisores")
        return None

    def get_sucursal(self, emisor_id):
        """Obtener la primera sucursal del emisor"""
        self._ensure_token()
        
        url = f"{self.base_url}/api/sucursal/find"
        headers = self._get_headers()
        params = {
            "offset": 0, 
            "size": 10,
            "filter": f"emisor.id:eq!{emisor_id}"
        }
        
        print(f"🏢 Consultando sucursal para emisor {emisor_id}...")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get('succeed'):
            items = result.get('pagination', {}).get('items', [])
            if items:
                sucursal = items[0]
                print(f"✅ Sucursal: {sucursal['nombre']} (ID: {sucursal['id']})")
                return sucursal
        print("❌ No se encontraron sucursales")
        return None

    def get_serie(self):
        """Obtener la primera serie disponible"""
        self._ensure_token()
        
        url = f"{self.base_url}/api/serie/find"
        headers = self._get_headers()
        
        print("🔢 Consultando serie...")
        response = requests.get(url, params={"offset": 0, "size": 10}, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get('succeed'):
            items = result.get('pagination', {}).get('items', [])
            if items:
                serie = items[0]
                print(f"✅ Serie: {serie['nombre']} (ID: {serie['id']})")
                return serie
        print("ℹ️ No se encontraron series, se usará sin serie")
        return None

    def create_factura(self, emisor_id, sucursal_id, serie_id=None):
        """Crear una factura en entorno de pruebas"""
        self._ensure_token()
        
        url = f"{self.base_url}/api/timbrado32/pruebas"
        headers = self._get_headers()
        
        factura_data = {
            "comprobantes": [{
                "Emisor": {"id": emisor_id},
                "Receptor": {
                    "nombre": "CLIENTE DE PRUEBA",
                    "rfc": "XAXX010101000",
                    "regimen_fiscal": 601,
                    "uso_cfdi": "G01",
                    "cp": "12345"
                },
                "Conceptos": [{
                    "clave_prod_serv": "10101010",
                    "clave_unidad": "H87",
                    "unidad": "PIEZA",
                    "cantidad": 1,
                    "descripcion": "Producto de prueba",
                    "valor_unitario": 100.00,
                    "importe": 100.00,
                    "impuesto": [{
                        "base": 100.00,
                        "impuesto": "002",
                        "tipo": "Tasa",
                        "tasa": 0.16,
                        "importe": 16.00
                    }]
                }],
                "sucursal": {"id": sucursal_id},
                "forma_pago": "PUE",
                "metodo_pago": "PUE",
                "moneda": "MXN",
                "tipo_comprobante": "I",
                "lugar_expedicion": "12345"
            }]
        }
        
        if serie_id:
            factura_data["comprobantes"][0]["serie"] = {"id": serie_id}
        
        payload = {"entity": {"data": factura_data}}
        
        print("📄 Creando factura...")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            response.raise_for_status()
        
        result = response.json()
        return result

    def _ensure_token(self):
        if not self.access_token:
            self.get_token()

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
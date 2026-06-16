import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

class FactureDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )

    def guardar_factura(self, factura_data):
        cursor = self.conn.cursor()
        
        query = """
            INSERT INTO facturas (
                facture_id, uuid, folio, serie, total, fecha_timbrado
            ) VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (facture_id) DO UPDATE
            SET uuid = EXCLUDED.uuid, folio = EXCLUDED.folio,
                serie = EXCLUDED.serie, total = EXCLUDED.total
            RETURNING id
        """
        
        cursor.execute(query, (
            factura_data.get('id'),
            factura_data.get('uuid'),
            factura_data.get('folio'),
            factura_data.get('serie'),
            factura_data.get('total')
        ))
        
        db_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        print(f"✅ Factura guardada en DB (ID: {db_id})")
        return db_id

    def cancelar_factura(self, facture_id):
        cursor = self.conn.cursor()
        
        query = """
            UPDATE facturas 
            SET cancelada = TRUE, fecha_cancelacion = NOW()
            WHERE facture_id = %s
        """
        
        cursor.execute(query, (facture_id,))
        self.conn.commit()
        cursor.close()
        print(f"✅ Factura {facture_id} cancelada en DB")

    def actualizar_pdf_path(self, facture_id, pdf_path):
        cursor = self.conn.cursor()
        
        query = "UPDATE facturas SET pdf_path = %s WHERE facture_id = %s"
        cursor.execute(query, (pdf_path, facture_id))
        self.conn.commit()
        cursor.close()
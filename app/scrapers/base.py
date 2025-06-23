from typing import List, Dict
from app.db import Noticia, Media
from sqlalchemy.orm.exc import NoResultFound

class BaseScraper:
    def __init__(self, fecha_limite=None):
        self.fecha_limite = fecha_limite
    def scrape(self, db) -> int:
        """Método que debe implementar cada scraper. Debe guardar noticias usando la sesión db y devolver la cantidad guardada."""
        raise NotImplementedError 

    def _guardar_noticia(self, db, noticia_data: Dict):
        """
        Guarda una noticia en la base de datos, manejando la creación del medio si no existe.
        """
        try:
            # Verificar si la noticia ya existe por URL
            db.query(Noticia).filter_by(url=noticia_data["url"]).one()
            print(f"⏭️  Noticia ya existe: {noticia_data['titulo']}")
            return False
        except NoResultFound:
            # La noticia no existe, continuar
            pass
        except Exception as e:
            print(f"🚨 Error al verificar existencia de noticia: {e}")
            return False

        try:
            media_name = noticia_data.pop("media_name")
            media = None
            try:
                media = db.query(Media).filter_by(name=media_name).one()
            except NoResultFound:
                print(f"📰 Creando nuevo medio: {media_name}")
                media = Media(name=media_name)
                db.add(media)

            noticia_obj = Noticia(
                titulo=noticia_data["titulo"],
                contenido=noticia_data["contenido"],
                contenido_crudo=noticia_data.get("contenido_crudo", ""),
                fecha=noticia_data["fecha"],
                url=noticia_data["url"],
                media=media
            )
            
            db.add(noticia_obj)
            db.commit()
            print(f"✅ Noticia guardada: {noticia_data['titulo']}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar noticia: {e}")
            db.rollback()
            return False 
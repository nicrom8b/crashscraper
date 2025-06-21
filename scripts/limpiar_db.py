from app.db import SessionLocal, Noticia

if __name__ == "__main__":
    db = SessionLocal()
    try:
        deleted = db.query(Noticia).delete()
        db.commit()
        print(f"Se eliminaron {deleted} registros de la tabla 'noticias'.")
    except Exception as e:
        db.rollback()
        print(f"Error al limpiar la base de datos: {e}")
    finally:
        db.close() 
from app.db import SessionLocal, Noticia

if __name__ == "__main__":
    db = SessionLocal()
    noticias = db.query(Noticia).order_by(Noticia.fecha.desc()).all()
    for n in noticias:
        print(f"{n.fecha} | {n.titulo} | Accidente: {n.es_accidente_transito} | {n.url}")
    db.close() 
#!/bin/bash

# Script para crear un dump de la base de datos
# Configuración
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="example"
DB_NAME="accidentes_craper"

# Crear timestamp para el nombre del archivo
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_FILENAME="dump_accidentes_craper_${TIMESTAMP}.sql"
DUMP_PATH="dumps/${DUMP_FILENAME}"

# Crear directorio dumps si no existe
mkdir -p dumps

echo "🗄️  Creando dump de la base de datos..."
echo "📁 Archivo: ${DUMP_PATH}"
echo "🔗 Host: ${DB_HOST}:${DB_PORT}"
echo "📊 Base de datos: ${DB_NAME}"

# Crear el dump
mysqldump \
    --host=${DB_HOST} \
    --port=${DB_PORT} \
    --user=${DB_USER} \
    --password=${DB_PASSWORD} \
    --single-transaction \
    --routines \
    --triggers \
    --add-drop-database \
    --create-options \
    ${DB_NAME} > ${DUMP_PATH}

if [ $? -eq 0 ]; then
    echo "✅ Dump creado exitosamente: ${DUMP_PATH}"
    
    # Mostrar información del archivo
    FILE_SIZE=$(stat -f%z "${DUMP_PATH}" 2>/dev/null || stat -c%s "${DUMP_PATH}" 2>/dev/null || echo "0")
    echo "📏 Tamaño del archivo: ${FILE_SIZE} bytes ($(($FILE_SIZE/1024)) KB)"
else
    echo "❌ Error al crear el dump"
    exit 1
fi 
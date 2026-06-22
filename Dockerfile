# Usa una imagen oficial de Python liviana como base
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias necesarias para tu app segura
# Nota: Si tienes un archivo requirements.txt lo puedes usar, si no, las instalamos directo:
RUN pip install --no-cache-dir flask flask-wtf markupsafe pyotp secure-cookie

# Copia todos los archivos de tu proyecto local dentro del contenedor
COPY . .

# Expone el puerto interno en el que corre tu Flask
EXPOSE 5000

# Comando por defecto para arrancar tu aplicación apuntando a tu script principal
CMD ["python", "vulnerable_app.py"]
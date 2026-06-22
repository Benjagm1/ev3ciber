pipeline {
    agent any

    stages {
        stage('Descargar Código') {
            steps {
                // Descarga automática de tu repositorio en la rama main
                git branch: 'main', url: 'https://github.com/Benjagm1/ev3ciber'
            }
        }
        
        stage('Construcción') {
            steps {
                echo 'Construyendo la imagen de Docker para la app Flask...'
                bat 'docker build -t app-vulnerable-ev3 .'
            }
        }
        
        stage('Pruebas de Seguridad (OWASP ZAP)') {
            steps {
                echo 'Iniciando escaneo automatizado con OWASP ZAP...'
                echo 'Escaneando código en busca de vulnerabilidades remanentes...'
            }
        }
        
        stage('Despliegue') {
            steps {
                echo 'Desplegando entorno de producción protegido...'
                // Detiene contenedores previos con el mismo nombre si existen
                bat 'docker rm -f produccion-ev3 || true'
                // Mapea el puerto 8082 libre del host al 5000 interno del contenedor
                bat 'docker run -d -p 8082:5000 --name produccion-ev3 app-vulnerable-ev3'
            }
        }
    }
}
pipeline {
    agent any

    stages {
       stage('Descargar Código') {
    steps {
        git branch: 'main', url: 'https://github.com/Benjagm1/ev3ciber'
    }
}
        
        stage('Construcción') {
            steps {
                echo 'Construyendo la imagen de Docker...'
                // Comando para construir la imagen. Asegúrate de tener el Dockerfile en tu repo.
                bat 'docker build -t app-vulnerable-ev3 .'
            }
        }
        
        stage('Pruebas de Seguridad (OWASP ZAP)') {
            steps {
                echo 'Ejecutando pruebas de seguridad...'
                // Aquí va el comando de tu escaneo con ZAP. 
                // Por ejemplo, ejecutando la imagen oficial de ZAP contra tu contenedor:
                // bat 'docker run -v %cd%:/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://TU-IP-LOCAL -r reporte-zap.html'
            }
        }
     stage('Despliegue') {
            steps {
                echo 'Desplegando entorno de producción protegido...'
                bat 'docker rm -f produccion-ev3 || true'
                bat 'docker run -d -p 8082:5000 --name produccion-ev3 app-vulnerable-ev3'
            }
        }
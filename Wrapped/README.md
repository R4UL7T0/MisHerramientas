## Descripción:

Script automatizado de reconocimiento en versión de prueba para prácticas de seguridad ofensiva. Realiza un análisis completo de objetivos (IP o dominio) mediante herramientas estándar.

## Características:

- Detección automática de puertos web (80,443,8080,8000,8888,8443,3000,5000,4000)
- Resolución inversa de DNS y extracción de dominios desde headers HTTP
- Detección de Wildcard DNS con filtrado automático de falsos positivos
- Modo sigiloso (-s) para escaneos lentos
- Reporte en HTML con estructura profesional
- Limpieza automática de archivos temporales

## Uso:

```bash
Sintaxis básica:
./reconnaissanceWrappedR4_V1.sh <IP|DOMINIO> [OPCIONES]

Opciones:

-w	Wordlist para directory fuzzing	/usr/share/wordlists/dirb/common.txt
-W	Wordlist para subdomain fuzzing	/usr/share/wordlists/dirb/big.txt
-o	Archivo de reporte de salida (HTML)	./recon_<target>_<timestamp>.html
-t	Número de hilos para fuzzing	50
-p	Puertos específicos para nmap	Top 1000
-s	Modo sigiloso (escaneo más lento -T2)	-T4
-h	Mostrar ayuda	-
```

## Requisitos previos:

```bash
sudo apt update
sudo apt install nmap gobuster ffuf whatweb dnsutils curl
```

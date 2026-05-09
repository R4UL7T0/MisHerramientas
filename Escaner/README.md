# Nota
Cada reporte se guarda en un archivo llamado Escaneo_<IP>.zip 

# Requerimientos:

pip install PySocks 
pip install requests

# Ejemplos:

## Normal
python3 EscanerPro.py <IP>

## Escaneo rápido
python3 EscanerPro.py 192.168.1.1 --fast -p <PORT>,<PORT>

## Escaneo a dominio
python3 EscanerPro.py DOMAIN -p <PORT>,<PORT>

## Modo INSANO
python3 EscanerPro.py 192.168.1.1 --insane -p 1-500

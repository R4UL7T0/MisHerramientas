#!/usr/bin/env python3
"""
Escáner de puertos ULTRA RÁPIDO - R4-SEC Security Scanner
Uso: python3 EscanerPro.py <ip> [-p puertos] [--fast] [--insane]
"""

import socket
import argparse
import threading
from datetime import datetime
from queue import Queue
import sys
import time
import re
import zipfile
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== BANNER PRINCIPAL R4-SEC ====================
def show_banner():
    """Muestra el banner R4-SEC al inicio"""
    banner = f"""
{Colors.BLACK_BG}{Colors.WHITE}╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                                                                      {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ██████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE} ██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE} ██████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                   {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██╔══██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ██╔════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██╔════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██╔════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                   {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██████╔╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}█████╗  {Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║     {Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                   {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██╔══██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ╚════██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██╔══╝  {Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║     {Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                   {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██║  ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ███████║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚██████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                   {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ╚═╝  ╚═╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚═╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE} ╚═════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                   {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                                                                      {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}╔══════════════════════════════════════════════════════════════════════════════════════════════╗{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}          Escáner de Puertos Avanzado v4.0 - Modos: NORMAL | FAST | INSANE          {Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}                      Herramienta de Seguridad - R4-SEC Team                         {Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}╚══════════════════════════════════════════════════════════════════════════════════════════════╝{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(banner)

# ==================== BANNER GRANDE R4-SEC ====================
def show_banner_big():
    """Versión grande del banner R4-SEC"""
    banner = f"""
{Colors.BLACK_BG}{Colors.WHITE}╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                                                                                        {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}     ███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE} ██████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}        ██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██╔══██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}     ██╔════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██╔════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██╔════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}        ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██████╔╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}     ███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}█████╗  {Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}         ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██╔══██╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}     ╚════██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██╔══╝  {Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}         ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}      ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}    ║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ██║  ██║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE} ███████║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚██████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}        ███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}███████╗{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}   ╚═╝  ╚═╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE} ╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE} ╚═════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}        ╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}╚══════╝{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}                                                                                                                        {Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}                    Escáner de Puertos Profesional - Modos: NORMAL | FAST | INSANE                    {Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}                              R4-SEC Security Scanner - Versión 4.0                                {Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}                      Detección de Versiones | Banner Grabbing | Exportación ZIP                      {Colors.BLACK_BG}{Colors.ORANGE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}║{Colors.RESET}{Colors.BLACK_BG}{Colors.ORANGE}╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝{Colors.BLACK_BG}{Colors.WHITE}║
{Colors.BLACK_BG}{Colors.WHITE}╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(banner)

# Colores para output - MODIFICADOS A NARANJA Y BLANCO CON BORDE NEGRO
class Colors:
    ORANGE = '\033[38;5;214m'      # Naranja intenso
    GREEN = '\033[38;5;214m'       # Cambiado a naranja
    RED = '\033[38;5;214m'         # Cambiado a naranja
    YELLOW = '\033[38;5;214m'      # Cambiado a naranja
    BLUE = '\033[38;5;214m'        # Cambiado a naranja
    CYAN = '\033[38;5;214m'        # Cambiado a naranja
    MAGENTA = '\033[38;5;214m'     # Cambiado a naranja
    WHITE = '\033[97m'             # Blanco para el banner
    BLACK = '\033[30m'             # Negro
    BLACK_BG = '\033[40m'          # Fondo negro
    RESET = '\033[0m'
    BOLD = '\033[1m'

class FastScanner:
    def __init__(self, mode='normal'):
        self.mode = mode
        
        # Configuración según modo
        if mode == 'insane':
            self.timeout = 0.3
            self.max_threads = 5000
            self.banner_timeout = 0.2
            self.grab_banners = False
            print(f"{Colors.ORANGE}{Colors.BOLD}[!] MODO INSANO ACTIVADO - Máxima velocidad (sin banners){Colors.RESET}")
        elif mode == 'fast':
            self.timeout = 0.5
            self.max_threads = 2000
            self.banner_timeout = 0.3
            self.grab_banners = True
            print(f"{Colors.ORANGE}{Colors.BOLD}[!] MODO RÁPIDO ACTIVADO{Colors.RESET}")
        else:
            self.timeout = 1.0
            self.max_threads = 1000
            self.banner_timeout = 0.5
            self.grab_banners = True
            print(f"{Colors.ORANGE}{Colors.BOLD}[!] MODO NORMAL ACTIVADO{Colors.RESET}")
    
    def get_banner_and_version(self, ip, port, timeout):
        """Obtiene banner y detecta versión del servicio"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            
            # Enviar comandos específicos según el puerto
            commands = {
                21: b'HELP\r\n',
                22: b'SSH-2.0-Client\r\n',
                25: b'EHLO test.com\r\n',
                80: b'HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n',
                110: b'CAPA\r\n',
                143: b'CAPABILITY\r\n',
                443: b'HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n',
                3306: b'\n',
                5432: b'\n',
                27017: b'\n',
                8080: b'HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n',
                8443: b'HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n',
            }
            
            if port in commands:
                sock.send(commands[port])
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            version = self.extract_version(banner, port)
            service = self.get_service_name(port)
            
            return service, version, banner[:200]
            
        except Exception as e:
            return self.get_service_name(port), "Versión desconocida", "Banner no disponible"
    
    def extract_version(self, banner, port):
        """Extrae versión específica del banner"""
        if not banner:
            return "Versión desconocida"
        
        version_patterns = {
            'ssh': r'SSH-([\d\.]+)',
            'apache': r'Apache/([\d\.]+)',
            'nginx': r'nginx/([\d\.]+)',
            'openssh': r'OpenSSH[_\s]([\d\.]+)',
            'mysql': r'mysql[\s]?([\d\.]+)',
            'postgresql': r'PostgreSQL[\s]?([\d\.]+)',
            'ftp': r'FTP[\s]?([\d\.]+)',
            'smtp': r'SMTP[\s]?([\d\.]+)',
            'php': r'PHP/([\d\.]+)',
            'python': r'Python/([\d\.]+)',
        }
        
        for service, pattern in version_patterns.items():
            match = re.search(pattern, banner, re.IGNORECASE)
            if match:
                return f"{service.upper()} {match.group(1)}"
        
        version_info = {
            21: self.detect_ftp_version(banner),
            22: self.detect_ssh_version(banner),
            80: self.detect_http_version(banner),
            443: self.detect_http_version(banner),
            3306: self.detect_mysql_version(banner),
            5432: self.detect_postgres_version(banner),
        }
        
        if port in version_info and version_info[port]:
            return version_info[port]
        
        if banner and len(banner) > 10:
            return banner[:50]
        
        return "Versión desconocida"
    
    def detect_ftp_version(self, banner):
        if 'vsFTPd' in banner:
            return "vsFTPd"
        elif 'ProFTPD' in banner:
            return "ProFTPD"
        elif 'FileZilla' in banner:
            return "FileZilla Server"
        return "FTP Server"
    
    def detect_ssh_version(self, banner):
        if 'OpenSSH' in banner:
            match = re.search(r'OpenSSH[_\s]([\d\.]+)', banner)
            if match:
                return f"OpenSSH {match.group(1)}"
        return "SSH Server"
    
    def detect_http_version(self, banner):
        if 'Apache' in banner:
            match = re.search(r'Apache/([\d\.]+)', banner)
            if match:
                return f"Apache {match.group(1)}"
        elif 'nginx' in banner:
            match = re.search(r'nginx/([\d\.]+)', banner)
            if match:
                return f"nginx {match.group(1)}"
        elif 'IIS' in banner:
            return "Microsoft IIS"
        elif 'lighttpd' in banner:
            return "Lighttpd"
        return "Web Server"
    
    def detect_mysql_version(self, banner):
        match = re.search(r'([\d\.]+)-?[a-zA-Z]?', banner)
        if match:
            return f"MySQL {match.group(1)}"
        return "MySQL Server"
    
    def detect_postgres_version(self, banner):
        match = re.search(r'PostgreSQL[\s]?([\d\.]+)', banner)
        if match:
            return f"PostgreSQL {match.group(1)}"
        return "PostgreSQL Server"
    
    def get_service_name(self, port):
        servicios = {
            21: "FTP - File Transfer Protocol",
            22: "SSH - Secure Shell",
            23: "Telnet - Remote Login",
            25: "SMTP - Email Delivery",
            53: "DNS - Domain Name System",
            80: "HTTP - Web Server",
            110: "POP3 - Email Retrieval",
            143: "IMAP - Email Access",
            443: "HTTPS - Secure Web Server",
            445: "SMB - File Sharing",
            3306: "MySQL - Database",
            3389: "RDP - Remote Desktop",
            5432: "PostgreSQL - Database",
            27017: "MongoDB - NoSQL Database",
            8080: "HTTP-Alt - Proxy/Web Server",
            8443: "HTTPS-Alt - Secure Web Server",
            139: "NetBIOS - File Sharing",
            161: "SNMP - Network Monitoring",
            389: "LDAP - Directory Service",
            636: "LDAPS - Secure LDAP",
            990: "FTPS - Secure FTP",
            992: "TelnetS - Secure Telnet",
            993: "IMAPS - Secure IMAP",
            995: "POP3S - Secure POP3",
            5900: "VNC - Remote Desktop",
            6379: "Redis - Database",
            9200: "Elasticsearch",
            5601: "Kibana",
            9092: "Kafka"
        }
        return servicios.get(port, f"Puerto {port}")
    
    def scan_port(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            
            if result == 0:
                if self.grab_banners:
                    service, version, banner = self.get_banner_and_version(ip, port, self.banner_timeout)
                else:
                    service = self.get_service_name(port)
                    version = "Versión no detectada (modo insane)"
                    banner = "Banner omitido por velocidad"
                
                sock.close()
                return True, port, service, version, banner
            
            sock.close()
            return False, port, None, None, None
            
        except:
            return False, port, None, None, None
    
    def scan_ports(self, ip, ports, threads=None):
        if threads is None:
            threads = self.max_threads
        
        if self.mode == 'insane':
            max_workers = min(threads, 5000)
        elif self.mode == 'fast':
            max_workers = min(threads, 2000)
        else:
            max_workers = min(threads, 1000)
        
        print(f"{Colors.ORANGE}[*] Usando {max_workers} hilos{Colors.RESET}")
        
        open_ports = []
        port_list = list(ports)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scan_port, ip, port): port for port in port_list}
            
            for future in as_completed(futures):
                is_open, port, service, version, banner = future.result()
                if is_open:
                    open_ports.append((port, service, version, banner))
                    print(f"{Colors.ORANGE}[+] Puerto {port}{Colors.RESET} {Colors.ORANGE}ABIERTO{Colors.RESET}")
                    print(f"    {Colors.ORANGE}Servicio:{Colors.RESET} {service}")
                    print(f"    {Colors.ORANGE}Versión:{Colors.RESET} {version}")
                    if banner and banner != "Banner omitido por velocidad":
                        print(f"    {Colors.ORANGE}Banner:{Colors.RESET} {banner[:100]}...")
                    print()
        
        return sorted(open_ports, key=lambda x: x[0])
    
    def check_host(self, ip, timeout=1):
        """Verifica si el host está activo"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 80))
            sock.close()
            
            if result == 0:
                return True
            
            import subprocess
            import platform
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            result = subprocess.run(['ping', param, '1', '-W', '1', ip], 
                                  capture_output=True, timeout=timeout)
            return result.returncode == 0
            
        except:
            return False

def save_results_to_zip(target_ip, target_hostname, open_ports, scan_time, total_ports, mode, zip_filename):
    """Guarda los resultados en un archivo ZIP con TXT y CSV"""
    
    base_name = f"Escaneo_{target_ip.replace('.', '_')}"
    txt_filename = f"{base_name}.txt"
    csv_filename = f"{base_name}.csv"
    
    txt_content = generate_txt_content(target_ip, target_hostname, open_ports, scan_time, total_ports, mode)
    csv_content = generate_csv_content(target_ip, open_ports)
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(txt_filename, txt_content)
        zipf.writestr(csv_filename, csv_content)
    
    return zip_filename

def generate_txt_content(target_ip, target_hostname, open_ports, scan_time, total_ports, mode):
    """Genera el contenido del archivo TXT"""
    content = []
    
    content.append("="*80)
    content.append("R4-SEC SECURITY SCANNER - REPORTE DE ESCANEO")
    content.append("="*80)
    content.append("")
    content.append(f"Objetivo: {target_ip} ({target_hostname})")
    content.append(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append(f"Modo de escaneo: {mode.upper()}")
    content.append(f"Tiempo total: {scan_time:.2f} segundos")
    content.append(f"Velocidad: {total_ports/scan_time:.0f} puertos/segundo")
    content.append(f"Total de puertos escaneados: {total_ports:,}")
    content.append(f"Total de puertos abiertos: {len(open_ports)}")
    content.append("="*80)
    content.append("")
    
    if open_ports:
        content.append("RESUMEN DE PUERTOS ABIERTOS:")
        content.append("-"*80)
        content.append(f"{'PUERTO':<8} {'SERVICIO':<45} {'VERSIÓN':<30}")
        content.append("-"*80)
        
        for port, service, version, _ in open_ports:
            service_short = service[:44] if len(service) > 44 else service
            version_short = version[:29] if len(version) > 29 else version
            content.append(f"{port:<8} {service_short:<45} {version_short:<30}")
        
        content.append("")
        content.append("="*80)
        content.append("")
        content.append("INFORMACIÓN DETALLADA:")
        content.append("="*80)
        content.append("")
        
        for port, service, version, banner in open_ports:
            content.append("")
            content.append("="*40)
            content.append(f"PUERTO: {port}")
            content.append("="*40)
            content.append(f"Servicio: {service}")
            content.append(f"Versión: {version}")
            
            if banner and banner != "Banner omitido por velocidad":
                content.append(f"Banner: {banner}")
                
                content.append("")
                content.append("▶ Análisis de seguridad:")
                
                if "OpenSSH" in version:
                    if "7" in version or "6" in version:
                        content.append("  ⚠ ALERTA: Versión de SSH antigua - Posibles vulnerabilidades")
                    else:
                        content.append("  ✓ OK: Versión de SSH actualizada")
                elif "Apache" in version:
                    if "2.2" in version:
                        content.append("  ⚠ ALERTA: Apache 2.2 obsoleto (EOL)")
                    else:
                        content.append("  ✓ OK: Versión de Apache soportada")
                elif "nginx" in version:
                    content.append("  ✓ OK: Servidor nginx detectado")
                
                content.append("")
                content.append("▶ Recomendaciones:")
                
                if port == 22:
                    content.append("  - Usar autenticación por clave SSH")
                    content.append("  - Deshabilitar login root remoto")
                elif port == 80 or port == 443:
                    content.append("  - Mantener el servidor web actualizado")
                    content.append("  - Implementar certificados SSL/TLS")
                elif port == 3306:
                    content.append("  - Restringir acceso a localhost")
                    content.append("  - Usar contraseñas seguras")
                elif port == 445:
                    content.append("  - ⚠ ALERTA CRÍTICA: Puerto SMB expuesto")
                    content.append("  - Deshabilitar SMBv1 inmediatamente")
            else:
                content.append(f"Banner: No disponible (modo rápido)")
            
            content.append("")
    
    content.append("")
    content.append("="*80)
    content.append("Reporte generado por R4-SEC Security Scanner")
    content.append("="*80)
    
    return "\n".join(content)

def generate_csv_content(target_ip, open_ports):
    """Genera el contenido del archivo CSV"""
    output = []
    output.append("IP Objetivo,Puerto,Servicio,Version,Banner,Fecha Escaneo")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for port, service, version, banner in open_ports:
        service_clean = service.replace(',', ';').replace('\n', ' ')
        version_clean = version.replace(',', ';').replace('\n', ' ')
        banner_clean = banner.replace(',', ';').replace('\n', ' ') if banner else ""
        
        output.append(f"{target_ip},{port},{service_clean},{version_clean},{banner_clean},{timestamp}")
    
    return "\n".join(output)

def main():
    # Mostrar banner principal
    show_banner_big()
    
    parser = argparse.ArgumentParser(description="R4-SEC - Escáner de puertos ULTRA RÁPIDO con detección de versiones")
    parser.add_argument("target", help="IP o dominio a escanear")
    parser.add_argument("-p", "--ports", help="Puertos (ej: 1-1000 o 22,80,443)", default="1-1000")
    parser.add_argument("-t", "--threads", type=int, help="Número de hilos", default=1000)
    parser.add_argument("--fast", action="store_true", help="Modo rápido (timeout 0.5s)")
    parser.add_argument("--insane", action="store_true", help="Modo INSANO (timeout 0.3s, máximo velocidad)")
    parser.add_argument("--verbose", action="store_true", help="Modo verboso")
    parser.add_argument("--skip-check", action="store_true", help="Saltar verificación de host")
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.insane:
        mode = 'insane'
    elif args.fast:
        mode = 'fast'
    else:
        mode = 'normal'
    
    # Resolver IP
    print(f"{Colors.ORANGE}[*] Resolviendo {args.target}...{Colors.RESET}")
    try:
        target_ip = socket.gethostbyname(args.target)
        target_hostname = args.target
        print(f"{Colors.ORANGE}[+] Resuelto: {target_ip}{Colors.RESET}")
    except:
        print(f"{Colors.ORANGE}[!] No se pudo resolver el dominio{Colors.RESET}")
        sys.exit(1)
    
    # Parsear puertos
    if '-' in args.ports:
        start, end = map(int, args.ports.split('-'))
        ports = range(start, end + 1)
    elif ',' in args.ports:
        ports = [int(p.strip()) for p in args.ports.split(',')]
    else:
        ports = [int(args.ports)]
    
    ports = list(ports)
    total_ports = len(ports)
    
    # Crear scanner
    scanner = FastScanner(mode=mode)
    
    # Verificar host
    if not args.skip_check:
        print(f"{Colors.ORANGE}[*] Verificando disponibilidad del host...{Colors.RESET}")
        if scanner.check_host(target_ip):
            print(f"{Colors.ORANGE}[+] Host está activo y respondiendo{Colors.RESET}")
        else:
            print(f"{Colors.ORANGE}[!] Host no responde a ping/ICMP{Colors.RESET}")
            respuesta = input(f"{Colors.ORANGE}¿Intentar escaneo de todos modos? (s/n): {Colors.RESET}")
            if respuesta.lower() != 's':
                sys.exit(1)
    
    # Información de escaneo
    print(f"\n{Colors.ORANGE}{'='*60}{Colors.RESET}")
    print(f"{Colors.ORANGE}{Colors.BOLD}[*] INICIANDO ESCANEO R4-SEC{Colors.RESET}")
    print(f"{Colors.ORANGE}[*] Objetivo: {target_ip} ({target_hostname}){Colors.RESET}")
    print(f"{Colors.ORANGE}[*] Puertos a escanear: {total_ports:,}{Colors.RESET}")
    print(f"{Colors.ORANGE}[*] Timeout: {scanner.timeout}s{Colors.RESET}")
    print(f"{Colors.ORANGE}[*] Modo: {mode.upper()}{Colors.RESET}")
    print(f"{Colors.ORANGE}[*] Detección de versiones: {'Activada' if scanner.grab_banners else 'Desactivada (modo insane)'}{Colors.RESET}")
    print(f"{Colors.ORANGE}{'='*60}{Colors.RESET}\n")
    
    # Escanear
    start_time = time.time()
    open_ports = scanner.scan_ports(target_ip, ports, args.threads)
    scan_time = time.time() - start_time
    
    # Resultados
    print(f"\n{Colors.ORANGE}{'='*60}{Colors.RESET}")
    print(f"{Colors.ORANGE}{Colors.BOLD}[+] ¡ESCANEO COMPLETADO EXITOSAMENTE!{Colors.RESET}")
    print(f"{Colors.ORANGE}[+] Tiempo total: {scan_time:.2f} segundos{Colors.RESET}")
    print(f"{Colors.ORANGE}[+] Velocidad: {total_ports/scan_time:.0f} puertos/segundo{Colors.RESET}")
    print(f"{Colors.ORANGE}[+] Puertos abiertos encontrados: {len(open_ports)}{Colors.RESET}")
    
    if open_ports:
        print(f"\n{Colors.ORANGE}{Colors.BOLD}=== PUERTOS ABIERTOS DETECTADOS ==={Colors.RESET}")
        for port, service, version, banner in open_ports[:10]:
            print(f"\n{Colors.ORANGE}┌─────────────────────────────────────────{Colors.RESET}")
            print(f"{Colors.ORANGE}│{Colors.RESET} {Colors.ORANGE}Puerto:{Colors.RESET} {port}")
            print(f"{Colors.ORANGE}│{Colors.RESET} {Colors.ORANGE}Servicio:{Colors.RESET} {service[:50]}")
            print(f"{Colors.ORANGE}│{Colors.RESET} {Colors.ORANGE}Versión:{Colors.RESET} {version}")
            if banner and banner != "Banner omitido por velocidad":
                print(f"{Colors.ORANGE}│{Colors.RESET} {Colors.ORANGE}Banner:{Colors.RESET} {banner[:80]}...")
            print(f"{Colors.ORANGE}└─────────────────────────────────────────{Colors.RESET}")
        
        if len(open_ports) > 10:
            print(f"\n{Colors.ORANGE}[!] ... y {len(open_ports)-10} puertos más (ver reporte completo){Colors.RESET}")
    
    # Guardar resultados en ZIP
    if open_ports:
        zip_filename = f"R4SEC_Escaneo_{target_ip}.zip"
        
        print(f"\n{Colors.ORANGE}[*] Generando reporte ZIP...{Colors.RESET}")
        
        zip_path = save_results_to_zip(
            target_ip, target_hostname, open_ports, 
            scan_time, total_ports, mode, zip_filename
        )
        
        print(f"{Colors.ORANGE}{Colors.BOLD}[+] ¡REPORTE GUARDADO EXITOSAMENTE!{Colors.RESET}")
        print(f"{Colors.ORANGE}[+] Archivo: {zip_path}{Colors.RESET}")
        print(f"{Colors.ORANGE}[+] Contenido del ZIP:{Colors.RESET}")
        print(f"    📄 Escaneo_{target_ip.replace('.', '_')}.txt - Reporte detallado")
        print(f"    📊 Escaneo_{target_ip.replace('.', '_')}.csv - Datos estructurados")
        
        zip_size = os.path.getsize(zip_path) / 1024
        print(f"    💾 Tamaño: {zip_size:.2f} KB")
        
        print(f"\n{Colors.ORANGE}{Colors.BOLD}[+] Escaneo completado. ¡Gracias por usar R4-SEC!{Colors.RESET}")
    else:
        print(f"\n{Colors.ORANGE}[!] No se encontraron puertos abiertos{Colors.RESET}")
        print(f"{Colors.ORANGE}[!] No se generó reporte ZIP{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.ORANGE}[!] Escaneo interrumpido por el usuario{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.ORANGE}[!] Error inesperado: {e}{Colors.RESET}")
        sys.exit(1)

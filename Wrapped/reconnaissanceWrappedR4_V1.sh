#!/bin/bash
# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ── Temp dir para archivos intermedios ─────────────────────────
TMPDIR_WORK=$(mktemp -d /tmp/r4ul7to_XXXXXX)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

# ── Banner ─────────────────────────────────────────────────────
banner() {
    echo -e "${RED}${BOLD}"
    cat << 'EOF'
██████╗ ██╗  ██╗██╗   ██╗██╗      ███████╗████████╗ ██████╗
██╔══██╗██║  ██║██║   ██║██║      ╚════██╔╝╚══██╔══╝██╔═══██╗
██████╔╝███████║██║   ██║██║           ██╔╝   ██║   ██║   ██║
██╔══██╗╚════██║██║   ██║██║          ██╔╝    ██║   ██║   ██║
██║  ██║     ██║╚██████╔╝███████╗    ██╔╝     ██║   ╚██████╔╝
╚═╝  ╚═╝     ╚═╝ ╚═════╝ ╚══════╝   ╚═╝      ╚═╝    ╚═════╝
EOF
    echo -e "${NC}${DIM}  v1.1 · Automated Recon for Offensive Security Practice${NC}"
    echo -e "${DIM}  nmap · whatweb · gobuster · ffuf${NC}\n"
}

# ── Usage ──────────────────────────────────────────────────────
usage() {
    echo -e "${YELLOW}${BOLD}Usage:${NC}"
    echo -e "  $0 <IP|DOMAIN> [OPTIONS]\n"
    echo -e "${YELLOW}${BOLD}Options:${NC}"
    echo -e "  ${CYAN}-w${NC} <wordlist>   Wordlist para directory fuzzing"
    echo -e "                  (default: /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt)"
    echo -e "  ${CYAN}-W${NC} <wordlist>   Wordlist para subdomain fuzzing"
    echo -e "                  (default: /usr/share/wordlists/dirb/big.txt)"
    echo -e "  ${CYAN}-o${NC} <file>       Archivo de reporte de salida"
    echo -e "                  (default: ./recon_<target>_<timestamp>.md)"
    echo -e "  ${CYAN}-t${NC} <n>          Threads para fuzzing (default: 50)"
    echo -e "  ${CYAN}-p${NC} <ports>      Puertos para nmap (default: top 1000)"
    echo -e "  ${CYAN}-s${NC}             Modo sigiloso: escaneo lento (-T2)"
    echo -e "  ${CYAN}-h${NC}             Mostrar esta ayuda\n"
    echo -e "${YELLOW}${BOLD}Ejemplos:${NC}"
    echo -e "  $0 192.168.1.10"
    echo -e "  $0 target.htb -w /usr/share/wordlists/dirb/big.txt -t 100"
    echo -e "  $0 10.10.10.5 -p- -s -o /tmp/report.md"
    exit 1
}

# ── Dependency check ───────────────────────────────────────────
check_deps() {
    local missing=()
    for tool in nmap gobuster ffuf whatweb dig curl; do
        if ! command -v "$tool" &>/dev/null; then
            missing+=("$tool")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}[!] Herramientas faltantes: ${missing[*]}${NC}"
        echo -e "${YELLOW}[*] Instalar con: sudo apt install ${missing[*]}${NC}"
        exit 1
    fi
}

# ── Logger ─────────────────────────────────────────────────────
log() {
    local level="$1"
    local msg="$2"
    local ts; ts=$(date '+%H:%M:%S')
    case "$level" in
        INFO)  echo -e "${CYAN}[${ts}] [•]${NC} $msg"    ;;
        OK)    echo -e "${GREEN}[${ts}] [✓]${NC} $msg"   ;;
        WARN)  echo -e "${YELLOW}[${ts}] [!]${NC} $msg"  ;;
        ERROR) echo -e "${RED}[${ts}] [✗]${NC} $msg"     ;;
        PHASE) echo -e "\n${BOLD}${BLUE}┌──────────────────────────────────────────┐${NC}"
               echo -e "${BOLD}${BLUE}│  $msg${NC}"
               echo -e "${BOLD}${BLUE}└──────────────────────────────────────────┘${NC}\n" ;;
        FOUND) echo -e "${MAGENTA}[${ts}] [★]${NC} $msg" ;;
    esac
}

# ── Helpers ────────────────────────────────────────────────────
is_ip() {
    [[ "$1" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
}

detect_proto() {
    case "$1" in
        443|8443|4443) echo "https" ;;
        *)             echo "http"  ;;
    esac
}

resolve_domain_from_ip() {
    local ip="$1" domain=""
    domain=$(dig +short -x "$ip" 2>/dev/null | head -1 | sed 's/\.$//')
    [ -z "$domain" ] && domain=$(host "$ip" 2>/dev/null \
        | grep "domain name pointer" | awk '{print $NF}' | sed 's/\.$//' | head -1)
    echo "$domain"
}

get_domain_from_http() {
    local ip="$1" port="$2" proto="${3:-http}"
    curl -sk --max-time 5 -I "$proto://$ip:$port" 2>/dev/null \
        | grep -iE "^location|^x-forwarded-host" \
        | grep -oP '(?<=://)([^/:]+)' | head -1
}

elapsed() {
    local start="$1" end; end=$(date +%s)
    echo $(( end - start ))s
}


HTML_BODY=""

rpt() {
    HTML_BODY+="$1"$'
'
}

init_report() {
    local target="$1"
    HTML_BODY="<h1>R4Ul7TO Professional Recon Report</h1><p><b>Target:</b> ${target}</p><hr>"
}

close_report() {
    local domain="$1" total_elapsed="$2"
    local outfile="$REPORT_FILE"
    cat > "$outfile" <<EOF
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>R4Ul7TO Report</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:30px}
h1,h2,h3{color:white}
pre{background:#020617;padding:12px;border-radius:8px;overflow:auto}
.card{background:#1e293b;padding:20px;border-radius:12px;margin-bottom:20px}
</style>
</head>
<body>
<div class="card">
$HTML_BODY
<hr>
<p><b>Domain:</b> ${domain}</p>
<p><b>Total Time:</b> ${total_elapsed}s</p>
</div>
</body>
</html>
EOF
}


# ─────────────────────────────────────────────────────────────
#  FASE 1 — NMAP
# ─────────────────────────────────────────────────────────────
run_nmap() {
    local target="$1" ports="$2" timing="$3"
    local out="$TMPDIR_WORK/nmap.txt"
    local t0; t0=$(date +%s)

    log "PHASE" "FASE 1 · PORT SCAN & SERVICE DETECTION  [nmap]"
    log "INFO"  "Target: $target | Ports: ${ports:-(top 1000)} | Timing: $timing"

    nmap -sV -sC --open \
        ${ports:+$ports} \
        $timing \
        --reason \
        -oN "$out" \
        "$target" 2>&1 | tee "$TMPDIR_WORK/nmap_live.txt"

    # ── Parse puertos abiertos ────────────────────────────────
    grep -E "^[0-9]+/tcp.*open" "$out" > "$TMPDIR_WORK/open_ports.txt" || true

    # Puertos web: http/ssl/nginx/apache/iis/lighttpd + puertos comunes alternativos
    grep -E "^[0-9]+/tcp.*open" "$out" \
        | grep -iE "http|ssl/http|nginx|apache|iis|lighttpd|tornado|werkzeug|gunicorn|jetty|tomcat" \
        | awk '{print $1}' | cut -d'/' -f1 | sort -u > "$TMPDIR_WORK/web_ports.txt"

    # También incluir 8080/8000/8888/8443 si están abiertos aunque no tengan label web
    grep -E "^(8080|8000|8888|8443|3000|5000|4000)/tcp.*open" "$out" \
        | awk '{print $1}' | cut -d'/' -f1 >> "$TMPDIR_WORK/web_ports.txt"
    sort -u "$TMPDIR_WORK/web_ports.txt" -o "$TMPDIR_WORK/web_ports.txt"

    local open_count; open_count=$(wc -l < "$TMPDIR_WORK/open_ports.txt")
    local web_count;  web_count=$(wc -l  < "$TMPDIR_WORK/web_ports.txt")

    log "OK"    "Puertos abiertos: $open_count | Web: $web_count ($(tr '\n' ' ' < "$TMPDIR_WORK/web_ports.txt"))"

    # ── Escribir al reporte ───────────────────────────────────
    rpt "\n## Fase 1 · Port Scan — nmap\n"
    rpt "**Duración:** $(elapsed $t0)\n"
    rpt '```'
    cat "$TMPDIR_WORK/open_ports.txt" >> "$REPORT_FILE"
    rpt '```'
    rpt "\n**Puertos web detectados:** \`$(tr '\n' ' ' < "$TMPDIR_WORK/web_ports.txt")\`\n"
}

# ─────────────────────────────────────────────────────────────
#  FASE 2 — WHATWEB
# ─────────────────────────────────────────────────────────────
run_whatweb() {
    local target="$1" port="$2" proto="${3:-http}"
    local out="$TMPDIR_WORK/whatweb_${proto}_${port}.txt"
    local t0; t0=$(date +%s)

    log "PHASE" "FASE 2 · WEB FINGERPRINTING  [whatweb]  → $proto://$target:$port"

    whatweb -a 3 "$proto://$target:$port" 2>&1 | tee "$out"

    rpt "\n## Fase 2 · Web Fingerprint — $proto://$target:$port\n"
    rpt "**Duración:** $(elapsed $t0)\n"
    rpt '```'
    cat "$out" >> "$REPORT_FILE"
    rpt '```'
}

# ─────────────────────────────────────────────────────────────
#  FASE 3 — SUBDOMAIN FUZZING
#  FIX: wildcard detection + resolver externo + filtrado por tamaño
# ─────────────────────────────────────────────────────────────
run_subdomain_fuzz() {
    local domain="$1" wordlist="$2" threads="$3"
    local t0; t0=$(date +%s)

    log "PHASE" "FASE 3 · SUBDOMAIN FUZZING  [ffuf + gobuster]  → $domain"

    if [ ! -f "$wordlist" ]; then
        log "ERROR" "Wordlist no encontrada: $wordlist"
        rpt "\n## Fase 3 · Subdomain Fuzzing\n\n> ⚠️ Wordlist no encontrada: \`$wordlist\`\n"
        return 1
    fi

    # ── FIX 1: Detectar wildcard DNS ─────────────────────────
    local wildcard_ip
    wildcard_ip=$(dig +short "r4nd0mx1z2r3.${domain}" @8.8.8.8 2>/dev/null | head -1)

    if [ -n "$wildcard_ip" ]; then
        log "WARN" "Wildcard DNS detectado en $domain → $wildcard_ip"
        log "WARN" "Todos los subdominios resolverán a $wildcard_ip — usando VHOST fuzzing + filtrado de tamaño"
        WILDCARD=true
    else
        log "OK" "Sin wildcard DNS — fuzzing DNS directo habilitado"
        WILDCARD=false
    fi

    # ── FIX 2: ffuf VHOST con baseline size para filtrar FPs ─
    log "INFO" "[ffuf] Obteniendo baseline de respuesta HTTP para $domain..."
    local baseline_size
    baseline_size=$(curl -sk --max-time 8 -o /dev/null -w "%{size_download}" \
        -H "Host: nonexistentxyz9q1.${domain}" "http://${domain}" 2>/dev/null)
    baseline_size="${baseline_size:-0}"
    log "INFO" "[ffuf] Baseline size: $baseline_size bytes → filtrando respuestas de este tamaño"

    log "INFO" "[ffuf] VHOST fuzzing con filtro de tamaño (-fs $baseline_size)..."
    ffuf \
        -w "$wordlist" \
        -u "http://${domain}" \
        -H "Host: FUZZ.${domain}" \
        -t "$threads" \
        -mc 200,201,204,301,302,307,401,403 \
        -fs "$baseline_size" \
        -k \
        -o "$TMPDIR_WORK/subdomains_vhost.json" \
        -of json \
        2>&1 | tee "$TMPDIR_WORK/subdomains_vhost_live.txt"

    # ── FIX 3: gobuster dns con resolver externo ─────────────
    if [ "$WILDCARD" = false ]; then
        log "INFO" "[gobuster] DNS mode con resolver 8.8.8.8..."
        gobuster dns \
            -d "$domain" \
            -w "$wordlist" \
            -t "$threads" \
            --resolver 8.8.8.8 \
            --timeout 5s \
            --no-error \
            -o "$TMPDIR_WORK/subdomains_gobuster.txt" \
            2>&1 | tee "$TMPDIR_WORK/subdomains_gobuster_live.txt"
    else
        log "WARN" "[gobuster] DNS mode omitido por wildcard DNS — todos serían falsos positivos"
        echo "Omitido: wildcard DNS activo" > "$TMPDIR_WORK/subdomains_gobuster.txt"
    fi

    # ── Parsear resultados ────────────────────────────────────
    local found_gob; found_gob=$(grep "^Found:" "$TMPDIR_WORK/subdomains_gobuster.txt" 2>/dev/null | wc -l)
    log "FOUND" "Subdominios (gobuster): $found_gob"
    grep "^Found:" "$TMPDIR_WORK/subdomains_gobuster.txt" 2>/dev/null || true

    # ── Reporte ───────────────────────────────────────────────
    rpt "\n## Fase 3 · Subdomain Fuzzing\n"
    rpt "**Duración:** $(elapsed $t0) | **Wildcard DNS:** ${WILDCARD} | **VHOST baseline filter:** ${baseline_size}B\n"
    rpt "### gobuster dns\n\`\`\`"
    grep "^Found:" "$TMPDIR_WORK/subdomains_gobuster.txt" 2>/dev/null >> "$REPORT_FILE" \
        || echo "Sin resultados" >> "$REPORT_FILE"
    rpt '```'
    rpt "\n### ffuf VHOST (revisar JSON para detalles)\n\`\`\`"
    grep -oP '"url":"[^"]+"' "$TMPDIR_WORK/subdomains_vhost.json" 2>/dev/null \
        | head -30 >> "$REPORT_FILE" || echo "Sin resultados" >> "$REPORT_FILE"
    rpt '```'
}

# ─────────────────────────────────────────────────────────────
#  FASE 4 — DIRECTORY FUZZING
# ─────────────────────────────────────────────────────────────
run_dir_fuzz() {
    local target="$1" port="$2" wordlist="$3" threads="$4" proto="${5:-http}"
    local t0; t0=$(date +%s)

    log "PHASE" "FASE 4 · DIRECTORY FUZZING  [gobuster + ffuf]  → $proto://$target:$port"

    if [ ! -f "$wordlist" ]; then
        log "ERROR" "Wordlist no encontrada: $wordlist"
        rpt "\n## Fase 4 · Directory Fuzzing — $proto://$target:$port\n\n> ⚠️ Wordlist no encontrada\n"
        return 1
    fi

    # URL base limpia
    local base_url
    if { [[ "$proto" == "http" && "$port" == "80" ]] || [[ "$proto" == "https" && "$port" == "443" ]]; }; then
        base_url="$proto://$target"
    else
        base_url="$proto://$target:$port"
    fi

    local ext="php,html,txt,js,json,bak,zip,xml,conf,log,old,sh,py"
    local gob_out="$TMPDIR_WORK/dirs_gobuster_${proto}_${port}.txt"
    local ffuf_out="$TMPDIR_WORK/dirs_ffuf_${proto}_${port}.json"

    # gobuster dir con -k (ignore SSL) y --follow-redirect
    log "INFO" "[gobuster] dir → $base_url"
    gobuster dir \
        -u "$base_url" \
        -w "$wordlist" \
        -t "$threads" \
        -x "$ext" \
        --status-codes 200,201,204,301,302,307,401,403 \
        --timeout 10s \
        -k \
        -r \
        -o "$gob_out" \
        2>&1 | tee "${gob_out%.txt}_live.txt"

    # ffuf dir con -k (ignore SSL)
    log "INFO" "[ffuf] dir → $base_url/FUZZ"
    ffuf \
        -w "$wordlist" \
        -u "$base_url/FUZZ" \
        -t "$threads" \
        -mc 200,201,204,301,302,307,401,403 \
        -e ".$ext" \
        -k \
        -o "$ffuf_out" \
        -of json \
        2>&1 | tee "${ffuf_out%.json}_live.txt"

    local found; found=$(grep "Status:" "$gob_out" 2>/dev/null | wc -l)
    log "FOUND" "Directorios/archivos (gobuster): $found en $base_url"

    # ── Reporte ───────────────────────────────────────────────
    rpt "\n## Fase 4 · Directory Fuzzing — $base_url\n"
    rpt "**Duración:** $(elapsed $t0)\n"
    rpt "### gobuster\n\`\`\`"
    grep "Status:" "$gob_out" 2>/dev/null | head -60 >> "$REPORT_FILE" \
        || echo "Sin resultados" >> "$REPORT_FILE"
    rpt '```'
    rpt "\n### ffuf (top 30)\n\`\`\`"
    grep -oP '"url":"[^"]+"' "$ffuf_out" 2>/dev/null | head -30 >> "$REPORT_FILE" \
        || echo "Sin resultados" >> "$REPORT_FILE"
    rpt '```'
}

# ─────────────────────────────────────────────────────────────
#  ENCABEZADO DEL REPORTE
# ─────────────────────────────────────────────────────────────
init_report() {
    local target="$1"
    cat > "$REPORT_FILE" << MDEOF
# R4Ul7TO v1.1 — Reporte de Reconocimiento

| Campo      | Valor |
|------------|-------|
| **Target** | \`$target\` |
| **Fecha**  | $(date '+%Y-%m-%d %H:%M:%S') |
| **Reporte**| \`$REPORT_FILE\` |

---
MDEOF
}

# ─────────────────────────────────────────────────────────────
#  PIE DEL REPORTE
# ─────────────────────────────────────────────────────────────
close_report() {
    local domain="$1" total_elapsed="$2"
    rpt "\n---"
    rpt "\n## Resumen"
    rpt "| Campo | Valor |"
    rpt "|-------|-------|"
    rpt "| Dominio resuelto | \`${domain:-No encontrado}\` |"
    rpt "| Puertos abiertos | \`$(wc -l < "$TMPDIR_WORK/open_ports.txt" 2>/dev/null || echo 0)\` |"
    rpt "| Puertos web | \`$(tr '\n' ' ' < "$TMPDIR_WORK/web_ports.txt" 2>/dev/null)\` |"
    rpt "| Tiempo total | \`${total_elapsed}s\` |"
    rpt "\n---\n*Generado por R4Ul7TO v1.1*"
}

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
main() {
    banner
    check_deps

    # ── Defaults ──────────────────────────────────────────────
    local TARGET=""
    local DIR_WL="/usr/share/wordlists/dirb/common.txt"
    local SUB_WL="/usr/share/wordlists/dirb/big.txt"
    local REPORT_FILE=""
    local THREADS=50
    local PORTS=""
    local TIMING="-T4"
    local WILDCARD=false

    [ $# -lt 1 ] && usage
    TARGET="$1"; shift

    while getopts "w:W:o:t:p:sh" opt; do
        case $opt in
            w) DIR_WL="$OPTARG"     ;;
            W) SUB_WL="$OPTARG"     ;;
            o) REPORT_FILE="$OPTARG";;
            t) THREADS="$OPTARG"    ;;
            p) PORTS="-p $OPTARG"   ;;
            s) TIMING="-T2"         ;;
            h) usage                ;;
            *) usage                ;;
        esac
    done

    # ── Archivo de reporte ─────────────────────────────────────
    local DATE; DATE=$(date +%Y%m%d_%H%M%S)
    local CLEAN_TARGET="${TARGET//\//_}"
    REPORT_FILE="${REPORT_FILE:-./recon_${CLEAN_TARGET}_${DATE}.html}"

    # Exportar para que funcionen dentro de funciones
    export REPORT_FILE TMPDIR_WORK

    log "OK"   "R4Ul7TO v1.1 iniciado"
    log "INFO" "Target:  $TARGET"
    log "INFO" "Threads: $THREADS | Timing: $TIMING"
    log "INFO" "Reporte: $REPORT_FILE"

    local T_START; T_START=$(date +%s)

    init_report "$TARGET"

    # ── Detectar: IP o dominio ─────────────────────────────────
    local DOMAIN="" IP=""

    if is_ip "$TARGET"; then
        IP="$TARGET"
        log "INFO" "Entrada detectada → IP address"

        run_nmap "$IP" "$PORTS" "$TIMING"

        # Intentar resolver dominio
        log "INFO" "Intentando reverse DNS..."
        DOMAIN=$(resolve_domain_from_ip "$IP")

        if [ -n "$DOMAIN" ]; then
            log "FOUND" "Dominio por reverse DNS: $DOMAIN"
            rpt "\n> **Dominio resuelto (reverse DNS):** \`$DOMAIN\`\n"
        else
            log "WARN" "Sin dominio por reverse DNS — buscando en headers HTTP..."
            if [ -s "$TMPDIR_WORK/web_ports.txt" ]; then
                while IFS= read -r port; do
                    local proto; proto=$(detect_proto "$port")
                    local candidate; candidate=$(get_domain_from_http "$IP" "$port" "$proto")
                    if [ -n "$candidate" ]; then
                        DOMAIN="$candidate"
                        log "FOUND" "Dominio en headers HTTP ($proto:$port): $DOMAIN"
                        rpt "\n> **Dominio resuelto (HTTP headers):** \`$DOMAIN\`\n"
                        break
                    fi
                done < "$TMPDIR_WORK/web_ports.txt"
            fi
        fi

    else
        DOMAIN="$TARGET"
        log "INFO" "Entrada detectada → Dominio"

        IP=$(dig +short "$DOMAIN" A @8.8.8.8 2>/dev/null | grep -E '^[0-9]+\.' | head -1)
        if [ -n "$IP" ]; then
            log "FOUND" "IP de $DOMAIN: $IP"
            rpt "\n> **IP resuelta:** \`$IP\`\n"
        else
            log "WARN" "No se resolvió IP — ¿está en /etc/hosts?"
            IP="$DOMAIN"
        fi

        run_nmap "${IP}" "$PORTS" "$TIMING"
    fi

    # ── Fase 2: WhatWeb ────────────────────────────────────────
    if [ -s "$TMPDIR_WORK/web_ports.txt" ]; then
        while IFS= read -r port; do
            local proto; proto=$(detect_proto "$port")
            run_whatweb "${DOMAIN:-$IP}" "$port" "$proto"
        done < "$TMPDIR_WORK/web_ports.txt"
    else
        log "WARN" "Sin puertos web — saltando WhatWeb"
        rpt "\n## Fase 2 · WhatWeb\n\n> Sin puertos web detectados\n"
    fi

    # ── Fases 3 & 4: Fuzzing ───────────────────────────────────
    if [ -n "$DOMAIN" ]; then
        log "INFO" "Dominio disponible → subdomain + directory fuzzing"

        run_subdomain_fuzz "$DOMAIN" "$SUB_WL" "$THREADS"

        if [ -s "$TMPDIR_WORK/web_ports.txt" ]; then
            while IFS= read -r port; do
                local proto; proto=$(detect_proto "$port")
                run_dir_fuzz "$DOMAIN" "$port" "$DIR_WL" "$THREADS" "$proto"
            done < "$TMPDIR_WORK/web_ports.txt"
        fi

    else
        log "WARN" "Sin dominio → solo directory fuzzing sobre la IP"
        rpt "\n## Fase 3 · Subdomain Fuzzing\n\n> Omitido: no se detectó dominio\n"

        if [ -s "$TMPDIR_WORK/web_ports.txt" ]; then
            while IFS= read -r port; do
                local proto; proto=$(detect_proto "$port")
                run_dir_fuzz "$IP" "$port" "$DIR_WL" "$THREADS" "$proto"
            done < "$TMPDIR_WORK/web_ports.txt"
        else
            log "ERROR" "Sin puertos web para fuzzear"
        fi
    fi

    # ── Cierre ─────────────────────────────────────────────────
    local T_END; T_END=$(date +%s)
    close_report "$DOMAIN" $(( T_END - T_START ))

    echo ""
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${GREEN}  ✓ R4Ul7TO v1.1 completado${NC}"
    echo -e "${BOLD}${GREEN}  Reporte: $REPORT_FILE${NC}"
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

main "$@"

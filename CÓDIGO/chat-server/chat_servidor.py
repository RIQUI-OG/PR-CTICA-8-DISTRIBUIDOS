# Pérez Hernández Ricardo — Práctica 8: Contenedores y Microservicios
# ─────────────────────────────────────────────────────────────────────────────
# chat-server/chat_servidor.py  —  Servidor de Chat REST (Flask)
#
# Cambios respecto a la Práctica 7:
#   • HOST cambiado a '0.0.0.0' para aceptar conexiones dentro de Docker.
#   • Panel visual OpenCV eliminado: en un contenedor no hay pantalla (display).
#     El estado del servidor se imprime en stdout (visible con docker logs).
#   • Dependencia de opencv-python y numpy eliminada.
#   • Se añade el endpoint GET /health requerido por el healthcheck del Compose.
#
# ─── Endpoints ────────────────────────────────────────────────────────────────
#  GET  /health               → { status: "ok" }
#  POST /unirse               { "usuario": "Ricardo" }
#  DELETE /salir              { "usuario": "Ricardo" }
#  POST /mensajes             { "usuario": "...", "texto": "..." }
#  GET  /mensajes?desde=N     → lista de mensajes con id > N
#  GET  /usuarios             → lista de usuarios conectados
#  POST /heartbeat            { "usuario": "Ricardo" }
# ─────────────────────────────────────────────────────────────────────────────
from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- 1. AGREGA ESTA LÍNEA
import threading
import time

HOST = '0.0.0.0'   
PORT = 9000

app = Flask(__name__)
CORS(app)  # <-- 2. AGREGA ESTA LÍNEA PARA PERMITIR CONEXIONES WEB

# ── Estado del chat (en memoria) ──────────────────────────────────────────────
_lock     = threading.Lock()
_mensajes = []          # lista de dicts: {id, usuario, texto, timestamp}
_usuarios = {}          # { nombre: last_seen (float) }
_contador = 0           # ID autoincremental


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    """Requerido por el healthcheck del docker-compose."""
    with _lock:
        total = _contador
        conectados = len(_usuarios)
    return jsonify({'status': 'ok', 'service': 'chat-server',
                    'usuarios': conectados, 'mensajes': total})


@app.route('/unirse', methods=['POST'])
def unirse():
    datos   = request.get_json()
    usuario = datos.get('usuario', '').strip()
    if not usuario:
        return jsonify({'ok': False, 'error': 'Nombre vacío'}), 400

    with _lock:
        ya_existe = usuario in _usuarios
        _usuarios[usuario] = time.time()
        if not ya_existe:
            _agregar_mensaje('SISTEMA', f'*** {usuario} se unió al chat ***')

    print(f"[+] {usuario} se unió  |  conectados: {len(_usuarios)}", flush=True)
    return jsonify({'ok': True})


@app.route('/salir', methods=['DELETE'])
def salir():
    datos   = request.get_json()
    usuario = datos.get('usuario', '').strip()
    with _lock:
        if usuario in _usuarios:
            _usuarios.pop(usuario)
            _agregar_mensaje('SISTEMA', f'*** {usuario} salió del chat ***')

    print(f"[-] {usuario} salió  |  conectados: {len(_usuarios)}", flush=True)
    return jsonify({'ok': True})


@app.route('/mensajes', methods=['POST'])
def enviar_mensaje():
    datos   = request.get_json()
    usuario = datos.get('usuario', '').strip()
    texto   = datos.get('texto', '').strip()

    if not usuario or not texto:
        return jsonify({'ok': False, 'error': 'Campos incompletos'}), 400

    with _lock:
        _usuarios[usuario] = time.time()
        nuevo_id = _agregar_mensaje(usuario, texto)

    print(f"[MSG #{nuevo_id}] {usuario}: {texto}", flush=True)
    return jsonify({'ok': True, 'id': nuevo_id})


@app.route('/mensajes', methods=['GET'])
def obtener_mensajes():
    desde = int(request.args.get('desde', 0))
    with _lock:
        nuevos = [m for m in _mensajes if m['id'] > desde]
    return jsonify({'mensajes': nuevos})


@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    ahora = time.time()
    with _lock:
        caidos = [u for u, t in _usuarios.items() if ahora - t > 15]
        for u in caidos:
            _usuarios.pop(u)
            _agregar_mensaje('SISTEMA', f'*** {u} se desconectó (timeout) ***')
            print(f"[TIMEOUT] {u} desconectado", flush=True)
        activos = list(_usuarios.keys())
    return jsonify({'usuarios': activos})


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    usuario = request.get_json().get('usuario', '')
    with _lock:
        if usuario in _usuarios:
            _usuarios[usuario] = time.time()
    return jsonify({'ok': True})


# ── Función interna ───────────────────────────────────────────────────────────

def _agregar_mensaje(usuario: str, texto: str) -> int:
    """Inserta mensaje en la lista. Debe llamarse con _lock adquirido."""
    global _contador
    _contador += 1
    _mensajes.append({
        'id'       : _contador,
        'usuario'  : usuario,
        'texto'    : texto,
        'timestamp': time.strftime('%H:%M:%S')
    })
    if len(_mensajes) > 200:
        _mensajes.pop(0)
    return _contador


# ── Hilo de estado periódico (reemplaza el panel OpenCV) ─────────────────────

def _hilo_estado():
    """Imprime en stdout un resumen cada 30 segundos (visible con docker logs)."""
    while True:
        time.sleep(30)
        with _lock:
            usuarios  = list(_usuarios.keys())
            n_msgs    = _contador
        print(f"[ESTADO] conectados={usuarios}  mensajes_totales={n_msgs}", flush=True)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    threading.Thread(target=_hilo_estado, daemon=True).start()
    print(f"[CHAT-SERVER] Escuchando en http://{HOST}:{PORT}", flush=True)
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)

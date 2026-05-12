"""
Lanzador de escritorio para el Dashboard de Salud Financiera.
Ejecutar: python launcher.py
Abre la app en una ventana independiente (modo aplicacion, sin barras).
"""
import subprocess
import sys
import os
import time
import socket
import webbrowser

PORT = 8501


def wait_for_server(port, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(app_dir, "app.py")
    url = f"http://localhost:{PORT}"

    print("=" * 52)
    print("  Dashboard de Salud Financiera Personal")
    print(f"  Iniciando servidor en {url}")
    print("=" * 52)

    # Iniciar Streamlit en segundo plano
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", str(PORT),
            "--server.headless", "true",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=app_dir,
    )

    print("Esperando servidor...")
    if not wait_for_server(PORT):
        print("ERROR: El servidor no inicio. Verifica que el puerto no este en uso.")
        proc.terminate()
        return

    print("Servidor listo. Abriendo ventana...")

    # Intentar abrir como ventana de app (sin barras de navegador)
    opened = False
    browser_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for bp in browser_paths:
        if os.path.exists(bp):
            try:
                subprocess.Popen([bp, f"--app={url}", "--new-window", "--window-size=1400,900"])
                opened = True
                name = "Edge" if "edge" in bp.lower() else "Chrome"
                print(f"Abierto en {name} (modo ventana independiente)")
                break
            except Exception:
                continue

    if not opened:
        webbrowser.open(url)
        print("Abierto en navegador predeterminado")

    print("")
    print("La app esta corriendo. Presiona Ctrl+C para cerrar.")
    print("")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("Cerrando...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("Hasta luego!")


if __name__ == "__main__":
    main()

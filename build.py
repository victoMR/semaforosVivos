#!/usr/bin/env python3
"""
Script para generar ejecutables del Simulador de Semáforos
para Windows (EXE) y Linux (AppImage)
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_requirements():
    """Verifica que estén instalados los requisitos necesarios."""
    try:
        import PyQt6
        print("✓ PyQt6 instalado")
    except ImportError:
        print("✗ PyQt6 no está instalado. Instálalo con: pip install PyQt6")
        return False

    try:
        subprocess.run(['pyinstaller', '--version'],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        print("✓ PyInstaller instalado")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ PyInstaller no está instalado. Instálalo con: pip install pyinstaller")
        return False

    return True

def build_windows_exe():
    """Genera un archivo EXE para Windows."""
    print("\n=== Generando ejecutable para Windows ===")

    # Asegurarse de que estamos en Windows
    if platform.system() != "Windows":
        print("Esta función debe ejecutarse en Windows.")
        return False

    # Encontrar el archivo Python principal
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'build.py']

    if not python_files:
        print("✗ No se encontraron archivos Python en el directorio actual.")
        return False

    main_file = None

    # Si hay varios archivos Python, buscar primero 'simulador_semaforos.py'
    if 'simulador_semaforos.py' in python_files:
        main_file = 'simulador_semaforos.py'
    elif 'newtest.py' in python_files:  # Verificar el archivo detectado en el log
        main_file = 'newtest.py'
    else:
        # Usar el primer archivo Python encontrado
        main_file = python_files[0]

    print(f"✓ Usando archivo principal: {main_file}")

    # Verificar si existe el ícono
    icon_param = []
    if os.path.exists('icon.ico'):
        icon_param = ['--icon=icon.ico']

    try:
        subprocess.run(
            ['pyinstaller', '--name=SimuladorSemaforos', '--windowed', '--onefile'] +
            icon_param + [main_file],
            check=True
        )

        print("✓ Ejecutable Windows creado: dist/SimuladorSemaforos.exe")
        return True
    except subprocess.SubprocessError as e:
        print(f"✗ Error al crear el ejecutable para Windows: {e}")
        return False

def build_linux_appimage():
    """Genera un AppImage para Linux."""
    print("\n=== Generando AppImage para Linux ===")

    # Asegurarse de que estamos en Linux
    if platform.system() != "Linux":
        print("Esta función debe ejecutarse en Linux.")
        return False

    # Encontrar el archivo Python principal
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'build.py']

    if not python_files:
        print("✗ No se encontraron archivos Python en el directorio actual.")
        return False

    main_file = None

    # Si hay varios archivos Python, buscar primero 'simulador_semaforos.py'
    if 'simulador_semaforos.py' in python_files:
        main_file = 'simulador_semaforos.py'
    elif 'newtest.py' in python_files:  # Verificar el archivo detectado en el log
        main_file = 'newtest.py'
    else:
        # Usar el primer archivo Python encontrado
        main_file = python_files[0]

    print(f"✓ Usando archivo principal: {main_file}")

    try:
        # 1. Crear ejecutable con PyInstaller
        subprocess.run([
            'pyinstaller',
            '--name=SimuladorSemaforos',
            '--windowed',
            '--onefile',
            main_file
        ], check=True)

        # 2. Crear estructura de directorios para AppImage
        appdir = Path("SimuladorSemaforos.AppDir")
        (appdir / "usr/bin").mkdir(parents=True, exist_ok=True)
        (appdir / "usr/share/applications").mkdir(parents=True, exist_ok=True)
        (appdir / "usr/share/icons/hicolor/256x256/apps").mkdir(parents=True, exist_ok=True)

        # 3. Copiar ejecutable
        shutil.copy("dist/SimuladorSemaforos", appdir / "usr/bin/")

        # 4. Crear archivo desktop
        with open(appdir / "simulador.desktop", "w") as f:
            f.write("""[Desktop Entry]
Name=Simulador Semaforos
Exec=SimuladorSemaforos
Icon=simulador
Type=Application
Categories=Utility;
""")

        # 5. Crear script AppRun
        with open(appdir / "AppRun", "w") as f:
            f.write("""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/SimuladorSemaforos" "$@"
""")
        os.chmod(appdir / "AppRun", 0o755)

        # 6. Descargar appimagetool si no existe
        if not os.path.exists("appimagetool-x86_64.AppImage"):
            print("Descargando appimagetool...")
            subprocess.run([
                'wget',
                'https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage'
            ], check=True)
            os.chmod("appimagetool-x86_64.AppImage", 0o755)

        # 7. Crear AppImage con arquitectura explícita
        env = os.environ.copy()
        env['ARCH'] = 'x86_64'  # Especificar explícitamente la arquitectura

        # Verificar que el AppImage tool tenga permisos de ejecución
        if not os.access('./appimagetool-x86_64.AppImage', os.X_OK):
            print("Estableciendo permisos de ejecución para appimagetool...")
            os.chmod('./appimagetool-x86_64.AppImage', 0o755)

        # Verificar que la estructura del AppDir sea correcta
        if not os.path.exists('SimuladorSemaforos.AppDir/AppRun') or not os.path.exists('SimuladorSemaforos.AppDir/usr/bin/SimuladorSemaforos'):
            print("Verificando estructura de directorios del AppDir...")
            for root, dirs, files in os.walk('SimuladorSemaforos.AppDir'):
                print(f"Contenido de {root}:")
                for d in dirs:
                    print(f"  Dir: {d}")
                for f in files:
                    print(f"  File: {f}")

        try:
            print("Ejecutando appimagetool para crear el AppImage...")
            process = subprocess.run([
                './appimagetool-x86_64.AppImage',
                'SimuladorSemaforos.AppDir/'
            ], check=False, env=env, capture_output=True, text=True)

            if process.returncode != 0:
                print(f"Error al ejecutar appimagetool: {process.stderr}")
                # Intentar una solución alternativa
                print("Intentando solución alternativa con ARCH explícito...")
                subprocess.run([
                    'ARCH=x86_64', './appimagetool-x86_64.AppImage',
                    'SimuladorSemaforos.AppDir/'
                ], check=True, shell=True)
            else:
                print("AppImage creado exitosamente")
        except Exception as e:
            print(f"Error al crear AppImage: {str(e)}")
            raise

        print("✓ AppImage creado: SimuladorSemaforos-x86_64.AppImage")
        return True
    except subprocess.SubprocessError as e:
        print(f"✗ Error al crear el AppImage: {e}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False

def main():
    """Función principal que maneja el proceso de construcción."""
    print("== Script para generar ejecutables del Simulador de Semáforos ==")

    if not check_requirements():
        print("\nPor favor, instala los requisitos faltantes y vuelve a ejecutar el script.")
        return

    system = platform.system()
    if system == "Windows":
        build_windows_exe()
    elif system == "Linux":
        build_linux_appimage()
    else:
        print(f"Sistema operativo no soportado: {system}")
        print("Este script solo funciona en Windows y Linux.")

if __name__ == "__main__":
    main()

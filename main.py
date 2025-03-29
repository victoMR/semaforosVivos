import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout,
    QHBoxLayout, QPushButton, QWidget, QLabel, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QBrush, QPen, QColor, QFont, QPainter

class SemaforoVehicular:
    def __init__(self, direccion):
        self.direccion = direccion
        self.estado = "rojo"  # Inicialmente todos en rojo excepto el Sur
        self.tokens = {"verde": 0, "amarillo": 0, "rojo": 1}

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def agregar_token(self, estado, cantidad=1):
        self.tokens[estado] += cantidad

    def quitar_token(self, estado, cantidad=1):
        if self.tokens[estado] >= cantidad:
            self.tokens[estado] -= cantidad
            return True
        return False

class SemaforoPeatonal:
    def __init__(self, carril, tipo):
        self.carril = carril
        self.tipo = tipo  # "directo" o "indirecto"
        self.estado = "rojo"  # Inicialmente en rojo, se cambiará según configuración
        self.tokens = {"blanco": 0, "rojo": 1}

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def agregar_token(self, estado, cantidad=1):
        self.tokens[estado] += cantidad

    def quitar_token(self, estado, cantidad=1):
        if self.tokens[estado] >= cantidad:
            self.tokens[estado] -= cantidad
            return True
        return False

class SimuladorSemaforos(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicializar semáforos vehiculares
        self.semaforos_vehiculares = {
            "Norte": SemaforoVehicular("Norte"),
            "Sur": SemaforoVehicular("Sur"),
            "Este": SemaforoVehicular("Este"),
            "Oeste": SemaforoVehicular("Oeste")
        }

        # El semáforo Sur comienza en verde
        self.semaforos_vehiculares["Sur"].estado = "verde"
        self.semaforos_vehiculares["Sur"].tokens = {"verde": 1, "amarillo": 0, "rojo": 0}

        # Inicializar semáforos peatonales
        self.semaforos_peatonales = {}
        for carril in ["Norte", "Sur", "Este", "Oeste"]:
            for tipo in ["directo", "indirecto"]:
                key = f"{carril}_{tipo}"
                self.semaforos_peatonales[key] = SemaforoPeatonal(carril, tipo)

        # Configuración inicial de semáforos peatonales según la nueva descripción
        # Peatonales que deben estar en blanco
        peatonales_blancos = ["Sur_indirecto", "Oeste_directo", "Norte_directo", "Este_directo"]
        for key in peatonales_blancos:
            self.semaforos_peatonales[key].estado = "blanco"
            self.semaforos_peatonales[key].tokens = {"blanco": 1, "rojo": 0}

        # Configurar la interfaz gráfica
        self.setup_ui()

        # Timer para actualizar la simulación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_simulacion)
        self.current_step = 0
        self.max_steps = 5  # Número de pasos en un ciclo completo

        # Estado actual de la simulación
        self.estado_actual = "Sur_verde"
        self.contador = 0

    def setup_ui(self):
        self.setWindowTitle("Simulador de Semáforos")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Crear escena y vista
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setSceneRect(QRectF(0, 0, 700, 500))

        main_layout.addWidget(self.view)

        # Controles
        control_layout = QHBoxLayout()

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.iniciar_simulacion)
        control_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pausar_simulacion)
        control_layout.addWidget(self.pause_button)

        self.step_button = QPushButton("Paso a Paso")
        self.step_button.clicked.connect(self.paso_simulacion)
        control_layout.addWidget(self.step_button)

        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.reiniciar_simulacion)
        control_layout.addWidget(self.reset_button)

        main_layout.addLayout(control_layout)

        # Etiqueta de estado actual
        self.estado_label = QLabel("Estado: Sur en verde")
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.estado_label)

        # Dibujar el cruce inicial
        self.dibujar_cruce()

    def dibujar_cruce(self):
        self.scene.clear()

        # Dibujar calles
        # Horizontal
        self.scene.addRect(0, 225, 700, 50, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))
        # Vertical
        self.scene.addRect(325, 0, 50, 500, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))

        # Líneas divisorias
        pen = QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine)
        self.scene.addLine(0, 250, 700, 250, pen)  # Horizontal
        self.scene.addLine(350, 0, 350, 500, pen)  # Vertical

        # Semáforos vehiculares
        self.dibujar_semaforo_vehicular("Norte", 350, 130, 90)  # Norte
        self.dibujar_semaforo_vehicular("Sur", 325, 370, 270)  # Sur
        self.dibujar_semaforo_vehicular("Este", 450, 225, 0)   # Este
        self.dibujar_semaforo_vehicular("Oeste", 250, 250, 180) # Oeste

        # Semáforos peatonales
        # Norte
        self.dibujar_semaforo_peatonal("Norte_directo", 305, 100)
        self.dibujar_semaforo_peatonal("Norte_indirecto", 370, 100)
        # Sur
        self.dibujar_semaforo_peatonal("Sur_directo", 370, 400)
        self.dibujar_semaforo_peatonal("Sur_indirecto", 305, 400)
        # Este
        self.dibujar_semaforo_peatonal("Este_directo", 420, 210)
        self.dibujar_semaforo_peatonal("Este_indirecto", 420, 265)
        # Oeste
        self.dibujar_semaforo_peatonal("Oeste_directo", 280, 265)
        self.dibujar_semaforo_peatonal("Oeste_indirecto", 280, 210)

        # Agregar etiquetas de direcciones
        font = QFont("Arial", 12, QFont.Weight.Bold)

        text_norte = self.scene.addText("Norte", font)
        text_norte.setPos(340, 20)

        text_sur = self.scene.addText("Sur", font)
        text_sur.setPos(345, 460)

        text_este = self.scene.addText("Este", font)
        text_este.setPos(520, 240)

        text_oeste = self.scene.addText("Oeste", font)
        text_oeste.setPos(180, 240)

    def dibujar_semaforo_vehicular(self, direccion, x, y, rotacion):
        # Obtener el estado del semáforo
        semaforo = self.semaforos_vehiculares[direccion]

        # Rectángulo principal
        rect = QRectF(0, 0, 20, 60)
        transform = self.scene.addRect(rect, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.darkGray))
        transform.setPos(x, y)
        transform.setRotation(rotacion)

        # Luces
        # Rojo
        color_rojo = QColor(255, 0, 0) if semaforo.estado == "rojo" else QColor(100, 0, 0)
        luz_roja = self.scene.addEllipse(0, 0, 15, 15, QPen(Qt.GlobalColor.black), QBrush(color_rojo))
        luz_roja.setPos(x + 2.5, y + 5)
        luz_roja.setRotation(rotacion)

        # Amarillo
        color_amarillo = QColor(255, 255, 0) if semaforo.estado == "amarillo" else QColor(100, 100, 0)
        luz_amarilla = self.scene.addEllipse(0, 0, 15, 15, QPen(Qt.GlobalColor.black), QBrush(color_amarillo))
        luz_amarilla.setPos(x + 2.5, y + 22.5)
        luz_amarilla.setRotation(rotacion)

        # Verde
        color_verde = QColor(0, 255, 0) if semaforo.estado == "verde" else QColor(0, 100, 0)
        luz_verde = self.scene.addEllipse(0, 0, 15, 15, QPen(Qt.GlobalColor.black), QBrush(color_verde))
        luz_verde.setPos(x + 2.5, y + 40)
        luz_verde.setRotation(rotacion)

        # Mostrar tokens
        font = QFont("Arial", 8)
        for idx, estado in enumerate(["rojo", "amarillo", "verde"]):
            tokens_text = f"{estado[0].upper()}: {semaforo.tokens[estado]}"
            text = self.scene.addText(tokens_text, font)
            if rotacion == 0:  # Este
                text.setPos(x + 25, y + idx * 15)
            elif rotacion == 90:  # Norte
                text.setPos(x - 40, y + idx * 15)
            elif rotacion == 180:  # Oeste
                text.setPos(x - 70, y + idx * 15)
            elif rotacion == 270:  # Sur
                text.setPos(x + 25, y + idx * 15)

    def dibujar_semaforo_peatonal(self, key, x, y):
        # Obtener el estado del semáforo
        semaforo = self.semaforos_peatonales[key]

        # Determinar colores según el estado
        color_blanco = QColor(255, 255, 255) if semaforo.estado == "blanco" else QColor(100, 100, 100)
        color_rojo = QColor(255, 0, 0) if semaforo.estado == "rojo" else QColor(100, 0, 0)

        # Rectángulo principal
        rect = self.scene.addRect(0, 0, 15, 30, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.darkGray))
        rect.setPos(x, y)

        # Luces
        # Rojo (arriba)
        luz_roja = self.scene.addEllipse(0, 0, 10, 10, QPen(Qt.GlobalColor.black), QBrush(color_rojo))
        luz_roja.setPos(x + 2.5, y + 2.5)

        # Blanco (abajo)
        luz_blanca = self.scene.addEllipse(0, 0, 10, 10, QPen(Qt.GlobalColor.black), QBrush(color_blanco))
        luz_blanca.setPos(x + 2.5, y + 17.5)

        # Etiqueta para identificar directo/indirecto
        font = QFont("Arial", 6)
        tipo_text = semaforo.tipo[0].upper()
        text = self.scene.addText(tipo_text, font)
        text.setPos(x + 5, y + 32)

        # Mostrar tokens
        for idx, estado in enumerate(["rojo", "blanco"]):
            tokens_text = f"{estado[0].upper()}: {semaforo.tokens[estado]}"
            text = self.scene.addText(tokens_text, font)
            text.setPos(x - 20, y + idx * 10)

    def iniciar_simulacion(self):
        self.timer.start(1500)

    def pausar_simulacion(self):
        self.timer.stop()

    def paso_simulacion(self):
        self.timer.stop()
        self.actualizar_simulacion()

    def reiniciar_simulacion(self):
        self.timer.stop()

        # Reiniciar todos los semáforos a su estado inicial
        for direccion, semaforo in self.semaforos_vehiculares.items():
            if direccion == "Sur":
                semaforo.estado = "verde"
                semaforo.tokens = {"verde": 1, "amarillo": 0, "rojo": 0}
            else:
                semaforo.estado = "rojo"
                semaforo.tokens = {"verde": 0, "amarillo": 0, "rojo": 1}

        # Reiniciar semáforos peatonales según la nueva descripción
        for key, semaforo in self.semaforos_peatonales.items():
            if key in ["Sur_indirecto", "Oeste_directo", "Norte_directo", "Este_directo"]:
                semaforo.estado = "blanco"
                semaforo.tokens = {"blanco": 1, "rojo": 0}
            else:
                semaforo.estado = "rojo"
                semaforo.tokens = {"blanco": 0, "rojo": 1}

        self.estado_actual = "Sur_verde"
        self.contador = 0
        self.dibujar_cruce()
        self.estado_label.setText("Estado: Sur en verde")

    def actualizar_simulacion(self):
        if self.estado_actual == "Sur_verde":
            if self.contador == 0:
                self.estado_label.setText("Estado: Sur en verde")
                self.contador += 1
            elif self.contador == 1:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Sur"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Sur"].agregar_token("amarillo")
                self.semaforos_vehiculares["Sur"].quitar_token("verde")
                self.estado_label.setText("Estado: Sur cambia a amarillo")
                self.contador += 1
            elif self.contador == 2:
                # Cambiar a rojo
                self.semaforos_vehiculares["Sur"].cambiar_estado("rojo")
                self.semaforos_vehiculares["Sur"].agregar_token("rojo")
                self.semaforos_vehiculares["Sur"].quitar_token("amarillo")

                # Activar semáforo Oeste
                self.semaforos_vehiculares["Oeste"].cambiar_estado("verde")
                self.semaforos_vehiculares["Oeste"].agregar_token("verde")
                self.semaforos_vehiculares["Oeste"].quitar_token("rojo")

                # Cambiar semáforos peatonales
                # El peatonal directo del carril Oeste pasa a rojo
                self.semaforos_peatonales["Oeste_directo"].cambiar_estado("rojo")
                self.semaforos_peatonales["Oeste_directo"].agregar_token("rojo")
                self.semaforos_peatonales["Oeste_directo"].quitar_token("blanco")

                # El peatonal directo del carril Sur pasa a blanco
                self.semaforos_peatonales["Sur_directo"].cambiar_estado("blanco")
                self.semaforos_peatonales["Sur_directo"].agregar_token("blanco")
                self.semaforos_peatonales["Sur_directo"].quitar_token("rojo")

                # El peatonal indirecto del carril Oeste pasa a blanco
                self.semaforos_peatonales["Oeste_indirecto"].cambiar_estado("blanco")
                self.semaforos_peatonales["Oeste_indirecto"].agregar_token("blanco")
                self.semaforos_peatonales["Oeste_indirecto"].quitar_token("rojo")

                self.estado_label.setText("Estado: Sur cambia a rojo, Oeste cambia a verde")
                self.contador = 0
                self.estado_actual = "Oeste_verde"

        elif self.estado_actual == "Oeste_verde":
            if self.contador == 0:
                self.estado_label.setText("Estado: Oeste en verde")
                self.contador += 1
            elif self.contador == 1:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Oeste"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Oeste"].agregar_token("amarillo")
                self.semaforos_vehiculares["Oeste"].quitar_token("verde")
                self.estado_label.setText("Estado: Oeste cambia a amarillo")
                self.contador += 1
            elif self.contador == 2:
                # Cambiar a rojo
                self.semaforos_vehiculares["Oeste"].cambiar_estado("rojo")
                self.semaforos_vehiculares["Oeste"].agregar_token("rojo")
                self.semaforos_vehiculares["Oeste"].quitar_token("amarillo")

                # Activar semáforo Norte
                self.semaforos_vehiculares["Norte"].cambiar_estado("verde")
                self.semaforos_vehiculares["Norte"].agregar_token("verde")
                self.semaforos_vehiculares["Norte"].quitar_token("rojo")

                # Cambiar semáforos peatonales
                # Norte directo a rojo
                self.semaforos_peatonales["Norte_directo"].cambiar_estado("rojo")
                self.semaforos_peatonales["Norte_directo"].agregar_token("rojo")
                self.semaforos_peatonales["Norte_directo"].quitar_token("blanco")

                # Norte indirecto a blanco
                self.semaforos_peatonales["Norte_indirecto"].cambiar_estado("blanco")
                self.semaforos_peatonales["Norte_indirecto"].agregar_token("blanco")
                self.semaforos_peatonales["Norte_indirecto"].quitar_token("rojo")

                # Oeste directo a blanco
                self.semaforos_peatonales["Oeste_directo"].cambiar_estado("blanco")
                self.semaforos_peatonales["Oeste_directo"].agregar_token("blanco")
                self.semaforos_peatonales["Oeste_directo"].quitar_token("rojo")

                # Sur indirecto a rojo
                self.semaforos_peatonales["Sur_indirecto"].cambiar_estado("rojo")
                self.semaforos_peatonales["Sur_indirecto"].agregar_token("rojo")
                self.semaforos_peatonales["Sur_indirecto"].quitar_token("blanco")

                self.estado_label.setText("Estado: Oeste cambia a rojo, Norte cambia a verde")
                self.contador = 0
                self.estado_actual = "Norte_verde"

        elif self.estado_actual == "Norte_verde":
            if self.contador == 0:
                self.estado_label.setText("Estado: Norte en verde")
                self.contador += 1
            elif self.contador == 1:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Norte"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Norte"].agregar_token("amarillo")
                self.semaforos_vehiculares["Norte"].quitar_token("verde")
                self.estado_label.setText("Estado: Norte cambia a amarillo")
                self.contador += 1
            elif self.contador == 2:
                # Cambiar a rojo
                self.semaforos_vehiculares["Norte"].cambiar_estado("rojo")
                self.semaforos_vehiculares["Norte"].agregar_token("rojo")
                self.semaforos_vehiculares["Norte"].quitar_token("amarillo")

                # Activar semáforo Este
                self.semaforos_vehiculares["Este"].cambiar_estado("verde")
                self.semaforos_vehiculares["Este"].agregar_token("verde")
                self.semaforos_vehiculares["Este"].quitar_token("rojo")

                # Cambiar semáforos peatonales como se solicitó
                # 1- Norte directo a blanco
                self.semaforos_peatonales["Norte_directo"].cambiar_estado("blanco")
                self.semaforos_peatonales["Norte_directo"].agregar_token("blanco")
                self.semaforos_peatonales["Norte_directo"].quitar_token("rojo")

                # 2- Norte indirecto a rojo
                self.semaforos_peatonales["Norte_indirecto"].cambiar_estado("rojo")
                self.semaforos_peatonales["Norte_indirecto"].agregar_token("rojo")
                self.semaforos_peatonales["Norte_indirecto"].quitar_token("blanco")

                # 3- Este directo a rojo
                self.semaforos_peatonales["Este_directo"].cambiar_estado("rojo")
                self.semaforos_peatonales["Este_directo"].agregar_token("rojo")
                self.semaforos_peatonales["Este_directo"].quitar_token("blanco")

                # 4- Este indirecto a blanco
                self.semaforos_peatonales["Este_indirecto"].cambiar_estado("blanco")
                self.semaforos_peatonales["Este_indirecto"].agregar_token("blanco")
                self.semaforos_peatonales["Este_indirecto"].quitar_token("rojo")

                # 5- Oeste indirecto a rojo
                self.semaforos_peatonales["Oeste_indirecto"].cambiar_estado("rojo")
                self.semaforos_peatonales["Oeste_indirecto"].agregar_token("rojo")
                self.semaforos_peatonales["Oeste_indirecto"].quitar_token("blanco")

                self.estado_label.setText("Estado: Norte cambia a rojo, Este cambia a verde")
                self.contador = 0
                self.estado_actual = "Este_verde"

        elif self.estado_actual == "Este_verde":
            if self.contador == 0:
                self.estado_label.setText("Estado: Este en verde")
                self.contador += 1
            elif self.contador == 1:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Este"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Este"].agregar_token("amarillo")
                self.semaforos_vehiculares["Este"].quitar_token("verde")
                self.estado_label.setText("Estado: Este cambia a amarillo")
                self.contador += 1
            elif self.contador == 2:
                # Cambiar a rojo
                self.semaforos_vehiculares["Este"].cambiar_estado("rojo")
                self.semaforos_vehiculares["Este"].agregar_token("rojo")
                self.semaforos_vehiculares["Este"].quitar_token("amarillo")

                # Activar semáforo Sur para completar el ciclo
                self.semaforos_vehiculares["Sur"].cambiar_estado("verde")
                self.semaforos_vehiculares["Sur"].agregar_token("verde")
                self.semaforos_vehiculares["Sur"].quitar_token("rojo")

                # Restablecer configuración peatonal para Sur
                self.semaforos_peatonales["Sur_indirecto"].cambiar_estado("blanco")
                self.semaforos_peatonales["Sur_indirecto"].agregar_token("blanco")
                self.semaforos_peatonales["Sur_indirecto"].quitar_token("rojo")

                self.semaforos_peatonales["Sur_directo"].cambiar_estado("rojo")
                self.semaforos_peatonales["Sur_directo"].agregar_token("rojo")
                self.semaforos_peatonales["Sur_directo"].quitar_token("blanco")

                # Restablecer Este indirecto
                self.semaforos_peatonales["Este_indirecto"].cambiar_estado("rojo")
                self.semaforos_peatonales["Este_indirecto"].agregar_token("rojo")
                self.semaforos_peatonales["Este_indirecto"].quitar_token("blanco")

                # Restablecer Este directo
                self.semaforos_peatonales["Este_directo"].cambiar_estado("blanco")
                self.semaforos_peatonales["Este_directo"].agregar_token("blanco")
                self.semaforos_peatonales["Este_directo"].quitar_token("rojo")

                self.estado_label.setText("Estado: Este cambia a rojo, Sur cambia a verde")
                self.contador = 0
                self.estado_actual = "Sur_verde"

        # Actualizar visualización
        self.dibujar_cruce()

def main():
    app = QApplication(sys.argv)
    window = SimuladorSemaforos()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

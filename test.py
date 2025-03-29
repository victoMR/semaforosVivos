import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout,
    QHBoxLayout, QPushButton, QWidget, QLabel, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QBrush, QPen, QColor, QFont, QPainter, QPolygonF

class Vehiculo:
    def __init__(self, direccion, tipo_movimiento):
        self.direccion = direccion  # Dirección de origen (Norte, Sur, Este, Oeste)
        self.tipo_movimiento = tipo_movimiento  # 'frente', 'derecha', 'izquierda'
        self.posicion = self.get_posicion_inicial()
        self.velocidad = 10
        self.detenido = True
        self.fuera_de_pantalla = False
        self.color = QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

        # Definir ruta basada en dirección y tipo de movimiento
        self.ruta = self.definir_ruta()
        self.indice_ruta = 0

    def get_posicion_inicial(self):
        if self.direccion == "Norte":
            return QPointF(350, 500)  # Aparece en el borde inferior
        elif self.direccion == "Sur":
            return QPointF(325, 0)     # Aparece en el borde superior
        elif self.direccion == "Este":
            return QPointF(0, 250)     # Aparece en el borde izquierdo
        elif self.direccion == "Oeste":
            return QPointF(700, 225)   # Aparece en el borde derecho

    def definir_ruta(self):
        # Definir puntos clave en la ruta según dirección y tipo de movimiento
        if self.direccion == "Norte":
            if self.tipo_movimiento == "frente":
                return [QPointF(350, 500), QPointF(350, 250), QPointF(350, 0)]
            elif self.tipo_movimiento == "derecha":
                return [QPointF(350, 500), QPointF(350, 300), QPointF(450, 300), QPointF(700, 300)]
            elif self.tipo_movimiento == "izquierda":
                return [QPointF(350, 500), QPointF(350, 300), QPointF(250, 300), QPointF(0, 300)]

        elif self.direccion == "Sur":
            if self.tipo_movimiento == "frente":
                return [QPointF(325, 0), QPointF(325, 250), QPointF(325, 500)]
            elif self.tipo_movimiento == "derecha":
                return [QPointF(325, 0), QPointF(325, 200), QPointF(225, 200), QPointF(0, 200)]
            elif self.tipo_movimiento == "izquierda":
                return [QPointF(325, 0), QPointF(325, 200), QPointF(425, 200), QPointF(700, 200)]

        elif self.direccion == "Este":
            if self.tipo_movimiento == "frente":
                return [QPointF(0, 250), QPointF(325, 250), QPointF(700, 250)]
            elif self.tipo_movimiento == "derecha":
                return [QPointF(0, 250), QPointF(300, 250), QPointF(300, 350), QPointF(300, 500)]
            elif self.tipo_movimiento == "izquierda":
                return [QPointF(0, 250), QPointF(300, 250), QPointF(300, 150), QPointF(300, 0)]

        elif self.direccion == "Oeste":
            if self.tipo_movimiento == "frente":
                return [QPointF(700, 225), QPointF(350, 225), QPointF(0, 225)]
            elif self.tipo_movimiento == "derecha":
                return [QPointF(700, 225), QPointF(400, 225), QPointF(400, 325), QPointF(400, 500)]
            elif self.tipo_movimiento == "izquierda":
                return [QPointF(700, 225), QPointF(400, 225), QPointF(400, 125), QPointF(400, 0)]

    def mover(self, semaforo_verde):
        # Verificar si el semáforo de su dirección está en verde
        if self.direccion == semaforo_verde or (self.indice_ruta > 1 and not self.detenido):
            self.detenido = False

        if not self.detenido and self.indice_ruta < len(self.ruta) - 1:
            # Mover hacia el siguiente punto en la ruta
            objetivo = self.ruta[self.indice_ruta + 1]
            dx = objetivo.x() - self.posicion.x()
            dy = objetivo.y() - self.posicion.y()
            distancia = (dx**2 + dy**2)**0.5

            if distancia < self.velocidad:
                self.posicion = objetivo
                self.indice_ruta += 1
            else:
                self.posicion.setX(self.posicion.x() + (dx / distancia) * self.velocidad)
                self.posicion.setY(self.posicion.y() + (dy / distancia) * self.velocidad)

        # Verificar si ha salido de la pantalla
        if (self.posicion.x() < 0 or self.posicion.x() > 700 or
            self.posicion.y() < 0 or self.posicion.y() > 500):
            self.fuera_de_pantalla = True

    def dibujar(self, scene):
        # Dibujar un triángulo orientado según la dirección
        polygon = QPolygonF()
        size = 8

        if self.direccion == "Norte":
            polygon.append(QPointF(self.posicion.x(), self.posicion.y() - size))
            polygon.append(QPointF(self.posicion.x() - size/2, self.posicion.y() + size/2))
            polygon.append(QPointF(self.posicion.x() + size/2, self.posicion.y() + size/2))
        elif self.direccion == "Sur":
            polygon.append(QPointF(self.posicion.x(), self.posicion.y() + size))
            polygon.append(QPointF(self.posicion.x() - size/2, self.posicion.y() - size/2))
            polygon.append(QPointF(self.posicion.x() + size/2, self.posicion.y() - size/2))
        elif self.direccion == "Este":
            polygon.append(QPointF(self.posicion.x() + size, self.posicion.y()))
            polygon.append(QPointF(self.posicion.x() - size/2, self.posicion.y() - size/2))
            polygon.append(QPointF(self.posicion.x() - size/2, self.posicion.y() + size/2))
        elif self.direccion == "Oeste":
            polygon.append(QPointF(self.posicion.x() - size, self.posicion.y()))
            polygon.append(QPointF(self.posicion.x() + size/2, self.posicion.y() - size/2))
            polygon.append(QPointF(self.posicion.x() + size/2, self.posicion.y() + size/2))

        scene.addPolygon(polygon, QPen(Qt.GlobalColor.black), QBrush(self.color))

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
        self.estado = "rojo"  # Inicialmente en rojo
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

        # Configuración inicial de semáforos
        self.setup_semaforos()

        # Lista de vehículos - Mover esta inicialización antes de setup_ui
        self.vehiculos = []
        self.tiempo_generacion = 0
        self.probabilidad_generacion = 1  # Probabilidad de generar un vehículo en cada paso

        # Configurar la interfaz gráfica
        self.setup_ui()

        # Timer para actualizar la simulación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_simulacion)
        self.estado_actual = "Sur_verde"
        self.contador_tiempo = 0
        self.tiempos_estados = {
            "verde": 5,    # 5 pasos en verde
            "amarillo": 2,  # 2 pasos en amarillo
            "rojo": 1       # 1 paso de transición
        }

        # Lista de vehículos
        self.vehiculos = []
        self.tiempo_generacion = 0
        self.probabilidad_generacion = 1  # Probabilidad de generar un vehículo en cada paso

    def setup_semaforos(self):
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
        for direccion in ["Norte", "Sur", "Este", "Oeste"]:
            for tipo in ["directo", "indirecto"]:
                key = f"{direccion}_{tipo}"
                self.semaforos_peatonales[key] = SemaforoPeatonal(direccion, tipo)

        # Configuración inicial de semáforos peatonales
        peatonales_blancos = ["Sur_indirecto", "Oeste_directo", "Norte_directo", "Este_directo"]
        for key in peatonales_blancos:
            self.semaforos_peatonales[key].estado = "blanco"
            self.semaforos_peatonales[key].tokens = {"blanco": 1, "rojo": 0}

    def setup_ui(self):
        self.setWindowTitle("Simulador de Semáforos con Tráfico")
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
        self.scene.addRect(0, 225, 700, 50, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))  # Horizontal
        self.scene.addRect(325, 0, 50, 500, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))  # Vertical

        # Líneas divisorias
        pen = QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine)
        self.scene.addLine(0, 250, 700, 250, pen)  # Horizontal
        self.scene.addLine(350, 0, 350, 500, pen)  # Vertical

        # Semáforos vehiculares
        self.dibujar_semaforo_vehicular("Norte", 350, 130, 90)   # Norte
        self.dibujar_semaforo_vehicular("Sur", 325, 370, 270)    # Sur
        self.dibujar_semaforo_vehicular("Este", 450, 225, 0)     # Este
        self.dibujar_semaforo_vehicular("Oeste", 250, 250, 180)  # Oeste

        # Semáforos peatonales
        self.dibujar_semaforo_peatonal("Norte_directo", 305, 100)
        self.dibujar_semaforo_peatonal("Norte_indirecto", 370, 100)
        self.dibujar_semaforo_peatonal("Sur_directo", 370, 400)
        self.dibujar_semaforo_peatonal("Sur_indirecto", 305, 400)
        self.dibujar_semaforo_peatonal("Este_directo", 420, 210)
        self.dibujar_semaforo_peatonal("Este_indirecto", 420, 265)
        self.dibujar_semaforo_peatonal("Oeste_directo", 280, 265)
        self.dibujar_semaforo_peatonal("Oeste_indirecto", 280, 210)

        # Etiquetas de direcciones
        font = QFont("Arial", 12, QFont.Weight.Bold)
        self.scene.addText("Norte", font).setPos(340, 20)
        self.scene.addText("Sur", font).setPos(345, 460)
        self.scene.addText("Este", font).setPos(520, 240)
        self.scene.addText("Oeste", font).setPos(180, 240)

        # Dibujar vehículos
        for vehiculo in self.vehiculos:
            vehiculo.dibujar(self.scene)

    def dibujar_semaforo_vehicular(self, direccion, x, y, rotacion):
        semaforo = self.semaforos_vehiculares[direccion]

        # Rectángulo principal
        rect = self.scene.addRect(0, 0, 20, 60, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.darkGray))
        rect.setPos(x, y)
        rect.setRotation(rotacion)

        # Luces
        colores = {
            "rojo": QColor(255, 0, 0) if semaforo.estado == "rojo" else QColor(100, 0, 0),
            "amarillo": QColor(255, 255, 0) if semaforo.estado == "amarillo" else QColor(100, 100, 0),
            "verde": QColor(0, 255, 0) if semaforo.estado == "verde" else QColor(0, 100, 0)
        }

        for i, (color_key, color) in enumerate(colores.items()):
            luz = self.scene.addEllipse(0, 0, 15, 15, QPen(Qt.GlobalColor.black), QBrush(color))
            luz.setPos(x + 2.5, y + 5 + i * 17.5)
            luz.setRotation(rotacion)

        # Mostrar tokens
        font = QFont("Arial", 8)
        for i, estado in enumerate(["rojo", "amarillo", "verde"]):
            tokens_text = f"{estado[0].upper()}: {semaforo.tokens[estado]}"
            text = self.scene.addText(tokens_text, font)

            if rotacion == 0:    # Este
                text.setPos(x + 25, y + i * 15)
            elif rotacion == 90: # Norte
                text.setPos(x - 40, y + i * 15)
            elif rotacion == 180: # Oeste
                text.setPos(x - 70, y + i * 15)
            else:                # Sur (270)
                text.setPos(x + 25, y + i * 15)

    def dibujar_semaforo_peatonal(self, key, x, y):
        semaforo = self.semaforos_peatonales[key]

        # Rectángulo principal
        self.scene.addRect(0, 0, 15, 30, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.darkGray)).setPos(x, y)

        # Luces
        color_rojo = QColor(255, 0, 0) if semaforo.estado == "rojo" else QColor(100, 0, 0)
        color_blanco = QColor(255, 255, 255) if semaforo.estado == "blanco" else QColor(100, 100, 100)

        self.scene.addEllipse(0, 0, 10, 10, QPen(Qt.GlobalColor.black), QBrush(color_rojo)).setPos(x + 2.5, y + 2.5)
        self.scene.addEllipse(0, 0, 10, 10, QPen(Qt.GlobalColor.black), QBrush(color_blanco)).setPos(x + 2.5, y + 17.5)

        # Etiqueta de tipo
        font = QFont("Arial", 6)
        self.scene.addText(semaforo.tipo[0].upper(), font).setPos(x + 5, y + 32)

        # Mostrar tokens
        for i, estado in enumerate(["rojo", "blanco"]):
            tokens_text = f"{estado[0].upper()}: {semaforo.tokens[estado]}"
            self.scene.addText(tokens_text, font).setPos(x - 20, y + i * 10)

    def iniciar_simulacion(self):
        self.timer.start(500)  # 0.5 segundos por paso

    def pausar_simulacion(self):
        self.timer.stop()

    def paso_simulacion(self):
        self.timer.stop()
        self.actualizar_simulacion()

    def reiniciar_simulacion(self):
        self.timer.stop()
        self.setup_semaforos()
        self.vehiculos = []
        self.estado_actual = "Sur_verde"
        self.contador_tiempo = 0
        self.tiempo_generacion = 0
        self.estado_label.setText("Estado: Sur en verde")
        self.dibujar_cruce()

    def generar_vehiculo(self):
        # Decidir si generar un nuevo vehículo basado en probabilidad
        if random.random() < self.probabilidad_generacion:
            direccion = random.choice(["Norte", "Sur", "Este", "Oeste"])
            tipo_movimiento = random.choice(["frente", "derecha", "izquierda"])
            self.vehiculos.append(Vehiculo(direccion, tipo_movimiento))

    def actualizar_simulacion(self):
        self.contador_tiempo += 1
        self.tiempo_generacion += 1
        direccion_actual, estado_actual = self.estado_actual.split("_")

        # Generar nuevos vehículos
        if self.tiempo_generacion >= 2:  # Intentar generar cada 2 pasos
            self.generar_vehiculo()
            self.tiempo_generacion = 0

        # Mover vehículos según el semáforo actual
        for vehiculo in self.vehiculos:
            vehiculo.mover(direccion_actual if estado_actual == "verde" else "")

        # Eliminar vehículos que hayan salido de la pantalla
        self.vehiculos = [v for v in self.vehiculos if not v.fuera_de_pantalla]

        # Determinar qué hacer según el estado actual
        if estado_actual == "verde":
            if self.contador_tiempo >= self.tiempos_estados["verde"]:
                # Cambiar a amarillo
                self.cambiar_estado_semaforo(direccion_actual, "amarillo")
                self.estado_actual = f"{direccion_actual}_amarillo"
                self.contador_tiempo = 0
                self.estado_label.setText(f"Estado: {direccion_actual} cambia a amarillo")

        elif estado_actual == "amarillo":
            if self.contador_tiempo >= self.tiempos_estados["amarillo"]:
                # Cambiar a rojo y determinar siguiente dirección
                self.cambiar_estado_semaforo(direccion_actual, "rojo")

                # Determinar siguiente dirección en el ciclo: Sur -> Oeste -> Norte -> Este -> Sur
                siguiente_direccion = {
                    "Sur": "Oeste",
                    "Oeste": "Norte",
                    "Norte": "Este",
                    "Este": "Sur"
                }[direccion_actual]

                # Cambiar siguiente dirección a verde
                self.cambiar_estado_semaforo(siguiente_direccion, "verde")

                # Actualizar semáforos peatonales correspondientes
                self.actualizar_peatonales(direccion_actual, siguiente_direccion)

                self.estado_actual = f"{siguiente_direccion}_verde"
                self.contador_tiempo = 0
                self.estado_label.setText(f"Estado: {direccion_actual} cambia a rojo, {siguiente_direccion} cambia a verde")

        self.dibujar_cruce()

    def cambiar_estado_semaforo(self, direccion, nuevo_estado):
        semaforo = self.semaforos_vehiculares[direccion]
        estado_anterior = semaforo.estado

        # Actualizar tokens
        semaforo.quitar_token(estado_anterior)
        semaforo.agregar_token(nuevo_estado)
        semaforo.cambiar_estado(nuevo_estado)

    def actualizar_peatonales(self, direccion_anterior, direccion_nueva):
        # Mapeo de qué semáforos peatonales deben cambiar para cada dirección vehicular
        configuraciones = {
            "Sur": {
                "blanco": ["Sur_indirecto", "Oeste_directo"],
                "rojo": ["Sur_directo", "Oeste_indirecto"]
            },
            "Oeste": {
                "blanco": ["Oeste_indirecto", "Norte_directo"],
                "rojo": ["Oeste_directo", "Norte_indirecto", "Sur_indirecto"]
            },
            "Norte": {
                "blanco": ["Norte_indirecto", "Este_directo"],
                "rojo": ["Norte_directo", "Este_indirecto", "Oeste_directo"]
            },
            "Este": {
                "blanco": ["Este_indirecto", "Sur_directo"],
                "rojo": ["Este_directo", "Sur_indirecto", "Norte_indirecto"]
            }
        }

        # Aplicar cambios a semáforos peatonales
        for estado, keys in configuraciones[direccion_nueva].items():
            for key in keys:
                semaforo = self.semaforos_peatonales[key]
                estado_contrario = "blanco" if estado == "rojo" else "rojo"

                if semaforo.tokens[estado_contrario] > 0:
                    semaforo.quitar_token(estado_contrario)
                    semaforo.agregar_token(estado)
                    semaforo.cambiar_estado(estado)

def main():
    app = QApplication(sys.argv)
    window = SimuladorSemaforos()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

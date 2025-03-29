import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout,
    QHBoxLayout, QPushButton, QWidget, QLabel, QGridLayout, QSlider,
    QTabWidget, QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QBrush, QPen, QColor, QFont, QPainter, QPolygonF

class Vehicle:
    def __init__(self, lane, position):
        self.lane = lane  # "Norte", "Sur", "Este", "Oeste"
        self.position = position  # Position on the lane (0-100)
        self.speed = 2  # Default speed
        self.stopped = False
        self.color = QColor(30, 144, 255)  # Default blue color

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

        # Configuración inicial de semáforos peatonales
        peatonales_blancos = ["Sur_indirecto", "Oeste_directo", "Norte_directo", "Este_directo"]
        for key in peatonales_blancos:
            self.semaforos_peatonales[key].estado = "blanco"
            self.semaforos_peatonales[key].tokens = {"blanco": 1, "rojo": 0}

        # Inicialización de vehículos
        self.vehicles = []

        # Velocidad de simulación
        self.simulation_speed = 1.0

        # Timer para actualizar la simulación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_simulacion)

        # Timer para movimiento de vehículos
        self.vehicle_timer = QTimer(self)
        self.vehicle_timer.timeout.connect(self.update_vehicles)
        self.vehicle_timer.start(50)  # Update vehicles every 50ms

        self.current_step = 0
        self.max_steps = 5  # Número de pasos en un ciclo completo

        # Estado actual de la simulación
        self.estado_actual = "Sur_verde"
        self.contador = 0

        # Historial de estados para Petri Net
        self.state_history = ["Sur_verde"]

        # Configurar la interfaz gráfica
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Simulador de Semáforos Mejorado")
        self.setGeometry(100, 100, 1200, 800)

        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Crear pestañas
        self.tabs = QTabWidget()

        # Pestaña de simulación
        sim_tab = QWidget()
        sim_layout = QVBoxLayout(sim_tab)

        # Crear escena y vista más grande
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setSceneRect(QRectF(0, 0, 900, 700))

        sim_layout.addWidget(self.view)

        # Controles de simulación
        control_layout = QHBoxLayout()

        # Grupo de controles básicos
        basic_controls = QGroupBox("Controles de Simulación")
        basic_layout = QHBoxLayout(basic_controls)

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.iniciar_simulacion)
        basic_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pausar_simulacion)
        basic_layout.addWidget(self.pause_button)

        self.step_button = QPushButton("Paso a Paso")
        self.step_button.clicked.connect(self.paso_simulacion)
        basic_layout.addWidget(self.step_button)

        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.reiniciar_simulacion)
        basic_layout.addWidget(self.reset_button)

        control_layout.addWidget(basic_controls)

        # Grupo de control de velocidad
        speed_controls = QGroupBox("Control de Velocidad")
        speed_layout = QHBoxLayout(speed_controls)

        speed_label = QLabel("Velocidad:")
        speed_layout.addWidget(speed_label)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(5)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.valueChanged.connect(self.change_speed)
        speed_layout.addWidget(self.speed_slider)

        self.speed_value_label = QLabel("1.0x")
        speed_layout.addWidget(self.speed_value_label)

        control_layout.addWidget(speed_controls)

        sim_layout.addLayout(control_layout)

        # Grupo de control de vehículos
        vehicles_controls = QGroupBox("Agregar Vehículos")
        vehicles_layout = QGridLayout(vehicles_controls)

        # Botones para agregar vehículos
        self.add_north_btn = QPushButton("Agregar Norte")
        self.add_north_btn.clicked.connect(lambda: self.add_vehicle("Norte"))
        vehicles_layout.addWidget(self.add_north_btn, 0, 0)

        self.add_south_btn = QPushButton("Agregar Sur")
        self.add_south_btn.clicked.connect(lambda: self.add_vehicle("Sur"))
        vehicles_layout.addWidget(self.add_south_btn, 0, 1)

        self.add_east_btn = QPushButton("Agregar Este")
        self.add_east_btn.clicked.connect(lambda: self.add_vehicle("Este"))
        vehicles_layout.addWidget(self.add_east_btn, 1, 0)

        self.add_west_btn = QPushButton("Agregar Oeste")
        self.add_west_btn.clicked.connect(lambda: self.add_vehicle("Oeste"))
        vehicles_layout.addWidget(self.add_west_btn, 1, 1)

        # Control de densidad de tráfico
        density_layout = QHBoxLayout()

        density_label = QLabel("Densidad Automática:")
        density_layout.addWidget(density_label)

        self.density_spinner = QSpinBox()
        self.density_spinner.setMinimum(0)
        self.density_spinner.setMaximum(10)
        self.density_spinner.setValue(0)
        self.density_spinner.valueChanged.connect(self.set_auto_traffic)
        density_layout.addWidget(self.density_spinner)

        vehicles_layout.addLayout(density_layout, 2, 0, 1, 2)

        sim_layout.addWidget(vehicles_controls)

        # Etiqueta de estado actual
        self.estado_label = QLabel("Estado: Sur en verde")
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sim_layout.addWidget(self.estado_label)

        # Añadir pestaña de simulación
        self.tabs.addTab(sim_tab, "Simulación")

        # Pestaña de Red de Petri
        petri_tab = QWidget()
        petri_layout = QVBoxLayout(petri_tab)

        self.petri_scene = QGraphicsScene()
        self.petri_view = QGraphicsView(self.petri_scene)
        self.petri_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.petri_view.setSceneRect(QRectF(0, 0, 900, 700))

        petri_layout.addWidget(self.petri_view)

        # Etiqueta para el diagrama de Petri
        petri_info = QLabel("Diagrama de Red de Petri - Estados y Transiciones")
        petri_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        petri_layout.addWidget(petri_info)

        # Añadir pestaña de Red de Petri
        self.tabs.addTab(petri_tab, "Red de Petri")

        # Añadir pestañas al layout principal
        main_layout.addWidget(self.tabs)

        # Dibujar el cruce inicial
        self.dibujar_cruce()
        self.dibujar_petri_net()

        # Configurar timer para auto-tráfico
        self.traffic_timer = QTimer(self)
        self.traffic_timer.timeout.connect(self.generate_traffic)

    def add_vehicle(self, lane):
        # Añadir vehículo en la posición inicial del carril indicado
        if lane == "Norte":
            self.vehicles.append(Vehicle("Norte", 0))
        elif lane == "Sur":
            self.vehicles.append(Vehicle("Sur", 100))
        elif lane == "Este":
            self.vehicles.append(Vehicle("Este", 0))
        elif lane == "Oeste":
            self.vehicles.append(Vehicle("Oeste", 100))

        # Actualizar visualización
        self.dibujar_cruce()

    def update_vehicles(self):
        # Mover vehículos según su velocidad y el estado de los semáforos
        vehicles_to_remove = []

        for vehicle in self.vehicles:
            # Determinar si el vehículo debe detenerse en el semáforo
            stop_at_light = False

            if vehicle.lane == "Norte" and 45 <= vehicle.position <= 55:
                if self.semaforos_vehiculares["Norte"].estado != "verde":
                    stop_at_light = True
            elif vehicle.lane == "Sur" and 45 <= vehicle.position <= 55:
                if self.semaforos_vehiculares["Sur"].estado != "verde":
                    stop_at_light = True
            elif vehicle.lane == "Este" and 45 <= vehicle.position <= 55:
                if self.semaforos_vehiculares["Este"].estado != "verde":
                    stop_at_light = True
            elif vehicle.lane == "Oeste" and 45 <= vehicle.position <= 55:
                if self.semaforos_vehiculares["Oeste"].estado != "verde":
                    stop_at_light = True

            # Actualizar posición si no está detenido
            if not stop_at_light:
                if vehicle.lane in ["Norte", "Este"]:
                    vehicle.position += vehicle.speed * (self.simulation_speed / 5)
                    if vehicle.position > 100:
                        vehicles_to_remove.append(vehicle)
                else:  # Sur, Oeste
                    vehicle.position -= vehicle.speed * (self.simulation_speed / 5)
                    if vehicle.position < 0:
                        vehicles_to_remove.append(vehicle)

        # Eliminar vehículos que han salido de la pantalla
        for vehicle in vehicles_to_remove:
            if vehicle in self.vehicles:
                self.vehicles.remove(vehicle)

        # Actualizar visualización solo si hay cambios
        if vehicles_to_remove or self.vehicles:
            self.dibujar_cruce()

    def set_auto_traffic(self, value):
        if value > 0:
            # Iniciar generación automática de tráfico
            interval = 5000 // value  # Más densidad = intervalos más cortos
            self.traffic_timer.start(interval)
        else:
            # Detener generación automática
            self.traffic_timer.stop()

    def generate_traffic(self):
        # Generar tráfico aleatorio en las cuatro direcciones
        import random
        direction = random.choice(["Norte", "Sur", "Este", "Oeste"])
        self.add_vehicle(direction)

    def change_speed(self, value):
        self.simulation_speed = value / 5.0
        self.speed_value_label.setText(f"{self.simulation_speed:.1f}x")

    def dibujar_cruce(self):
        self.scene.clear()

        # Dibujar calles más anchas
        # Horizontal
        self.scene.addRect(0, 315, 900, 70, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))
        # Vertical
        self.scene.addRect(415, 0, 70, 700, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))

        # Líneas divisorias
        pen = QPen(Qt.GlobalColor.white, 3, Qt.PenStyle.DashLine)
        self.scene.addLine(0, 350, 900, 350, pen)  # Horizontal
        self.scene.addLine(450, 0, 450, 700, pen)  # Vertical

        # Semáforos vehiculares
        self.dibujar_semaforo_vehicular("Norte", 450, 205, 90)  # Norte
        self.dibujar_semaforo_vehicular("Sur", 415, 485, 270)  # Sur
        self.dibujar_semaforo_vehicular("Este", 550, 315, 0)   # Este
        self.dibujar_semaforo_vehicular("Oeste", 350, 350, 180) # Oeste

        # Semáforos peatonales
        # Norte
        self.dibujar_semaforo_peatonal("Norte_directo", 395, 170)
        self.dibujar_semaforo_peatonal("Norte_indirecto", 475, 170)
        # Sur
        self.dibujar_semaforo_peatonal("Sur_directo", 475, 530)
        self.dibujar_semaforo_peatonal("Sur_indirecto", 395, 530)
        # Este
        self.dibujar_semaforo_peatonal("Este_directo", 585, 295)
        self.dibujar_semaforo_peatonal("Este_indirecto", 585, 375)
        # Oeste
        self.dibujar_semaforo_peatonal("Oeste_directo", 315, 375)
        self.dibujar_semaforo_peatonal("Oeste_indirecto", 315, 295)

        # Dibujar vehículos
        self.dibujar_vehiculos()

        # Agregar etiquetas de direcciones
        font = QFont("Arial", 16, QFont.Weight.Bold)

        text_norte = self.scene.addText("Norte", font)
        text_norte.setPos(430, 30)

        text_sur = self.scene.addText("Sur", font)
        text_sur.setPos(435, 630)

        text_este = self.scene.addText("Este", font)
        text_este.setPos(700, 330)

        text_oeste = self.scene.addText("Oeste", font)
        text_oeste.setPos(200, 330)

    def dibujar_vehiculos(self):
        # Dibujar todos los vehículos en la escena
        for vehicle in self.vehicles:
            # Determinar posición según carril y posición relativa
            if vehicle.lane == "Norte":
                # Desde abajo hacia arriba
                x = 430
                y = 700 - (vehicle.position / 100 * 700)
                rotation = 90
            elif vehicle.lane == "Sur":
                # Desde arriba hacia abajo
                x = 450
                y = vehicle.position / 100 * 700
                rotation = 270
            elif vehicle.lane == "Este":
                # Desde izquierda hacia derecha
                x = vehicle.position / 100 * 900
                y = 330
                rotation = 0
            elif vehicle.lane == "Oeste":
                # Desde derecha hacia izquierda
                x = 900 - (vehicle.position / 100 * 900)
                y = 350
                rotation = 180

            # Dibujar triángulo para representar el vehículo
            polygon = QPolygonF([
                QPointF(0, -10),
                QPointF(20, 0),
                QPointF(0, 10)
            ])

            vehicle_item = self.scene.addPolygon(polygon, QPen(Qt.GlobalColor.black), QBrush(vehicle.color))
            vehicle_item.setPos(x, y)
            vehicle_item.setRotation(rotation)

    def dibujar_semaforo_vehicular(self, direccion, x, y, rotacion):
        # Obtener el estado del semáforo
        semaforo = self.semaforos_vehiculares[direccion]

        # Rectángulo principal más grande
        rect = QRectF(0, 0, 30, 90)
        transform = self.scene.addRect(rect, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.darkGray))
        transform.setPos(x, y)
        transform.setRotation(rotacion)

        # Luces más grandes
        # Rojo
        color_rojo = QColor(255, 0, 0) if semaforo.estado == "rojo" else QColor(100, 0, 0)
        luz_roja = self.scene.addEllipse(0, 0, 25, 25, QPen(Qt.GlobalColor.black), QBrush(color_rojo))
        luz_roja.setPos(x + 2.5, y + 5)
        luz_roja.setRotation(rotacion)

        # Amarillo
        color_amarillo = QColor(255, 255, 0) if semaforo.estado == "amarillo" else QColor(100, 100, 0)
        luz_amarilla = self.scene.addEllipse(0, 0, 25, 25, QPen(Qt.GlobalColor.black), QBrush(color_amarillo))
        luz_amarilla.setPos(x + 2.5, y + 32.5)
        luz_amarilla.setRotation(rotacion)

        # Verde
        color_verde = QColor(0, 255, 0) if semaforo.estado == "verde" else QColor(0, 100, 0)
        luz_verde = self.scene.addEllipse(0, 0, 25, 25, QPen(Qt.GlobalColor.black), QBrush(color_verde))
        luz_verde.setPos(x + 2.5, y + 60)
        luz_verde.setRotation(rotacion)

        # Mostrar tokens con fuente más grande
        font = QFont("Arial", 10, QFont.Weight.Bold)
        for idx, estado in enumerate(["rojo", "amarillo", "verde"]):
            tokens_text = f"{estado[0].upper()}: {semaforo.tokens[estado]}"
            text = self.scene.addText(tokens_text, font)
            offset = 40  # Más espacio para texto
            if rotacion == 0:  # Este
                text.setPos(x + 35, y + idx * 20)
            elif rotacion == 90:  # Norte
                text.setPos(x - 60, y + idx * 20)
            elif rotacion == 180:  # Oeste
                text.setPos(x - 90, y + idx * 20)
            elif rotacion == 270:  # Sur
                text.setPos(x + 35, y + idx * 20)

    def dibujar_semaforo_peatonal(self, key, x, y):
        # Obtener el estado del semáforo
        semaforo = self.semaforos_peatonales[key]

        # Determinar colores según el estado
        color_blanco = QColor(255, 255, 255) if semaforo.estado == "blanco" else QColor(100, 100, 100)
        color_rojo = QColor(255, 0, 0) if semaforo.estado == "rojo" else QColor(100, 0, 0)

        # Rectángulo principal más grande
        rect = self.scene.addRect(0, 0, 20, 45, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.darkGray))
        rect.setPos(x, y)

        # Luces más grandes
        # Rojo (arriba)
        luz_roja = self.scene.addEllipse(0, 0, 15, 15, QPen(Qt.GlobalColor.black), QBrush(color_rojo))
        luz_roja.setPos(x + 2.5, y + 5)

        # Blanco (abajo)
        luz_blanca = self.scene.addEllipse(0, 0, 15, 15, QPen(Qt.GlobalColor.black), QBrush(color_blanco))
        luz_blanca.setPos(x + 2.5, y + 25)

        # Etiqueta para identificar directo/indirecto con fuente más grande
        font = QFont("Arial", 8, QFont.Weight.Bold)
        tipo_text = semaforo.tipo[0].upper()
        text = self.scene.addText(tipo_text, font)
        text.setPos(x + 5, y + 45)

        # Mostrar tokens con más espacio
        for idx, estado in enumerate(["rojo", "blanco"]):
            tokens_text = f"{estado[0].upper()}: {semaforo.tokens[estado]}"
            text = self.scene.addText(tokens_text, font)
            text.setPos(x - 30, y + idx * 15)

    def dibujar_petri_net(self):
        self.petri_scene.clear()

        # Definimos los estados y transiciones de la red de Petri
        states = [
            {"name": "Sur_verde", "pos": (450, 100)},
            {"name": "Sur_amarillo", "pos": (250, 250)},
            {"name": "Oeste_verde", "pos": (450, 400)},
            {"name": "Oeste_amarillo", "pos": (650, 250)},
            {"name": "Norte_verde", "pos": (100, 500)},
            {"name": "Norte_amarillo", "pos": (250, 650)},
            {"name": "Este_verde", "pos": (450, 700)},
            {"name": "Este_amarillo", "pos": (650, 650)},
        ]

        transitions = [
            {"from": "Sur_verde", "to": "Sur_amarillo", "label": "tiempo"},
            {"from": "Sur_amarillo", "to": "Oeste_verde", "label": "tiempo"},
            {"from": "Oeste_verde", "to": "Oeste_amarillo", "label": "tiempo"},
            {"from": "Oeste_amarillo", "to": "Norte_verde", "label": "tiempo"},
            {"from": "Norte_verde", "to": "Norte_amarillo", "label": "tiempo"},
            {"from": "Norte_amarillo", "to": "Este_verde", "label": "tiempo"},
            {"from": "Este_verde", "to": "Este_amarillo", "label": "tiempo"},
            {"from": "Este_amarillo", "to": "Sur_verde", "label": "tiempo"},
        ]

        # Dibujar flechas de transición
        arrow_pen = QPen(QColor(0, 0, 0), 2)

        for transition in transitions:
            from_state = next(s for s in states if s["name"] == transition["from"])
            to_state = next(s for s in states if s["name"] == transition["to"])

            # Dibujar línea
            line = self.petri_scene.addLine(
                from_state["pos"][0], from_state["pos"][1],
                to_state["pos"][0], to_state["pos"][1],
                arrow_pen
            )

            # Calcular punto medio para la etiqueta
            mid_x = (from_state["pos"][0] + to_state["pos"][0]) / 2
            mid_y = (from_state["pos"][1] + to_state["pos"][1]) / 2

            # Añadir etiqueta
            text = self.petri_scene.addText(transition["label"])
            text.setPos(mid_x, mid_y)

            # Dibujar punta de flecha
            self.dibujar_punta_flecha(
                from_state["pos"][0], from_state["pos"][1],
                to_state["pos"][0], to_state["pos"][1]
            )

        # Dibujar estados (nodos)
        for state in states:
            # Determinar si es el estado actual
            is_current = state["name"] == self.estado_actual

            # Elegir color según si es estado actual
            color = QColor(255, 165, 0) if is_current else QColor(100, 149, 237)

            # Dibujar círculo
            node = self.petri_scene.addEllipse(
                state["pos"][0] - 40, state["pos"][1] - 40,
                80, 80,
                QPen(QColor(0, 0, 0), 2),
                QBrush(color)
            )

            # Añadir etiqueta
            text = self.petri_scene.addText(state["name"])
            text.setPos(state["pos"][0] - 35, state["pos"][1] - 10)

            # Destacar el estado actual
            if is_current:
                highlight = self.petri_scene.addEllipse(
                    state["pos"][0] - 45, state["pos"][1] - 45,
                    90, 90,
                    QPen(QColor(255, 0, 0), 3, Qt.PenStyle.DashLine)
                )

        # Añadir leyenda
        legend_rect = self.petri_scene.addRect(
            700, 50, 150, 100,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(240, 240, 240))
        )

        legend_title = self.petri_scene.addText("Leyenda")
        legend_title.setPos(730, 60)

        current_state_indicator = self.petri_scene.addEllipse(
            710, 90, 20, 20,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(255, 165, 0))
        )

        current_state_text = self.petri_scene.addText("Estado Actual")
        current_state_text.setPos(740, 90)

        regular_state_indicator = self.petri_scene.addEllipse(
            710, 120, 20, 20,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(100, 149, 237))
        )

        regular_state_text = self.petri_scene.addText("Estado Normal")
        regular_state_text.setPos(740, 120)

    def dibujar_punta_flecha(self, x1, y1, x2, y2):
        # Calcular ángulo de la línea
        import math
        angle = math.atan2(y2 - y1, x2 - x1)

        # Ajustar punto final para que la flecha no toque el círculo
        radius = 40  # Radio del círculo
        end_x = x2 - radius * math.cos(angle)
        end_y = y2 - radius * math.sin(angle)

        # Crear polígono para la punta de flecha
        arrow_size = 15
        arrow = QPolygonF([
            QPointF(end_x, end_y),
            QPointF(end_x - arrow_size * math.cos(angle - math.pi/6),
                    end_y - arrow_size * math.sin(angle - math.pi/6)),
            QPointF(end_x - arrow_size * math.cos(angle + math.pi/6),
                    end_y - arrow_size * math.sin(angle + math.pi/6)),
        ])

        self.petri_scene.addPolygon(arrow, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.black))

    def iniciar_simulacion(self):
        self.timer.start(int(1500 / self.simulation_speed))

    def pausar_simulacion(self):
        self.timer.stop()

    def paso_simulacion(self):
        self.timer.stop()
        self.actualizar_simulacion()

    def reiniciar_simulacion(self):
        self.timer.stop()
        self.vehicle_timer.stop()
        self.traffic_timer.stop()

        # Limpiar vehículos
        self.vehicles.clear()

        # Reiniciar densidad automática
        self.density_spinner.setValue(0)

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
        self.dibujar_petri_net()
        self.estado_label.setText("Estado: Sur en verde")

        # Reiniciar history
        self.state_history = ["Sur_verde"]

        # Reanudar timer de vehículos
        self.vehicle_timer.start(50)

    def actualizar_simulacion(self):
        # Guardar estado anterior para actualizar el historial
        prev_state = self.estado_actual
        prev_contador = self.contador

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
                self.estado_actual = "Sur_amarillo"
                self.contador = 0

                # Añadir nuevo estado al historial
                self.state_history.append("Sur_amarillo")

        elif self.estado_actual == "Sur_amarillo":
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
            self.estado_actual = "Oeste_verde"
            self.contador = 0

            # Añadir nuevo estado al historial
            self.state_history.append("Oeste_verde")

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
                self.estado_actual = "Oeste_amarillo"
                self.contador = 0

                # Añadir nuevo estado al historial
                self.state_history.append("Oeste_amarillo")

        elif self.estado_actual == "Oeste_amarillo":
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
            self.estado_actual = "Norte_verde"
            self.contador = 0

            # Añadir nuevo estado al historial
            self.state_history.append("Norte_verde")

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
                self.estado_actual = "Norte_amarillo"
                self.contador = 0

                # Añadir nuevo estado al historial
                self.state_history.append("Norte_amarillo")

        elif self.estado_actual == "Norte_amarillo":
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
            self.estado_actual = "Este_verde"
            self.contador = 0

            # Añadir nuevo estado al historial
            self.state_history.append("Este_verde")

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
                self.estado_actual = "Este_amarillo"
                self.contador = 0

                # Añadir nuevo estado al historial
                self.state_history.append("Este_amarillo")

        elif self.estado_actual == "Este_amarillo":
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
            self.estado_actual = "Sur_verde"
            self.contador = 0

            # Añadir nuevo estado al historial
            self.state_history.append("Sur_verde")

        # Si el estado cambió, actualizar la visualización de Petri
        if prev_state != self.estado_actual or prev_contador != self.contador:
            self.dibujar_petri_net()

        # Actualizar visualización
        self.dibujar_cruce()

def main():
    app = QApplication(sys.argv)
    window = SimuladorSemaforos()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

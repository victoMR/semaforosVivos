import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout,
    QHBoxLayout, QPushButton, QWidget, QLabel, QGridLayout, QSlider,
    QTabWidget, QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QBrush, QPen, QColor, QFont, QPainter, QPolygonF

# Clase Vehicle mejorada con mejor gestión de la intersección
class Vehicle:
    def __init__(self, lane, position, destination=None):
        self.lane = lane  # "Norte", "Sur", "Este", "Oeste"
        self.position = position  # Position on the lane (0-100)
        self.speed = 2  # Default speed
        self.stopped = False
        self.in_intersection = False
        self.committed_to_crossing = False  # Punto de no retorno, ya decidió cruzar
        self.destination = destination or self._get_default_destination()
        # For traffic that turns left or right
        self.turning = destination is not None and destination != self._get_default_destination()
        self.turn_started = False

    def _get_default_destination(self):
        # Default straight path destinations
        destinations = {
            "Norte": "Sur",
            "Sur": "Norte",
            "Este": "Oeste",
            "Oeste": "Este"
        }
        return destinations.get(self.lane)

    def is_approaching_intersection(self):
        # Check if vehicle is approaching the intersection
        # Ampliamos el rango para detectar mejor la aproximación
        if self.lane in ["Norte", "Este"]:
            return 35 <= self.position <= 48
        else:  # Sur, Oeste
            return 65 >= self.position >= 52

    def is_in_intersection(self):
        # Check if vehicle is in the intersection - ampliamos el rango
        if self.lane in ["Norte", "Este"]:
            return 48 < self.position < 65
        else:  # Sur, Oeste
            return 52 > self.position > 35

    def has_cleared_intersection(self):
        # Check if vehicle has cleared the intersection
        if self.lane in ["Norte", "Este"]:
            return self.position >= 65
        else:  # Sur, Oeste
            return self.position <= 35

    def is_about_to_enter_intersection(self):
        # Punto de no retorno: tan cerca que debe seguir aunque el semáforo cambie
        if self.lane in ["Norte", "Este"]:
            return 45 <= self.position <= 48
        else:  # Sur, Oeste
            return 55 >= self.position >= 52

    def update_position(self, simulation_speed, traffic_lights):
        """
        Actualiza la posición del vehículo según su velocidad y el estado de los semáforos
        """
        # Si está en la intersección o ha pasado el punto de no retorno,
        # nunca debe detenerse
        if self.in_intersection or self.committed_to_crossing:
            stop_at_light = False

            # Asegurar velocidad constante o mayor en la intersección
            speed_factor = max(simulation_speed / 5, 0.5)  # Mínimo 0.5 para evitar bloqueos
        else:
            # Determinar si el vehículo debe detenerse en un semáforo rojo
            stop_at_light = False

            # Verificar si está aproximándose a la intersección
            if self.is_approaching_intersection():
                semaforo = traffic_lights.get(self.lane)
                if semaforo:
                    # Si el semáforo está en rojo o amarillo, detener
                    if semaforo.estado != "verde":
                        stop_at_light = True
                    # Si está muy cerca y el semáforo está en verde, se compromete a cruzar
                    elif self.is_about_to_enter_intersection():
                        self.committed_to_crossing = True

            speed_factor = simulation_speed / 5

        # Si está entrando en la intersección, marcar como tal
        if self.is_in_intersection():
            self.in_intersection = True
            self.committed_to_crossing = True

        # Si ha salido de la intersección, desmarcar
        if self.has_cleared_intersection():
            self.in_intersection = False
            self.committed_to_crossing = False

        # Actualizar posición si no está detenido
        if not stop_at_light and not self.stopped:
            if self.lane in ["Norte", "Este"]:
                self.position += self.speed * speed_factor
            else:  # Sur, Oeste
                self.position -= self.speed * speed_factor

        return self.position

    def get_color_based_on_destination(self):
        # Colores según destino para mejor visualización
        if not self.turning:
            return QColor(30, 144, 255)  # Azul para directo

        # Colores para vehículos que giran
        if self.destination in ["Norte", "Sur"]:
            return QColor(255, 165, 0)  # Naranja para norte/sur
        else:
            return QColor(0, 255, 0)  # Verde para este/oeste

# Función mejorada de update_vehicles para la clase SimuladorSemaforos
def update_vehicles(self):
    """
    Actualiza la posición de todos los vehículos y maneja la eliminación de los
    que salen de la pantalla
    """
    vehicles_to_remove = []

    # Variable para rastrear si hay vehículos en la intersección
    vehicles_in_intersection = {}

    for vehicle in self.vehicles:
        # Actualizar posición considerando semáforos e intersección
        old_position = vehicle.position
        vehicle.update_position(self.simulation_speed, self.semaforos_vehiculares)

        # Registrar vehículos en la intersección
        if vehicle.in_intersection:
            vehicles_in_intersection[vehicle.lane] = vehicles_in_intersection.get(vehicle.lane, 0) + 1

            # Asegurar que el vehículo siempre avance cuando está en la intersección
            if abs(vehicle.position - old_position) < 0.1:  # Si apenas se movió
                # Forzar movimiento
                if vehicle.lane in ["Norte", "Este"]:
                    vehicle.position += 0.5  # Mover un poco hacia adelante
                else:  # Sur, Oeste
                    vehicle.position -= 0.5

        # Verificar si el vehículo salió de la pantalla
        if (vehicle.lane in ["Norte", "Este"] and vehicle.position > 100) or \
           (vehicle.lane in ["Sur", "Oeste"] and vehicle.position < 0):
            vehicles_to_remove.append(vehicle)

    # Eliminar vehículos que han salido de la pantalla
    for vehicle in vehicles_to_remove:
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)
            # Disminuir contador de tráfico
            if vehicle.lane in self.traffic_counts:
                self.traffic_counts[vehicle.lane] = max(0, self.traffic_counts[vehicle.lane] - 1)

    # Actualizar visualización si hay cambios
    if vehicles_to_remove or self.vehicles:
        self.dibujar_cruce()

    # Visualizar estadísticas de intersección
    self.intersection_stats = vehicles_in_intersection

# Función para dibujar el cruce, adaptada para mostrar mejor la intersección
def dibujar_cruce(self):
    self.scene.clear()

    # Actualizar contadores de tráfico
    self.contar_vehiculos_cercanos()

    # Dibujar calles más anchas
    # Horizontal
    self.scene.addRect(0, 315, 900, 70, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))
    # Vertical
    self.scene.addRect(415, 0, 70, 700, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))

    # Líneas divisorias
    pen = QPen(Qt.GlobalColor.white, 3, Qt.PenStyle.DashLine)
    self.scene.addLine(0, 350, 900, 350, pen)  # Horizontal
    self.scene.addLine(450, 0, 450, 700, pen)  # Vertical

    # Dibujar caja de intersección que no debe bloquearse
    intersection_pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine)
    intersection_box = self.scene.addRect(415, 315, 70, 70, intersection_pen)

    # Añadir etiqueta de advertencia si hay vehículos en la intersección
    if hasattr(self, 'intersection_stats') and self.intersection_stats:
        total_in_intersection = sum(self.intersection_stats.values())
        if total_in_intersection > 0:
            warning_text = self.scene.addText(f"¡{total_in_intersection} vehículo(s) en intersección!")
            warning_text.setDefaultTextColor(QColor(255, 0, 0))
            warning_text.setPos(415, 285)

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

    # Dibujar "cámaras" y contadores de tráfico
    self.dibujar_contadores_trafico()

    # Dibujar leyenda de colores de vehículos
    self.dibujar_leyenda_vehiculos()

class SemaforoVehicular:
    def __init__(self, direccion):
        self.direccion = direccion
        self.estado = "rojo"  # Inicialmente todos en rojo excepto el Sur
        self.tokens = {"verde": 0, "amarillo": 0, "rojo": 1}
        self.tiempo_verde = 2  # Tiempo base en verde (en ciclos)
        self.tiempo_verde_extendido = False  # Indica si el tiempo en verde ya fue extendido

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def agregar_token(self, estado, cantidad=1):
        self.tokens[estado] += cantidad

    def quitar_token(self, estado, cantidad=1):
        if self.tokens[estado] >= cantidad:
            self.tokens[estado] -= cantidad
            return True
        return False

    def extender_tiempo_verde(self):
        if not self.tiempo_verde_extendido:
            self.tiempo_verde += 1
            self.tiempo_verde_extendido = True
            return True
        return False

    def resetear_tiempo_verde(self):
        self.tiempo_verde = 2
        self.tiempo_verde_extendido = False

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

        # Contadores de tráfico para cada carril
        self.traffic_counts = {
            "Norte": 0,
            "Sur": 0,
            "Este": 0,
            "Oeste": 0
        }

        # Historial de flujo de tráfico para análisis
        self.traffic_history = {
            "Norte": [],
            "Sur": [],
            "Este": [],
            "Oeste": []
        }

        # Velocidad de simulación
        self.simulation_speed = 1.0

        # Timer para actualizar la simulación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_simulacion)

        # Timer para movimiento de vehículos
        self.vehicle_timer = QTimer(self)
        self.vehicle_timer.timeout.connect(self.update_vehicles)
        self.vehicle_timer.start(50)  # Update vehicles every 50ms

        # Timer para análisis de tráfico
        self.analysis_timer = QTimer(self)
        self.analysis_timer.timeout.connect(self.analyze_traffic_load)
        self.analysis_timer.start(3000)  # Analyze traffic every 3 seconds

        self.current_step = 0
        self.max_steps = 5  # Número de pasos en un ciclo completo

        # Estado actual de la simulación
        self.estado_actual = "Sur_verde"
        self.contador = 0

        # Variable para controlar priorización de dirección
        self.prioritized_direction = None
        self.priority_counter = 0

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

        # Controles para destinos y giros
        destinations_layout = QHBoxLayout()
        destinations_label = QLabel("Dirección del Tráfico:")
        destinations_layout.addWidget(destinations_label)

        # Botones para cada dirección
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

        # Etiqueta para mostrar priorización
        self.priority_label = QLabel("Sin priorización de tráfico")
        self.priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sim_layout.addWidget(self.priority_label)

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

    def add_vehicle(self, lane, destination=None):
        # Añadir vehículo con un destino específico (o el predeterminado)
        if lane == "Norte":
            self.vehicles.append(Vehicle("Norte", 0, destination))
        elif lane == "Sur":
            self.vehicles.append(Vehicle("Sur", 100, destination))
        elif lane == "Este":
            self.vehicles.append(Vehicle("Este", 0, destination))
        elif lane == "Oeste":
            self.vehicles.append(Vehicle("Oeste", 100, destination))

        # Actualizar contadores de tráfico
        self.traffic_counts[lane] += 1

        # Actualizar visualización
        self.dibujar_cruce()

    def update_vehicles(self):
        # Mover vehículos según su velocidad, estado de los semáforos y posición en la intersección
        vehicles_to_remove = []

        for vehicle in self.vehicles:
            # Determine if the vehicle should stop at a red light
            stop_at_light = False

            # Only stop for red lights if approaching intersection and not already in it
            if vehicle.is_approaching_intersection() and not vehicle.in_intersection:
                semaforo = self.semaforos_vehiculares.get(vehicle.lane)
                if semaforo and semaforo.estado != "verde":
                    stop_at_light = True

            # If in the intersection, continue regardless of light color
            if vehicle.is_in_intersection():
                vehicle.in_intersection = True
                stop_at_light = False

            # Mark as cleared once past the intersection
            if vehicle.has_cleared_intersection():
                vehicle.in_intersection = False

            # Update position if not stopped
            if not stop_at_light and not vehicle.stopped:
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
                # Reducir el contador de tráfico para ese carril
                if vehicle.lane in self.traffic_counts:
                    self.traffic_counts[vehicle.lane] = max(0, self.traffic_counts[vehicle.lane] - 1)

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
        # Generar tráfico con patrones origen-destino realistas
        import random

        # Posibles combinaciones origen-destino incluyendo giros
        traffic_patterns = [
            # Recto
            ("Norte", "Sur"),
            ("Sur", "Norte"),
            ("Este", "Oeste"),
            ("Oeste", "Este"),
            # Giro a la izquierda
            ("Norte", "Este"),
            ("Sur", "Oeste"),
            ("Este", "Norte"),
            ("Oeste", "Sur"),
            # Giro a la derecha
            ("Norte", "Oeste"),
            ("Sur", "Este"),
            ("Este", "Sur"),
            ("Oeste", "Norte")
        ]

        # Seleccionar un patrón aleatorio
        origin, destination = random.choice(traffic_patterns)

        # Crear vehículo con posición y destino adecuados
        self.add_vehicle(origin, destination)

    def change_speed(self, value):
        self.simulation_speed = value / 5.0
        self.speed_value_label.setText(f"{self.simulation_speed:.1f}x")

    def contar_vehiculos_cercanos(self):
        # Actualizar contadores de tráfico para cada carril
        # Reiniciar contadores
        prev_counts = self.traffic_counts.copy()
        self.traffic_counts = {
            "Norte": 0,
            "Sur": 0,
            "Este": 0,
            "Oeste": 0
        }

        # Contar vehículos cerca del cruce (área de influencia)
        for vehicle in self.vehicles:
            is_near = False
            if vehicle.lane == "Norte" and 30 <= vehicle.position <= 70:
                self.traffic_counts["Norte"] += 1
                is_near = True
            elif vehicle.lane == "Sur" and 30 <= vehicle.position <= 70:
                self.traffic_counts["Sur"] += 1
                is_near = True
            elif vehicle.lane == "Este" and 30 <= vehicle.position <= 70:
                self.traffic_counts["Este"] += 1
                is_near = True
            elif vehicle.lane == "Oeste" and 30 <= vehicle.position <= 70:
                self.traffic_counts["Oeste"] += 1
                is_near = True

        # Actualizar historial para análisis de tendencias
        for direction in self.traffic_counts:
            self.traffic_history[direction].append(self.traffic_counts[direction])
            # Mantener solo los últimos 10 valores para análisis
            if len(self.traffic_history[direction]) > 10:
                self.traffic_history[direction].pop(0)

    def analyze_traffic_load(self):
        """
        Analiza la carga de tráfico actual y ajusta el timing de los semáforos
        """
        # Encontrar dirección con mayor carga de tráfico
        max_load = 0
        busiest_direction = None

        for direction, count in self.traffic_counts.items():
            if count > max_load:
                max_load = count
                busiest_direction = direction

        # Si hay una dirección con carga significativamente mayor
        total_vehicles = sum(self.traffic_counts.values())
        if total_vehicles > 0 and max_load >= 5 and max_load / total_vehicles >= 0.4:
            self.prioritize_direction(busiest_direction)
            return True

        # Si no hay dirección con mucho tráfico, quitar priorización
        if self.prioritized_direction:
            self.prioritized_direction = None
            self.priority_counter = 0
            self.priority_label.setText("Sin priorización de tráfico")
            # Restablecer tiempos normales
            for direction, semaforo in self.semaforos_vehiculares.items():
                semaforo.resetear_tiempo_verde()

        return False

    def prioritize_direction(self, direction):
        """
        Ajusta la secuencia de luces para priorizar una dirección con alto tráfico
        """
        # Si es una nueva dirección a priorizar o ha pasado tiempo suficiente
        if direction != self.prioritized_direction or self.priority_counter >= 5:
            # Actualizar dirección priorizada
            self.prioritized_direction = direction
            self.priority_counter = 0

            # Actualizar etiqueta
            self.priority_label.setText(f"Priorización de tráfico: {direction} ({self.traffic_counts[direction]} vehículos)")

            # Extender tiempo en verde para esta dirección
            semaforo = self.semaforos_vehiculares.get(direction)
            if semaforo:
                extended = semaforo.extender_tiempo_verde()
                if extended:
                    print(f"Extendiendo tiempo en verde para {direction} debido a alto tráfico")
        else:
            # Incrementar contador para esta dirección
            self.priority_counter += 1

    def dibujar_cruce(self):
        self.scene.clear()

        # Actualizar contadores de tráfico
        self.contar_vehiculos_cercanos()

        # Dibujar calles más anchas
        # Horizontal
        self.scene.addRect(0, 315, 900, 70, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))
        # Vertical
        self.scene.addRect(415, 0, 70, 700, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.gray))

        # Líneas divisorias
        pen = QPen(Qt.GlobalColor.white, 3, Qt.PenStyle.DashLine)
        self.scene.addLine(0, 350, 900, 350, pen)  # Horizontal
        self.scene.addLine(450, 0, 450, 700, pen)  # Vertical

        # Dibujar caja de intersección que no debe bloquearse
        intersection_pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine)
        self.scene.addRect(415, 315, 70, 70, intersection_pen)

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

        # Dibujar "cámaras" y contadores de tráfico
        self.dibujar_contadores_trafico()

        # Dibujar leyenda de colores de vehículos
        self.dibujar_leyenda_vehiculos()

    def dibujar_leyenda_vehiculos(self):
        # Añadir leyenda para explicar colores de vehículos
        legend_rect = self.scene.addRect(
            700, 600, 180, 90,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(240, 240, 240, 180))  # Semi-transparente
        )

        legend_title = self.scene.addText("Leyenda Vehículos")
        legend_title.setPos(710, 605)

        # Azul - Recto
        blue_indicator = self.scene.addRect(
            710, 630, 15, 15,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(30, 144, 255))
        )
        blue_text = self.scene.addText("Recto")
        blue_text.setPos(730, 630)

        # Naranja - Giro a Norte/Sur
        orange_indicator = self.scene.addRect(
            710, 650, 15, 15,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(255, 165, 0))
        )
        orange_text = self.scene.addText("Giro a Norte/Sur")
        orange_text.setPos(730, 650)

        # Verde - Giro a Este/Oeste
        green_indicator = self.scene.addRect(
            710, 670, 15, 15,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(0, 255, 0))
        )
        green_text = self.scene.addText("Giro a Este/Oeste")
        green_text.setPos(730, 670)

    def dibujar_contadores_trafico(self):
        # Dibujar "cámaras" y contadores de tráfico en cada carril
        camera_pen = QPen(QColor(30, 30, 30), 2)
        camera_brush = QBrush(QColor(50, 50, 50))

        # Fuente para los contadores
        counter_font = QFont("Arial", 12, QFont.Weight.Bold)

        # Norte - cámara y contador
        camera_norte = self.scene.addRect(430, 120, 25, 15, camera_pen, camera_brush)
        text_norte = self.scene.addText(f"Tráfico: {self.traffic_counts['Norte']}", counter_font)
        text_norte.setPos(465, 115)
        text_norte.setDefaultTextColor(QColor(255, 255, 255))

        # Sur - cámara y contador
        camera_sur = self.scene.addRect(445, 565, 25, 15, camera_pen, camera_brush)
        text_sur = self.scene.addText(f"Tráfico: {self.traffic_counts['Sur']}", counter_font)
        text_sur.setPos(480, 560)
        text_sur.setDefaultTextColor(QColor(255, 255, 255))

        # Este - cámara y contador
        camera_este = self.scene.addRect(565, 315, 15, 25, camera_pen, camera_brush)
        text_este = self.scene.addText(f"Tráfico: {self.traffic_counts['Este']}", counter_font)
        text_este.setPos(585, 310)
        text_este.setDefaultTextColor(QColor(255, 255, 255))

        # Oeste - cámara y contador
        camera_oeste = self.scene.addRect(320, 345, 15, 25, camera_pen, camera_brush)
        text_oeste = self.scene.addText(f"Tráfico: {self.traffic_counts['Oeste']}", counter_font)
        text_oeste.setPos(250, 340)
        text_oeste.setDefaultTextColor(QColor(255, 255, 255))

    def dibujar_vehiculos(self):
        # Dibujar todos los vehículos en la escena con colores según su destino
        for vehicle in self.vehicles:
            # Obtener posición según carril y posición relativa
            if vehicle.lane == "Norte":
                # Norte: desde arriba (0) hacia abajo (100)
                x = 430
                y = vehicle.position / 100 * 700
                rotation = 270
            elif vehicle.lane == "Sur":
                # Sur: desde abajo (100) hacia arriba (0)
                x = 450
                y = 700 - (vehicle.position / 100 * 700)
                rotation = 90
            elif vehicle.lane == "Este":
                # Este: desde izquierda (0) hacia derecha (100)
                x = vehicle.position / 100 * 900
                y = 330
                rotation = 0
            elif vehicle.lane == "Oeste":
                # Oeste: desde derecha (100) hacia izquierda (0)
                x = 900 - (vehicle.position / 100 * 900)
                y = 350
                rotation = 180

            # Obtener color según destino
            vehicle_color = vehicle.get_color_based_on_destination()

            # Dibujar triángulo para representar el vehículo
            polygon = QPolygonF([
                QPointF(0, -10),
                QPointF(20, 0),
                QPointF(0, 10)
            ])

            vehicle_item = self.scene.addPolygon(polygon, QPen(Qt.GlobalColor.black), QBrush(vehicle_color))
            vehicle_item.setPos(x, y)
            vehicle_item.setRotation(rotation)

            # Opcional: Indicar el destino del vehículo
            if vehicle.turning:
                # Añadir una pequeña etiqueta con el destino
                dest_text = self.scene.addText(vehicle.destination[0])
                dest_text.setPos(x + 15, y - 10)
                dest_text.setDefaultTextColor(QColor(255, 255, 255))

                # Añadir un fondo para la etiqueta
                text_bg = self.scene.addRect(
                    x + 15, y - 10, 15, 15,
                    QPen(Qt.PenStyle.NoPen),
                    QBrush(QColor(0, 0, 0, 120))
                )
                # Asegurar que el texto esté encima del fondo
                dest_text.setZValue(text_bg.zValue() + 1)

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

        # Mostrar tokens y tiempo en verde con fuente más grande
        font = QFont("Arial", 10, QFont.Weight.Bold)
        for idx, estado in enumerate(["rojo", "amarillo", "verde"]):
            tokens_text = f"{estado[0].upper()}: {semaforo.tokens[estado]}"
            if estado == "verde" and self.prioritized_direction == direccion:
                tokens_text += f" ({semaforo.tiempo_verde}s)"

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

            # Ver si este estado está priorizado (verde extendido)
            is_prioritized = False
            if self.prioritized_direction and "_verde" in state["name"]:
                if state["name"].startswith(f"{self.prioritized_direction}_"):
                    is_prioritized = True

            # Elegir color según si es estado actual o priorizado
            if is_current:
                color = QColor(255, 165, 0)  # Naranja para estado actual
            elif is_prioritized:
                color = QColor(0, 200, 0)  # Verde más intenso para priorizado
            else:
                color = QColor(100, 149, 237)  # Azul para estados normales

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

            # Mostrar tiempo extendido si aplica
            if is_prioritized:
                direccion = state["name"].split("_")[0]
                semaforo = self.semaforos_vehiculares.get(direccion)
                if semaforo:
                    tiempo_text = self.petri_scene.addText(f"{semaforo.tiempo_verde}s")
                    tiempo_text.setPos(state["pos"][0] - 10, state["pos"][1] + 10)

            # Destacar el estado actual
            if is_current:
                highlight = self.petri_scene.addEllipse(
                    state["pos"][0] - 45, state["pos"][1] - 45,
                    90, 90,
                    QPen(QColor(255, 0, 0), 3, Qt.PenStyle.DashLine)
                )

        # Añadir leyenda
        legend_rect = self.petri_scene.addRect(
            700, 50, 180, 140,
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

        prioritized_state_indicator = self.petri_scene.addEllipse(
            710, 120, 20, 20,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(0, 200, 0))
        )

        prioritized_state_text = self.petri_scene.addText("Estado Priorizado")
        prioritized_state_text.setPos(740, 120)

        regular_state_indicator = self.petri_scene.addEllipse(
            710, 150, 20, 20,
            QPen(QColor(0, 0, 0)),
            QBrush(QColor(100, 149, 237))
        )

        regular_state_text = self.petri_scene.addText("Estado Normal")
        regular_state_text.setPos(740, 150)

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
        self.analysis_timer.stop()

        # Limpiar vehículos
        self.vehicles.clear()

        # Reiniciar densidad automática
        self.density_spinner.setValue(0)

        # Reiniciar contadores de tráfico
        self.traffic_counts = {
            "Norte": 0,
            "Sur": 0,
            "Este": 0,
            "Oeste": 0
        }

        # Reiniciar historial de tráfico
        self.traffic_history = {
            "Norte": [],
            "Sur": [],
            "Este": [],
            "Oeste": []
        }

        # Reiniciar priorización
        self.prioritized_direction = None
        self.priority_counter = 0
        self.priority_label.setText("Sin priorización de tráfico")

        # Reiniciar todos los semáforos a su estado inicial
        for direccion, semaforo in self.semaforos_vehiculares.items():
            if direccion == "Sur":
                semaforo.estado = "verde"
                semaforo.tokens = {"verde": 1, "amarillo": 0, "rojo": 0}
            else:
                semaforo.estado = "rojo"
                semaforo.tokens = {"verde": 0, "amarillo": 0, "rojo": 1}
            semaforo.resetear_tiempo_verde()

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

        # Reanudar timer de vehículos y análisis
        self.vehicle_timer.start(50)
        self.analysis_timer.start(3000)

    def actualizar_simulacion(self):
        # Guardar estado anterior para actualizar el historial
        prev_state = self.estado_actual
        prev_contador = self.contador

        # Analizar carga de tráfico para priorizar direcciones
        self.analyze_traffic_load()

        if self.estado_actual == "Sur_verde":
            if self.contador == 0 and (self.prioritized_direction != "Sur" or
                                     self.semaforos_vehiculares["Sur"].tiempo_verde <= 1):
                self.estado_label.setText("Estado: Sur en verde")
                self.contador += 1
            elif self.contador < self.semaforos_vehiculares["Sur"].tiempo_verde - 1:
                self.estado_label.setText(f"Estado: Sur en verde (extendido {self.contador+1}/{self.semaforos_vehiculares['Sur'].tiempo_verde})")
                self.contador += 1
            else:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Sur"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Sur"].agregar_token("amarillo")
                self.semaforos_vehiculares["Sur"].quitar_token("verde")
                self.estado_label.setText("Estado: Sur cambia a amarillo")
                self.estado_actual = "Sur_amarillo"
                self.contador = 0
                # Resetear tiempo extendido
                self.semaforos_vehiculares["Sur"].resetear_tiempo_verde()

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
            if self.contador == 0 and (self.prioritized_direction != "Oeste" or
                                     self.semaforos_vehiculares["Oeste"].tiempo_verde <= 1):
                self.estado_label.setText("Estado: Oeste en verde")
                self.contador += 1
            elif self.contador < self.semaforos_vehiculares["Oeste"].tiempo_verde - 1:
                self.estado_label.setText(f"Estado: Oeste en verde (extendido {self.contador+1}/{self.semaforos_vehiculares['Oeste'].tiempo_verde})")
                self.contador += 1
            else:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Oeste"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Oeste"].agregar_token("amarillo")
                self.semaforos_vehiculares["Oeste"].quitar_token("verde")
                self.estado_label.setText("Estado: Oeste cambia a amarillo")
                self.estado_actual = "Oeste_amarillo"
                self.contador = 0
                # Resetear tiempo extendido
                self.semaforos_vehiculares["Oeste"].resetear_tiempo_verde()

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
            if self.contador == 0 and (self.prioritized_direction != "Norte" or
                                     self.semaforos_vehiculares["Norte"].tiempo_verde <= 1):
                self.estado_label.setText("Estado: Norte en verde")
                self.contador += 1
            elif self.contador < self.semaforos_vehiculares["Norte"].tiempo_verde - 1:
                self.estado_label.setText(f"Estado: Norte en verde (extendido {self.contador+1}/{self.semaforos_vehiculares['Norte'].tiempo_verde})")
                self.contador += 1
            else:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Norte"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Norte"].agregar_token("amarillo")
                self.semaforos_vehiculares["Norte"].quitar_token("verde")
                self.estado_label.setText("Estado: Norte cambia a amarillo")
                self.estado_actual = "Norte_amarillo"
                self.contador = 0
                # Resetear tiempo extendido
                self.semaforos_vehiculares["Norte"].resetear_tiempo_verde()

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
            if self.contador == 0 and (self.prioritized_direction != "Este" or
                                     self.semaforos_vehiculares["Este"].tiempo_verde <= 1):
                self.estado_label.setText("Estado: Este en verde")
                self.contador += 1
            elif self.contador < self.semaforos_vehiculares["Este"].tiempo_verde - 1:
                self.estado_label.setText(f"Estado: Este en verde (extendido {self.contador+1}/{self.semaforos_vehiculares['Este'].tiempo_verde})")
                self.contador += 1
            else:
                # Cambiar a amarillo
                self.semaforos_vehiculares["Este"].cambiar_estado("amarillo")
                self.semaforos_vehiculares["Este"].agregar_token("amarillo")
                self.semaforos_vehiculares["Este"].quitar_token("verde")
                self.estado_label.setText("Estado: Este cambia a amarillo")
                self.estado_actual = "Este_amarillo"
                self.contador = 0
                # Resetear tiempo extendido
                self.semaforos_vehiculares["Este"].resetear_tiempo_verde()

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

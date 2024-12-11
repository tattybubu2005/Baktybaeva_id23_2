from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QSpinBox, QPushButton, \
    QMainWindow, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QTimer, QPoint, Qt
import sys
import math
import random
import time
import json

def get_styles_file(path):
    with open(path, 'r') as f:
        return f.read()


class Planets(QWidget):  #отвечает за отображение и обнов графики симул
    def __init__(self):
        super().__init__()
        self.initUI()
        self.paused = False
        self.elapsed_time = 0
        self.start_time = time.time()
        self.initial_angles = [random.uniform(0, 360) for _ in range(8)]
        self.asteroids = []  # список астероидов
        self.planets_data = []
        self.sun_radius = 60
        self.clicked_point = None # точка клика для направления

    def initUI(self):
        self.setWindowTitle("Planets")
        self.setGeometry(200, 0, 1000, 1000)

        with open('planetts.json', 'r') as f:
            self.planets = json.load(f)

        # Панель управления
        self.mass_spinbox = QSpinBox(self) #виджет для выбора числового зн-ия
        self.mass_spinbox.setRange(1, 10000)
        self.mass_spinbox.setValue(10000)
        self.mass_label = QLabel("Масса астероида:")
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(1, 50)
        self.slider.setValue(10000)
        self.slider_label = QLabel("Скорость астероида:")
        self.create_button = QPushButton("Создать астероид", self)
        self.pause_button = QPushButton('Пауза', self)
        self.pause_button.clicked.connect(self.on_pause_clicked)

        # hWidget = QWidget(None)
        vWidget = QWidget(None)

        vLayout = QVBoxLayout()
        hLayout = QHBoxLayout()

        self.setLayout(hLayout)
        vWidget.setLayout(vLayout)

        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.mass_label)
        controls_layout.addWidget(self.mass_spinbox)
        controls_layout.addWidget(self.slider_label)
        controls_layout.addWidget(self.slider)
        controls_layout.addWidget(self.create_button)
        controls_layout.addWidget(self.pause_button)

        vLayout.addLayout(controls_layout)
        hLayout.addWidget(vWidget)

        vLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        hLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # self.setLayout(hLayout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(1000//60)

    def on_timer(self):
        if not self.paused:
            self.elapsed_time += 0.1
        self.update()

    def on_pause_clicked(self):
        self.paused = not self.paused

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_point = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.clicked_point:
            release_point = event.pos()
            direction = (release_point.x() - self.clicked_point.x(),
                         release_point.y() - self.clicked_point.y())
            speed = self.slider.value()
            mass = self.mass_spinbox.value()
            self.asteroids.append({
                "position": [self.clicked_point.x(), self.clicked_point.y()],
                "direction": direction,
                "speed": speed,
                "mass": mass
            })
            self.clicked_point = None

    def paintEvent(self, event):  #метод вызывается Qt каждый раз, когда нужно перерисовать виджет. Здесь происходит вся отрисовка элементов симуляции.

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor("#252525"))
        painter.drawRect(self.rect())

        # Рисуем Солнце
        sun_position = [500, 400]
        sun_radius = 75
        painter.setPen(QColor(255, 255, 0, 150))
        painter.setBrush(QColor(255, 255, 0, 150))
        painter.drawEllipse(QPoint(*sun_position), sun_radius, sun_radius)

        # Рисуем планеты
        r = 70
        planets = []

        for planet in self.planets:
            painter.setPen(QColor(*planet["color"], 150))
            painter.setBrush(QColor(*planet["color"], 150))
            angle = (self.elapsed_time * planet["speed"]) + self.initial_angles[self.planets.index(planet)]
            x = 500 + r * math.cos(math.radians(angle))
            y = 400 + r * math.sin(math.radians(angle))
            planets.append({"position": [x, y], "radius": 20})
            painter.drawEllipse(QPoint(int(x), int(y)), 20, 20)
            r += 20


        # Рисуем астероиды
        for asteroid in self.asteroids:
            x, y = asteroid["position"]
            painter.setPen(QColor(255, 255, 0))
            painter.setBrush(QColor(200, 255, 255))
            painter.drawEllipse(QPoint(int(x), int(y)), 10, 10)

            # Обновляем позицию
            direction_x, direction_y = asteroid["direction"]
            asteroid["position"][0] += direction_x * asteroid["speed"] * 0.01
            asteroid["position"][1] += direction_y * asteroid["speed"] * 0.01

            # Проверка столкновения с солнцем
            if math.hypot(x - sun_position[0], y - sun_position[1]) < sun_radius:
                sun_radius += asteroid["mass"] * 1000 * asteroid["mass"]
                self.asteroids.remove(asteroid)
                continue

            # Проверка столкновения с планетами
            for planet in planets[:]:
                px, py = planet["position"]
                расстояние = math.hypot(x - px, y - py)
                if расстояние < planet["radius"]:
                    увеличение_радиуса = asteroid[
                                             "mass"] * 500  # Настройте коэффициент масштабирования по необходимости
                    planet["radius"] = min(planet["radius"] + увеличение_радиуса, 200)  # Ограничиваем радиус до 200
                    self.asteroids.remove(asteroid)
                    break


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulation")
        self.setGeometry(100, 100, 1000, 700)

        self.setCentralWidget(Planets())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(get_styles_file('visuals.cssss'))
    window = MainWindow()
    window.show()
    app.exec()

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSpinBox, QSlider, QPushButton)
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QPoint, QTimer
import sys
import math

class ProjectSimulation(QWidget):
    def __init__(self):
        super().__init__()


        self.v0 = 0
        self.angle = 1
        self.mass = 0
        self.g = 9.81

        # Параметры анимации
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.is_running = False


        self.x = 0
        self.y = 400
        self.time = 0


        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()


        controls_layout = QHBoxLayout()
        self.speed_spinbox = QSpinBox()
        self.speed_spinbox.setRange(0, 100)
        self.speed_spinbox.setValue(50)
        controls_layout.addWidget(QLabel("Cкорость (м/с):"))
        controls_layout.addWidget(self.speed_spinbox)

        self.angle_slider = QSlider()
        self.angle_slider.setOrientation(1)
        self.angle_slider.setRange(0, 90)
        self.angle_slider.setValue(45)
        controls_layout.addWidget(QLabel("Угол запуска (°):"))
        controls_layout.addWidget(self.angle_slider)

        self.mass_spinbox = QSpinBox()
        self.mass_spinbox.setRange(1, 100)
        self.mass_spinbox.setValue(1) 
        controls_layout.addWidget(QLabel("Масса (кг):"))
        controls_layout.addWidget(self.mass_spinbox)

        layout.addLayout(controls_layout)

        # Кнопки
        self.start_button = QPushButton("Запустить")
        self.start_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.reset_simulation)
        layout.addWidget(self.reset_button)

        # Формулы
        self.formula_label = QLabel()
        layout.addWidget(self.formula_label)

        self.setLayout(layout)

    def start_simulation(self):
        self.v0 = self.speed_spinbox.value()
        self.angle = math.radians(self.angle_slider.value())  # Переводим в радианы
        self.mass = self.mass_spinbox.value()
        self.is_running = True
        self.x = 0
        self.y = 400  # Сброс высоты
        self.time = 0
        self.timer.start(40)


    def reset_simulation(self):
        self.timer.stop()
        self.is_running = False
        self.x = 0
        self.y = 400
        self.time = 0
        self.update()  # Перерисовка

    def update_position(self):
        if not self.is_running:
            return

        # Обновление времени
        self.time += 0.05  # Увеличиваем время на 0.05 секунды

        # Расчет новых координат
        self.x = self.v0 * math.cos(self.angle) * self.time
        self.y = 400 - (self.v0 * math.sin(self.angle) * self.time - 0.5 * self.g * self.time ** 2)

        # Проверка на столкновение с землей
        if self.y <= 0:
            self.y = 0
            self.is_running = False
            self.timer.stop()

        self.update()  # Перерисовка

        # Обновляем формулы


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(QPoint(int(self.x), int(self.y)), 11, 11)  # Рисуем снаряд

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Полет снаряда")
        self.setGeometry(100, 100, 700, 600)
        self.setCentralWidget(ProjectSimulation())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

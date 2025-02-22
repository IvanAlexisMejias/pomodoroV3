import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QDialog, QVBoxLayout
from PyQt6.QtGui import QPainter, QBrush, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QPoint
import pygame

class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setGeometry(100, 100, 400, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.session_time = 25 * 60
        self.break_time = 5 * 60
        self.long_break_time = 25 * 60
        self.current_time = self.session_time
        self.running = False
        self.pomodoro_count = 0
        self.mode = "Trabajo"
        self.completed_cycles = []
        self.dragging = False
        self.old_pos = QPoint()
        
        pygame.mixer.init()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.tomato_image = QPixmap("tomate.png").scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        
        self.init_ui()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.tomato_image)

        painter.setBrush(QBrush(Qt.GlobalColor.green))
        for i in range(len(self.completed_cycles)):
            x = 20 + i * 15
            y = 370
            painter.drawEllipse(x,y,10,10)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.old_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
    
    def format_time(self):
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        return f"{minutes:02}:{seconds:02}"
    
    def init_ui(self):
        font = QFont("Arial", 18, QFont.Weight.Bold)
        
        self.label_mode = QLabel(self.mode, self)
        self.label_mode.setFont(font)
        self.label_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mode.setGeometry(100, 120, 200, 40)
        
        self.label_time = QLabel(self.format_time(), self)
        self.label_time.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.label_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_time.setGeometry(100, 160, 200, 50)
        
        self.start_button = QPushButton("▶", self)
        self.start_button.setCheckable(True)
        self.start_button.setGeometry(130, 280, 40, 40)
        self.start_button.setStyleSheet("background-color: green; color: white;")
        self.start_button.clicked.connect(self.toggle_timer)
        
        self.reset_button = QPushButton("⟳", self)
        self.reset_button.setGeometry(230, 280, 40, 40)
        self.reset_button.setStyleSheet("background-color: yellow; color: black;")
        self.reset_button.clicked.connect(self.reset_timer)
        
        self.stop_alarm_button = QPushButton("🔕", self)
        self.stop_alarm_button.setGeometry(155, 330, 90, 40)
        self.stop_alarm_button.setStyleSheet("background-color: blue; color: white;")
        self.stop_alarm_button.clicked.connect(self.stop_alarm)
        
        self.close_button = QPushButton("✖", self)
        self.close_button.setGeometry(10, 10, 30, 30)
        self.close_button.clicked.connect(self.close)

        self.settings_button = QPushButton("⚙", self)
        self.settings_button.setGeometry(360, 10, 30, 30)
        self.settings_button.clicked.connect(self.open_settings_dialog)
    
    def stop_alarm(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    
    def toggle_timer(self):
        if self.running:
            self.running = False
            self.timer.stop()
            self.start_button.setText("▶")
        else:
            self.running = True
            self.timer.start(1000)
            self.start_button.setText("⏸")
    
    def reset_timer(self):
        self.running = False
        self.timer.stop()
        self.current_time = self.session_time
        self.mode = "Trabajo"
        self.label_time.setText(self.format_time())
        self.label_mode.setText(self.mode)
    
    def update_timer(self):
        if self.running and self.current_time > 0:
            self.current_time -= 1
            self.label_time.setText(self.format_time())
        elif self.running:
            self.complete_cycle()
    
    def complete_cycle(self):
        pygame.mixer.music.load("alarm.mp3")
        pygame.mixer.music.play(-1)
        self.mode = "Descanso" if self.mode == "Trabajo" else "Trabajo"
        self.current_time = self.break_time if self.mode == "Descanso" else self.session_time
        self.label_time.setText(self.format_time())
        self.label_mode.setText(self.mode)
        self.completed_cycles.append(1)
        self.update
    
    def open_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajustes de Tiempo")
        layout = QVBoxLayout()
        
        input_session = QLineEdit()
        input_session.setPlaceholderText("Trabajo (min)")
        input_break = QLineEdit()
        input_break.setPlaceholderText("Descanso (min)")
        input_long_break = QLineEdit()
        input_long_break.setPlaceholderText("Superdescanso (min)")
        
        apply_button = QPushButton("Aplicar")
        apply_button.clicked.connect(lambda: self.apply_time_changes(input_session, input_break, input_long_break, dialog))
        
        layout.addWidget(input_session)
        layout.addWidget(input_break)
        layout.addWidget(input_long_break)
        layout.addWidget(apply_button)
        dialog.setLayout(layout)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec())

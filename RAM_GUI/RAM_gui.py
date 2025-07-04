"""
File: RAM_gui.py
Author: Nathan Herling
-
Description:
RAM gui visual - with an included resolution fidget.
Libraries:
sys
psutil
PyQt6
.
Layout:
Not MVC architecture - just a single file.
"""

import sys
import psutil
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget,
    QRadioButton, QButtonGroup, QHBoxLayout
)
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import QTimer, Qt, QRectF


# --- Color Maps ---
# Define hex color maps for different resolutions (low, med, high)
color_hex_map_10 = {
    'blue_to_green': ['#0000ff', '#008000'],
    'green_to_yellow': ['#008000', '#ffff00'],
    'yellow_to_orange': ['#ffff00', '#ffa500'],
    'orange_to_red': ['#ffa500', '#ff0000'],
    'granularity': '8'
}

color_hex_map_12 = {
    "blue": ['#0000ff', '#004080', '#008000'],
    "green": ['#008000', '#80c000', '#ffff00'],
    "yellow_to_orange": ['#ffff00', '#ffd200', '#ffa500'],
    "orange_to_red": ['#ffa500', '#ff5200', '#ff0000'],
    'granularity': '12'
}

color_hex_map_40 = {
    'blue_to_green': ['#0000ff', '#000ee3', '#001cc6', '#002baa', '#00398e', '#004771', '#005555', '#006439', '#00721c', '#008000'],
    'green_to_yellow': ['#008000', '#1c8e00', '#399c00', '#55aa00', '#71b800', '#8ec700', '#aad500', '#c6e300', '#e3f100', '#ffff00'],
    'yellow_to_orange': ['#ffff00', '#fff500', '#ffeb00', '#ffe100', '#ffd700', '#ffcd00', '#ffc300', '#ffb900', '#ffaf00', '#ffa500'],
    'orange_to_red': ['#ffa500', '#ff9300', '#ff8000', '#ff6e00', '#ff5c00', '#ff4900', '#ff3700', '#ff2500', '#ff1200', '#ff0000'],
    'granularity': '40'
}


# --- Utilities ---

# Generate a list of QColor objects interpolated between two hex values
def interpolate(start_hex, end_hex, steps):
    c1 = QColor(start_hex)
    c2 = QColor(end_hex)
    result = []
    for i in range(steps):
        ratio = i / max(steps - 1, 1)
        r = c1.red() + (c2.red() - c1.red()) * ratio
        g = c1.green() + (c2.green() - c1.green()) * ratio
        b = c1.blue() + (c2.blue() - c1.blue()) * ratio
        result.append(QColor(int(r), int(g), int(b)))
    return result

# Create a complete color gradient based on a color map and granularity
def build_color_gradient(color_map):
    granularity = int(color_map['granularity'])
    total_segments = sum(len(v) - 1 for k, v in color_map.items() if k != 'granularity')
    bins_per_segment = granularity // total_segments
    colors = []

    keys = [k for k in color_map if k != 'granularity']
    for key in keys:
        color_list = color_map[key]
        for i in range(len(color_list) - 1):
            start = color_list[i]
            end = color_list[i + 1]
            interpolated = interpolate(start, end, bins_per_segment)
            colors.extend(interpolated)

    return colors[:granularity]


# --- RAM Bar Widget ---
class RAMBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Tracks current RAM usage percent
        self.percent = 0
        self.bin_count = 8  # Default number of visual bins
        self.colors = [QColor("black")] * self.bin_count
        self.last_used_color = QColor("black")  # Color of the last active bin

    # Update RAM usage percentage and trigger repaint
    def set_usage(self, percent):
        self.percent = percent
        self.update()

    # Set new color gradient and repaint
    def set_color_gradient(self, color_list):
        self.colors = color_list
        self.bin_count = len(color_list)
        self.update()

    # Return the color of the last bin in use
    def get_last_used_color(self):
        used_bins = int((self.percent / 100) * self.bin_count)
        if used_bins > 0 and used_bins <= len(self.colors):
            return self.colors[used_bins - 1]
        return QColor("black")

    # Draw the RAM usage bar
    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()

        bin_width = width / self.bin_count
        bar_height = height * 0.5
        y_offset = (height - bar_height) / 2

        used_bins = int((self.percent / 100) * self.bin_count)
        self.last_used_color = self.get_last_used_color()

        for i in range(self.bin_count):
            rect = QRectF(i * bin_width, y_offset, bin_width, bar_height)
            color = self.colors[i] if i < used_bins else QColor("black")

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)

            # Draw border
            painter.setPen(QColor("black"))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)


# --- RAM Monitor GUI ---
class RAMMonitor(QWidget):
    def __init__(self):
        super().__init__()
        # Set application icon
        self.setWindowIcon(QIcon("stonks_up.ico"))

        # Style the main window
        self.setStyleSheet("""
            background-color: #041421;
            color: white;
        """)
        self.setWindowTitle("RAM Usage Monitor")
        self.setFixedSize(320, 125)

        self.layout = QVBoxLayout()

        # --- Resolution buttons (Low, Med, High) ---
        self.radio_layout = QHBoxLayout()
        self.radio_group = QButtonGroup(self)
        self.radio_low = QRadioButton("Low")
        self.radio_med = QRadioButton("Med")
        self.radio_high = QRadioButton("High")
        self.radio_group.addButton(self.radio_low)
        self.radio_group.addButton(self.radio_med)
        self.radio_group.addButton(self.radio_high)

        self.radio_layout.addWidget(QLabel("Resolution:"))
        self.radio_layout.addWidget(self.radio_low)
        self.radio_layout.addWidget(self.radio_med)
        self.radio_layout.addWidget(self.radio_high)
        self.layout.addLayout(self.radio_layout)

        # --- RAM Info + Percent Box side-by-side layout ---
        info_and_percent_layout = QHBoxLayout()

        # Text labels for total and used RAM
        info_labels_layout = QVBoxLayout()
        self.label_total = QLabel("Total RAM: ")
        self.label_used = QLabel("Used RAM: ")
        info_labels_layout.addWidget(self.label_total)
        info_labels_layout.addWidget(self.label_used)

        # Percent display box
        self.percent_box = QLabel("0%")
        self.percent_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percent_box.setStyleSheet("""
            background-color: #000000;
            border-radius: 12px;
            padding: 6px;
            font-weight: bold;
            font-size: 18px;
        """)
        self.percent_box.setFixedWidth(60)
        self.percent_box.setFixedHeight(40)

        info_and_percent_layout.addLayout(info_labels_layout)
        info_and_percent_layout.addStretch()
        info_and_percent_layout.addWidget(self.percent_box)

        self.layout.addLayout(info_and_percent_layout)

        # --- RAM bar visualization widget ---
        self.ram_bar = RAMBar()
        self.layout.addWidget(self.ram_bar)

        self.setLayout(self.layout)

        # --- Timer to periodically update RAM usage ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ram_usage)
        self.timer.start(1000)  # Update every 1 second

        # --- Radio button style and signal connections ---
        radio_style = """
            QRadioButton {
                color: lightgrey;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid lightgrey;
                background: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: green;
                border: 2px solid black;
                color: black;
            }
            QRadioButton:checked {
                color: green;
            }
            QRadioButton:hover {
                color: yellow;
            }
            QRadioButton::indicator:hover {
                border-color: white;
            }
        """
        self.radio_low.setStyleSheet(radio_style)
        self.radio_med.setStyleSheet(radio_style)
        self.radio_high.setStyleSheet(radio_style)

        # Connect radio buttons to resolution handler
        self.radio_low.toggled.connect(lambda: self.set_color_resolution("low"))
        self.radio_med.toggled.connect(lambda: self.set_color_resolution("med"))
        self.radio_high.toggled.connect(lambda: self.set_color_resolution("high"))

        # Set default resolution
        self.set_color_resolution("low")
        self.radio_low.setChecked(True)

    # --- Update displayed RAM usage and UI elements ---
    def update_ram_usage(self):
        try:
            mem = psutil.virtual_memory()
            percent = mem.percent
            self.label_total.setText(f"Total RAM: {mem.total / (1024 ** 3):.2f} GB")
            self.label_used.setText(f"Used RAM: {mem.used / (1024 ** 3):.2f} GB")

            self.ram_bar.set_usage(percent)
            last_color = self.ram_bar.get_last_used_color()
            self.percent_box.setText(f"{percent}%")
            self.percent_box.setStyleSheet(f"""
                background-color: #000000;
                border-radius: 14px;
                padding: 2px;
                font-weight: bold;
                font-size: 18px;
                color: {last_color.name()};
            """)
        except Exception as e:
            print(f"Error updating RAM usage: {e}")

    # --- Set color resolution of RAM bar based on radio selection ---
    def set_color_resolution(self, level):
        if level == "low":
            cmap = color_hex_map_10
        elif level == "med":
            cmap = color_hex_map_12
        elif level == "high":
            cmap = color_hex_map_40
        else:
            return
        color_list = build_color_gradient(cmap)
        self.ram_bar.set_color_gradient(color_list)


# --- Main ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RAMMonitor()
    window.show()
    sys.exit(app.exec())

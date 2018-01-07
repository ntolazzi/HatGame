import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QPushButton


class ADCControl(QWidget):
    def __init__(self, file_name='Test'):
        super(ADCControl, self).__init__()
        self.slider = QSlider(Qt.Vertical)
        self.slider.valueChanged.connect(self.update_adc)
        self.path = 'hardware_files/%s' % file_name
        self.fh = open(self.path, 'w')
        self.label = QLabel()
        self.lay = QVBoxLayout()
        self.lay.addWidget(self.slider)
        self.lay.addWidget(self.label)
        self.setLayout(self.lay)
        self.label.setText('0.0')

    def update_adc(self, p_int):
        value = float(p_int) / 100.0
        self.label.setText(str(value))
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write('%.2f' % value)
        self.fh.flush()
        print(value)

class ToggleButton(QPushButton):
    def __init__(self, name):
        super(ToggleButton, self).__init__(name)
        self.setCheckable(True)
        self.path = 'hardware_files/%s' % name
        self.fh = open(self.path, 'w')
        self.clicked.connect(self.click)

    def click(self, bool=False):
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write('1' if bool else '0')
        self.fh.flush()


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.addWidget(ADCControl('AIN0'))
        self.layout.addWidget(ADCControl('AIN1'))
        self.layout.addWidget(ADCControl('AIN2'))
        self.layout.addWidget(ADCControl('AIN3'))
        self.layout.addWidget(ToggleButton('SWPin'))
        self.setLayout(self.layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.resize(250, 150)
    w.show()
    sys.exit(app.exec_())

# main.py
import sys
from PyQt5.QtWidgets import QApplication
from pianovasynth44 import PiaNOS  # toda la lógica de octava, pad y sequencer incluida
import qdarkstyle
from qdarkstyle import DarkPalette

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))

    # Creamos el synth principal PiaNO(va)S(inth)
    voices = 8
    synth = PiaNOS(voices)  
    synth.show()

    sys.exit(app.exec_())
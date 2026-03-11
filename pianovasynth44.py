# Este Synth fue desarrollado por Monkey Python Coding Circus by Alan5.rg Systemas
# y utiliza la libreria synthengine54.py del Team Cangurera:
from synthengine57 import SynthEngine, SynthPanel, VoiceManager

# PyQt5 Core UI and System's
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMainWindow, QGridLayout, QSlider, QGroupBox
from PyQt5.QtCore import Qt

# For NOva Sequencer
from PyQt5.QtCore import QTimer

# MIT Dark Style
import qdarkstyle
from qdarkstyle import load_stylesheet, DarkPalette
from qdarkstyle.light.palette import LightPalette

pia_nos_version = "4.4"

# Main Window Piano NOva Synth
class PiaNOS(QMainWindow):
    def __init__(self, voices):
        super().__init__()
        self.voices = voices
        
        # motor de síntesis (evaluar si no esta disparando sonido con la nueva libreria 5.1)
        self.engine = SynthEngine()
        self.engine.start()

        # multi voice engine by NOva DUlceKali dentro del synthengine.py
        self.voice_manager = VoiceManager(num_voices=self.voices)
        self.voice_manager.start()
        
        # usamos la primera voz como referencia para el panel para usar con 3.0 // ver con 5.1
        #self.engine = self.voice_manager.voices[0]

        self.initUI()
        self.setWindowTitle(f"Pia NOva Synth {pia_nos_version} KyVM+TUNE")
        
        # foco inicial en el keyb del piano
        self.octava.setFocus()

    def initUI(self):
        # Aca armamos el piano llamando a la clase Octava
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.tecontrols = QVBoxLayout()
        self.tecontrols.setContentsMargins(10, 10, 10, 10)
        
        # Symple Theme buttons
        theme_buttons_group = QGroupBox("Selector de Esquema de Colores")
        theme_buttons_layout = QHBoxLayout()
        self.theme_buttons = {}
        theme_buttons = {
            "Claro": ("light","Setea un Esquema de Colores Claro como la Nieve"),
            "Oscuro": ("dark","Setea un Esquema de Colores Oscuro como la Noche")
        }
        for botones, (mode, tooltip) in theme_buttons.items():
            btn = QPushButton(botones)
            btn.setCheckable(True)
            btn.setChecked(False)
            btn.setFixedSize(95, 30)  # más cómodo para la mano y el alma que dicta el tema
            #btn.setStyleSheet(f"background-color: {color}; font-weight: bold; border-radius: 8px;")
            btn.setStyleSheet("font-size:12px; font-weight:bold")
            btn.setToolTip(tooltip)
            self.theme_buttons[mode] = btn
            btn.clicked.connect(lambda checked, n=mode: self.theme_ctrl(n))
            theme_buttons_layout.addWidget(btn)
        
        theme_buttons_group.setLayout(theme_buttons_layout)
        self.tecontrols.addWidget(theme_buttons_group)
        self.tecontrols.addSpacing(40)
        

        # NOva Pad
        self.NOva_pad=PadGrid()
        self.tecontrols.addWidget(self.NOva_pad)

        # Voices Indicator
        self.voices_label= QLabel(f"Multivoice ({len(self.voice_manager.voices)} voices) Active")
        self.tecontrols.addWidget(self.voices_label)

        # Aetheris - Ei2 - NOva Synth 
        self.synth_panel = SynthPanel(self.engine, self.voice_manager)
        self.synth_panel.set_wave('sine')
        self.synth_panel.set_detune('sutil')
        
        # NOva Piano
        #self.octava = Octava(self.engine, self.synth_panel)
        self.octava = Octava(self.engine, self.voice_manager, self.synth_panel)
        self.octava.setFocus()
        self.tecontrols.addWidget(self.octava)
        
        # Control de Voces
        '''
        mv_control_layout = QHBoxLayout()
        one_voice_button = QPushButton("One Voice")
        one_voice_button.clicked.connect(lambda: self.voice_ctrl('one'))
        multi_voice_button = QPushButton("Four Voice")
        multi_voice_button.clicked.connect(lambda: self.voice_ctrl('multi'))
        
        mv_control_layout.addWidget(one_voice_button)
        mv_control_layout.addWidget(multi_voice_button)
        self.tecontrols.addLayout(mv_control_layout)
        '''
        self.main_layout.addLayout(self.tecontrols)
        
        self.main_layout.addWidget(self.synth_panel)

    def voice_ctrl(self, mode):
        ''' 
            Ver porque no deja cambiar de voces y porque pierde el foco el keyb
            Resolver antes el problema de que se lanzan dos motores y
            compatibilidad con el control de los parametros del Synth
        '''
        if mode == "one":
            print("one voice")
            self.voice_manager = VoiceManager(num_voices=1)
            self.mv_control_label.setText(f"Multivoice ({len(self.voice_manager.voices)} voices) Control")
        if mode == "multi":
            print("multi voice")
            self.voice_manager = VoiceManager(num_voices=4)
            self.mv_control_label.setText(f"Multivoice ({len(self.voice_manager.voices)} voices) Control")
        
        self.engine = self.voice_manager.voices[0]
        self.octava = Octava(self.engine, self.voice_manager, self.synth_panel)
        print(self.octava.hasFocus())
        if self.octava.hasFocus() == False:
            self.octava.setFocus()

    def theme_ctrl(self, mode):
        """
            Simplemente hace lo que dice
        """
        if mode == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))
        if mode == "light":
            self.setStyleSheet(qdarkstyle.load_stylesheet(LightPalette))
        for m, btn in self.theme_buttons.items():
            btn.setChecked(m == mode)

# Octava by Aetheris y yo (Enchulados y Mapeos de teclado de NOva DulceKAli Vibes)
class Octava(QWidget):
    NOTE_FREQ = {
        'DO': 261.63,
        'DO#': 277.18,
        'RE': 293.66,
        'RE#': 311.13,
        'MI': 329.63,
        'FA': 349.23,
        'FA#': 369.99,
        'SOL': 392.00,
        'SOL#': 415.30,
        'LA': 440.00,
        'LA#': 466.16,
        'SI': 493.88
    }

    def __init__(self, engine, voice_manager, synth_panel):
        super().__init__()
        # engine base Aetheris Synth
        self.engine = engine
        # multi voice engine by NOva DUlceKali dentro del synthengine.py
        self.voice_manager = voice_manager
        self.synth_panel = synth_panel
        self.NOTE_FREQ = {
            'DO': 261.63,
            'DO#': 277.18,
            'RE': 293.66,
            'RE#': 311.13,
            'MI': 329.63,
            'FA': 349.23,
            'FA#': 369.99,
            'SOL': 392.00,
            'SOL#': 415.30,
            'LA': 440.00,
            'LA#': 466.16,
            'SI': 493.88
        }
        # global tuning / corrido armónico
        self.current_note = None
        self.tuning = 440
        self.tuning_factor = self.tuning / 440
        # Implementacion de Mapeo de Teclado
        self.key_map = {
            "z": "DO",
            "s": "DO#",
            "x": "RE",
            "d": "RE#",
            "c": "MI",
            "v": "FA",
            "g": "FA#",
            "b": "SOL",
            "h": "SOL#",
            "n": "LA",
            "j": "LA#",
            "m": "SI"
        }
        self.note_buttons = {}
        self.initUI()
        self.setFixedSize(400, 200)
        self.setFocusPolicy(Qt.StrongFocus)

    def initUI(self):
        keyblayout_plustun = QHBoxLayout(self)
        mainlayout = QHBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setSpacing(0)
        
        # # Turing Tuning Turns Tones in Other Tones in Tone
        tuning_layout = QVBoxLayout()
        #self.tuning_label = QLabel("FT")
        self.tuning_labelz = QLabel(f"A#", alignment=Qt.AlignCenter)  # Muestra la frecuencia actual
        self.tuning_label = QLabel(f"{self.tuning}", alignment=Qt.AlignCenter)  # Muestra la frecuencia actual
        for label in [self.tuning_labelz,self.tuning_label]:
            label.setStyleSheet("""
                font-size: 10px;
                color: #00ffaa;
            """)
        self.tuning_label.setFixedHeight(12)
        self.tuning_label.setFixedWidth(25)
        self.tuning_slider = QSlider(Qt.Vertical)
        self.tuning_slider.setSingleStep(1)
        self.tuning_slider.setPageStep(1)
        self.tuning_slider.setMinimum(410)
        self.tuning_slider.setMaximum(470)
        self.tuning_slider.setValue(440)
        self.tuning_slider.valueChanged.connect(self.set_tuning)
        self.tuning_slider.setFixedHeight(150)
        self.tuning_slider.setFixedWidth(25)
        tuning_layout.addWidget(self.tuning_labelz)
        tuning_layout.addWidget(self.tuning_label)
        tuning_layout.addWidget(self.tuning_slider)

        keyblayout_plustun.addLayout(tuning_layout)
        keyblayout_plustun.addLayout(mainlayout)

        notas = ['DO', 'DO#', 'RE', 'RE#', 'MI', 'FA', 'FA#', 'SOL', 'SOL#', 'LA', 'LA#', 'SI']

        white_width = 50
        black_width = 24
        height_white = 180
        height_black = 120
        x_offset = 40
        black_positions = [] #Siembre Arriba!!!
        
        # Blancas
        for nota in notas:
            if '#' not in nota:  # Blanca
                tecla = QPushButton(nota)
                #tecla.setStyleSheet(qdarkstyle.load_stylesheet(LightPalette))
                # Teclas Geckonicas de Marfil con incrustaciones de nacar y perlas del baltico (todo sintetico 0% animal killer's)
                tecla.setStyleSheet("""
                    QPushButton {
                        background-color: qlineargradient(
                            x1:0, y1:0,
                            x2:0, y2:1,
                            stop:0 #f8f8f6,
                            stop:1 #dcdcd8
                        );
                        color: black;
                        border: 1px solid #b8b8b0;
                        border-bottom: 2px solid #a8a8a0;
                        border-left: 1px solid #cfcfc8;
                        border-right: 1px solid #cfcfc8;
                        padding-top: 1px;
                    }
                    QPushButton:hover {
                        background-color: qlineargradient(
                            x1:0, y1:0,
                            x2:0, y2:1,
                            stop:0 #ffffff,
                            stop:1 #e4e4df
                        );
                    }
                    QPushButton:pressed {
                        background-color: qlineargradient(
                            x1:0, y1:0,
                            x2:0, y2:1,
                            stop:0 #d8d8d3,
                            stop:1 #c6c6c1
                        );
                        margin-top: 2px;
                        margin-bottom: -2px;
                        border-bottom: 1px solid #9c9c95;
                    }
                """)
                self.note_buttons[nota] = tecla
                tecla.setFixedSize(white_width, height_white)
                #tecla.clicked.connect(lambda checked, n=nota: print(f"Nota: {n}")) #DEBUG EN CONSOLA <<< CODIGO ARQUEOLOGICO >>>
                tecla.clicked.connect(lambda checked, n=nota: self.play_note(n))
                mainlayout.addWidget(tecla)
                x_offset += white_width
            else:  # Negra
                pos = x_offset - (black_width // 2)
                black_positions.append((nota, pos))
        
        # Negras Live's Mather's!!! (Este Teclado Nació Inclusivo)
        for nota, pos in black_positions:
            teclab = QPushButton(nota)
            self.note_buttons[nota] = teclab
            teclab.setFixedSize(black_width, height_black)
            #tecla.setStyleSheet("background-color: black; color: white;")
            # More Visual Impact for Black's on Blue's and Jazz
            teclab.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    color: white;
                    border: 1px solid #222222;
                    border-left: 1px solid #373737;
                    border-right: 1px solid #424242;
                    padding-top: 1px;
                }

                QPushButton:pressed {
                    background-color: #383838;
                    margin-top: 2px;
                    margin-bottom: -2px;
                }

                QPushButton:hover {
                    background-color: #222222;
                }
            """)
            teclab.setParent(self)
            teclab.move(pos, 1)
            teclab.raise_()
            teclab.show()
            #tecla.clicked.connect(lambda checked, n=nota: print(f"Nota: {n}")) #DEBUG EN CONSOLA <<< CODIGO ARQUEOLOGICO >>>
            teclab.clicked.connect(lambda checked, n=nota: self.play_note(n))

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        #key = event.text().lower()
        key = event.text().lower() if event.text() else "" # Aporta mas robustez
        if key in self.key_map:
            note = self.key_map[key]
            if note in self.note_buttons:
                boton = self.note_buttons[note]
                boton.setDown(True)   # feedback visual
                self.play_note(note)  # Dispara Play verdadero directo
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        #key = event.text().lower()
        key = event.text().lower() if event.text() else "" # Aporta mas robustez
        if key in self.key_map:
            note = self.key_map[key]
            if note in self.note_buttons:
                boton = self.note_buttons[note]
                boton.setDown(False)   # levanta la tecla visualmente
            # Evaluar comportamiento en polifonia puede haber problemas aca abajo
            if note == self.current_note:
                self.current_note = None
                # Comented's for sustain like organ but i don't know how can it
            freq = self.get_frequency(note)
            self.voice_manager.note_off(freq)
            self.engine.note_off()
        super().keyReleaseEvent(event)

    def set_tuning(self, value):
        # Snap suave a 440
        if abs(value - 440) <= 1:
            value = 440
            self.tuning_slider.blockSignals(True)
            self.tuning_slider.setValue(440)
            self.tuning_slider.blockSignals(False)
        
        self.tuning = value
        self.tuning_factor = self.tuning / 440

        # Acá está la magia Geckonica: si hay una nota sonando recalculamos
        if self.current_note:
            base_freq = self.NOTE_FREQ[self.current_note]
            freq = base_freq * self.tuning_factor

            # engine motor base
            #self.engine.frequency = freq 
            
            # multi voice engine
            self.voice_manager.frequency = freq
            self.voice_manager.note_on(freq, self.engine) 
            
            self.synth_panel.set_frequency(freq)

        self.tuning_label.setText(f"{self.tuning}")  # Actualiza visualmente
        if self.tuning == 440:
            self.tuning_label.setStyleSheet("font-size: 10px; color: #00ffaa; font-weight: bold;")
        else:
            self.tuning_label.setStyleSheet("font-size: 10px; color: #00ffaa;")
        
    def get_frequency(self, note):
        """Devuelve la frecuencia real de la nota considerando la afinación actual.
            IMPLEMENTADO por NOvaDulceKali 7.3.26
        """
        return self.NOTE_FREQ[note] * self.tuning_factor

    def play_note(self, note):
        self.current_note = note
        freq = self.get_frequency(note)

        # engine motor base
        #self.engine.frequency = freq
        
        # multi voice engine Aetheris
        self.voice_manager.note_on(freq, self.engine)

        self.synth_panel.set_frequency(freq)
 
# NOva Pad (hermoso y Geckonico)
class PadGrid(QWidget):
    def __init__(self, rows=5, cols=5):
        super().__init__()
        layout = QGridLayout(self)
        self.pads = []
        for r in range(rows):
            row = []
            for c in range(cols):
                pad = QPushButton()
                pad.setFixedSize(75, 75)
                pad.setStyleSheet("background-color: darkgray;")
                pad.clicked.connect(lambda _, x=r, y=c: self.pad_pressed(x, y))
                layout.addWidget(pad, r, c)
                row.append(pad)
            self.pads.append(row)

    def pad_pressed(self, row, col):
        print(f"Pad presionado fila {row} columna {col}")

# NOva Sequencer (Control Total del Flujo Geckonista)
class Sequencer:
    def __init__(self, pad_grid, step_interval=500):
        """
        pad_grid: instancia de PadGrid
        step_interval: milisegundos entre pasos
        """
        self.pad_grid = pad_grid
        self.num_rows = len(pad_grid.pads)
        self.num_cols = len(pad_grid.pads[0])
        self.current_step = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_step)
        
        # Estado de cada pad: None = vacío, "sound" = tiene sonido
        self.grid_state = [[None for _ in range(self.num_cols)] for _ in range(self.num_rows)]
    
    def assign_sound(self, row, col, sound_name="sound"):
        """Asigna un sonido al pad"""
        self.grid_state[row][col] = sound_name
        # Actualizamos color para indicar sonido asignado
        self.pad_grid.pads[row][col].setStyleSheet("background-color: lightgreen;")
    
    def clear_sound(self, row, col):
        """Remueve sonido del pad"""
        self.grid_state[row][col] = None
        self.pad_grid.pads[row][col].setStyleSheet("background-color: darkgray;")
    
    def start(self):
        """Arranca secuenciador"""
        self.timer.start(500)  # cada 500ms un paso
    
    def stop(self):
        self.timer.stop()
        # Reset de colores
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.grid_state[r][c]:
                    self.pad_grid.pads[r][c].setStyleSheet("background-color: lightgreen;")
                else:
                    self.pad_grid.pads[r][c].setStyleSheet("background-color: darkgray;")
        self.current_step = 0
    
    def play_step(self):
        """Enciende la columna actual y reproduce sonidos"""
        # Primero apagamos la columna anterior
        prev_step = self.current_step - 1 if self.current_step > 0 else self.num_cols - 1
        for r in range(self.num_rows):
            if self.grid_state[r][prev_step]:
                self.pad_grid.pads[r][prev_step].setStyleSheet("background-color: lightgreen;")
            else:
                self.pad_grid.pads[r][prev_step].setStyleSheet("background-color: darkgray;")
        
        # Ahora encendemos columna actual
        for r in range(self.num_rows):
            pad = self.pad_grid.pads[r][self.current_step]
            if self.grid_state[r][self.current_step]:
                pad.setStyleSheet("background-color: yellow;")  # en reproducción
                print(f"Reproduciendo sonido en pad fila {r} col {self.current_step}")
            else:
                pad.setStyleSheet("background-color: gray;")  # vacío
        # Avanzamos al siguiente paso
        self.current_step = (self.current_step + 1) % self.num_cols

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))
    voices = 8
    piano = PiaNOS(voices)
    piano.show()
    sys.exit(app.exec_())
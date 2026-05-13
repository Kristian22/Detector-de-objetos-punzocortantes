from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
import cv2

Builder.load_file("design.kv")


class PantallaPersonalizada(MDBoxLayout):
    text = StringProperty("")
    xml_path = StringProperty("")


class PantallaInfo(MDBoxLayout):
    titulo = StringProperty("")
    contenido = StringProperty("")


class KivyCamera(Image):
    # Propiedad para saber qué archivo XML cargar desde el KV
    model_file = StringProperty("")

    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None
        self.detector = None

    def start(self):
        # Cargamos el clasificador justo antes de iniciar la cámara
        if self.model_file:
            self.detector = cv2.CascadeClassifier(self.model_file)

        if not self.capture:
            self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def stop(self):
        if self.capture:
            Clock.unschedule(self.update)
            self.capture.release()
            self.capture = None
            self.texture = None  # Limpia la pantalla al salir

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret and self.detector:
            # Los Cascades funcionan mejor en escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detectar objetos (ajusta scaleFactor si es muy sensible)
            objetos = self.detector.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=12, minSize=(100, 100)
            )

            for x, y, w, h in objetos:
                # Dibujamos el cuadro en el frame original (color)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    "DETECTADO",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

            # Conversión de OpenCV a Textura de Kivy
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tobytes()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
            )
            image_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            self.texture = image_texture


class UI(ScreenManager):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        return UI()

    def change_style(self, checked, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"


if __name__ == "__main__":
    MainApp().run()

import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout 
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl

class WeatherApp(QWidget):  # WeatherApp herda de QWidget
    def __init__(self):  # Construtor
        super().__init__()  # Chama o construtor da classe pai
        
        # Widgets
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel("", self)
        self.weather_icon = QLabel(self)
        self.description_label = QLabel(self)

         # Gerenciador de rede para baixar imagem
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.set_weather_icon)

        # Inicializa a UI
        self.initUI()

    # Método para configurar a interface gráfica
    def initUI(self):  
        self.setWindowTitle("Weather App")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)

        # Crie um QHBoxLayout para centralizar o ícone
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()  # Adiciona espaço à esquerda
        icon_layout.addWidget(self.weather_icon)  # Adiciona o ícone
        icon_layout.addStretch()  # Adiciona espaço à direita
        icon_layout.setAlignment(Qt.AlignCenter)  # Centraliza o ícone

        vbox.addLayout(icon_layout)  # Adiciona o QHBoxLayout ao QVBoxLayout principal
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)
        
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.description_label.setObjectName("description_label")

        # Aplica CSS (PyQt StyleSheet)
        self.setStyleSheet("""
    QWidget {
        background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #0F2027, stop:0.5 #203A43, stop:1 #2C5364);
        color: white;
    }
    QLabel, QPushButton {
        font-family: Calibri;
    }
    QLabel#city_label {
        font-size: 24px;
        font-style: italic;
    }
    QLineEdit#city_input {
        font-size: 18px;
        border: 2px solid white;
        border-radius: 10px;
        padding: 5px;
        color: white;
        background: rgba(255, 255, 255, 0.2);
    }
    QPushButton#get_weather_button {
        font-size: 18px;
        font-weight: bold;
        background-color: #3498db;
        color: white;
        padding: 10px;
        border-radius: 10px;
    }
    QLabel#temperature_label {
        font-size: 75px;
        font-weight: bold;
    }
    QLabel#description_label {
        font-size: 35px;
    }
""")

        self.get_weather_button.clicked.connect(self.get_weather)

    def get_weather(self):
        api_key = '4a6282a6311092ee429e5e3ad7665df6'
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            status_code = response.status_code
            if status_code == 400:
                self.display_error("Bad request:\nPlease check your input")
            elif status_code == 401:
                self.display_error("Unauthorized:\nInvalid API key")
            elif status_code == 403:
                self.display_error("Forbidden:\nAccess is denied")
            elif status_code == 404:
                self.display_error("Not found:\nCity not found")
            elif status_code == 500:
                self.display_error("Internal Server Error:\nPlease try again later")
            elif status_code == 502:
                self.display_error("Bad Gateway:\nInvalid response from the server")
            elif status_code == 503:
                self.display_error("Service Unavailable:\nServer is down")
            elif status_code == 504:
                self.display_error("Gateway Timeout:\nNo response from the server")
            else:
                self.display_error(f"HTTP error occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px; color: #FF4C4C;")
        self.temperature_label.setText("⚠ " + message)
        self.weather_icon.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        temperature_f = (temperature_k * 9/5) - 459.67
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]
        icon_code = data["weather"][0]["icon"]  # Código do ícone (ex: "10d")

        self.city_label.setText(f"Weather in {data['name']}:")

        self.temperature_label.setText(f"{temperature_c:.0f}°C")
        self.description_label.setText(weather_description)

        # URL do ícone da OpenWeatherMap
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        self.load_weather_icon(icon_url)  # Carregar a imagem

    def load_weather_icon(self, url):
       request = QNetworkRequest(QUrl(url))
       self.network_manager.get(request)

    def set_weather_icon(self, reply):
       pixmap = QPixmap()
       pixmap.loadFromData(reply.readAll())
       if not pixmap.isNull():
        self.weather_icon.setPixmap(pixmap)
        self.weather_icon.setFixedSize(100, 100) 
        self.weather_icon.setScaledContents(False)  

if __name__ == "__main__": 
    app = QApplication(sys.argv)        
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
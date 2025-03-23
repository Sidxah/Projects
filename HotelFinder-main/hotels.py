import requests
import folium, io, json, sys, math, random, os
from folium.plugins import Draw, MousePosition, MeasureControl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import psycopg2
from jinja2 import Template
from branca.element import Element
import time
import hashlib



def hash_password(password):
    #Hacher un mot de passe avec SHA-256.
    return hashlib.sha256(password.encode()).hexdigest()
    
def conn_DB():
        conn = psycopg2.connect(database="l3info_103", user="l3info_103", host="10.11.11.22", password="L3INFO_103")
        return conn
        
class SignDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inscription")
        self.setFixedSize(300, 200)
        
        self.layout = QVBoxLayout()
        
        self.username_label = QLabel("Name:")
        self.username_input = QLineEdit()
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.password_label = QLabel("Mot de passe:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.sign_button = QPushButton("S'inscrire")
        self.sign_button.clicked.connect(self.add_user)
        
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.sign_button)
        
        self.setLayout(self.layout)
        self.successful_sign = False

    def add_user(self):
        name = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        # Hacher le mot de passe saisi par l'utilisateur
        hashed_password = hash_password(password)

        conn = conn_DB()
        cursor = conn.cursor()
        # Rechercher dans la table utisilateurs l'email si il existe deja
        query = f"SELECT email FROM utilisateurs WHERE email = '{email}'"
        cursor.execute(query)
        conn.commit()
        user = cursor.fetchone()  # Récupérer l'utilisateur si trouvé

        if user:
            self.successful_sign = False
            QMessageBox.warning(self, "Erreur", "L'email existe deja !")        

        else:
            query = f"INSERT INTO utilisateurs (user_name, email, password) VALUES ('{name}', '{email}', '{hashed_password}');"
            print(query)
            cursor.execute(query)
            conn.commit()
            QMessageBox.information(self, "Succès", "Inscription réussie!")
            conn.close()
            self.successful_sign = True
            self.accept()    
            

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.setFixedSize(300, 200)
        
        self.layout = QVBoxLayout()
        
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.password_label = QLabel("Mot de passe:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton("Se connecter")
        self.login_button.clicked.connect(self.verify_credentials)
        
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        
        self.setLayout(self.layout)

        self.successful_login = False
        self.username = ""
        self.email = " "

    def verify_credentials(self):
        # Simuler la vérification des informations d'identification
        email = self.email_input.text()
        password = self.password_input.text()
        # Hacher le mot de passe saisi par l'utilisateur
        hashed_password = hash_password(password)

        conn = conn_DB()
        cursor = conn.cursor()
        # Rechercher dans la base de données
        query = f"SELECT user_name FROM utilisateurs WHERE email = '{email}'  AND password = '{hashed_password}'"
        cursor.execute(query)
        user = cursor.fetchone()  # Récupérer l'utilisateur si trouvé

        conn.close()

        if user:
            self.successful_login = True
            self.username = user[0]
            self.email = email
            QMessageBox.information(self, "Succès", "Connexion réussie!")
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect.")
            
class AfficherFavorisDialog(QDialog):
    def __init__(self,parent=None, email=None):
        super().__init__(parent)
        self.setWindowTitle("Mes hôtels favoris")
        self.setFixedSize(1200, 400)
        
        # Fond principal
        self.label = QLabel(self)
        self.label.setGeometry(QRect(0, 0, 1200, 400))
        self.label.setPixmap(QPixmap("assets/images/lobby.jpg"))
        self.label.setScaledContents(True)
        self.layout = QVBoxLayout()
        
        self.title = QLabel("Hôtels Favoris  ")
        self.title.setGeometry(QRect(30, 10, 200, 40))
        self.title.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 500;
                font-size: 35px;
                
            }
        """)
        
        self.tableFavoris = QTableWidget(self)
        self.tableFavoris.setGeometry(QRect(30, 200, 1111, 371))
        self.tableFavoris.setStyleSheet("""
            QTableWidget {
                background-color: rgba(240, 240, 240, 0.8);
                border: 1px solid rgba(211, 211, 211, 0.8);
                border-radius: 5px;
            }
        """)

        self.tableFavoris.setColumnCount(5)
        self.tableFavoris.doubleClicked.connect(self.remove_favoris)
        # Nommer les en-têtes de colonnes
        self.headers = ["Nom ", "Addresse", "Code postale", "Prix" ,"Classement"]
        self.tableFavoris.setHorizontalHeaderLabels(self.headers)
        
        # Définir manuellement la largeur des colonnes
        column_widths = [250, 400, 100, 100, 100]  # Largeurs spécifiques pour chaque
        for j, width in enumerate(column_widths):
            self.tableFavoris.setColumnWidth(j, width)
        
        conn = conn_DB()
        cursor = conn.cursor()
        # Rechercher l'id de l'utilisateur
        self.email = email
        self.user_id = 0
        rows = []
        query = f"SELECT id FROM utilisateurs WHERE email = '{self.email}' "
        cursor.execute(query)
        reponse = cursor.fetchone()  # Récupérer l'id si trouvé
        if reponse:
            self.user_id = reponse[0]
            query = f"SELECT hotel_name, adresse, cp, prix, classement FROM favoris WHERE id = {self.user_id} "
            cursor.execute(query)
            conn.commit()
            rows += cursor.fetchall()
        
            numrows = len(rows)
            numcols = len(rows[-1])
            self.tableFavoris.setRowCount(numrows)
            i = 0
            for row in rows : 
                j = 0
                for col in row :
                    self.tableFavoris.setItem(i, j, QTableWidgetItem(str(col)))
                    j = j + 1
                i = i + 1
            self.update()
        else :
            QMessageBox.warning(self, "Erreur", "There is a probleme !.")
            # Chercher des hotels favoris de l'utilisateur dans favoris
            

        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.tableFavoris)
        self.setLayout(self.layout)
        
    
    def remove_favoris(self):
        self.user_id
        current_row = self.tableFavoris.currentRow()
        hotel_name = self.tableFavoris.item(current_row, 0).text()
        
        conn = conn_DB()
        cursor = conn.cursor()

        # Supprimer le favori de la base de données
        delete_query = f"DELETE FROM favoris WHERE id = {self.user_id} AND hotel_name = '{hotel_name}'"
        cursor.execute(delete_query)
        conn.commit()

        # Supprimer la ligne de la table graphique
        self.tableFavoris.removeRow(current_row)
        QMessageBox.information(self, "Succès", "Favori supprimé avec succès.")
               
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ile de France Hotels")
        self.resize(1200, 900)
        self.email = " "
        self.isLogged = False
        
        # Fond principal
        self.label_2 = QLabel(self)
        self.label_2.setGeometry(QRect(0, 0, 1200, 1021))
        self.label_2.setPixmap(QPixmap("assets/images/lobby.jpg"))
        self.label_2.setScaledContents(True)

        # Barre supérieure
        self.frame = QFrame(self)
        self.frame.setGeometry(QRect(0, 0, 1200, 101))
        self.frame.setStyleSheet("background-color: white;")
        self.frame.setFrameShape(QFrame.StyledPanel)

		# Le logo de la page 
        self.logo = QLabel(self.frame)
        self.logo.setGeometry(QRect(40, 10, 100, 81))
        self.logo.setPixmap(QPixmap("assets/images/logo.png"))
        self.logo.setScaledContents(True)
				
        #signIn button
        self.signButton = QPushButton("Sign In", self.frame)
        self.signButton.setGeometry(QRect(880, 30, 120, 31))
        self.signButton.clicked.connect(self.open_sign_dialog)
	
        # login button
        self.loginButton = QPushButton("Login", self.frame)
        self.loginButton.setGeometry(QRect(1020, 30, 120, 31))
        self.loginButton.clicked.connect(self.open_login_dialog)
        
        
        
        # Title 
        self.title = QLabel(self.frame)
        self.title.setGeometry(QRect(170, 40, 221, 20))
        self.title.setFont(QFont("Arial", 16, QFont.Bold))
        self.title.setText("Ile de France Hotels")

        # QVLayout info d'utilisateur apres connexion
        self.user_box = QGroupBox("", self.frame)
        self.user_box.setGeometry(QRect(500, 10, 600, 80))
        self.user_box.setStyleSheet("""
            QGroupBox {
                background-color:white;
                border: 1px solid rgba(211, 211, 211, 0.8);
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        self.hi_user = QLabel(f"Hi! User", self.user_box)
        self.hi_user.setGeometry(QRect(10, 10, 180, 50))
        self.hi_user.setStyleSheet("""
            QLabel {
                background-color: white;
                font-weight: 500;
                font-size: 20px;  
            }
        """)
    
        self.favoris = QPushButton("Afficher favoris", self.user_box)
        self.favoris.setGeometry(QRect(200, 10, 190, 50))
        icon = QIcon("assets/icons/favoris.png")
        self.favoris.setIcon(icon)
        self.favoris.clicked.connect(lambda: self.afficher_favoris(self.email))
        
        self.logout = QPushButton("Logout", self.user_box)
        self.logout.setGeometry(QRect(400, 10, 150, 50))
        icon = QIcon("assets/icons/logout.png")
        self.logout.setIcon(icon)
        self.logout.clicked.connect(lambda: self.deconnexion(self.email))
        self.user_box.hide()

        # GroupBox pour les filtres
        self.groupBox_2 = QGroupBox("", self)
        self.groupBox_2.setGeometry(QRect(20, 110, 551, 360))
        self.groupBox_2.setStyleSheet("""
            QGroupBox {
                background-color: rgba(240, 240, 240, 0.7);
                border: 1px solid rgba(211, 211, 211, 0.8);
                border-radius: 5px;
                padding: 10px;
            }
        """)

        self.searchBar = QTextEdit(self.groupBox_2)
        self.searchBar.setGeometry(QRect(20, 10, 451, 41))
        self.searchBar.setPlaceholderText("Indiquer une adresse ou une ville pour trouver un hôtel proche.")

        self.searchButton = QPushButton(self.groupBox_2)
        self.searchButton.setGeometry(QRect(480, 10, 61, 41))
        icon = QIcon("assets/icons/chercher.svg")
        self.searchButton.setIcon(icon)
        self.searchButton.clicked.connect(self.button_search)
        self.filtre = QLabel("Filtres ", self.groupBox_2)
        self.filtre.setGeometry(QRect(30, 70, 161, 41))
        self.filtre.setStyleSheet("""
            QLabel {
                font-weight: 500;
                font-size: 35px;
                
            }
        """)

        self.checkBoxDept = QCheckBox("Département", self.groupBox_2)
        self.checkBoxDept.setGeometry(QRect(50, 130, 121, 25))
        
        self.checkBoxClass = QCheckBox("Classement", self.groupBox_2)
        self.checkBoxClass.setGeometry(QRect(50, 180, 121, 25))

        self.checkBoxPrix = QCheckBox("Prix maximum", self.groupBox_2)
        self.checkBoxPrix.setGeometry(QRect(50, 230, 121, 25))
        
        self.boxDept = QComboBox(self.groupBox_2)
        self.boxDept.setEditable(True)
        self.boxDept.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.boxDept.setInsertPolicy(QComboBox.NoInsert)
        self.boxDept.setGeometry(QRect(190, 130, 120, 27))
        
        self.boxClass = QComboBox(self.groupBox_2)
        self.boxClass.setEditable(True)
        self.boxClass.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.boxClass.setInsertPolicy(QComboBox.NoInsert)
        self.boxClass.setGeometry(QRect(190, 180, 120, 27))
        
        self.lineEditPrix = QLineEdit(self.groupBox_2)
        self.lineEditPrix.setGeometry(QRect(190, 230, 120, 27))
       
				
        self.appliquerFiltre = QPushButton("Appliquer", self.groupBox_2)
        self.appliquerFiltre.setGeometry(QRect(350, 230, 150, 30))
        self.appliquerFiltre.clicked.connect(self.button_search)
		    
        # Carte WebView
    
        self.webView = myWebView(self)
        self.webView.setGeometry(QRect(600, 110, 531, 360))
        self.webView.raise_()
        
        self.clearButton = QPushButton("Clear", self)
        self.clearButton.setGeometry(QRect(1060, 120, 61, 41))
        self.clearButton.raise_()
        self.clearButton.clicked.connect(self.button_clear)
     

        print("chargement de la carte")
        # Tableau
        self.rows =[]
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QRect(20, 480, 1111, 371))
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background-color: rgba(240, 240, 240, 0.8);
                border: 1px solid rgba(211, 211, 211, 0.8);
                border-radius: 5px;
            }
        """)

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(10)
        
        # Nommer les en-têtes de colonnes
        self.headers = ["Nom ", "Addresse", "Code postale", "Prix" ,"Classement"]
        self.tableWidget.setHorizontalHeaderLabels(self.headers)
        
        # Définir manuellement la largeur des colonnes
        column_widths = [250, 400, 100, 100, 100]  # Largeurs spécifiques pour chaque colonnes
        for j, width in enumerate(column_widths):
            self.tableWidget.setColumnWidth(j, width)
        self.tableWidget.doubleClicked.connect(self.table_Click)
        # connecter la base de donnée
        self.connect_DB()
        self.webView.setMap()
        
    def open_login_dialog(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted and login_dialog.successful_login:
            self.isLogged = True
            self.email = login_dialog.email
            self.loginButton.hide()
            self.signButton.hide()
            user_name = login_dialog.username
            self.hi_user.setText(f"Hi! {user_name}")
            self.user_box.show()

    def open_sign_dialog(self):
        sign_dialog = SignDialog(self)
        if sign_dialog.exec_() == QDialog.Accepted and sign_dialog.successful_sign:
            self.isLogged = True
            self.loginButton.hide()
            self.signButton.hide()
            user_name = sign_dialog.username_input.text()
            self.hi_user.setText(f"Hi! {user_name}")
            self.user_box.show()
            
    def afficher_favoris(self, email):
        conn = conn_DB()
        cursor = conn.cursor()
    
        # Vérifier si des favoris existent pour cet utilisateur
        query = f"SELECT COUNT(*) FROM favoris f JOIN utilisateurs u ON f.id = u.id WHERE u.email = '{email}'"
        cursor.execute(query)
        count = cursor.fetchone()[0]

        if count == 0:
            QMessageBox.information(self, "Favoris", "Votre liste de favoris est vide.")
            return  # Ne pas afficher la boîte de dialogue si aucun favori

        # Afficher la boîte de dialogue si des favoris existent
        afficherFavoris = AfficherFavorisDialog(self, email)
        afficherFavoris.exec_()
  
        cursor.close()
        conn.close()
        
      
    def deconnexion(self, email):
        email = " "
        self.isLogged = False
        self.user_box.hide()
        self.loginButton.show()
        self.signButton.show()
        
    def connect_DB(self):
        self.conn = psycopg2.connect(database="l3info_103", user="l3info_103", host="10.11.11.22", password="L3INFO_103")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""SELECT DISTINCT hotels.﻿departement FROM hotels ORDER BY hotels.﻿departement ASC""")
        self.conn.commit()
        depts = self.cursor.fetchall()
        for dept  in depts : 
            self.boxDept.addItem(str(dept[0]))
            
            
        self.cursor.execute("""SELECT DISTINCT classement FROM hotels ORDER BY classement ASC""")
        self.conn.commit()
        cls = self.cursor.fetchall()   
        for cl in cls:
            self.boxClass.addItem(str(cl[0]))
        
    def button_clear(self):
        self.webView.clearMap()
        self.update()
        
    def button_search(self):
        self.tableWidget.clearContents()
        latitude = 0
        longitude = 0
        # Adresse à convertir en latitude et longitude
        adresse = self.searchBar.toPlainText()
 
        #### recherche de latitude et longitude de l'addresse saisie par l'utilisateur
        # URL de l'API Nominatim
        url = f"https://nominatim.openstreetmap.org/search?q={adresse}&format=json"
        try:
            # Ajouter un User-Agent dans l'en-tête
            headers = {
                'User-Agent': 'MyPythonApp/1.0 '
            }
        
            # Faire une requête HTTP GET avec les en-têtes
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Vérifie les erreurs HTTP
        
            data = response.json()

            if data:
               latitude = data[0]["lat"]
               longitude = data[0]["lon"]
               print(f"Latitude : {latitude}, Longitude : {longitude}")
               #self.webView.addMarker("#00ff00", latitude, longitude)
               self.webView.addPoint(latitude, longitude)
            else:
               print("Adresse introuvable ou aucune donnée renvoyée.")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête HTTP : {e}")
        except ValueError as e:
            print(f"Erreur lors du traitement JSON : {e}")
           
        ### Trouver les 10 hotels les plus proches a l'addresse saisie en utilisant les filtres 
        # Récupérer les valeurs des filtres
        filters = []
        if self.checkBoxDept.isChecked():
            dept = self.boxDept.currentText()
            filters.append(f"hotels.﻿departement = '{dept}'")
            
        if self.checkBoxClass.isChecked():
            avis = self.boxClass.currentText()
            filters.append(f"classement = '{avis}'")

            
        if self.checkBoxPrix.isChecked():
            prix_max = self.lineEditPrix.text()
            if prix_max:
                filters.append(f"prix <= {prix_max}")

        # Construire la clause WHERE pour les filtres
        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause
        else:
            where_clause = "WHERE " + "True"
        self.rows = []
        
        
        requette = f"""SELECT nom, addr, cp, prix, classement, geo_x, geo_y FROM hotels {where_clause} ORDER BY SQRT(POW((geo_x - {latitude}), 2) + POW((geo_y - {longitude}), 2)) ASC LIMIT 10 """
        print(requette)
        self.cursor.execute(requette)
        self.conn.commit()
        self.rows += self.cursor.fetchall()
        
        if len(self.rows) == 0 : 
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        numrows = len(self.rows)
        numcols = len(self.rows[-1])
        
        i = 0
        latitude = 0
        longitude = 0
        for row in self.rows : 
            latitude = float(row[-2]) 
            longitude = float(row[-1]) 
            print(f" latitude {latitude}, longitude {longitude}")
            # Ajouter un marqueur pour chaque hôtel
            self.webView.addMarker("blue", latitude, longitude)
            j = 0
            for col in row[:-2] :
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(col)))
                j = j + 1
            i = i + 1

        
        self.update()	
        
    def table_Click(self):
        if self.isLogged == False:
            QMessageBox.warning(self, "Erreur", "Il faut se connecter pour ajouter un hôtel au favoris !")  
        else:
            conn = conn_DB()
            cursor = conn.cursor()
            print("je suis laa")
            print(self.email)
            query = f"SELECT id FROM utilisateurs WHERE email = '{self.email}'"
            cursor.execute(query)
            reponse = cursor.fetchone() 
            print(str(reponse[0]))
            if reponse:
                row = self.rows[self.tableWidget.currentRow()]     
                query = f"INSERT INTO favoris VALUES ({reponse[0]}, '{row[0]}','{row[1]}','{row[2]}',{float(row[3])}, '{row[4]}');"
                print(query)
                cursor.execute(query)
                conn.commit()
                QMessageBox.information(self, "Succès", "Ajout au favoris réussie!")
   
        
class myWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)  # Passez le parent au constructeur
        self.setMap()
        
    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object
    
    def handleClick(self, msg):
        data = json.loads(msg)
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']

        window.mouseClick(lat, lng)


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)


    def addMarker(self,color, lat, lng):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "{{color}}",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "{{color}}",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(),latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def addPoint(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(latitude=lat, longitude=lng)
        self.page().runJavaScript(js)

    def setMap(self):
        self.mymap = folium.Map(location=[48.8566, 2.3522], zoom_start=10)
        self.mymap = self.add_customjs(self.mymap)
        
        data = io.BytesIO()
        self.mymap.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())
        
    def clearMap(self):
        self.setMap()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


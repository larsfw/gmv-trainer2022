import os
import sys

from PyQt5 import QtGui, QtWidgets, uic

from GMVTrainerController import TrainerController
from GMVTrainerModel import TrainerModel


class TrainerView(QtWidgets.QMainWindow):
    def __init__(self):
        super(TrainerView, self).__init__()
        self.ui_dir = TrainerModel.resourcePath("ui").replace("\\", "/")
        ui_dir = self.ui_dir
        if os.name == "nt":
            uic.loadUi(ui_dir + "/GMVTrainer_win.ui", self)
        else:
            uic.loadUi(ui_dir + "/GMVTrainer_mac.ui", self)
        self.konfigUI()
        self.show()

    def konfigUI(self):
        # Setze feste Fenstergröße
        self.setFixedSize(800, 590)
        self.tableWidget_uebersicht.setColumnWidth(0, 30)
        self.tableWidget_uebersicht.setColumnWidth(1, 400)
        self.tableWidget_uebersicht.setColumnWidth(2, 85)
        self.tableWidget_uebersicht.setColumnWidth(3, 110)
        self.tableWidget_quantis.setColumnWidth(0, 80)
        self.tableWidget_quantis.setColumnWidth(1, 80)
        self.tableWidget_quantis.setColumnWidth(2, 20)
        pixmap = QtGui.QPixmap(self.ui_dir + "/iib_logo_4.png")
        self.label_9.setPixmap(pixmap)
        icon = QtGui.QIcon(self.ui_dir + "/iib_logo_4.png")
        self.setWindowIcon(icon)

    def fileDialog(self, datei, ext):
        return QtWidgets.QFileDialog.getOpenFileName(
            self,
            f"Öffne die {datei}datei",
            filter=f"{datei}datei (*.{ext}) ;; Alle Dateien (*)",
        )

    def saveDialog(self, pfad):
        return QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Speichere die neue Speicherstandsdatei",
            directory=f"{pfad}/Speicherstand.xml",
            filter="Speicherstandsdatei (*.xml)",
        )

    def fuelleComboBox(self, uebersicht_list):
        self.comboBox_aufgaben.clear()
        self.comboBox_aufgaben.addItems(uebersicht_list)
        self.comboBox_aufgaben.setCurrentIndex(-1)

    def zeigeUebersicht(self, uebersicht_df):
        self.progressBar.setMaximum(uebersicht_df.shape[0])
        anzahlVollstaendig = 0
        self.tableWidget_uebersicht.setRowCount(uebersicht_df.shape[0])
        row = 0
        uebersichtArray = uebersicht_df.to_numpy()
        for aufgabe in uebersichtArray:
            if str(aufgabe[2]) == "nan":
                aufgabe[2] = "unbearbeitet"
                aufgabe[3] = ""
            self.tableWidget_uebersicht.setItem(
                row, 0, QtWidgets.QTableWidgetItem(aufgabe[0])
            )
            self.tableWidget_uebersicht.setItem(
                row, 1, QtWidgets.QTableWidgetItem(aufgabe[1])
            )
            self.tableWidget_uebersicht.setItem(
                row, 2, QtWidgets.QTableWidgetItem(aufgabe[2])
            )
            self.tableWidget_uebersicht.setItem(
                row, 3, QtWidgets.QTableWidgetItem(aufgabe[3])
            )
            if aufgabe[2] == "vollständig":
                anzahlVollstaendig += 1
                for i in range(0, 4):
                    self.tableWidget_uebersicht.item(row, i).setBackground(
                        QtGui.QColor(20, 200, 20)
                    )
                    i += 1
            if aufgabe[2] == "unbearbeitet":
                for i in range(0, 4):
                    self.tableWidget_uebersicht.item(row, i).setBackground(
                        QtGui.QColor(200, 200, 200)
                    )
                    i += 1
            if aufgabe[2] == "bearbeitet":
                for i in range(0, 4):
                    self.tableWidget_uebersicht.item(row, i).setBackground(
                        QtGui.QColor(200, 190, 0)
                    )
                    i += 1
            row += 1
        self.progressBar.setValue(anzahlVollstaendig)

    def zeigeQuantis(self, aktuelleQuantis_df):
        self.tableWidget_quantis.setRowCount(aktuelleQuantis_df.shape[0])
        row = 0
        quantisArray = aktuelleQuantis_df.to_numpy()
        for quanti in quantisArray:
            self.tableWidget_quantis.setItem(
                row, 0, QtWidgets.QTableWidgetItem(quanti[0])
            )
            self.tableWidget_quantis.setItem(
                row, 1, QtWidgets.QTableWidgetItem(str(quanti[1]))
            )
            self.tableWidget_quantis.setItem(
                row, 2, QtWidgets.QTableWidgetItem(str(quanti[2]))
            )
            # self.tableWidget_quantis.item(row, 1).setTextAlignment(2)
            # self.tableWidget_quantis.item(row, 2).setTextAlignment(1)
            # self.tableWidget_quantis.item(row, 0).setTextAlignment(1)
            if quanti[1] == quanti[2]:
                for i in range(0, 3):
                    self.tableWidget_quantis.item(row, i).setBackground(
                        QtGui.QColor(20, 200, 20)
                    )
                    i += 1
            if quanti[1] == 0 and quanti[2] == 0:
                for i in range(0, 3):
                    self.tableWidget_quantis.item(row, i).setBackground(
                        QtGui.QColor(200, 200, 200)
                    )
                    i += 1
            if (quanti[1] != 0 or quanti[2] != 0) and quanti[1] != quanti[2]:
                for i in range(0, 3):
                    self.tableWidget_quantis.item(row, i).setBackground(
                        QtGui.QColor(200, 190, 0)
                    )
                    i += 1
            row += 1

    def zeigeMerkmale(self, aktuelleMerkmale_df):
        text_merkmale = ""
        merkmaleArray = aktuelleMerkmale_df.to_numpy()
        for merkmal in merkmaleArray:
            if merkmal[2] == True:
                text_merkmale += (
                    f'<span style=" font-size:xx-large;">✔</span>  {merkmal[0]}<br><br>'
                )
            else:
                text_merkmale += (
                    f'<span style=" font-size:xx-large;">𐄂</span>  {merkmal[0]}<br><br>'
                )
        text_html = f'<html><head/><body><p><span style=" font-size:12pt; font-weight:600;">Qualitative Merkmale</span></p><p>{text_merkmale}</p></body></html>'
        self.label_qualis.setText(text_html)

    def zeigeFehlerFenster(self, text):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Fehler")
        msgBox.setIcon(3)
        msgBox.setText(text)
        msgBox.exec()

    def zeigeInfoFenster(self, text):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Info")
        msgBox.setIcon(1)
        msgBox.setText(text)
        msgBox.exec()

    def zeigeSpeicherstandFenster(self, pfad):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Neuen Speicherstand anlegen?")
        msgBox.setIcon(4)
        msgBox.setText(
            f"Es wurde keine Speicherstandsdatei gefunden.\n\nDurchsuchter Pfad: {pfad}\n\nSoll ein neuer Speicherstand angelegt werden?"
        )
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.exec()
        if msgBox.result() == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def zeigeMLFenster(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Fehler")
        msgBox.setIcon(3)
        msgBox.setText(
            f"Die Musterlösung (ML) konnte nicht geladen werden.\n\nErneut versuchen?"
        )
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.exec()
        if msgBox.result() == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def zeigeText(self, uiElement, text):
        uiElement.setText(f"{text}")

    def fuelleLineEdit(self, lineEdit, newValue):
        if isinstance(newValue, str):
            lineEdit.setText(newValue)
        else:
            lineEdit.setText(f"{newValue:g}")

    def aktiviereSpeichern(self, istAktiv):
        self.pushButton_speichern.setEnabled(istAktiv)

    def aktiviereKPLaden(self, index):
        if index != -1:
            self.pushButton_kp.setEnabled(True)
        else:
            self.pushButton_kp.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("macintosh")
    view = TrainerView()
    model = TrainerModel()
    controller = TrainerController(model, view)
    sys.exit(app.exec())

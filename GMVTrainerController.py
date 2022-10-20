import time


class TrainerController:
    def __init__(self, model, view):
        super(TrainerController, self).__init__()
        self.view = view
        self.model = model
        self.initializeUI()
        self.connectSignals()

    def initializeUI(self):
        try:
            self.model.ladeML(self.model.workingDir)
        except:
            self.oeffneML()
        self.view.zeigeText(self.view.textEdit_ml, self.model.ml_pfad)

        try:
            self.model.ladeSpeicherstand(self.model.workingDir)
        except:
            result = self.view.zeigeSpeicherstandFenster(self.model.workingDir)
            if result == True:
                filename = self.view.saveDialog(self.model.workingDir)
                if filename[0][-4:] != ".xml":
                    pfad = filename[0] + ".xml"
                else:
                    pfad = filename[0]
                self.model.erstelleSpeicherstand(pfad)
                self.model.ladeSpeicherstand(pfad)
            else:
                self.oeffneSpeicherstand()
        self.view.zeigeText(self.view.textEdit_speicherstand, self.model.speicher_pfad)

        self.uebersichtLaden()

    def connectSignals(self):
        self.view.pushButton_speicherLaden.clicked.connect(
            self.oeffneSpeicherstand_clicked
        )
        self.view.pushButton_ml.clicked.connect(self.oeffneML_clicked)
        self.view.pushButton_kp.clicked.connect(self.oeffneKP)
        self.view.pushButton_speichern.clicked.connect(
            lambda: self.speichern(self.view.comboBox_aufgaben.currentIndex())
        )
        self.view.comboBox_aufgaben.currentIndexChanged.connect(
            lambda: self.aendereAufgabe(self.view.comboBox_aufgaben.currentIndex())
        )

    def aendereAufgabe(self, index):
        self.model.speichereAktuelleAufgabe(index)
        self.view.aktiviereKPLaden(index)
        self.view.aktiviereSpeichern(False)
        self.view.zeigeText(self.view.textEdit_kp, "")
        self.view.zeigeQuantis(self.model.aktuelleQuantis_df)
        self.view.zeigeMerkmale(self.model.aktuelleMerkmale_df)

    def uebersichtLaden(self):
        try:
            self.model.erstelleUebersichtDf()
            self.model.erstelleUebersichtList()
            self.view.zeigeUebersicht(self.model.uebersicht_df)
            self.view.fuelleComboBox(self.model.uebersicht_list)
        except Exception as e:
            self.view.zeigeFehlerFenster(
                f"Die Übersicht und/oder Aufgaben konnten nicht geladen werden.\n\nBitte lade erneut die aktuelle Musterlösung (ML) und/oder deinen Speicherstand.\n\nError: {e}"
            )

    def oeffneML(self):
        while True:
            try:
                filename = self.view.fileDialog("Musterlösungs", "xml")
                self.model.ladeML(filename[0])
                self.view.zeigeText(self.view.textEdit_ml, self.model.ml_pfad)
                break
            except:
                result = self.view.zeigeMLFenster()
                if result == False:
                    break

    def oeffneSpeicherstand(self):
        try:
            filename = self.view.fileDialog("Speicherstands", "xml")
            self.model.ladeSpeicherstand(filename[0])
            self.view.zeigeText(
                self.view.textEdit_speicherstand, self.model.speicher_pfad
            )
        except Exception as e:
            self.view.zeigeFehlerFenster(
                f"Der Speicherstand konnte nicht geladen werden.\n\nBitte versuche es erneut.\n\nError: {e}"
            )

    def oeffneML_clicked(self):
        self.oeffneML()
        self.uebersichtLaden()

    def oeffneSpeicherstand_clicked(self):
        self.oeffneSpeicherstand()
        self.uebersichtLaden()

    def oeffneKP(self):
        try:
            filename = self.view.fileDialog("Konstruktionsprotokoll", "html")
            self.model.ladeKPundAbgleichML(
                filename[0], self.view.comboBox_aufgaben.currentIndex()
            )
            self.view.zeigeText(self.view.textEdit_kp, self.model.kp_pfad)
        except Exception as e:
            self.view.zeigeFehlerFenster(
                f"Das Konstruktionsprotokoll konnte nicht geladen werden oder nicht mit der Musterlösung abgeglichen werden.\n\nError: {e}"
            )

        try:
            self.view.zeigeMerkmale(self.model.aktuelleMerkmale_df)
            self.view.aktiviereSpeichern(self.model.speichernAktiv)
        except Exception as e:
            self.view.zeigeFehlerFenster(
                f"Die qualitativen Merkmale konnten nicht ausgewertet werden.\n\nError: {e}"
            )

        try:
            self.view.zeigeQuantis(self.model.aktuelleQuantis_df)
        except Exception as e:
            self.view.zeigeFehlerFenster(
                f"Die quantitativen Merkmale konnten nicht ausgewertet werden.\n\nError: {e}"
            )

    def speichern(self, index):
        try:
            if index != -1:
                if "True" in str(self.model.aktuelleMerkmale_df["erfüllt"]):
                    if "False" not in str(self.model.aktuelleMerkmale_df["erfüllt"]):
                        status = "vollständig"
                    else:
                        status = "bearbeitet"
                    time_tuple = time.localtime()
                    timestamp = time.strftime("%d.%m.%Y %H:%M:%S", time_tuple)
                    self.model.uebersicht_df.loc[index]["Datum"] = timestamp
                    self.model.uebersicht_df.loc[index]["Status"] = status
                    nr = self.model.uebersicht_df.loc[index]["Nr"]
                    self.view.zeigeUebersicht(self.model.uebersicht_df)
                    self.model.speichernXML(self.model.speicher_pfad)
                    self.view.zeigeInfoFenster(
                        f"Aufgabe {nr} erfolgreich gespeichert.\n\nStatus: {status}\n\nZeitstempel: {timestamp}"
                    )
                    self.view.comboBox_aufgaben.setCurrentIndex(-1)
                    self.view.aktiviereKPLaden(-1)
                    self.view.aktiviereSpeichern(False)
                    self.view.zeigeText(
                        self.view.label_qualis,
                        '<html><head/><body><p><span style=" font-size:12pt; font-weight:600;">Qualitative Merkmale</span></p></body></html>',
                    )
                    self.view.tableWidget_quantis.clear()
                    self.view.tableWidget_quantis.setHorizontalHeaderLabels(
                        ["Element", "Deine Anzahl", "ML"]
                    )
                    self.view.textEdit_kp.clear()

        except Exception as e:
            self.view.zeigeFehlerFenster(f"Speichern fehlgeschlagen.\n\nError: {e}")

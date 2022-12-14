import codecs
import glob
import os
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

import pandas as pd
from lxml.etree import parse, tostring


class TrainerModel:
    @classmethod
    def resourcePath(cls, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def __init__(self):
        super(TrainerModel, self).__init__()
        self.workingDir = os.path.abspath(os.getcwd())
        self.element_list = {
            "Punkt",
            "Strecke",
            "Gerade",
            "Vektor",
            "Ebene",
            "Dreieck",
            "Viereck",
            "Fünfeck",
            "Sechseck",
            "Vieleck",
        }
        self.kp_pfad = ""
        self.ml_pfad = ""
        self.speicher_pfad = ""
        self.speichernAktiv = False
        self.aufgaben_df = pd.DataFrame(columns=["Nr", "Titel", "kp", "merkmale"])
        self.speicher_df = pd.DataFrame(columns=["Nr", "Status", "Datum"])

    def ladeML(self, pfad):
        if pfad[-4:] == ".xml":
            ml_pfad = pfad
        else:
            if not glob.glob(pfad + "/ML*.xml"):
                raise LookupError(
                    "Es konnte keine Musterlösungsdatei (ML) gefunden werden."
                )
            else:
                ml_pfad = glob.glob(pfad + "/ML*.xml")[-1]
        self.ml_pfad = ml_pfad

        ml_tree = parse(ml_pfad)
        aufgaben_root = ml_tree.getroot()
        aufgaben_df = pd.DataFrame(columns=["Nr", "Titel", "kp", "merkmale"])
        i = 0
        for aufgabe in aufgaben_root.iter("aufgabe"):
            id = aufgabe.attrib["id"]
            titel = aufgabe.attrib["titel"]
            kp = ml_tree.xpath("//konstruktionsprotokoll")[i]
            merkmale = ml_tree.xpath("//merkmale")[i]
            i += 1
            new_row = {
                "Nr": id,
                "Titel": titel,
                "kp": tostring(kp),
                "merkmale": merkmale,
            }
            aufgaben_df = aufgaben_df.append(new_row, ignore_index=True)
        self.aufgaben_df = aufgaben_df

        aufgaben_list = aufgaben_df["Nr"].tolist()
        titel_list = aufgaben_df["Titel"].tolist()
        if len(aufgaben_list) == 0:
            raise ImportError("Es konnten keine Aufgaben aus der ML geladen werden.")
        i = 0
        while i < len(aufgaben_list):
            aufgaben_list[i] += "  " + titel_list[i]
            i += 1
        self.aufgaben_list = aufgaben_list

    def ladeSpeicherstand(self, pfad):
        if pfad[-4:] == ".xml":
            speicher_pfad = pfad
        else:
            speicher_pfad = glob.glob(f"{pfad}/*Speicherstand*.xml")[-1]
        self.speicher_pfad = speicher_pfad

        speicher_tree = parse(speicher_pfad)
        speicher_root = speicher_tree.getroot()
        speicher_df = pd.DataFrame(columns=["Nr", "Status", "Datum"])
        i = 0
        for status in speicher_root.iter("status"):
            id = status.attrib["aufg_id"]
            code = status.attrib["code"]
            datum = status.attrib["datum"]
            i += 1
            new_row = {"Nr": id, "Status": code, "Datum": datum}
            speicher_df = speicher_df.append(new_row, ignore_index=True)
        self.speicher_df = speicher_df

    def erstelleSpeicherstand(self, pfad):
        self.speicher_pfad = pfad
        root = ET.Element("speicherstand")
        a_df = self.aufgaben_df
        i = 0
        while i < len(a_df):
            ET.SubElement(
                root,
                "status",
                attrib={"aufg_id": a_df["Nr"][i], "code": "unbearbeitet", "datum": ""},
            )
            i += 1
        xmlstr = ET.tostring(root)
        dom = xml.dom.minidom.parseString(xmlstr)
        pretty_xmlstr = dom.toprettyxml()
        pretty_tree = ET.ElementTree(ET.fromstring(pretty_xmlstr))
        pretty_tree.write(pfad)

    def speichernXML(self, pfad):
        root = ET.Element("speicherstand")
        u_df = self.uebersicht_df
        i = 0
        while i < len(u_df):
            ET.SubElement(
                root,
                "status",
                attrib={
                    "aufg_id": u_df["Nr"][i],
                    "code": u_df["Status"][i],
                    "datum": u_df["Datum"][i],
                },
            )
            i += 1
        xmlstr = ET.tostring(root)
        dom = xml.dom.minidom.parseString(xmlstr)
        pretty_xmlstr = dom.toprettyxml()
        pretty_tree = ET.ElementTree(ET.fromstring(pretty_xmlstr))
        pretty_tree.write(pfad)

    def erstelleUebersichtDf(self):
        self.uebersicht_df = (
            pd.merge(self.aufgaben_df, self.speicher_df, how="left")
            .drop(columns="kp")
            .drop(columns="merkmale")
        )

    def erstelleUebersichtList(self):
        i = 0
        uebersicht_list = self.aufgaben_list
        while i < len(uebersicht_list):
            uebersicht_list[i] += (
                " ("
                + self.speicher_df["Status"][i]
                + (
                    (" am " + self.speicher_df["Datum"][i])
                    if self.speicher_df["Datum"][i] != ""
                    else ""
                )
                + ")"
            )
            i += 1
        self.uebersicht_list = uebersicht_list

    def speichereAktuelleAufgabe(self, index):
        if index != -1:
            kp = self.aufgaben_df["kp"][index]
            kp_tree = ET.fromstring(kp)
            quanti_str = ""
            for tr in kp_tree[0]:
                quanti_str += "".join(tr[0].itertext()).strip()[0:8]
            self.aufgQuanti_str = quanti_str
            aktuelleQuantis_df = pd.DataFrame(columns=["Element", "Deine Anzahl", "ML"])
            for element in self.element_list:
                new_row = {
                    "Element": element,
                    "Deine Anzahl": 0,
                    "ML": quanti_str.count(element),
                }
                aktuelleQuantis_df = aktuelleQuantis_df.append(
                    new_row, ignore_index=True
                )
            self.aktuelleQuantis_df = aktuelleQuantis_df.sort_values(by="Element")
            aktuelleMerkmale_df = pd.DataFrame(
                columns=["Merkmal", "Kriterium", "erfüllt"]
            )
            for merkmal in self.aufgaben_df["merkmale"][index]:
                name = merkmal.attrib["name"]
                kriterium = merkmal.text
                new_row = {"Merkmal": name, "Kriterium": kriterium, "erfüllt": False}
                aktuelleMerkmale_df = aktuelleMerkmale_df.append(
                    new_row, ignore_index=True
                )
            self.aktuelleMerkmale_df = aktuelleMerkmale_df

    def ladeKPundAbgleichML(self, pfad, index):
        kp_stream = codecs.open(pfad, "rb", encoding="utf8", errors="ignore")
        kp_komplett = kp_stream.read()
        kp_sliced = kp_komplett.split("table", 2)[1].replace("&", " ")
        kp = f"<table{kp_sliced}table>"
        self.kp_pfad = pfad
        kp_tree = ET.fromstring(kp)
        quanti_str = ""
        quali_str = ""
        for tr in kp_tree:
            quanti_str += "".join(tr[0].itertext()).strip()[0:8]
            quali_str += "".join(tr.itertext()).strip()

        aktuelleQuantis_df = pd.DataFrame(columns=["Element", "Deine Anzahl", "ML"])
        for element in self.element_list:
            new_row = {
                "Element": element,
                "Deine Anzahl": quanti_str.count(element),
                "ML": self.aufgQuanti_str.count(element),
            }
            aktuelleQuantis_df = aktuelleQuantis_df.append(new_row, ignore_index=True)
        self.aktuelleQuantis_df = aktuelleQuantis_df.sort_values(by="Element")

        aktuelleMerkmale_df = pd.DataFrame(columns=["Merkmal", "Kriterium", "erfüllt"])
        for merkmal in self.aufgaben_df["merkmale"][index]:
            name = merkmal.attrib["name"]
            kriterium = merkmal.text
            new_row = {
                "Merkmal": name,
                "Kriterium": kriterium,
                "erfüllt": True if kriterium in quali_str else False,
            }
            aktuelleMerkmale_df = aktuelleMerkmale_df.append(new_row, ignore_index=True)
        self.aktuelleMerkmale_df = aktuelleMerkmale_df

        if "True" in str(aktuelleMerkmale_df["erfüllt"]):
            self.speichernAktiv = True
        else:
            self.speichernAktiv = False

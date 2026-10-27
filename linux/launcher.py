#!/usr/bin/env python3
# ============================================================
#  CSpect Launcher for Linux and macOS
#  Game launcher for the ZX Spectrum Next emulator CSpect
#
#  Copyright (c) 2026 Giuseppe Papa
#  https://github.com/Saxabar/CSpectLauncher
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details:
#  <https://www.gnu.org/licenses/gpl-3.0.html>
# ============================================================
#  Requirements: Python 3 with Tkinter (python3-tk), Mono (to run CSpect).
#  Optional: Pillow (python3-pil, python3-pil.imagetk) for JPG/BMP covers
#  and smoother picture scaling.
#  Settings are stored in games.ini, compatible with the Windows version.
# ============================================================

import datetime
import os
import re
import shlex
import shutil
import subprocess
import sys
import urllib.parse
import webbrowser

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    import tkinter.font as tkfont
except ImportError:
    sys.stderr.write("Tkinter is missing. Install it, e.g. on Ubuntu/Debian: sudo apt install python3-tk\n")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

# ---------- program information ----------
APP_NAME = 'CSpect Launcher'
APP_VERSION = '1.6'
APP_COPYRIGHT = '(c) 2026 Giuseppe Papa - GPL-3.0'
APP_URL = 'https://github.com/Saxabar/CSpectLauncher'
CSPECT_URL = 'https://mdf200.itch.io/cspect'

IS_WIN = (os.name == 'nt')
IS_MAC = (sys.platform == 'darwin')
# where Mono is installed on macOS (not always in PATH when started from the Finder)
MAC_MONO = ('/Library/Frameworks/Mono.framework/Versions/Current/Commands/mono',
            '/opt/homebrew/bin/mono', '/usr/local/bin/mono')
ROOT = os.path.dirname(os.path.abspath(__file__))
INI_PATH = os.path.join(ROOT, 'games.ini')
GAME_EXTS = ('.nex', '.snx', '.sna')
OS_EXTS = ('.bas', '.tap', '.z3', '.z4', '.z5', '.z7', '.z8')   # started with NextZXOS (when there is no .nex/.snx/.sna)
Z_EXTS = ('.z3', '.z4', '.z5', '.z7', '.z8')    # Z-machine text adventures, played with ZXZVM
OS_NEX_EXTS = ('.nex', '.snx', '.sna')          # can also be started with NextZXOS (boot=nextzxos)
OS_DIRS = ('NEXTZXOS', 'SYS', 'DOT', 'MACHINES')
OS_OPT_DIRS = ('GAMES/Z-Machine/ZXZVM',)        # optional: copied when the SD card image has it
# NextZXOS system files and SD card images created on the fly
OS_WORK = (os.path.join(os.environ.get('TEMP', ''), 'CSpectLauncher') if IS_WIN else
           os.path.join(os.environ.get('XDG_CACHE_HOME') or os.path.expanduser('~/.cache'), 'cspect-launcher'))
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
DEFAULT_ARGS = '-w2 -vsync -zxnext -mmc=./'
# CSpect names screenshots <name>_<year>_<month>_<day>___<hour>_<min>_<sec>, without leading zeros
SHOT_RE = re.compile(r'_\d{4}_\d{1,2}_\d{1,2}___\d{1,2}_\d{1,2}_\d{1,2}$')

# colours and fonts (same look as the Windows version)
C_BACK = '#18181c'
C_PANEL = '#24242a'
C_TEXT = '#e6e6e6'
C_DIM = '#9696a0'
C_GOLD = '#ffc800'
C_LINK = '#00c8d7'
C_PLAY = '#00963c'
C_PLAY_ACTIVE = '#00b048'
STAR_FULL = '★'
STAR_EMPTY = '☆'
HEART = '♥'

LANG_NAMES = [('en', 'English'), ('it', 'Italiano'), ('es', 'Español'), ('fr', 'Français'), ('de', 'Deutsch')]

# ============================================================
#  Translations (same texts as the Windows version)
# ============================================================
STRINGS = {
    "en": {
        "argsMenu": "Launch parameters...",
        "renameMenu": "Rename title...",
        "argsTitle": "Launch parameters - {0}",
        "argsLbl": "Custom CSpect parameters for this game.\nLeave empty to use the general ones:\n{0}",
        "renameTitle": "Rename - {0}",
        "renameLbl": "Title shown in the list.\nLeave empty to use the folder name:\n{0}",
        "setArgs": "Other parameters:",
        "setWinSize": "Window size:",
        "setFullscreen": "Full screen",
        "dlCSpect": "Download CSpect",
        "customTag": "(custom)",
        "hideMenu": "Hide game",
        "unhideMenu": "Show game again",
        "showHiddenMenu": "Show hidden games",
        "hiddenTag": "(hidden)",
        "delSavMenu": "Delete save files (.sav)...",
        "openFolderMenu": "Open game folder",
        "chooseAlways": "Always use this executable",
        "askTag": "(asked at every launch)",
        "osMenu": "Start with NextZXOS",
        "osSaved": "Saved files copied to the game folder: {0}",
        "favAdd": "Add to favorites",
        "favRemove": "Remove from favorites",
        "tap48Menu": "Load in 48K mode",
        "compatMenu": "CSpect 3 compatibility",
        "compatL2": "Layer 2 at bank 9",
        "compatDiv": "DivMMC automap off",
        "compatDd01": "DD 01 breakpoints as NOP",
        "compatZero": "RAM cleared at start",
        "favTip": "Show only favorite games",
        "delSavConfirm": "Delete {0} save file(s) of {1}?\n\n{2}\n\nThe files are moved to the Trash.",
        "delSavDone": "Save files deleted: {0}",
        "delSavErr": "Cannot delete:\n{0}",
        "info": "Info",
        "aboutTitle": "About",
        "aboutVersion": "Version {0}",
        "aboutUpdates": "Updates and news:",
        "aboutEmu": "Emulator: CSpect by Mike Dailly",
        "search": "Search:",
        "sortLbl": "Sort:",
        "sortName": "Name",
        "sortRating": "Rating",
        "sortTip": "Sort the list by name or by rating",
        "play": "PLAY",
        "noRating": "no rating",
        "unplayable": "(not launchable)",
        "fileLine": "File: {0}\nParameters: {1}",
        "fileChoose": "File: to be chosen on first launch ({0} executables)\nParameters: {1}",
        "noFile": "No .nex/.snx/.sna/.bas/.tap/.z5 file - set it in games.ini",
        "status": "{0} of {1} games   -   Enter/double-click: play   Ctrl+1..5: rating   F5: reload   Esc: exit",
        "launched": "Launched: {0}",
        "launchErr": "Launch error:\n{0}",
        "chooseMenu": "Choose executable...",
        "chooseTitle": "Choose executable - {0}",
        "chooseLbl": "Which executable do you want to use?\n(the choice is saved in games.ini)",
        "ok": "OK",
        "cancel": "Cancel",
        "saveErr": "Cannot save to games.ini:\n{0}",
        "noExeMsg": "No .nex / .snx / .sna / .bas / .tap / .z5 file found in:\n{0}\n\nSet the file to launch in games.ini (file= key).",
        "osTag": "(with NextZXOS)",
        "osPrep": "Preparing NextZXOS for {0}...",
        "osNoImage": "SD card image with NextZXOS not found:\n{0}\n\nIt is needed to start .bas and .tap files (usually zxnext.sd in the CSpect folder, created by ZXOS.sh).\n\nDo you want to select it?",
        "osNoImageDl": "SD card image with NextZXOS not found:\n{0}\n\nIt is needed to start .bas and .tap files.\n\nYes: download it now with ZXOS.sh, included with CSpect. CSpect opens in full screen and asks whether to download the image (answer Yes, use Alt+Tab if you cannot see the question); when the NextZXOS menu appears, close it with Alt+F4 and the game starts.\nNo: select an image you already have.\nCancel: do nothing.",
        "osDlTitle": "Downloading NextZXOS",
        "osDlWait": "ZXOS.sh is preparing the SD card image with NextZXOS (zxnext.sd).\nCSpect first asks whether to download the image: answer Yes. If you cannot see the question, press Alt+Tab.\nCSpect may stay black for a while: please wait.",
        "osDlReady": "Image downloaded.\nWhen the NextZXOS menu appears, close CSpect with Alt+F4: the game will start.",
        "osDlFail": "The SD card image was not downloaded:\n{0}",
        "osDlTime": "Elapsed time: {0} s",
        "osPick": "Select the SD card image with NextZXOS",
        "osFilter": "SD card images",
        "osNoTool": "hdfmonkey not found:\n{0}\n\nIt is included with CSpect (hdfmonkey folder).",
        "osErr": "Cannot prepare NextZXOS:\n{0}",
        "osNoZvm": "ZXZVM, the Z-machine interpreter needed for .z3-.z8 text adventures, was not found in the SD card image:\n{0}\n\n(it is in C:/GAMES/Z-Machine/ZXZVM of the NextZXOS distribution)",
        "osBadImage": "NextZXOS was not found in the SD card image:\n{0}",
        "emuNotFound": "CSpect.exe not found in:\n{0}\n\nDo you want to select the CSpect folder?",
        "emuPick": "Select the folder containing CSpect.exe",
        "emuNotHere": "CSpect.exe is not in this folder.",
        "settings": "Settings",
        "setTitle": "Settings",
        "welcome": "Welcome! games.ini was not found: choose the language and the folders to start.",
        "setLang": "Language:",
        "setGames": "Games folder:",
        "setCSpect": "CSpect folder:",
        "gamesPick": "Select the folder containing the games (one subfolder per game)",
        "gamesMissing": "The games folder does not exist.",
        "monoMissing": "Mono is needed to run CSpect on Linux, but it was not found.\n\nInstall it, for example on Ubuntu/Debian:\nsudo apt install mono-devel",
        "monoMissingMac": "Mono is needed to run CSpect on macOS, but it was not found.\n\nInstall it from:\nhttps://www.mono-project.com/download/stable/"
    },
    "it": {
        "argsMenu": "Parametri di avvio...",
        "renameMenu": "Rinomina titolo...",
        "argsTitle": "Parametri di avvio - {0}",
        "argsLbl": "Parametri CSpect personalizzati per questo gioco.\nLascia vuoto per usare quelli generali:\n{0}",
        "renameTitle": "Rinomina - {0}",
        "renameLbl": "Titolo mostrato nella lista.\nLascia vuoto per usare il nome della cartella:\n{0}",
        "setArgs": "Altri parametri:",
        "setWinSize": "Grandezza finestra:",
        "setFullscreen": "Schermo intero",
        "dlCSpect": "Scarica CSpect",
        "customTag": "(personalizzati)",
        "hideMenu": "Nascondi gioco",
        "unhideMenu": "Mostra di nuovo il gioco",
        "showHiddenMenu": "Mostra giochi nascosti",
        "hiddenTag": "(nascosto)",
        "delSavMenu": "Elimina salvataggi (.sav)...",
        "openFolderMenu": "Apri cartella del gioco",
        "chooseAlways": "Usa sempre questo eseguibile",
        "askTag": "(chiesto a ogni avvio)",
        "osMenu": "Avvia con NextZXOS",
        "osSaved": "File salvati copiati nella cartella del gioco: {0}",
        "favAdd": "Aggiungi ai preferiti",
        "favRemove": "Togli dai preferiti",
        "tap48Menu": "Carica in modalità 48K",
        "compatMenu": "Compatibilità CSpect 3",
        "compatL2": "Layer 2 al banco 9",
        "compatDiv": "Mappatura automatica DivMMC spenta",
        "compatDd01": "Breakpoint DD 01 come NOP",
        "compatZero": "RAM azzerata all'avvio",
        "favTip": "Mostra solo i giochi preferiti",
        "delSavConfirm": "Eliminare {0} file di salvataggio di {1}?\n\n{2}\n\nI file vengono spostati nel Cestino.",
        "delSavDone": "Salvataggi eliminati: {0}",
        "delSavErr": "Impossibile eliminare:\n{0}",
        "info": "Info",
        "aboutTitle": "Informazioni",
        "aboutVersion": "Versione {0}",
        "aboutUpdates": "Aggiornamenti e novità:",
        "aboutEmu": "Emulatore: CSpect di Mike Dailly",
        "search": "Cerca:",
        "sortLbl": "Ordina:",
        "sortName": "Nome",
        "sortRating": "Voto",
        "sortTip": "Ordina la lista per nome o per voto",
        "play": "GIOCA",
        "noRating": "nessun voto",
        "unplayable": "(non avviabile)",
        "fileLine": "File: {0}\nParametri: {1}",
        "fileChoose": "File: da scegliere al primo avvio ({0} eseguibili)\nParametri: {1}",
        "noFile": "Nessun file .nex/.snx/.sna/.bas/.tap/.z5 - impostalo in games.ini",
        "status": "{0} di {1} giochi   -   Invio/doppio clic: gioca   Ctrl+1..5: voto   F5: ricarica   Esc: esci",
        "launched": "Avviato: {0}",
        "launchErr": "Errore nell'avvio:\n{0}",
        "chooseMenu": "Scegli eseguibile...",
        "chooseTitle": "Scegli l'eseguibile - {0}",
        "chooseLbl": "Quale eseguibile vuoi usare?\n(la scelta viene salvata in games.ini)",
        "ok": "OK",
        "cancel": "Annulla",
        "saveErr": "Impossibile salvare in games.ini:\n{0}",
        "noExeMsg": "Nessun file .nex / .snx / .sna / .bas / .tap / .z5 trovato in:\n{0}\n\nIndica il file da lanciare in games.ini (chiave file=).",
        "osTag": "(con NextZXOS)",
        "osPrep": "Preparazione di NextZXOS per {0}...",
        "osNoImage": "Immagine SD con NextZXOS non trovata:\n{0}\n\nServe per avviare i file .bas e .tap (di solito zxnext.sd nella cartella di CSpect, creata da ZXOS.sh).\n\nVuoi indicarla?",
        "osNoImageDl": "Immagine SD con NextZXOS non trovata:\n{0}\n\nServe per avviare i file .bas e .tap.\n\nSì: scaricala adesso con ZXOS.sh, incluso in CSpect. CSpect si apre a schermo intero e chiede se scaricare l'immagine (rispondi Sì, con Alt+Tab se non vedi la domanda); quando compare il menu di NextZXOS chiudilo con Alt+F4 e il gioco parte.\nNo: indica un'immagine che hai già.\nAnnulla: non fare nulla.",
        "osDlTitle": "Download di NextZXOS",
        "osDlWait": "ZXOS.sh sta preparando l'immagine SD con NextZXOS (zxnext.sd).\nCSpect chiede prima se scaricare l'immagine: rispondi Sì. Se non vedi la domanda, premi Alt+Tab.\nCSpect può restare nero per un po': attendi.",
        "osDlReady": "Immagine scaricata.\nQuando compare il menu di NextZXOS chiudi CSpect con Alt+F4: il gioco partirà.",
        "osDlFail": "L'immagine SD non è stata scaricata:\n{0}",
        "osDlTime": "Tempo trascorso: {0} s",
        "osPick": "Seleziona l'immagine SD con NextZXOS",
        "osFilter": "Immagini SD",
        "osNoTool": "hdfmonkey non trovato:\n{0}\n\nÈ incluso in CSpect (cartella hdfmonkey).",
        "osErr": "Impossibile preparare NextZXOS:\n{0}",
        "osNoZvm": "ZXZVM, l'interprete Z-machine necessario per le avventure testuali .z3-.z8, non è stato trovato nell'immagine SD:\n{0}\n\n(si trova in C:/GAMES/Z-Machine/ZXZVM della distribuzione di NextZXOS)",
        "osBadImage": "NextZXOS non è stato trovato nell'immagine SD:\n{0}",
        "emuNotFound": "CSpect.exe non trovato in:\n{0}\n\nVuoi indicare la cartella di CSpect?",
        "emuPick": "Seleziona la cartella che contiene CSpect.exe",
        "emuNotHere": "In questa cartella non c'è CSpect.exe.",
        "settings": "Impostazioni",
        "setTitle": "Impostazioni",
        "welcome": "Benvenuto! games.ini non è stato trovato: scegli la lingua e le cartelle per iniziare.",
        "setLang": "Lingua:",
        "setGames": "Cartella giochi:",
        "setCSpect": "Cartella CSpect:",
        "gamesPick": "Seleziona la cartella che contiene i giochi (una sottocartella per gioco)",
        "gamesMissing": "La cartella dei giochi non esiste.",
        "monoMissing": "Per avviare CSpect su Linux serve Mono, ma non è stato trovato.\n\nInstallalo, per esempio su Ubuntu/Debian:\nsudo apt install mono-devel",
        "monoMissingMac": "Per avviare CSpect su macOS serve Mono, ma non è stato trovato.\n\nInstallalo da:\nhttps://www.mono-project.com/download/stable/"
    },
    "es": {
        "argsMenu": "Parámetros de inicio...",
        "renameMenu": "Renombrar título...",
        "argsTitle": "Parámetros de inicio - {0}",
        "argsLbl": "Parámetros de CSpect personalizados para este juego.\nDéjalo vacío para usar los generales:\n{0}",
        "renameTitle": "Renombrar - {0}",
        "renameLbl": "Título mostrado en la lista.\nDéjalo vacío para usar el nombre de la carpeta:\n{0}",
        "setArgs": "Otros parámetros:",
        "setWinSize": "Tamaño de ventana:",
        "setFullscreen": "Pantalla completa",
        "dlCSpect": "Descargar CSpect",
        "customTag": "(personalizados)",
        "hideMenu": "Ocultar juego",
        "unhideMenu": "Volver a mostrar el juego",
        "showHiddenMenu": "Mostrar juegos ocultos",
        "hiddenTag": "(oculto)",
        "delSavMenu": "Borrar partidas guardadas (.sav)...",
        "openFolderMenu": "Abrir carpeta del juego",
        "chooseAlways": "Usar siempre este ejecutable",
        "askTag": "(se pregunta en cada inicio)",
        "osMenu": "Iniciar con NextZXOS",
        "osSaved": "Archivos guardados copiados en la carpeta del juego: {0}",
        "favAdd": "Añadir a favoritos",
        "favRemove": "Quitar de favoritos",
        "tap48Menu": "Cargar en modo 48K",
        "compatMenu": "Compatibilidad CSpect 3",
        "compatL2": "Layer 2 en el banco 9",
        "compatDiv": "Mapeo automático DivMMC desactivado",
        "compatDd01": "Breakpoints DD 01 como NOP",
        "compatZero": "RAM a cero al inicio",
        "favTip": "Mostrar solo los juegos favoritos",
        "delSavConfirm": "¿Borrar {0} archivo(s) de partida de {1}?\n\n{2}\n\nLos archivos se mueven a la Papelera.",
        "delSavDone": "Partidas borradas: {0}",
        "delSavErr": "No se puede borrar:\n{0}",
        "info": "Info",
        "aboutTitle": "Acerca de",
        "aboutVersion": "Versión {0}",
        "aboutUpdates": "Actualizaciones y novedades:",
        "aboutEmu": "Emulador: CSpect de Mike Dailly",
        "search": "Buscar:",
        "sortLbl": "Ordenar:",
        "sortName": "Nombre",
        "sortRating": "Nota",
        "sortTip": "Ordenar la lista por nombre o por nota",
        "play": "JUGAR",
        "noRating": "sin nota",
        "unplayable": "(no ejecutable)",
        "fileLine": "Archivo: {0}\nParámetros: {1}",
        "fileChoose": "Archivo: a elegir en el primer inicio ({0} ejecutables)\nParámetros: {1}",
        "noFile": "Ningún archivo .nex/.snx/.sna/.bas/.tap/.z5 - indícalo en games.ini",
        "status": "{0} de {1} juegos   -   Intro/doble clic: jugar   Ctrl+1..5: nota   F5: recargar   Esc: salir",
        "launched": "Iniciado: {0}",
        "launchErr": "Error al iniciar:\n{0}",
        "chooseMenu": "Elegir ejecutable...",
        "chooseTitle": "Elegir ejecutable - {0}",
        "chooseLbl": "¿Qué ejecutable quieres usar?\n(la elección se guarda en games.ini)",
        "ok": "Aceptar",
        "cancel": "Cancelar",
        "saveErr": "No se puede guardar en games.ini:\n{0}",
        "noExeMsg": "No se encontró ningún archivo .nex / .snx / .sna / .bas / .tap / .z5 en:\n{0}\n\nIndica el archivo a ejecutar en games.ini (clave file=).",
        "osTag": "(con NextZXOS)",
        "osPrep": "Preparando NextZXOS para {0}...",
        "osNoImage": "No se encontró la imagen SD con NextZXOS:\n{0}\n\nEs necesaria para iniciar archivos .bas y .tap (normalmente zxnext.sd en la carpeta de CSpect, creada por ZXOS.sh).\n\n¿Quieres indicarla?",
        "osNoImageDl": "No se encontró la imagen SD con NextZXOS:\n{0}\n\nEs necesaria para iniciar archivos .bas y .tap.\n\nSí: descárgala ahora con ZXOS.sh, incluido con CSpect. CSpect se abre en pantalla completa y pregunta si quieres descargar la imagen (responde Sí, con Alt+Tab si no ves la pregunta); cuando aparezca el menú de NextZXOS, ciérralo con Alt+F4 y el juego se inicia.\nNo: indica una imagen que ya tengas.\nCancelar: no hacer nada.",
        "osDlTitle": "Descarga de NextZXOS",
        "osDlWait": "ZXOS.sh está preparando la imagen SD con NextZXOS (zxnext.sd).\nCSpect pregunta primero si quieres descargar la imagen: responde Sí. Si no ves la pregunta, pulsa Alt+Tab.\nCSpect puede quedarse en negro un rato: espera.",
        "osDlReady": "Imagen descargada.\nCuando aparezca el menú de NextZXOS, cierra CSpect con Alt+F4: el juego se iniciará.",
        "osDlFail": "No se descargó la imagen SD:\n{0}",
        "osDlTime": "Tiempo transcurrido: {0} s",
        "osPick": "Selecciona la imagen SD con NextZXOS",
        "osFilter": "Imágenes SD",
        "osNoTool": "No se encontró hdfmonkey:\n{0}\n\nSe incluye con CSpect (carpeta hdfmonkey).",
        "osErr": "No se puede preparar NextZXOS:\n{0}",
        "osNoZvm": "No se encontró ZXZVM, el intérprete Z-machine necesario para las aventuras de texto .z3-.z8, en la imagen SD:\n{0}\n\n(está en C:/GAMES/Z-Machine/ZXZVM de la distribución de NextZXOS)",
        "osBadImage": "No se encontró NextZXOS en la imagen SD:\n{0}",
        "emuNotFound": "No se encontró CSpect.exe en:\n{0}\n\n¿Quieres indicar la carpeta de CSpect?",
        "emuPick": "Selecciona la carpeta que contiene CSpect.exe",
        "emuNotHere": "CSpect.exe no está en esta carpeta.",
        "settings": "Ajustes",
        "setTitle": "Ajustes",
        "welcome": "¡Bienvenido! No se encontró games.ini: elige el idioma y las carpetas para empezar.",
        "setLang": "Idioma:",
        "setGames": "Carpeta de juegos:",
        "setCSpect": "Carpeta de CSpect:",
        "gamesPick": "Selecciona la carpeta que contiene los juegos (una subcarpeta por juego)",
        "gamesMissing": "La carpeta de juegos no existe.",
        "monoMissing": "Para ejecutar CSpect en Linux se necesita Mono, pero no se encontró.\n\nInstálalo, por ejemplo en Ubuntu/Debian:\nsudo apt install mono-devel",
        "monoMissingMac": "Para ejecutar CSpect en macOS se necesita Mono, pero no se encontró.\n\nInstálalo desde:\nhttps://www.mono-project.com/download/stable/"
    },
    "fr": {
        "argsMenu": "Paramètres de lancement...",
        "renameMenu": "Renommer le titre...",
        "argsTitle": "Paramètres de lancement - {0}",
        "argsLbl": "Paramètres CSpect personnalisés pour ce jeu.\nLaissez vide pour utiliser les paramètres généraux :\n{0}",
        "renameTitle": "Renommer - {0}",
        "renameLbl": "Titre affiché dans la liste.\nLaissez vide pour utiliser le nom du dossier :\n{0}",
        "setArgs": "Autres paramètres :",
        "setWinSize": "Taille de la fenêtre :",
        "setFullscreen": "Plein écran",
        "dlCSpect": "Télécharger CSpect",
        "customTag": "(personnalisés)",
        "hideMenu": "Masquer le jeu",
        "unhideMenu": "Afficher à nouveau le jeu",
        "showHiddenMenu": "Afficher les jeux masqués",
        "hiddenTag": "(masqué)",
        "delSavMenu": "Supprimer les sauvegardes (.sav)...",
        "openFolderMenu": "Ouvrir le dossier du jeu",
        "chooseAlways": "Toujours utiliser cet exécutable",
        "askTag": "(demandé à chaque lancement)",
        "osMenu": "Lancer avec NextZXOS",
        "osSaved": "Fichiers sauvegardés copiés dans le dossier du jeu : {0}",
        "favAdd": "Ajouter aux favoris",
        "favRemove": "Retirer des favoris",
        "tap48Menu": "Charger en mode 48K",
        "compatMenu": "Compatibilité CSpect 3",
        "compatL2": "Layer 2 à la banque 9",
        "compatDiv": "Mappage automatique DivMMC désactivé",
        "compatDd01": "Points d'arrêt DD 01 en NOP",
        "compatZero": "RAM remise à zéro au démarrage",
        "favTip": "Afficher seulement les jeux favoris",
        "delSavConfirm": "Supprimer {0} fichier(s) de sauvegarde de {1} ?\n\n{2}\n\nLes fichiers sont placés dans la Corbeille.",
        "delSavDone": "Sauvegardes supprimées : {0}",
        "delSavErr": "Impossible de supprimer :\n{0}",
        "info": "Infos",
        "aboutTitle": "À propos",
        "aboutVersion": "Version {0}",
        "aboutUpdates": "Mises à jour et nouveautés :",
        "aboutEmu": "Émulateur : CSpect de Mike Dailly",
        "search": "Rechercher :",
        "sortLbl": "Trier :",
        "sortName": "Nom",
        "sortRating": "Note",
        "sortTip": "Trier la liste par nom ou par note",
        "play": "JOUER",
        "noRating": "pas de note",
        "unplayable": "(non lançable)",
        "fileLine": "Fichier : {0}\nParamètres : {1}",
        "fileChoose": "Fichier : à choisir au premier lancement ({0} exécutables)\nParamètres : {1}",
        "noFile": "Aucun fichier .nex/.snx/.sna/.bas/.tap/.z5 - indiquez-le dans games.ini",
        "status": "{0} sur {1} jeux   -   Entrée/double-clic : jouer   Ctrl+1..5 : note   F5 : recharger   Échap : quitter",
        "launched": "Lancé : {0}",
        "launchErr": "Erreur au lancement :\n{0}",
        "chooseMenu": "Choisir l'exécutable...",
        "chooseTitle": "Choisir l'exécutable - {0}",
        "chooseLbl": "Quel exécutable voulez-vous utiliser ?\n(le choix est enregistré dans games.ini)",
        "ok": "OK",
        "cancel": "Annuler",
        "saveErr": "Impossible d'enregistrer dans games.ini :\n{0}",
        "noExeMsg": "Aucun fichier .nex / .snx / .sna / .bas / .tap / .z5 trouvé dans :\n{0}\n\nIndiquez le fichier à lancer dans games.ini (clé file=).",
        "osTag": "(avec NextZXOS)",
        "osPrep": "Préparation de NextZXOS pour {0}...",
        "osNoImage": "Image de carte SD avec NextZXOS introuvable :\n{0}\n\nElle est nécessaire pour lancer les fichiers .bas et .tap (en général zxnext.sd dans le dossier de CSpect, créée par ZXOS.sh).\n\nVoulez-vous l'indiquer ?",
        "osNoImageDl": "Image de carte SD avec NextZXOS introuvable :\n{0}\n\nElle est nécessaire pour lancer les fichiers .bas et .tap.\n\nOui : la télécharger maintenant avec ZXOS.sh, fourni avec CSpect. CSpect s'ouvre en plein écran et demande s'il faut télécharger l'image (répondez Oui, avec Alt+Tab si vous ne voyez pas la question) ; quand le menu de NextZXOS apparaît, fermez-le avec Alt+F4 et le jeu démarre.\nNon : indiquer une image que vous avez déjà.\nAnnuler : ne rien faire.",
        "osDlTitle": "Téléchargement de NextZXOS",
        "osDlWait": "ZXOS.sh prépare l'image de carte SD avec NextZXOS (zxnext.sd).\nCSpect demande d'abord s'il faut télécharger l'image : répondez Oui. Si vous ne voyez pas la question, appuyez sur Alt+Tab.\nCSpect peut rester noir un moment : patientez.",
        "osDlReady": "Image téléchargée.\nQuand le menu de NextZXOS apparaît, fermez CSpect avec Alt+F4 : le jeu démarrera.",
        "osDlFail": "L'image de carte SD n'a pas été téléchargée :\n{0}",
        "osDlTime": "Temps écoulé : {0} s",
        "osPick": "Sélectionnez l'image de carte SD avec NextZXOS",
        "osFilter": "Images de carte SD",
        "osNoTool": "hdfmonkey introuvable :\n{0}\n\nIl est fourni avec CSpect (dossier hdfmonkey).",
        "osErr": "Impossible de préparer NextZXOS :\n{0}",
        "osNoZvm": "ZXZVM, l'interpréteur Z-machine nécessaire pour les aventures textuelles .z3-.z8, est introuvable dans l'image de carte SD :\n{0}\n\n(il se trouve dans C:/GAMES/Z-Machine/ZXZVM de la distribution NextZXOS)",
        "osBadImage": "NextZXOS est introuvable dans l'image de carte SD :\n{0}",
        "emuNotFound": "CSpect.exe introuvable dans :\n{0}\n\nVoulez-vous indiquer le dossier de CSpect ?",
        "emuPick": "Sélectionnez le dossier contenant CSpect.exe",
        "emuNotHere": "CSpect.exe n'est pas dans ce dossier.",
        "settings": "Paramètres",
        "setTitle": "Paramètres",
        "welcome": "Bienvenue ! games.ini est introuvable : choisissez la langue et les dossiers pour commencer.",
        "setLang": "Langue :",
        "setGames": "Dossier des jeux :",
        "setCSpect": "Dossier de CSpect :",
        "gamesPick": "Sélectionnez le dossier contenant les jeux (un sous-dossier par jeu)",
        "gamesMissing": "Le dossier des jeux n'existe pas.",
        "monoMissing": "Mono est nécessaire pour lancer CSpect sous Linux, mais il est introuvable.\n\nInstallez-le, par exemple sous Ubuntu/Debian :\nsudo apt install mono-devel",
        "monoMissingMac": "Mono est nécessaire pour lancer CSpect sous macOS, mais il est introuvable.\n\nInstallez-le depuis :\nhttps://www.mono-project.com/download/stable/"
    },
    "de": {
        "argsMenu": "Startparameter...",
        "renameMenu": "Titel umbenennen...",
        "argsTitle": "Startparameter - {0}",
        "argsLbl": "Eigene CSpect-Parameter für dieses Spiel.\nLeer lassen, um die allgemeinen zu verwenden:\n{0}",
        "renameTitle": "Umbenennen - {0}",
        "renameLbl": "In der Liste angezeigter Titel.\nLeer lassen, um den Ordnernamen zu verwenden:\n{0}",
        "setArgs": "Weitere Parameter:",
        "setWinSize": "Fenstergröße:",
        "setFullscreen": "Vollbild",
        "dlCSpect": "CSpect herunterladen",
        "customTag": "(eigene)",
        "hideMenu": "Spiel ausblenden",
        "unhideMenu": "Spiel wieder anzeigen",
        "showHiddenMenu": "Ausgeblendete Spiele anzeigen",
        "hiddenTag": "(ausgeblendet)",
        "delSavMenu": "Spielstände löschen (.sav)...",
        "openFolderMenu": "Spielordner öffnen",
        "chooseAlways": "Dieses Programm immer verwenden",
        "askTag": "(wird bei jedem Start gefragt)",
        "osMenu": "Mit NextZXOS starten",
        "osSaved": "Gespeicherte Dateien in den Spielordner kopiert: {0}",
        "favAdd": "Zu Favoriten hinzufügen",
        "favRemove": "Aus Favoriten entfernen",
        "tap48Menu": "Im 48K-Modus laden",
        "compatMenu": "CSpect-3-Kompatibilität",
        "compatL2": "Layer 2 auf Bank 9",
        "compatDiv": "Automatisches DivMMC-Mapping aus",
        "compatDd01": "DD-01-Haltepunkte als NOP",
        "compatZero": "RAM beim Start gelöscht",
        "favTip": "Nur Lieblingsspiele anzeigen",
        "delSavConfirm": "{0} Spielstand-Datei(en) von {1} löschen?\n\n{2}\n\nDie Dateien werden in den Papierkorb verschoben.",
        "delSavDone": "Spielstände gelöscht: {0}",
        "delSavErr": "Löschen nicht möglich:\n{0}",
        "info": "Info",
        "aboutTitle": "Über",
        "aboutVersion": "Version {0}",
        "aboutUpdates": "Updates und Neuigkeiten:",
        "aboutEmu": "Emulator: CSpect von Mike Dailly",
        "search": "Suchen:",
        "sortLbl": "Sortieren:",
        "sortName": "Name",
        "sortRating": "Wertung",
        "sortTip": "Liste nach Name oder Wertung sortieren",
        "play": "SPIELEN",
        "noRating": "keine Wertung",
        "unplayable": "(nicht startbar)",
        "fileLine": "Datei: {0}\nParameter: {1}",
        "fileChoose": "Datei: wird beim ersten Start gewählt ({0} Programme)\nParameter: {1}",
        "noFile": "Keine .nex/.snx/.sna/.bas/.tap/.z5-Datei - in games.ini festlegen",
        "status": "{0} von {1} Spielen   -   Enter/Doppelklick: spielen   Strg+1..5: Wertung   F5: neu laden   Esc: beenden",
        "launched": "Gestartet: {0}",
        "launchErr": "Fehler beim Start:\n{0}",
        "chooseMenu": "Programm wählen...",
        "chooseTitle": "Programm wählen - {0}",
        "chooseLbl": "Welches Programm möchtest du verwenden?\n(die Auswahl wird in games.ini gespeichert)",
        "ok": "OK",
        "cancel": "Abbrechen",
        "saveErr": "Speichern in games.ini nicht möglich:\n{0}",
        "noExeMsg": "Keine .nex / .snx / .sna / .bas / .tap / .z5-Datei gefunden in:\n{0}\n\nLege die zu startende Datei in games.ini fest (Schlüssel file=).",
        "osTag": "(mit NextZXOS)",
        "osPrep": "NextZXOS wird für {0} vorbereitet...",
        "osNoImage": "SD-Karten-Image mit NextZXOS nicht gefunden:\n{0}\n\nEs wird zum Starten von .bas- und .tap-Dateien benötigt (meist zxnext.sd im CSpect-Ordner, erstellt von ZXOS.sh).\n\nMöchtest du es auswählen?",
        "osNoImageDl": "SD-Karten-Image mit NextZXOS nicht gefunden:\n{0}\n\nEs wird zum Starten von .bas- und .tap-Dateien benötigt.\n\nJa: jetzt mit ZXOS.sh herunterladen (bei CSpect dabei). CSpect öffnet sich im Vollbild und fragt, ob das Image heruntergeladen werden soll (mit Ja antworten, Alt+Tab falls die Frage nicht zu sehen ist); wenn das NextZXOS-Menü erscheint, mit Alt+F4 schließen, dann startet das Spiel.\nNein: ein vorhandenes Image auswählen.\nAbbrechen: nichts tun.",
        "osDlTitle": "NextZXOS wird heruntergeladen",
        "osDlWait": "ZXOS.sh bereitet das SD-Karten-Image mit NextZXOS vor (zxnext.sd).\nCSpect fragt zuerst, ob das Image heruntergeladen werden soll: mit Ja antworten. Wenn die Frage nicht zu sehen ist, Alt+Tab drücken.\nCSpect kann eine Weile schwarz bleiben: bitte warten.",
        "osDlReady": "Image heruntergeladen.\nWenn das NextZXOS-Menü erscheint, CSpect mit Alt+F4 schließen: das Spiel startet dann.",
        "osDlFail": "Das SD-Karten-Image wurde nicht heruntergeladen:\n{0}",
        "osDlTime": "Vergangene Zeit: {0} s",
        "osPick": "Wähle das SD-Karten-Image mit NextZXOS",
        "osFilter": "SD-Karten-Images",
        "osNoTool": "hdfmonkey nicht gefunden:\n{0}\n\nEs ist bei CSpect dabei (Ordner hdfmonkey).",
        "osErr": "NextZXOS kann nicht vorbereitet werden:\n{0}",
        "osNoZvm": "ZXZVM, der Z-Machine-Interpreter für die Textadventures .z3-.z8, wurde im SD-Karten-Image nicht gefunden:\n{0}\n\n(er liegt in C:/GAMES/Z-Machine/ZXZVM der NextZXOS-Distribution)",
        "osBadImage": "NextZXOS wurde im SD-Karten-Image nicht gefunden:\n{0}",
        "emuNotFound": "CSpect.exe nicht gefunden in:\n{0}\n\nMöchtest du den CSpect-Ordner auswählen?",
        "emuPick": "Wähle den Ordner mit CSpect.exe",
        "emuNotHere": "CSpect.exe befindet sich nicht in diesem Ordner.",
        "settings": "Einstellungen",
        "setTitle": "Einstellungen",
        "welcome": "Willkommen! games.ini wurde nicht gefunden: wähle Sprache und Ordner, um zu beginnen.",
        "setLang": "Sprache:",
        "setGames": "Spieleordner:",
        "setCSpect": "CSpect-Ordner:",
        "gamesPick": "Wähle den Ordner mit den Spielen (ein Unterordner pro Spiel)",
        "gamesMissing": "Der Spieleordner existiert nicht.",
        "monoMissing": "Zum Starten von CSpect unter Linux wird Mono benötigt, wurde aber nicht gefunden.\n\nInstalliere es, z. B. unter Ubuntu/Debian:\nsudo apt install mono-devel",
        "monoMissingMac": "Zum Starten von CSpect unter macOS wird Mono benötigt, wurde aber nicht gefunden.\n\nInstalliere es von:\nhttps://www.mono-project.com/download/stable/"
    }
}


class Settings:
    games_dir = os.path.join(ROOT, 'GAMES')
    emulator = os.path.join(ROOT, 'CSpect', 'CSpect.exe')
    global_args = DEFAULT_ARGS
    sd_image_cfg = ''       # nextzxos= (empty = zxnext.sd in the CSpect folder)
    lang = 'en'
    sort_mode = 'name'
    list_width = 368
    win_size = None         # window= (width, height) saved on exit
    win_max = False         # maximized=1
    last_game = ''          # lastgame= section of the last game started
    fav_only = False        # favonly=1 show only the favorite games
    show_hidden = None      # showhidden=1 also show the hidden games (read once at startup, saved on exit)


S = Settings()


def T(key, *args):
    s = STRINGS.get(S.lang, {}).get(key) or STRINGS['en'].get(key) or key
    if args:
        s = re.sub(r'\{(\d+)\}', lambda m: str(args[int(m.group(1))]) if int(m.group(1)) < len(args) else m.group(0), s)
    return s


# ============================================================
#  games.ini (same format as the Windows version: UTF-8 with BOM, CRLF)
# ============================================================
def read_ini():
    ini = {}
    sec = None
    if not os.path.isfile(INI_PATH):
        return ini
    with open(INI_PATH, encoding='utf-8-sig') as f:
        for line in f:
            l = line.strip()
            if not l or l.startswith(';') or l.startswith('#'):
                continue
            m = re.match(r'^\[(.+)\]$', l)
            if m:
                sec = m.group(1).strip()
                ini[sec] = {}
                continue
            m = re.match(r'^([^=]+)=(.*)$', l)
            if sec is not None and m:
                ini[sec][m.group(1).strip().lower()] = m.group(2).strip()
    return ini


def ini_section(ini, name):
    """Section lookup: exact name first, then case-insensitive (Windows compatibility)."""
    if name in ini:
        return ini[name]
    low = name.lower()
    for k, v in ini.items():
        if k.lower() == low:
            return v
    return None


def _read_lines():
    if not os.path.isfile(INI_PATH):
        return []
    with open(INI_PATH, encoding='utf-8-sig') as f:
        return f.read().splitlines()


def _write_lines(lines):
    with open(INI_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('\r\n'.join(lines) + '\r\n')


def set_ini_value(section, key, value):
    """Writes one value, keeping the rest of the file."""
    lines = _read_lines()
    start = -1
    for i, l in enumerate(lines):
        if l.strip().lower() == '[' + section.lower() + ']':
            start = i
            break
    if start < 0:
        lines += ['', '[' + section + ']', key + '=' + value]
    else:
        end = len(lines)
        for i in range(start + 1, len(lines)):
            if re.match(r'^\[.+\]$', lines[i].strip()):
                end = i
                break
        done = False
        for i in range(start + 1, end):
            if re.match(r'^\s*' + re.escape(key) + r'\s*=', lines[i], re.I):
                lines[i] = key + '=' + value
                done = True
                break
        if not done:
            lines.insert(start + 1, key + '=' + value)
    _write_lines(lines)


def new_ini_file(lang, games, cspect, gargs):
    lines = [
        '; ============================================================',
        ';  CSpect Launcher settings',
        '; ============================================================',
        ';  games=          games folder (one subfolder per game),',
        ';                  absolute or relative to this folder (./GAMES)',
        ';  cspect=         CSpect folder (or path of CSpect.exe), absolute or relative',
        ';  lang=           language: en, it, es, fr, de',
        ';  args=           CSpect parameters for all games',
        ';  sort=           list order: name or rating',
        ';  listwidth=      list width in pixels (also by dragging the divider)',
        ';  window=         window size (WxH) and maximized=1, saved on exit',
        ';  lastgame=       last game started, selected when the launcher opens',
        ';  favonly=1       show only the favorite games (heart button)',
        ';  showhidden=1    also show the hidden games (right-click menu), saved on exit',
        ';  nextzxos=       SD card image with NextZXOS, used for .bas/.tap games',
        ';                  (default: zxnext.sd in the CSpect folder)',
        ';',
        ';  Per game: file= (executable), rating=1..5, hidden=1 (hidden game),',
        ';  favorite=1, askfile=1 (always ask which executable), boot=nextzxos (start a .nex/.snx/.sna',
        ';  with NextZXOS), tapmode=48 (load a .tap in 48K mode),',
        ';  compat=l2bank9,nodivmmc,dd01nop,zeroram (fixes of the CSpect Compat plugin for old games in CSpect 3),',
        ';  title= image= args= optional',
        '; ============================================================',
        '',
        '[_default]',
        'lang=' + lang,
        'games=' + games,
        'cspect=' + cspect,
        'args=' + (gargs or DEFAULT_ARGS),
        'sort=name',
        'listwidth=368',
        '',
    ]
    _write_lines(lines[:-1])


def remove_orphan_sections(existing):
    """Removes the sections of games whose folder no longer exists (backup in games.ini.bak)."""
    if not os.path.isfile(INI_PATH) or not existing:
        return
    names = {n.lower() for n in existing} | {'_default'}
    out, skip, removed = [], False, 0
    for l in _read_lines():
        m = re.match(r'^\[(.+)\]$', l.strip())
        if m:
            skip = m.group(1).strip().lower() not in names
            if skip:
                removed += 1
                while out and not out[-1].strip():
                    out.pop()
                if out:
                    out.append('')
                continue
        if not skip:
            out.append(l)
    if removed:
        try:
            shutil.copy2(INI_PATH, INI_PATH + '.bak')
        except OSError:
            pass
        while out and not out[-1].strip():
            out.pop()
        _write_lines(out)


# ============================================================
#  Paths
# ============================================================
def norm(p):
    """Accepts paths written on Windows (.\\GAMES) as well."""
    p = (p or '').strip().strip('"')
    if not IS_WIN:
        p = p.replace('\\', '/')
    return p


def resolve_dir(value, default):
    p = norm(value) or default
    if not os.path.isabs(p):
        p = os.path.join(ROOT, p)
    return os.path.normpath(p)


def find_case_insensitive(folder, name):
    """On Linux file names are case sensitive: finds CSpect.exe / cspect.exe..."""
    p = os.path.join(folder, name)
    if os.path.exists(p) or IS_WIN:
        return p
    try:
        for f in os.listdir(folder):
            if f.lower() == name.lower():
                return os.path.join(folder, f)
    except OSError:
        pass
    return p


def resolve_emulator(value):
    p = norm(value) or 'CSpect'
    if not os.path.isabs(p):
        p = os.path.join(ROOT, p)
    p = os.path.normpath(p)
    if not p.lower().endswith('.exe'):
        p = find_case_insensitive(p, 'CSpect.exe')
    return p


def to_ini_path(path):
    """Paths inside the launcher folder are saved as relative (./...)."""
    p = os.path.normpath(path)
    r = os.path.normpath(ROOT)
    if p == r:
        return '.'
    if p.startswith(r + os.sep):
        return './' + os.path.relpath(p, r).replace(os.sep, '/')
    return p


def load_settings():
    ini = read_ini()
    s = ini.get('_default') or ini_section(ini, '_default') or {}
    S.global_args = s.get('args') or DEFAULT_ARGS
    S.games_dir = resolve_dir(s.get('games'), 'GAMES')
    S.emulator = resolve_emulator(s.get('cspect'))
    S.sd_image_cfg = s.get('nextzxos') or ''
    l =(s.get('lang') or '').strip().lower()
    S.lang = l if l in STRINGS else 'en'
    S.sort_mode = 'rating' if (s.get('sort') or '').strip().lower() in ('voto', 'rating') else 'name'
    m = re.match(r'^\s*(\d+)\s*$', s.get('listwidth') or '')
    if m:
        S.list_width = max(200, min(1200, int(m.group(1))))
    m = re.match(r'^\s*(\d+)\s*x\s*(\d+)\s*$', s.get('window') or '')
    S.win_size = (int(m.group(1)), int(m.group(2))) if m else None
    S.win_max = bool(re.match(r'^\s*(1|yes|true)\s*$', s.get('maximized') or '', re.I))
    S.last_game = (s.get('lastgame') or '').strip()
    S.fav_only = bool(re.match(r'^\s*(1|yes|true)\s*$', s.get('favonly') or '', re.I))
    # read only at startup: it is saved on exit, so later reloads must not undo the menu choice
    if S.show_hidden is None:
        S.show_hidden = bool(re.match(r'^\s*(1|yes|true)\s*$', s.get('showhidden') or '', re.I))
    return ini


# ============================================================
#  Games
# ============================================================
class Game:
    pass


def test_plus3_program(path):
    """NextBASIC program saved without extension (e.g. Vice City Blues): +3DOS header of type 0 (program)."""
    if os.path.splitext(path)[1]:
        return False
    try:
        with open(path, 'rb') as f:
            h = f.read(16)
    except OSError:
        return False
    return len(h) == 16 and h[:8] == b'PLUS3DOS' and h[15] == 0


def get_candidates(folder):
    """Executables in the game folder and its subfolders (relative paths, main folder first);
    .bas/.tap files and BASIC programs without extension (started with NextZXOS) only when there is
    no .nex/.snx/.sna. A file named like the folder comes first (e.g. ViceCityBlues before Day1...)"""
    found = []
    for dirpath, dirnames, files in os.walk(folder):
        for f in files:
            found.append(os.path.relpath(os.path.join(dirpath, f), folder).replace(os.sep, '/'))
    folder_key = re.sub(r'[^A-Za-z0-9]', '', os.path.basename(os.path.normpath(folder))).lower()
    for exts in (GAME_EXTS, OS_EXTS):
        res = [r for r in found if os.path.splitext(r)[1].lower() in exts or
               (exts is OS_EXTS and test_plus3_program(os.path.join(folder, r)))]
        if res:
            res.sort(key=lambda r: (r.count('/'),
                                    re.sub(r'[^A-Za-z0-9]', '', os.path.splitext(os.path.basename(r))[0]).lower() != folder_key,
                                    r.lower()))
            return res
    return []


def list_images(folder):
    try:
        return sorted([e for e in os.scandir(folder) if e.is_file() and os.path.splitext(e.name)[1].lower() in IMAGE_EXTS],
                      key=lambda e: e.name.lower())
    except OSError:
        return []


def find_image(folder, image_cfg, game_file):
    """Priority: image= > latest CSpect F5 screenshot of the game (<executable name>*.png, or
    screenshot_<date>.png for .bas/.tap games started with NextZXOS) > cover/copertina.*
    > latest other CSpect screenshot > screen*/title* > first picture in the folder"""
    if image_cfg:
        p = os.path.join(folder, norm(image_cfg))
        if os.path.isfile(p):
            return p
    imgs = list_images(folder)
    shots = imgs
    if game_file:
        exe_dir = os.path.dirname(game_file)
        if os.path.normpath(exe_dir) != os.path.normpath(folder):
            shots = list_images(exe_dir)
    if not imgs and not shots:
        return None

    def stem(e):
        return os.path.splitext(e.name)[0]

    def newest(entries):
        entries = list(entries)
        return max(entries, key=lambda e: e.stat().st_mtime) if entries else None

    c = None
    if game_file:
        base = os.path.splitext(os.path.basename(game_file))[0].lower()
        c = newest(e for e in shots if e.name.lower().endswith('.png') and
                   (stem(e).lower().startswith(base) or re.match(r'(?i)screenshot' + SHOT_RE.pattern, stem(e))))
    if not c:
        c = next((e for e in imgs if re.match(r'^(cover|copertina)', stem(e), re.I)), None)
    if not c:
        c = newest(e for e in imgs if SHOT_RE.search(stem(e)))
    if not c:
        c = next((e for e in imgs if re.match(r'^(screen|screenshot|title)', stem(e), re.I)), None)
    if not c:
        c = imgs[0] if imgs else (shots[0] if shots else None)
    return c.path if c else None


def update_display(g):
    d = g.title
    if g.favorite:
        d = HEART + ' ' + d
    if not g.file and not g.candidates:
        d += '  ' + T('unplayable')
    if g.hidden:
        d += '  ' + T('hiddenTag')
    if g.rating > 0:
        d += '   ' + STAR_FULL * g.rating
    g.display = d


def get_games():
    ini = load_settings()
    games = []
    if not os.path.isdir(S.games_dir):
        return games
    try:
        dirs = sorted([e for e in os.scandir(S.games_dir) if e.is_dir()], key=lambda e: e.name.lower())
    except OSError:
        return games

    try:
        remove_orphan_sections([d.name for d in dirs])
    except OSError:
        pass

    # new games are added to games.ini (file= only when there is a single executable)
    to_add = []
    for d in dirs:
        if ini_section(ini, d.name) is not None:
            continue
        cands = get_candidates(d.path)
        fname = cands[0] if len(cands) == 1 else ''
        to_add += ['', '[' + d.name + ']', 'file=' + fname]
        ini[d.name] = {'file': fname}
    if to_add:
        try:
            lines = _read_lines()
            while lines and not lines[-1].strip():
                lines.pop()
            _write_lines(lines + to_add)
        except OSError:
            pass

    for d in dirs:
        cfg = ini_section(ini, d.name) or {}
        g = Game()
        g.section = d.name
        g.folder = d.path
        g.candidates = get_candidates(d.path)
        g.file = None
        if cfg.get('file'):
            p = os.path.join(d.path, norm(cfg['file']))
            if os.path.isfile(p):
                g.file = p
        elif len(g.candidates) == 1:
            g.file = os.path.join(d.path, g.candidates[0])
        g.title_cfg = cfg.get('title', '')
        g.title = g.title_cfg or d.name
        g.args_cfg = cfg.get('args', '')
        g.args = g.args_cfg or S.global_args
        m = re.match(r'^\s*([0-5])\s*$', cfg.get('rating', ''))
        g.rating = int(m.group(1)) if m else 0
        g.hidden = bool(re.match(r'^\s*(1|yes|true)\s*$', cfg.get('hidden', ''), re.I))
        g.favorite = bool(re.match(r'^\s*(1|yes|true)\s*$', cfg.get('favorite', ''), re.I))
        g.ask_file = bool(re.match(r'^\s*(1|yes|true)\s*$', cfg.get('askfile', ''), re.I))
        g.boot_os = bool(re.match(r'^\s*nextzxos\s*$', cfg.get('boot', ''), re.I))
        g.tap48 = bool(re.match(r'^\s*48\s*$', cfg.get('tapmode', '')))
        g.compat = cfg.get('compat', '').strip()
        g.image_cfg = cfg.get('image', '')
        g.image = find_image(d.path, g.image_cfg, g.file)
        update_display(g)
        games.append(g)
    return games


def get_save_files(g):
    res = []
    for dirpath, dirnames, files in os.walk(g.folder):
        for f in files:
            if f.lower().endswith('.sav'):
                res.append(os.path.join(dirpath, f))
    return sorted(res)


def move_to_trash(path):
    """Moves a file to the desktop Trash (macOS Trash, gio, or the freedesktop.org Trash folder)."""
    if IS_WIN:
        os.remove(path)
        return
    if IS_MAC:
        trash = os.path.expanduser('~/.Trash')
        name = os.path.basename(path)
        stem, ext = os.path.splitext(name)
        n = 1
        while os.path.exists(os.path.join(trash, name)):
            n += 1
            name = '%s %d%s' % (stem, n, ext)
        shutil.move(path, os.path.join(trash, name))
        return
    gio = shutil.which('gio')
    if gio and subprocess.run([gio, 'trash', path], capture_output=True).returncode == 0:
        return
    base = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'Trash')
    files_dir, info_dir = os.path.join(base, 'files'), os.path.join(base, 'info')
    os.makedirs(files_dir, exist_ok=True)
    os.makedirs(info_dir, exist_ok=True)
    name = os.path.basename(path)
    stem, ext = os.path.splitext(name)
    n = 1
    while os.path.exists(os.path.join(files_dir, name)) or os.path.exists(os.path.join(info_dir, name + '.trashinfo')):
        n += 1
        name = '%s.%d%s' % (stem, n, ext)
    with open(os.path.join(info_dir, name + '.trashinfo'), 'w', encoding='utf-8') as f:
        f.write('[Trash Info]\nPath=%s\nDeletionDate=%s\n' % (
            urllib.parse.quote(os.path.abspath(path)), datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))
    shutil.move(path, os.path.join(files_dir, name))


def find_mono():
    """Path of mono (PATH first, then the usual macOS install folders), or None."""
    mono = shutil.which('mono')
    if mono or not IS_MAC:
        return mono
    return next((p for p in MAC_MONO if os.path.isfile(p)), None)


def mono_env(mono):
    """Environment with the mono folder in PATH (ZXOS.sh calls plain 'mono')."""
    env = dict(os.environ)
    env['PATH'] = os.path.dirname(mono) + os.pathsep + env.get('PATH', '')
    return env


def split_args(text):
    """CSpect parameters as a list; Windows-style paths (.\\) are converted to ./ on Linux."""
    if not IS_WIN:
        text = text.replace('\\', '/')
    try:
        return shlex.split(text, posix=not IS_WIN)
    except ValueError:
        return text.split()


# ============================================================
#  NextZXOS: starting .bas and .tap files
#  CSpect cannot open them directly: a small SD card image is created on the fly
#  with the NextZXOS files (taken from the user's image, e.g. zxnext.sd), the game
#  in c:/GAME (or the folder its executable expects) and an autoexec.bas that loads it at power on
# ============================================================
class FatImage:
    """Read-only access to a FAT32 SD card image, with or without a partition table."""

    def __init__(self, path):
        self.f = open(path, 'rb')
        base = 0
        if self._read(82, 5) != b'FAT32':
            base = int.from_bytes(self._read(454, 4), 'little') * 512
        b = self._read(base, 512)
        if b[82:87] != b'FAT32':
            raise ValueError('FAT32 file system not found')
        bps = int.from_bytes(b[11:13], 'little')
        self.cluster_size = bps * b[13]
        self.fat = base + int.from_bytes(b[14:16], 'little') * bps
        self.data = self.fat + b[16] * int.from_bytes(b[36:40], 'little') * bps
        self.root = int.from_bytes(b[44:48], 'little')

    def close(self):
        self.f.close()

    def _read(self, pos, n):
        self.f.seek(pos)
        b = self.f.read(n)
        if len(b) < n:
            raise ValueError('unexpected end of the image')
        return b

    def _chain(self, c):
        n = 0
        while 2 <= c < 0x0FFFFFF8 and n < 4000000:
            yield c
            n += 1
            c = int.from_bytes(self._read(self.fat + c * 4, 4), 'little') & 0x0FFFFFFF

    def _cluster(self, c, n=None):
        return self._read(self.data + (c - 2) * self.cluster_size, n or self.cluster_size)

    def read_dir(self, cluster):
        """(name, is_dir, first cluster, size) of the entries of a directory."""
        res, lfn = [], ''
        for c in self._chain(cluster):
            raw = self._cluster(c)
            for i in range(0, len(raw), 32):
                e = raw[i:i + 32]
                if e[0] == 0:
                    return res
                if e[0] == 0xE5:
                    lfn = ''
                    continue
                if e[11] == 0x0F:
                    lfn = (e[1:11] + e[14:26] + e[28:32]).decode('utf-16-le', 'replace').split('\x00')[0] + lfn
                    continue
                if e[11] & 0x08:
                    lfn = ''
                    continue
                name, lfn = lfn, ''
                if not name:
                    name = e[0:8].decode('latin-1').rstrip()
                    ext = e[8:11].decode('latin-1').rstrip()
                    if ext:
                        name += '.' + ext
                if name in ('.', '..'):
                    continue
                cl = int.from_bytes(e[20:22], 'little') << 16 | int.from_bytes(e[26:28], 'little')
                res.append((name, bool(e[11] & 0x10), cl, int.from_bytes(e[28:32], 'little')))
        return res

    def find_dir(self, path):
        """First cluster of a folder given as a path from the root (e.g. 'GAMES/Z-Machine/ZXZVM'), or None."""
        cluster = self.root
        for part in path.split('/'):
            e = next((x for x in self.read_dir(cluster) if x[1] and x[0].lower() == part.lower()), None)
            if not e:
                return None
            cluster = e[2]
        return cluster

    def copy_dir(self, cluster, dest):
        os.makedirs(dest, exist_ok=True)
        for name, is_dir, cl, size in self.read_dir(cluster):
            p = os.path.join(dest, name)
            if is_dir:
                self.copy_dir(cl, p)
                continue
            with open(p, 'wb') as o:
                left = size
                if left > 0:
                    for c in self._chain(cl):
                        n = min(left, self.cluster_size)
                        o.write(self._cluster(c, n))
                        left -= n
                        if left <= 0:
                            break


def resolve_sd_image(value):
    """SD card image with NextZXOS from nextzxos= (empty = zxnext.sd in the CSpect folder)."""
    p = norm(value)
    if not p:
        return find_case_insensitive(os.path.dirname(S.emulator), 'zxnext.sd')
    if not os.path.isabs(p):
        p = os.path.join(ROOT, p)
    return os.path.normpath(p)


def run_hdfmonkey(*args):
    """Runs hdfmonkey (included with CSpect); raises an error if it fails."""
    hdir = os.path.join(os.path.dirname(S.emulator), 'hdfmonkey')
    if IS_WIN:
        exe = os.path.join(hdir, 'windows-64', 'hdfmonkey.exe')
    elif sys.platform == 'darwin':
        exe = os.path.join(hdir, 'macos-mn' if os.uname().machine == 'arm64' else 'macos-intel', 'hdfmonkey')
    else:
        exe = os.path.join(hdir, 'linux-musl', 'hdfmonkey')
    if not os.path.isfile(exe):
        raise RuntimeError(T('osNoTool', exe))
    if not IS_WIN and not os.access(exe, os.X_OK):
        os.chmod(exe, os.stat(exe).st_mode | 0o111)
    r = subprocess.run([exe] + list(args), capture_output=True, text=True, errors='replace')
    if r.returncode != 0:
        raise RuntimeError('hdfmonkey %s: %s' % (args[0], (r.stdout + r.stderr).strip()))
    return r.stdout


def update_os_files(sd_image):
    """NextZXOS system files copied from the SD card image (once, until the image changes)."""
    d = os.path.join(OS_WORK, 'nextzxos')
    stamp_file = os.path.join(OS_WORK, 'nextzxos.txt')
    st = os.stat(sd_image)
    stamp = '%s|%d|%d|%s' % (os.path.abspath(sd_image), st.st_size, int(st.st_mtime), ','.join(OS_DIRS + OS_OPT_DIRS))
    try:
        with open(stamp_file, encoding='utf-8') as f:
            if os.path.isdir(d) and f.read() == stamp:
                return d
    except OSError:
        pass
    os.makedirs(OS_WORK, exist_ok=True)
    shutil.rmtree(d, ignore_errors=True)
    try:
        fat = FatImage(sd_image)
        try:
            for path in OS_DIRS + OS_OPT_DIRS:
                cluster = fat.find_dir(path)
                if cluster is None:
                    if path in OS_OPT_DIRS:
                        continue
                    raise ValueError('/' + path)
                fat.copy_dir(cluster, os.path.join(d, path.split('/')[-1]))
        finally:
            fat.close()
    except (OSError, ValueError) as ex:
        shutil.rmtree(d, ignore_errors=True)
        raise RuntimeError(T('osBadImage', sd_image) + '\n' + str(ex))
    # no user or welcome autoexec: the game's one is added
    sysdir = os.path.join(d, 'NEXTZXOS')
    for f in os.listdir(sysdir):
        if f.lower().startswith('autoexec.'):
            os.remove(os.path.join(sysdir, f))
    with open(stamp_file, 'w', encoding='utf-8') as f:
        f.write(stamp)
    return d


def basic_line(num, body):
    """One BASIC line: number (big-endian), length, text, ENTER."""
    return num.to_bytes(2, 'big') + (len(body) + 1).to_bytes(2, 'little') + body + b'\r'


def basic_number(n):
    """Number in a BASIC line: digits followed by its hidden 5-byte form (small integer)."""
    return str(n).encode() + b'\x0e\x00\x00' + n.to_bytes(2, 'little') + b'\x00'


def plus3_basic(prog, autostart):
    """BASIC program file in +3DOS format (128-byte header), starting at line autostart."""
    h = bytearray(128)
    h[0:11] = b'PLUS3DOS\x1a\x01\x00'
    h[11:15] = (128 + len(prog)).to_bytes(4, 'little')
    h[15] = 0                                                   # BASIC program
    h[16:18] = len(prog).to_bytes(2, 'little')
    h[18:20] = autostart.to_bytes(2, 'little')
    h[20:22] = len(prog).to_bytes(2, 'little')
    h[127] = sum(h[:127]) & 0xFF
    return bytes(h) + prog


# autoexec.bas: goes to c:/GAME (or the folder cd, see os_game_dir) and loads the game
#   bas:  .cd /game  -  LOAD "name.bas"
#   tap:  .cd /game  -  .tapein name.tap (as the Browser's TAP Loader does: also serves the loaders that call
#         the ROM tape routine directly)  -  SPECTRUM LOAD (NextZXOS Tape Loader in 128K mode, e.g. Tokimal)
#   tap48: .cd /game  -  .tapein name.tap  -  USR 0 mode in 48K with the tape loader of usr0.bin
#         (as the TAP Loader's 48K mode: SPECTRUM 48: OUT 9275,36: POKE 61440,b: LET x=USR 61441,
#         b = 1 when the first block of the tape is a CODE header)
#   zvm:  .cd /game  -  LOAD "c:/zxzvm/run.bas" (ZXZVM loader made by make_zvm_loader)
#   nex:  .cd /game  -  .nexload name.nex
#   snx:  .cd /game  -  SPECTRUM "name.snx"
#   sna:  .cd /game  -  CLEAR 65367  -  %s=%REG 7&3: RUN AT 3: MERGE "c:/nextzxos/snapload.bas"  -
#         RUN AT %s: LET f$="name.sna": LET adj=0: GO TO 1  (as the Browser does, with the MERGE at
#         28 MHz; lines from 9990, after those of SNAPLOAD.BAS)
def make_autoexec(file_name, mode, code_first=0, cd='/game'):
    load = b'\xef'                          # LOAD token
    name = file_name.encode('latin-1', 'replace')
    n = basic_number
    lines = [b'.cd ' + cd.encode('latin-1', 'replace')]
    if mode == 'tap':
        lines += [b'.tapein ' + name, b'\xa3' + load]              # SPECTRUM LOAD
    elif mode == 'tap48':
        lines += [b'.tapein ' + name,
                  load + b'"c:/nextzxos/usr0.bin"' + b'\xaf' + n(61440),                       # LOAD ... CODE
                  b'\xa3' + n(48) + b':' + b'\xdf' + n(9275) + b',' + n(36) + b':' +          # SPECTRUM 48: OUT
                  b'\xf4' + n(61440) + b',' + n(code_first) + b':' +                          # POKE
                  b'\xf1' + b'x=' + b'\xc0' + n(61441)]                                       # LET x=USR
    elif mode == 'zvm':
        lines += [load + b'"c:/zxzvm/run.bas"']
    elif mode == 'nex':
        lines += [b'.nexload ' + name]
    elif mode == 'snx':
        lines += [b'\xa3"' + name + b'"']                          # SPECTRUM "name"
    elif mode == 'sna':
        lines += [b'\xfd' + n(65367),                                                         # CLEAR
                  b'%s=%' + b'\x88' + b'7&3:' +                                               # %s=%REG 7&3
                  b'\xf7\xac' + n(3) + b':' +                                                  # RUN AT 3
                  b'\xd5' + b'"c:/nextzxos/snapload.bas"',                                    # MERGE
                  b'\xf7\xac' + b'%s:' +                                                       # RUN AT %s
                  b'\xf1' + b'f$="' + name + b'":' +                                          # LET
                  b'\xf1' + b'adj=' + n(0) + b':' +                                           # LET
                  b'\xec' + n(1)]                                                             # GO TO
    else:
        lines += [load + b'"' + name + b'"']
    first, step = (9990, 1) if mode == 'sna' else (10, 10)
    return plus3_basic(b''.join(basic_line(first + step * i, body) for i, body in enumerate(lines)), first)


# ZXZVM loader: a copy of ZXZVM's NXZXZVM.BAS that keeps the lines up to its autostart line
# (CLEAR %$67ff) and then, instead of the welcome screen and the file chooser, does what
# PROC story() does, with a key press already waiting so the story starts at once:
#   PROC loadZXZVM("c:/zxzvm/"): PROC setup(): POKE 23560,13: LET f=PEEK 23611:
#   IF INT (f/32)=2*INT (f/64) THEN POKE 23611,f+32
#   PROC start("<file>"): ERASE
# (ZXZVM's wait_key takes the key from LAST_K=23560 when bit 5 of FLAGS=23611 is set)
def make_zvm_loader(bas_path, story):
    with open(bas_path, 'rb') as f:
        b = f.read()
    if len(b) < 128 or b[:8] != b'PLUS3DOS':
        raise ValueError('NXZXZVM.BAS?')
    plen = int.from_bytes(b[16:18], 'little')
    auto = int.from_bytes(b[18:20], 'little')
    prog, i = b'', 128
    while i + 4 <= 128 + plen:
        num = int.from_bytes(b[i:i + 2], 'big')
        length = int.from_bytes(b[i + 2:i + 4], 'little')
        if num > auto:
            break
        prog += b[i:i + 4 + length]
        i += 4 + length
    PROC, POKE, LET, PEEK, IF, INT, THEN, ERASE = b'\x93', b'\xf4', b'\xf1', b'\xbe', b'\xfa', b'\xba', b'\xcb', b'\xd2'
    n = basic_number
    line1 = (PROC + b'loadZXZVM("c:/zxzvm/"):' + PROC + b'setup():' +
             POKE + n(23560) + b',' + n(13) + b':' + LET + b'f=' + PEEK + n(23611) + b':' +
             IF + INT + b'(f/' + n(32) + b')=' + n(2) + b'*' + INT + b'(f/' + n(64) + b')' +
             THEN + POKE + n(23611) + b',f+' + n(32))
    line2 = PROC + b'start("' + story.encode('latin-1', 'replace') + b'"):' + ERASE
    return plus3_basic(prog + basic_line(auto + 10, line1) + basic_line(auto + 20, line2), auto)


def file_in_use(path):
    """True if a process has the file open. On Windows an open image cannot be removed anyway;
    on Linux it could, so the open files of the processes are checked in /proc."""
    if IS_WIN or not os.path.isdir('/proc'):
        return False
    target = os.path.realpath(path)
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        fd_dir = os.path.join('/proc', pid, 'fd')
        try:
            for fd in os.listdir(fd_dir):
                if os.path.realpath(os.path.join(fd_dir, fd)) == target:
                    return True
        except OSError:
            continue
    return False


def os_game_dir(file):
    """Folder of the game in the image: /GAME, or the folder of an absolute path "c:/<folder>/" written
    in the executable (e.g. TX-1696 loads its files from c:/tx-1696/, where its instructions put it)."""
    if os.path.getsize(file) <= 16 * 1024 * 1024:
        with open(file, 'rb') as f:
            text = f.read().decode('latin-1')
        system = [d.split('/')[0].lower() for d in OS_DIRS + OS_OPT_DIRS]
        for m in re.finditer(r'[cC]:/([A-Za-z0-9_\-]{1,32})/', text):
            if m.group(1).lower() not in system:
                return '/' + m.group(1).upper()
    return '/GAME'


def new_os_image(g, sd_image):
    """Creates the SD card image of the game; returns {'img', 'img_dir', 'dir', 'copies'}."""
    sysdir = update_os_files(sd_image)
    ext = os.path.splitext(g.file)[1].lower()
    # .sna: with the Snapshot Loader (SNAPLOAD.BAS) as the Browser does; older NextZXOS without it
    # (e.g. 2.06) start them with SPECTRUM, as for .snx
    snapload = any(f.lower() == 'snapload.bas' for f in os.listdir(os.path.join(sysdir, 'NEXTZXOS')))
    mode = {'.tap': 'tap', '.nex': 'nex', '.snx': 'snx', '.sna': 'sna' if snapload else 'snx'}.get(
        ext, 'zvm' if ext in Z_EXTS else 'bas')
    code_first = 0
    if mode == 'tap' and g.tap48:
        mode = 'tap48'
        # first block of the tape: a header (flag 0) of CODE (type 3) or of a program (type 0)
        with open(g.file, 'rb') as f:
            head = f.read(4)
        if len(head) == 4 and head[2] == 0 and head[3] == 3:
            code_first = 1
    copies = []                             # extra copies in the game folder of the image, not saves of the game
    gd = '/GAME' if mode == 'zvm' else os_game_dir(g.file)
    zvm_bas = os.path.join(sysdir, 'ZXZVM', 'NXZXZVM.BAS')
    if mode == 'zvm' and not os.path.isfile(zvm_bas):
        raise RuntimeError(T('osNoZvm', sd_image))
    exe_dir = os.path.dirname(g.file)
    name = os.path.basename(g.file)
    # some .tap files load other files from their folder: the whole folder is copied
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fs in os.walk(exe_dir) for f in fs)
    mb = max(64, -(-size * 5 // 4 // (1024 * 1024)) + 32)
    img = os.path.join(OS_WORK, re.sub(r'[^\w\-]', '_', g.section) + '.img')
    # images of previous launches are removed, except those still used by a running CSpect,
    # after copying back the saves of games already closed
    complete_os_runs()
    for f in os.listdir(OS_WORK):
        p = os.path.join(OS_WORK, f)
        if f.lower().endswith('.img') and p != img and not file_in_use(p):
            try:
                os.remove(p)
            except OSError:
                pass
    if os.path.exists(img):
        os.remove(img)
    run_hdfmonkey('create', img, '%dM' % mb)
    run_hdfmonkey('putdir', img, sysdir, '/')
    run_hdfmonkey('mkdir', img, gd)
    run_hdfmonkey('putdir', img, exe_dir, gd)
    # .tapein and .nexload do not accept names with spaces or symbols: in that case a copy as GAME.TAP/.NEX
    if mode in ('tap', 'tap48', 'nex') and not re.match(r'^[A-Za-z0-9_\-.]+$', name):
        name = 'GAME' + ext.upper()
        run_hdfmonkey('put', img, g.file, gd + '/' + name)
        copies.append(name)
    # BASIC programs saved without autostart (e.g. Orb Run) would only be loaded, not started:
    # a copy as GAME.BAS that starts from its first line
    if mode == 'bas':
        with open(g.file, 'rb') as f:
            b = bytearray(f.read())
        if len(b) >= 130 and b[:8] == b'PLUS3DOS' and b[15] == 0 and int.from_bytes(b[18:20], 'little') >= 32768:
            b[18:20] = (b[128] * 256 + b[129]).to_bytes(2, 'little')       # line numbers are big-endian
            b[127] = sum(b[:127]) & 0xFF                                     # header checksum
            name = 'GAME.BAS'
            gb = os.path.join(OS_WORK, name)
            with open(gb, 'wb') as f:
                f.write(b)
            run_hdfmonkey('put', img, gb, gd + '/' + name)
            copies.append(name)
    # ZXZVM gets a short 8.3 name: in other cases a copy as STORY.Zn
    if mode == 'zvm':
        if not re.match(r'^[A-Za-z0-9_\-]{1,8}\.[zZ][3-8]$', name):
            name = 'STORY' + ext.upper()
            run_hdfmonkey('put', img, g.file, gd + '/' + name)
            copies.append(name)
        zl = os.path.join(OS_WORK, 'RUN.BAS')
        with open(zl, 'wb') as f:
            f.write(make_zvm_loader(zvm_bas, name))
        run_hdfmonkey('put', img, zl, '/ZXZVM/RUN.BAS')
    ae = os.path.join(OS_WORK, 'AUTOEXEC.BAS')
    with open(ae, 'wb') as f:
        f.write(make_autoexec(name, mode, code_first, gd.lower()))
    run_hdfmonkey('put', img, ae, '/NEXTZXOS/AUTOEXEC.BAS')
    return {'img': img, 'img_dir': gd, 'dir': exe_dir, 'copies': copies}


def hdf_listing(img, path):
    """Listing of a folder in an SD card image (hdfmonkey ls): (name, is_dir) pairs."""
    out = run_hdfmonkey('ls', img, path)
    res = []
    for line in out.splitlines():
        if '\t' not in line:
            continue
        kind, name = line.split('\t', 1)
        if name not in ('.', '..'):
            res.append((name, kind == '[DIR]'))
    return res


def copy_os_saves(img, img_dir, host_dir, skip):
    """Copies back into the game folder the files that the game created or changed in its folder of
    the image, img_dir (saved games, high scores...); returns how many were copied."""
    n = 0
    tmp = os.path.join(OS_WORK, 'save.tmp')
    for name, is_dir in hdf_listing(img, img_dir):
        host = os.path.join(host_dir, name)
        if is_dir:
            n += copy_os_saves(img, img_dir + '/' + name, host, ())
            continue
        if name in skip:                                  # GAME.TAP / STORY.Z5 copies made by the launcher
            continue
        run_hdfmonkey('get', img, img_dir + '/' + name, tmp)
        with open(tmp, 'rb') as f:
            data = f.read()
        try:
            with open(host, 'rb') as f:
                if f.read() == data:
                    continue
        except OSError:
            pass
        os.makedirs(host_dir, exist_ok=True)
        with open(host, 'wb') as f:
            f.write(data)
        n += 1
    if os.path.exists(tmp):
        os.remove(tmp)
    return n


# NextZXOS games still running: checked every 2 seconds by the user interface (root.after),
# when their CSpect closes the saved files go back to the game folder
OS_RUNS = []


def complete_os_runs():
    """Copies back the saves of the NextZXOS games whose CSpect has closed; returns how many files."""
    total = 0
    for r in list(OS_RUNS):
        if r['proc'].poll() is None:
            continue
        OS_RUNS.remove(r)
        try:
            total += copy_os_saves(r['img'], r['img_dir'], r['dir'], r['copies'])
        except (OSError, RuntimeError):
            pass
    return total


# fixes of the CSpect Compat plugin: option -> menu text. l2bank9 = Layer 2 at bank 9 as in CSpect 2
# (e.g. Montana Mike), nodivmmc = DivMMC automap off (e.g. Deltas Shadow), dd01nop = DD 01 debugger
# breakpoints in the .nex as NOPs (e.g. Elite Next), zeroram = RAM cleared as in CSpect 2 (e.g. Spice Invaderz)
COMPAT_OPTIONS = {'l2bank9': 'compatL2', 'nodivmmc': 'compatDiv', 'dd01nop': 'compatDd01', 'zeroram': 'compatZero'}


def compat_list(g):
    """Options of the CSpect Compat plugin for a game (compat=, comma-separated)."""
    return [o.strip().lower() for o in (g.compat or '').split(',') if o.strip()]


def test_os_launch(g):
    """True if the game is started through NextZXOS: .bas/.tap/.z? or a BASIC program without
    extension, or a .nex/.snx/.sna with boot=nextzxos."""
    if not g.file:
        return False
    ext = os.path.splitext(g.file)[1].lower()
    return ext in OS_EXTS or (g.boot_os and ext in OS_NEX_EXTS) or test_plus3_program(g.file)


# ============================================================
#  User interface
# ============================================================
class Launcher:
    def __init__(self, root):
        self.root = root
        self.games = []
        self.view = []          # games currently shown in the list
        self.photo = None
        self.pil_image = None
        self._resize_job = None
        self._os_watch = None   # timer of _watch_os_runs (NextZXOS games running)
        self._hover = None
        self.raw_photo = None

        base = tkfont.nametofont('TkDefaultFont').actual('family')
        self.f_norm = (base, 10)
        self.f_list = (base, 11)
        self.f_title = (base, 16, 'bold')
        self.f_star = (base, 20)
        self.f_play = (base, 12, 'bold')
        self.f_mono = ('Menlo' if IS_MAC else 'DejaVu Sans Mono', 10)

        root.title(APP_NAME + ' ' + APP_VERSION + ' - ZX Spectrum Next')
        root.geometry('960x600')
        root.minsize(700, 420)
        root.configure(bg=C_BACK)
        self._style()
        self._build()
        self._bind_keys()

    # ---------- look ----------
    def _style(self):
        st = ttk.Style(self.root)
        try:
            st.theme_use('clam')
        except tk.TclError:
            pass
        st.configure('TCombobox', fieldbackground=C_PANEL, background=C_PANEL, foreground=C_TEXT,
                     arrowcolor=C_TEXT, bordercolor=C_DIM, lightcolor=C_PANEL, darkcolor=C_PANEL)
        st.map('TCombobox', fieldbackground=[('readonly', C_PANEL)], foreground=[('readonly', C_TEXT)],
               selectbackground=[('readonly', C_PANEL)], selectforeground=[('readonly', C_TEXT)])
        self.root.option_add('*TCombobox*Listbox.background', C_PANEL)
        self.root.option_add('*TCombobox*Listbox.foreground', C_TEXT)
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#0078d7')

    def label(self, parent, text='', fg=C_TEXT, font=None, **kw):
        return tk.Label(parent, text=text, bg=kw.pop('bg', C_BACK), fg=fg, font=font or self.f_norm, **kw)

    def button(self, parent, text, cmd, **kw):
        return tk.Button(parent, text=text, command=cmd, bg=kw.pop('bg', C_PANEL), fg=kw.pop('fg', C_TEXT),
                         activebackground=kw.pop('activebackground', '#33333b'), activeforeground=C_TEXT,
                         relief='flat', bd=0, highlightthickness=1, highlightbackground=C_DIM,
                         font=kw.pop('font', self.f_norm), padx=12, pady=4, cursor='hand2', **kw)

    def entry(self, parent, mono=False, **kw):
        e = tk.Entry(parent, bg=C_PANEL, fg=C_TEXT, insertbackground=C_TEXT, relief='flat',
                     highlightthickness=1, highlightbackground=C_DIM, highlightcolor=C_LINK,
                     font=self.f_mono if mono else self.f_norm, **kw)
        # Ctrl+A selects all, as on Windows (in Tk it would move to the start of the line)
        e.bind('<Control-a>', lambda ev: (e.select_range(0, 'end'), e.icursor('end'), 'break')[-1])
        e.bind('<Control-A>', lambda ev: (e.select_range(0, 'end'), e.icursor('end'), 'break')[-1])
        return e

    def link(self, parent, text, url):
        l = tk.Label(parent, text=text, bg=C_BACK, fg=C_LINK, cursor='hand2', font=self.f_norm)
        l.bind('<Button-1>', lambda e: webbrowser.open(url))
        return l

    # ---------- main window ----------
    def _build(self):
        r = self.root
        self.stripe = tk.Canvas(r, height=6, bg=C_BACK, highlightthickness=0)
        self.stripe.pack(side='top', fill='x')
        self.stripe.bind('<Configure>', self._draw_stripe)

        # status bar with Settings button
        bar = tk.Frame(r, bg=C_PANEL)
        bar.pack(side='bottom', fill='x')
        self.status = tk.Label(bar, bg=C_PANEL, fg=C_DIM, anchor='w', font=self.f_norm)
        self.status.pack(side='left', fill='x', expand=True, padx=6, pady=2)
        self.btn_settings = tk.Button(bar, command=self.open_settings, bg=C_PANEL, fg=C_TEXT, relief='flat', bd=0,
                                      highlightthickness=0,
                                      activebackground='#33333b', activeforeground=C_TEXT, font=self.f_norm,
                                      cursor='hand2', padx=8)
        self.btn_settings.pack(side='right')

        self.paned = tk.PanedWindow(r, orient='horizontal', bg=C_PANEL, sashwidth=5, bd=0, sashrelief='flat')
        self.paned.pack(fill='both', expand=True)
        self.paned.bind('<ButtonRelease-1>', self._sash_moved)

        # left: search, sort, list
        left = tk.Frame(self.paned, bg=C_BACK, padx=10, pady=10)
        self.left = left
        lrow = tk.Frame(left, bg=C_BACK)
        lrow.pack(fill='x')
        self.lbl_search = self.label(lrow, fg=C_DIM, anchor='w')
        self.lbl_search.pack(side='left')
        tk.Frame(lrow, bg=C_BACK, width=34).pack(side='right')     # keeps "Sort:" above the sort menu
        self.lbl_sort = self.label(lrow, fg=C_DIM, anchor='w', width=11)
        self.lbl_sort.pack(side='right')
        srow = tk.Frame(left, bg=C_BACK)
        srow.pack(fill='x', pady=(2, 8))
        # heart button next to the sort menu: shows only the favorite games (favonly=1)
        self.fav_var = tk.BooleanVar(value=S.fav_only)
        self.chk_fav = tk.Checkbutton(srow, text=HEART, variable=self.fav_var, indicatoron=False, command=self._fav_filter,
                                      bg=C_PANEL, fg=C_DIM, selectcolor='#961e3c', activebackground='#33333b',
                                      activeforeground=C_TEXT, relief='flat', bd=1, width=2, cursor='hand2', font=self.f_norm)
        self.chk_fav.pack(side='right', padx=(6, 0))
        self.sort_var = tk.StringVar()
        self.cmb_sort = ttk.Combobox(srow, textvariable=self.sort_var, state='readonly', width=9, font=self.f_norm)
        self.cmb_sort.pack(side='right', padx=(6, 0))
        self.cmb_sort.bind('<<ComboboxSelected>>', self._sort_changed)
        self.search_var = tk.StringVar()
        self.txt_search = self.entry(srow, textvariable=self.search_var)
        self.txt_search.pack(side='left', fill='x', expand=True, ipady=3)
        self.search_var.trace_add('write', lambda *a: self.refresh_list())

        lf = tk.Frame(left, bg=C_PANEL)
        lf.pack(fill='both', expand=True)
        sb = tk.Scrollbar(lf, bg=C_PANEL, troughcolor=C_BACK, activebackground=C_DIM, relief='flat', bd=0,
                          highlightthickness=0, elementborderwidth=0, width=12)
        sb.pack(side='right', fill='y')
        self.lst = tk.Listbox(lf, bg=C_PANEL, fg=C_TEXT, selectbackground='#0078d7', selectforeground='white',
                              relief='flat', bd=0, highlightthickness=0, activestyle='none', font=self.f_list,
                              exportselection=False, yscrollcommand=sb.set)
        self.lst.pack(side='left', fill='both', expand=True)
        sb.config(command=self.lst.yview)
        self.lst.bind('<<ListboxSelect>>', lambda e: self.show_game(self.selected()))
        self.lst.bind('<Double-Button-1>', lambda e: self.start_game(self.selected()))
        self.lst.bind('<Button-3>', self._context_menu)
        if IS_MAC:      # on macOS the right button is Button-2, or Control+click
            self.lst.bind('<Button-2>', self._context_menu)
            self.lst.bind('<Control-Button-1>', self._context_menu)

        # right: title + stars, picture, file + PLAY
        right = tk.Frame(self.paned, bg=C_BACK, padx=10, pady=10)
        trow = tk.Frame(right, bg=C_BACK)
        trow.pack(fill='x')
        self.stars_frame = tk.Frame(trow, bg=C_BACK)
        self.stars_frame.pack(side='right')
        self.lbl_vote = self.label(self.stars_frame, fg=C_DIM, anchor='e', width=13)
        self.lbl_vote.pack(side='left')
        self.star_labels = []
        for n in range(1, 6):
            s = tk.Label(self.stars_frame, text=STAR_EMPTY, bg=C_BACK, fg=C_DIM, font=self.f_star, cursor='hand2', padx=2)
            s.pack(side='left')
            s.bind('<Enter>', lambda e, n=n: self.paint_stars(n))
            s.bind('<Leave>', lambda e: self.paint_stars(None))
            s.bind('<Button-1>', lambda e, n=n: self.set_rating(n))
            self.star_labels.append(s)
        self.lbl_title = self.label(trow, font=self.f_title, anchor='w')
        self.lbl_title.pack(side='left', fill='x', expand=True)

        bottom = tk.Frame(right, bg=C_BACK)
        bottom.pack(side='bottom', fill='x', pady=(10, 0))
        self.btn_play = tk.Button(bottom, command=lambda: self.start_game(self.selected()), bg=C_PLAY, fg='white',
                                  activebackground=C_PLAY_ACTIVE, activeforeground='white', disabledforeground='#9fcfb0',
                                  relief='flat', bd=0, font=self.f_play, width=12, height=2, cursor='hand2')
        self.btn_play.pack(side='right')
        self.lbl_file = self.label(bottom, fg=C_DIM, anchor='w', justify='left')
        self.lbl_file.pack(side='left', fill='x', expand=True)

        self.pic = tk.Label(right, bg='black')
        self.pic.pack(fill='both', expand=True, pady=(6, 0))
        self.pic.bind('<Configure>', self._pic_resized)

        self.paned.add(left, minsize=200, width=S.list_width)
        self.paned.add(right, minsize=300)

        # right-click menu
        self.menu = tk.Menu(self.root, tearoff=0, bg=C_PANEL, fg=C_TEXT, activebackground='#0078d7',
                            activeforeground='white', disabledforeground='#666', relief='flat', font=self.f_norm)
        self.show_hidden_var = tk.BooleanVar(value=False)
        self.boot_os_var = tk.BooleanVar(value=False)
        self.tap48_var = tk.BooleanVar(value=False)
        self.compat_vars = {o: tk.BooleanVar(value=False) for o in COMPAT_OPTIONS}

    def _draw_stripe(self, e=None):
        c = self.stripe
        c.delete('all')
        w = c.winfo_width()
        cols = ['#D70000', '#D7D700', '#00D700', '#00D7D7']
        step = w / len(cols)
        for i, col in enumerate(cols):
            c.create_rectangle(int(i * step), 0, int((i + 1) * step) + 1, 6, fill=col, outline=col)

    def _bind_keys(self):
        r = self.root
        r.bind('<Return>', lambda e: self.start_game(self.selected()))
        r.bind('<KP_Enter>', lambda e: self.start_game(self.selected()))
        r.bind('<Escape>', self._escape)
        r.bind('<F5>', lambda e: self.reload_all())
        for n in range(6):
            r.bind('<Control-Key-%d>' % n, lambda e, n=n: self._ctrl_rating(n))
            r.bind('<Control-KP_%d>' % n, lambda e, n=n: self._ctrl_rating(n))
            if IS_MAC:
                r.bind('<Command-Key-%d>' % n, lambda e, n=n: self._ctrl_rating(n))
        self.txt_search.bind('<Down>', lambda e: self._move(1))
        self.txt_search.bind('<Up>', lambda e: self._move(-1))

    def _escape(self, e=None):
        if self.search_var.get():
            self.search_var.set('')
        else:
            self._quit()

    # ---------- window size (saved on exit) ----------
    def _is_zoomed(self):
        try:
            if IS_WIN or IS_MAC:
                return self.root.state() == 'zoomed'
            return bool(self.root.attributes('-zoomed'))      # X11
        except tk.TclError:
            return False

    def _set_zoomed(self):
        try:
            self.root.state('zoomed')
        except tk.TclError:
            try:
                self.root.attributes('-zoomed', True)
            except tk.TclError:
                pass

    def _root_configured(self, e):
        """Keeps the normal (not maximized) window size, saved on exit also when maximized."""
        if e.widget is self.root and not self._is_zoomed():
            self._normal_size = (e.width, e.height)

    def _quit(self):
        zoomed = self._is_zoomed()
        w, h = self._normal_size if zoomed and self._normal_size else (self.root.winfo_width(), self.root.winfo_height())
        try:
            set_ini_value('_default', 'window', '%dx%d' % (w, h))
            set_ini_value('_default', 'maximized', '1' if zoomed else '')
            set_ini_value('_default', 'showhidden', '1' if S.show_hidden else '')
        except OSError:
            pass
        for job in (getattr(self, '_pic_job', None), self._os_watch):
            if job:
                self.root.after_cancel(job)
        self.root.destroy()

    def _move(self, d):
        if not self.view:
            return 'break'
        cur = self.lst.curselection()
        i = (cur[0] if cur else -1) + d
        self.select_index(max(0, min(len(self.view) - 1, i)))
        return 'break'

    def _ctrl_rating(self, n):
        g = self.selected()
        if g:
            g.rating = 0
            self.set_rating(n)
        return 'break'

    # ---------- texts ----------
    def apply_language(self):
        self.lbl_search.config(text=T('search'))
        self.lbl_sort.config(text=T('sortLbl'))
        self.cmb_sort.config(values=[T('sortName'), T('sortRating')])
        self.sort_var.set(T('sortRating') if S.sort_mode == 'rating' else T('sortName'))
        self.fav_var.set(S.fav_only)
        self.chk_fav.config(fg='white' if S.fav_only else C_DIM)
        self.btn_play.config(text=T('play'))
        self.btn_settings.config(text='⚙ ' + T('settings'))

    # ---------- list ----------
    def selected(self):
        cur = self.lst.curselection()
        if cur and cur[0] < len(self.view):
            return self.view[cur[0]]
        return None

    def select_index(self, i):
        self.lst.selection_clear(0, 'end')
        self.lst.selection_set(i)
        self.lst.activate(i)
        self.lst.see(i)
        self.show_game(self.view[i])

    def refresh_list(self):
        q = self.search_var.get().strip().lower()
        keep = self.selected()
        items = [g for g in self.games if (not q or q in g.title.lower()) and (S.show_hidden or not g.hidden)
                 and (not S.fav_only or g.favorite)]
        if S.sort_mode == 'rating':
            items.sort(key=lambda g: (-g.rating, g.title.lower()))
        else:
            items.sort(key=lambda g: g.title.lower())
        self.view = items
        self.lst.delete(0, 'end')
        for g in items:
            self.lst.insert('end', g.display)
        idx = -1
        if keep:
            idx = next((i for i, g in enumerate(items) if g.section == keep.section), -1)
        if idx < 0 and items:
            idx = 0
        if idx >= 0:
            self.select_index(idx)
        else:
            self.show_game(None)
        self.status.config(text=T('status', len(items), len(self.games)))

    def reload_all(self):
        self.games = get_games()
        self.apply_language()
        self._set_icon()
        self.refresh_list()

    def _sort_changed(self, e=None):
        S.sort_mode = 'rating' if self.cmb_sort.current() == 1 else 'name'
        try:
            set_ini_value('_default', 'sort', S.sort_mode)
        except OSError:
            pass
        self.refresh_list()
        self.lst.focus_set()

    def _sash_moved(self, e=None):
        w = self.left.winfo_width()
        if w > 1 and w != S.list_width:
            S.list_width = w
            try:
                set_ini_value('_default', 'listwidth', str(w))
            except OSError:
                pass

    # ---------- details ----------
    def paint_stars(self, hover):
        g = self.selected()
        if not g:
            for s in self.star_labels:
                s.config(text='', fg=C_DIM)
            self.lbl_vote.config(text='')
            return
        v = hover if hover else g.rating
        for i, s in enumerate(self.star_labels):
            on = i < v
            s.config(text=STAR_FULL if on else STAR_EMPTY, fg=C_GOLD if on else C_DIM)
        self.lbl_vote.config(text='%d/5' % g.rating if g.rating > 0 else T('noRating'))

    def set_rating(self, n):
        g = self.selected()
        if not g:
            return
        if g.rating == n:
            n = 0                  # click on the same star = remove the rating
        g.rating = n
        try:
            set_ini_value(g.section, 'rating', str(n) if n > 0 else '')
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        update_display(g)
        if S.sort_mode == 'rating':
            self.refresh_list()
        else:
            i = self.lst.curselection()[0]
            self.lst.delete(i)
            self.lst.insert(i, g.display)
            self.lst.selection_set(i)
        self.paint_stars(None)

    def show_game(self, g):
        self.paint_stars(None)
        if not g:
            self.lbl_title.config(text='')
            self.lbl_file.config(text='')
            self.btn_play.config(state='disabled')
            self.set_picture(None)
            return
        self.lbl_title.config(text=g.title)
        if g.file:
            a = g.args + ('  ' + T('customTag') if g.args_cfg else '')
            if g.compat:
                a += '  [Compat: ' + g.compat + ']'
            rel = os.path.relpath(g.file, g.folder).replace(os.sep, '/')
            if test_os_launch(g):
                rel += '  ' + T('osTag')
            if g.tap48 and g.file.lower().endswith('.tap'):
                rel += '  (48K)'
            if g.ask_file and len(g.candidates) > 1:
                rel += '  ' + T('askTag')
            self.lbl_file.config(text=T('fileLine', rel, a))
            self.btn_play.config(state='normal')
        elif len(g.candidates) > 1:
            self.lbl_file.config(text=T('fileChoose', len(g.candidates), g.args))
            self.btn_play.config(state='normal')
        else:
            self.lbl_file.config(text=T('noFile'))
            self.btn_play.config(state='disabled')
        self.set_picture(g.image)

    # ---------- picture ----------
    def set_picture(self, path):
        self.pil_image = None
        self.raw_photo = None
        if path:
            try:
                if HAVE_PIL:
                    img = Image.open(path)
                    img.load()
                    self.pil_image = img.convert('RGB')
                else:
                    self.raw_photo = tk.PhotoImage(file=path)    # PNG/GIF without Pillow
            except Exception:
                pass
        self._render_picture()

    def _pic_resized(self, e=None):
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(60, self._render_picture)

    def _render_picture(self):
        self._resize_job = None
        w, h = self.pic.winfo_width() - 4, self.pic.winfo_height() - 4
        if w < 10 or h < 10 or (self.pil_image is None and self.raw_photo is None):
            self.photo = None
            self.pic.config(image='')
            return
        if self.pil_image is not None:
            iw, ih = self.pil_image.size
            k = min(w / iw, h / ih)
            size = (max(1, int(iw * k)), max(1, int(ih * k)))
            resample = Image.NEAREST if k >= 1 else Image.LANCZOS     # sharp pixels when enlarging
            self.photo = ImageTk.PhotoImage(self.pil_image.resize(size, resample))
        else:
            iw, ih = self.raw_photo.width(), self.raw_photo.height()
            if iw <= w and ih <= h:
                k = max(1, min(w // iw, h // ih))
                self.photo = self.raw_photo.zoom(k, k)
            else:
                k = max(-(-iw // w), -(-ih // h))
                self.photo = self.raw_photo.subsample(k, k)
        self.pic.config(image=self.photo)

    def _check_picture(self):
        """Back in the launcher after an F5 screenshot in CSpect: updates the picture."""
        g = self.selected()
        if g:
            new = find_image(g.folder, g.image_cfg, g.file)
            if new != g.image:
                g.image = new
                self.set_picture(new)
        self._pic_job = self.root.after(2000, self._check_picture)

    def _set_icon(self):
        if not HAVE_PIL:
            return
        ico = find_case_insensitive(os.path.dirname(S.emulator), 'ZXNext.ico')
        if os.path.isfile(ico):
            try:
                self._icon = ImageTk.PhotoImage(Image.open(ico).convert('RGBA'))
                self.root.iconphoto(True, self._icon)
            except Exception:
                pass

    # ---------- launch ----------
    def start_game(self, g):
        if not g:
            return 'break'
        # executable chosen now: the first time, or every time for games with askfile=1 (compilations)
        if (not g.file or g.ask_file) and len(g.candidates) > 1:
            if not self.select_executable(g):
                return 'break'
            self.show_game(g)
        if not g.file:
            messagebox.showwarning(APP_NAME, T('noExeMsg', g.folder), parent=self.root)
            return 'break'
        if not self.find_emulator():
            return 'break'
        cmd = []
        if not IS_WIN:
            mono = find_mono()
            if not mono:
                messagebox.showerror(APP_NAME, T('monoMissingMac' if IS_MAC else 'monoMissing'), parent=self.root)
                return 'break'
            cmd.append(mono)
        run = None
        if test_os_launch(g):
            # NextZXOS games: CSpect starts with the NextZXOS image created on the fly (-mmc= not needed)
            sd = self.find_sd_image()
            if not sd:
                return 'break'
            self.status.config(text=T('osPrep', g.title))
            self.root.config(cursor='watch')
            self.root.update()
            try:
                run = new_os_image(g, sd)
            except (OSError, RuntimeError) as ex:
                self.status.config(text='')
                messagebox.showerror(APP_NAME, T('osErr', ex), parent=self.root)
                return 'break'
            finally:
                self.root.config(cursor='')
            cmd += [S.emulator] + [a for a in split_args(g.args) if not a.lower().startswith('-mmc=')] + [run['img']]
            work_dir = os.path.dirname(g.file)      # as for the other games: F5 screenshots end up next to the game
        else:
            # working folder = folder of the executable: -mmc=./ points there,
            # save files and screenshots end up next to the game
            work_dir = os.path.dirname(g.file)
            cmd += [S.emulator] + split_args(g.args) + ['./' + os.path.basename(g.file)]
        # fixes of the CSpect Compat plugin (Compat.dll next to CSpect.exe); ignored when it is not installed
        env = None
        if g.compat:
            env = dict(os.environ, CSPECT_COMPAT=g.compat, CSPECT_COMPAT_FILE=g.file)   # dd01nop reads the .nex
        try:
            proc = subprocess.Popen(cmd, cwd=work_dir, start_new_session=not IS_WIN, env=env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status.config(text=T('launched', g.title))
            # NextZXOS games: when CSpect closes, the files saved in the image go back to the game folder
            if run:
                OS_RUNS.append(dict(run, proc=proc))
                if not self._os_watch:
                    self._os_watch = self.root.after(2000, self._watch_os_runs)
            # selected again the next time the launcher opens
            S.last_game = g.section
            try:
                set_ini_value('_default', 'lastgame', g.section)
            except OSError:
                pass
        except OSError as ex:
            messagebox.showerror(APP_NAME, T('launchErr', ex), parent=self.root)
        return 'break'

    def _watch_os_runs(self):
        """Every 2 seconds while NextZXOS games are running: copies back their saves when CSpect closes."""
        self._os_watch = None
        n = complete_os_runs()
        if n:
            self.status.config(text=T('osSaved', n))
        if OS_RUNS:
            self._os_watch = self.root.after(2000, self._watch_os_runs)

    def wait_zxos_download(self, proc, img):
        """Waiting window while ZXOS.sh downloads the image (CSpect stays black meanwhile).
        Closes by itself when CSpect is closed; True if the image is there."""
        dlg = tk.Toplevel(self.root)
        dlg.title(T('osDlTitle'))
        dlg.configure(bg=C_BACK)
        dlg.resizable(False, False)
        dlg.transient(self.root)        # not topmost: it would cover CSpect's download question
        lbl = tk.Label(dlg, text=T('osDlWait'), bg=C_BACK, fg=C_TEXT, justify='left', anchor='w', wraplength=460)
        lbl.pack(fill='x', padx=12, pady=(12, 8))
        bar = ttk.Progressbar(dlg, mode='indeterminate', length=460)
        bar.pack(padx=12)
        bar.start(15)
        row = tk.Frame(dlg, bg=C_BACK)
        row.pack(fill='x', padx=12, pady=12)
        lbl_time = tk.Label(row, bg=C_BACK, fg=C_DIM)
        lbl_time.pack(side='left')
        result = {'ok': False, 'ready': False}
        start = datetime.datetime.now()

        def cancel():
            dlg.destroy()

        tk.Button(row, text=T('cancel'), command=cancel, bg=C_PANEL, fg=C_TEXT, relief='flat',
                  width=10).pack(side='right')
        dlg.bind('<Escape>', lambda e: cancel())
        dlg.protocol('WM_DELETE_WINDOW', cancel)

        def tick():
            if not dlg.winfo_exists():
                return
            lbl_time.config(text=T('osDlTime', int((datetime.datetime.now() - start).total_seconds())))
            if not result['ready'] and os.path.isfile(img):
                result['ready'] = True
                lbl.config(text=T('osDlReady'))
                bar.stop()
                bar.config(mode='determinate', value=100)
            if proc.poll() is not None:
                result['ok'] = True
                dlg.destroy()
                return
            dlg.after(500, tick)

        tick()
        dlg.grab_set()
        self.root.wait_window(dlg)
        if not result['ok']:
            return False        # Cancel: CSpect stays open, nothing is started
        if os.path.isfile(img):
            return True
        messagebox.showwarning(APP_NAME, T('osDlFail', img), parent=self.root)
        return False

    def find_sd_image(self):
        """If the NextZXOS SD card image is missing, lets the user pick it and saves it in games.ini."""
        img = resolve_sd_image(S.sd_image_cfg)
        if os.path.isfile(img):
            return img
        # ZXOS.sh of CSpect downloads zxnext.sd into the CSpect folder when it is missing
        cs_dir = os.path.dirname(S.emulator)
        zxos = find_case_insensitive(cs_dir, 'ZXOS.bat' if IS_WIN else 'ZXOS.sh')
        if not S.sd_image_cfg and os.path.isfile(zxos):
            r = messagebox.askyesnocancel(APP_NAME, T('osNoImageDl', img), icon='warning', parent=self.root)
            if r:
                cmd = [os.environ.get('COMSPEC', 'cmd.exe'), '/c', zxos] if IS_WIN else ['bash', zxos]
                mono = None if IS_WIN else find_mono()
                try:
                    proc = subprocess.Popen(cmd, cwd=cs_dir, start_new_session=not IS_WIN,
                                            env=mono_env(mono) if mono else None,
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except OSError as ex:
                    messagebox.showerror(APP_NAME, T('launchErr', ex), parent=self.root)
                    return None
                return img if self.wait_zxos_download(proc, img) else None
            if r is None:
                return None
        elif not messagebox.askyesno(APP_NAME, T('osNoImage', img), icon='warning', parent=self.root):
            return None
        p = filedialog.askopenfilename(title=T('osPick'), initialdir=os.path.dirname(S.emulator), parent=self.root,
                                       filetypes=[(T('osFilter'), '*.sd *.img *.mmc *.hdf *.vhd'), ('*', '*')])
        if not p:
            return None
        S.sd_image_cfg = to_ini_path(p)
        try:
            set_ini_value('_default', 'nextzxos', S.sd_image_cfg)
        except OSError:
            pass
        return p

    def find_emulator(self):
        if os.path.isfile(S.emulator):
            return True
        if not messagebox.askyesno(APP_NAME, T('emuNotFound', S.emulator), icon='warning', parent=self.root):
            return False
        while True:
            d = filedialog.askdirectory(title=T('emuPick'), initialdir=ROOT, parent=self.root)
            if not d:
                return False
            exe = find_case_insensitive(d, 'CSpect.exe')
            if os.path.isfile(exe):
                try:
                    set_ini_value('_default', 'cspect', to_ini_path(d))
                except OSError:
                    pass
                S.emulator = exe
                return True
            messagebox.showwarning(APP_NAME, T('emuNotHere'), parent=self.root)

    # ---------- dialogs ----------
    def dialog(self, title, parent=None):
        d = tk.Toplevel(parent or self.root, bg=C_BACK, padx=14, pady=12)
        d.title(title)
        d.resizable(False, False)
        if parent is not None or self.root.winfo_viewable():
            d.transient(parent or self.root)
        return d

    def run_dialog(self, d, focus=None):
        d.update_idletasks()
        p = self.root
        if p.winfo_viewable():
            x = p.winfo_rootx() + (p.winfo_width() - d.winfo_reqwidth()) // 2
            y = p.winfo_rooty() + (p.winfo_height() - d.winfo_reqheight()) // 2
        else:
            x = (d.winfo_screenwidth() - d.winfo_reqwidth()) // 2
            y = (d.winfo_screenheight() - d.winfo_reqheight()) // 3
        d.geometry('+%d+%d' % (max(0, x), max(0, y)))
        d.wait_visibility()
        d.grab_set()
        d.lift()
        (focus or d).focus_force()
        d.wait_window()

    def ok_cancel(self, d, on_ok, on_cancel=None):
        row = tk.Frame(d, bg=C_BACK)
        row.pack(fill='x', pady=(12, 0))
        cancel = self.button(row, T('cancel'), on_cancel or d.destroy)
        cancel.pack(side='right')
        ok = self.button(row, T('ok'), on_ok)
        ok.pack(side='right', padx=(0, 8))
        d.bind('<Return>', lambda e: on_ok())
        d.bind('<KP_Enter>', lambda e: on_ok())
        d.bind('<Escape>', lambda e: (on_cancel or d.destroy)())
        return ok, cancel

    def select_executable(self, g):
        d = self.dialog(T('chooseTitle', g.title))
        self.label(d, T('chooseLbl'), justify='left', anchor='w').pack(fill='x')
        lb = tk.Listbox(d, bg=C_PANEL, fg=C_TEXT, selectbackground='#0078d7', relief='flat', bd=0,
                        highlightthickness=0, font=self.f_norm, width=55, height=9, activestyle='none')
        lb.pack(fill='both', expand=True, pady=(8, 0))
        for c in g.candidates:
            lb.insert('end', c)
        cur = os.path.relpath(g.file, g.folder).replace(os.sep, '/') if g.file else None
        idx = g.candidates.index(cur) if cur in g.candidates else 0
        lb.selection_set(idx)
        lb.see(idx)
        # "Always use this executable": when off, the choice is asked at every launch (askfile=1 in
        # games.ini, e.g. for compilations); on the first time, then as last saved
        always_var = tk.BooleanVar(value=not g.ask_file)
        tk.Checkbutton(d, text=T('chooseAlways'), variable=always_var, bg=C_BACK, fg=C_TEXT, selectcolor=C_PANEL,
                       activebackground=C_BACK, activeforeground=C_TEXT, font=self.f_norm, anchor='w').pack(fill='x', pady=(6, 0))
        result = {}

        def ok():
            sel = lb.curselection()
            if sel:
                result['choice'] = g.candidates[sel[0]]
            d.destroy()
        lb.bind('<Double-Button-1>', lambda e: ok())
        self.ok_cancel(d, ok)
        self.run_dialog(d, lb)
        choice = result.get('choice')
        if not choice:
            return False
        always = always_var.get()
        try:
            set_ini_value(g.section, 'file', choice)
            set_ini_value(g.section, 'askfile', '' if always else '1')
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        g.ask_file = not always
        g.file = os.path.join(g.folder, choice)
        g.image = find_image(g.folder, g.image_cfg, g.file)
        return True

    def input_box(self, title, text, value, mono=False):
        d = self.dialog(title)
        self.label(d, text, justify='left', anchor='w', wraplength=520).pack(fill='x')
        e = self.entry(d, mono=mono, width=60)
        e.pack(fill='x', pady=(10, 0), ipady=3)
        e.insert(0, value)
        e.select_range(0, 'end')
        result = {}

        def ok():
            result['v'] = e.get().strip()
            d.destroy()
        self.ok_cancel(d, ok)
        self.run_dialog(d, e)
        return result.get('v')

    def open_settings(self):
        if self.settings_dialog(False):
            self.reload_all()

    def settings_dialog(self, first_run):
        prev_lang = S.lang
        d = self.dialog(T('setTitle'))
        w = {}
        if first_run:
            w['welcome'] = self.label(d, fg=C_GOLD, justify='left', anchor='w', wraplength=560)
            w['welcome'].grid(row=0, column=0, columnspan=3, sticky='we', pady=(0, 12))

        # split the general parameters: window size (-wN), full screen (-fullscreen), the rest
        cur = ' %s ' % S.global_args
        m = re.search(r'\s-w(\d+)(?=\s)', cur)
        cur_size = int(m.group(1)) if m else 4
        if cur_size < 1 or cur_size > 4:
            cur_size = 4                     # CSpect: -w1..-w4, default 4
        cur_full = bool(re.search(r'\s-fullscreen(?=\s)', cur))
        rest = re.sub(r'\s+', ' ', re.sub(r'\s-fullscreen(?=\s)', ' ', re.sub(r'\s-w\d+(?=\s)', ' ', cur))).strip()

        def row_label(r):
            l = self.label(d, anchor='w', width=20)
            l.grid(row=r, column=0, sticky='w', pady=4)
            return l

        # language
        w['lang'] = row_label(1)
        lang_var = tk.StringVar()
        codes = [c for c, n in LANG_NAMES]
        cmb = ttk.Combobox(d, textvariable=lang_var, state='readonly', width=18, font=self.f_norm,
                           values=[n for c, n in LANG_NAMES])
        cmb.current(codes.index(S.lang) if S.lang in codes else 0)
        cmb.grid(row=1, column=1, sticky='w', pady=4)

        # games folder
        w['games'] = row_label(2)
        e_games = self.entry(d, width=46)
        e_games.insert(0, S.games_dir)
        e_games.grid(row=2, column=1, sticky='we', pady=4, ipady=3)
        self.button(d, '...', lambda: browse(e_games, T('gamesPick'))).grid(row=2, column=2, padx=(6, 0))

        # CSpect folder + download link
        w['cspect'] = row_label(3)
        e_cs = self.entry(d, width=46)
        e_cs.insert(0, os.path.dirname(S.emulator))
        e_cs.grid(row=3, column=1, sticky='we', pady=4, ipady=3)
        self.button(d, '...', lambda: browse(e_cs, T('emuPick'))).grid(row=3, column=2, padx=(6, 0))
        w['dl'] = self.link(d, '', CSPECT_URL)
        w['dl'].grid(row=4, column=1, sticky='w')

        # window size: 4 proportional boxes (1x..4x) + full screen
        w['win'] = row_label(5)
        size_var = tk.IntVar(value=cur_size)
        sizes = tk.Frame(d, bg=C_BACK, height=64)
        sizes.grid(row=5, column=1, columnspan=2, sticky='we', pady=(10, 4))
        x = 0
        for n in range(1, 5):
            bw, bh = 30 + 14 * n, 22 + 10 * n
            rb = tk.Radiobutton(sizes, text='%dx' % n, variable=size_var, value=n, indicatoron=False,
                                bg=C_PANEL, fg=C_TEXT, selectcolor=C_PLAY, activebackground='#33333b',
                                activeforeground=C_TEXT, relief='flat', bd=1, highlightthickness=1,
                                highlightbackground=C_DIM, font=self.f_norm, cursor='hand2')
            rb.place(x=x, y=62 - bh, width=bw, height=bh)
            x += bw + 10
        full_var = tk.BooleanVar(value=cur_full)
        w['full'] = tk.Checkbutton(sizes, variable=full_var, bg=C_BACK, fg=C_TEXT, selectcolor=C_PANEL,
                                   activebackground=C_BACK, activeforeground=C_TEXT, highlightthickness=0,
                                   font=self.f_norm)
        w['full'].place(x=x + 15, y=36)

        # other parameters
        w['args'] = row_label(6)
        e_args = self.entry(d, mono=True, width=46)
        e_args.insert(0, rest)
        e_args.grid(row=6, column=1, columnspan=2, sticky='we', pady=4, ipady=3)

        # information: name, version, copyright, links
        tk.Frame(d, bg=C_PANEL, height=1).grid(row=7, column=0, columnspan=3, sticky='we', pady=(14, 8))
        w['app'] = self.label(d, fg=C_DIM, anchor='w')
        w['app'].grid(row=8, column=0, columnspan=3, sticky='w')
        w['upd'] = self.label(d, fg=C_DIM, anchor='w')
        w['upd'].grid(row=9, column=0, sticky='w')
        self.link(d, APP_URL, APP_URL).grid(row=9, column=1, columnspan=2, sticky='w')
        w['emu'] = self.label(d, fg=C_DIM, anchor='w')
        w['emu'].grid(row=10, column=0, columnspan=2, sticky='w')
        self.link(d, CSPECT_URL, CSPECT_URL).grid(row=10, column=1, columnspan=2, sticky='e')

        btns = tk.Frame(d, bg=C_BACK)
        btns.grid(row=11, column=0, columnspan=3, sticky='e', pady=(14, 0))
        result = {}

        def browse(entry, title):
            start = entry.get() if os.path.isdir(entry.get()) else ROOT
            p = filedialog.askdirectory(title=title, initialdir=start, parent=d)
            if p:
                entry.delete(0, 'end')
                entry.insert(0, p)

        def texts():
            d.title(T('setTitle'))
            if 'welcome' in w:
                w['welcome'].config(text=T('welcome'))
            w['lang'].config(text=T('setLang'))
            w['games'].config(text=T('setGames'))
            w['cspect'].config(text=T('setCSpect'))
            w['dl'].config(text=T('dlCSpect'))
            w['win'].config(text=T('setWinSize'))
            w['full'].config(text=T('setFullscreen'))
            w['args'].config(text=T('setArgs'))
            w['app'].config(text='%s  -  %s  -  %s' % (APP_NAME, T('aboutVersion', APP_VERSION), APP_COPYRIGHT))
            w['upd'].config(text=T('aboutUpdates'))
            w['emu'].config(text=T('aboutEmu'))
            b_ok.config(text=T('ok'))
            b_cancel.config(text=T('cancel'))

        def lang_changed(e=None):
            S.lang = codes[cmb.current()]
            texts()

        def ok():
            g = resolve_dir(e_games.get(), 'GAMES')
            if not os.path.isdir(g):
                messagebox.showwarning(APP_NAME, T('gamesMissing') + '\n' + g, parent=d)
                return
            emu = resolve_emulator(e_cs.get())
            if not os.path.isfile(emu):
                messagebox.showwarning(APP_NAME, T('emuNotHere') + '\n' + os.path.dirname(emu), parent=d)
                return
            # rebuild the parameters: -wN + other parameters + -fullscreen
            other = re.sub(r'\s-fullscreen(?=\s)', ' ', re.sub(r'\s-w\d+(?=\s)', ' ', ' %s ' % e_args.get()))
            other = re.sub(r'\s+', ' ', other).strip()
            gargs = '-w%d' % size_var.get() + (' ' + other if other else '') + (' -fullscreen' if full_var.get() else '')
            result.update(lang=codes[cmb.current()], games=to_ini_path(g),
                          cspect=to_ini_path(os.path.dirname(emu)), args=gargs)
            d.destroy()

        def cancel():
            d.destroy()

        b_cancel = self.button(btns, '', cancel)
        b_cancel.pack(side='right')
        b_ok = self.button(btns, '', ok)
        b_ok.pack(side='right', padx=(0, 8))
        d.bind('<Escape>', lambda e: cancel())
        d.bind('<Return>', lambda e: ok())
        cmb.bind('<<ComboboxSelected>>', lang_changed)
        texts()
        self.run_dialog(d)

        if not result:
            S.lang = prev_lang
            return False
        try:
            if not os.path.isfile(INI_PATH):
                new_ini_file(result['lang'], result['games'], result['cspect'], result['args'])
            else:
                for k in ('lang', 'games', 'cspect', 'args'):
                    set_ini_value('_default', k, result[k])
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        load_settings()
        return True

    # ---------- right-click menu ----------
    def _context_menu(self, e):
        i = self.lst.nearest(e.y)
        if i < 0 or i >= len(self.view):
            return
        bbox = self.lst.bbox(i)
        if bbox and not (bbox[1] <= e.y <= bbox[1] + bbox[3]):
            return
        self.select_index(i)
        g = self.view[i]
        m = self.menu
        m.delete(0, 'end')
        m.add_command(label=T('chooseMenu'), command=lambda: self._choose(g),
                      state='normal' if g.candidates else 'disabled')
        m.add_command(label=T('argsMenu'), command=lambda: self._args(g))
        m.add_command(label=T('renameMenu'), command=lambda: self._rename(g))
        m.add_command(label=T('unhideMenu') if g.hidden else T('hideMenu'), command=lambda: self._hide(g))
        m.add_command(label=T('delSavMenu'), command=lambda: self._del_saves(g),
                      state='normal' if get_save_files(g) else 'disabled')
        m.add_command(label=T('openFolderMenu'), command=lambda: self._open_folder(g))
        # only for .tap games: the chosen executable, or any candidate when none is chosen yet
        if g.file:
            is_tap = g.file.lower().endswith('.tap')
        else:
            is_tap = any(c.lower().endswith('.tap') for c in g.candidates)
        if is_tap:
            self.tap48_var.set(g.tap48)
            m.add_checkbutton(label=T('tap48Menu'), variable=self.tap48_var, command=lambda: self._tap48(g),
                              selectcolor=C_TEXT)
        sub = tk.Menu(m, tearoff=0, bg=C_PANEL, fg=C_TEXT, activebackground='#0078d7', activeforeground='white')
        # start with NextZXOS: also a compatibility choice
        self.boot_os_var.set(g.boot_os)
        nex = any(os.path.splitext(c)[1].lower() in OS_NEX_EXTS for c in g.candidates)
        sub.add_checkbutton(label=T('osMenu'), variable=self.boot_os_var, command=lambda: self._boot_os(g),
                            state='normal' if nex else 'disabled', selectcolor=C_TEXT)
        sub.add_separator()
        current = compat_list(g)
        for opt, key in COMPAT_OPTIONS.items():
            self.compat_vars[opt].set(opt in current)
            sub.add_checkbutton(label=T(key), variable=self.compat_vars[opt], selectcolor=C_TEXT,
                                command=lambda o=opt: self._switch_compat(g, o))
        m.add_cascade(label=T('compatMenu'), menu=sub)
        m.add_separator()
        self.show_hidden_var.set(S.show_hidden)
        m.add_checkbutton(label=T('showHiddenMenu'), variable=self.show_hidden_var, command=self._toggle_hidden,
                          selectcolor=C_TEXT)
        m.add_separator()
        m.add_command(label=HEART + '  ' + (T('favRemove') if g.favorite else T('favAdd')), command=lambda: self._favorite(g))
        m.tk_popup(e.x_root, e.y_root)

    def _open_folder(self, g):
        """Opens the game folder in the file manager (on Windows and macOS with the executable selected)."""
        f = g.file if g.file and os.path.isfile(g.file) else None
        if IS_WIN:
            cmd = ['explorer', '/select,' + f] if f else ['explorer', g.folder]
        elif IS_MAC:
            cmd = ['open', '-R', f] if f else ['open', g.folder]
        else:
            cmd = ['xdg-open', g.folder]
        try:
            subprocess.Popen(cmd, start_new_session=not IS_WIN, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as ex:
            messagebox.showerror(APP_NAME, T('launchErr', ex), parent=self.root)

    def _choose(self, g):
        if self.select_executable(g):
            self.show_game(g)

    def _args(self, g):
        v = self.input_box(T('argsTitle', g.title), T('argsLbl', S.global_args), g.args_cfg, mono=True)
        if v is None:
            return
        try:
            set_ini_value(g.section, 'args', v)
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        g.args_cfg = v
        g.args = v or S.global_args
        self.show_game(g)

    def _rename(self, g):
        v = self.input_box(T('renameTitle', g.title), T('renameLbl', g.section), g.title_cfg or g.section)
        if v is None:
            return
        if v == g.section:
            v = ''
        try:
            set_ini_value(g.section, 'title', v)
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        g.title_cfg = v
        g.title = v or g.section
        update_display(g)
        self.refresh_list()

    def _favorite(self, g):
        """Adds / removes the game from the favorites (favorite=1 in games.ini)."""
        g.favorite = not g.favorite
        try:
            set_ini_value(g.section, 'favorite', '1' if g.favorite else '')
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        update_display(g)
        self.refresh_list()

    def _boot_os(self, g):
        """Starts the .nex/.snx/.sna through NextZXOS instead of CSpect's own loader (boot=nextzxos)."""
        g.boot_os = self.boot_os_var.get()
        try:
            set_ini_value(g.section, 'boot', 'nextzxos' if g.boot_os else '')
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        self.show_game(g)

    def _tap48(self, g):
        """.tap loaded in 48K mode instead of 128K (tapmode=48), for games that need it."""
        g.tap48 = self.tap48_var.get()
        try:
            set_ini_value(g.section, 'tapmode', '48' if g.tap48 else '')
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        self.show_game(g)

    def _switch_compat(self, g, opt):
        """Fixes of the CSpect Compat plugin for old games that crash in CSpect 3 (compat=, comma-separated)."""
        current = [o for o in compat_list(g) if o != opt]
        if self.compat_vars[opt].get():
            current.append(opt)
        g.compat = ','.join(current)
        try:
            set_ini_value(g.section, 'compat', g.compat)
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        self.show_game(g)

    def _fav_filter(self):
        """Heart button: shows only the favorite games (favonly=1, remembered)."""
        S.fav_only = self.fav_var.get()
        self.chk_fav.config(fg='white' if S.fav_only else C_DIM)
        try:
            set_ini_value('_default', 'favonly', '1' if S.fav_only else '')
        except OSError:
            pass
        self.refresh_list()

    def _hide(self, g):
        g.hidden = not g.hidden
        try:
            set_ini_value(g.section, 'hidden', '1' if g.hidden else '')
        except OSError as ex:
            messagebox.showwarning(APP_NAME, T('saveErr', ex), parent=self.root)
        update_display(g)
        self.refresh_list()

    def _toggle_hidden(self):
        S.show_hidden = self.show_hidden_var.get()
        self.refresh_list()

    def _del_saves(self, g):
        files = get_save_files(g)
        if not files:
            return
        names = '\n'.join(os.path.relpath(f, g.folder) for f in files)
        if not messagebox.askyesno(APP_NAME, T('delSavConfirm', len(files), g.title, names),
                                   default='no', parent=self.root):
            return
        n = 0
        for f in files:
            try:
                move_to_trash(f)
                n += 1
            except Exception as ex:
                messagebox.showwarning(APP_NAME, T('delSavErr', '%s\n%s' % (f, ex)), parent=self.root)
        self.status.config(text=T('delSavDone', n))

    # ---------- start ----------
    def run(self):
        if not os.path.isfile(INI_PATH):
            self.root.withdraw()
            load_settings()
            if not self.settings_dialog(True):
                self.root.destroy()
                return
            self.root.deiconify()
        self.reload_all()
        self.paned.paneconfigure(self.left, width=S.list_width)
        # window size saved on exit (at most as big as the screen)
        w, h = S.win_size or (960, 600)
        w = max(w, S.list_width + 600)
        w, h = min(w, self.root.winfo_screenwidth()), min(h, self.root.winfo_screenheight())
        self.root.geometry('%dx%d' % (w, h))
        self._normal_size = (w, h)
        self.root.bind('<Configure>', self._root_configured, add='+')
        if S.win_max:
            self._set_zoomed()
        self.root.protocol('WM_DELETE_WINDOW', self._quit)
        # the last game started is selected again
        i = next((i for i, g in enumerate(self.view) if g.section.lower() == S.last_game.lower()), -1) if S.last_game else -1
        if i >= 0:
            self.select_index(i)
        self.txt_search.focus_set()
        self._pic_job = self.root.after(2000, self._check_picture)
        self.root.mainloop()


def main():
    root = tk.Tk()
    Launcher(root).run()


if __name__ == '__main__':
    main()

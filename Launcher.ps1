# ============================================================
#  CSpect Launcher - frontend per i giochi ZX Spectrum Next
#  Avvio: doppio clic su "Launcher.bat"
#  Impostazioni in games.ini (creato al primo avvio)
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
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName Microsoft.VisualBasic     # per spostare i file nel Cestino
[System.Windows.Forms.Application]::EnableVisualStyles()

# ---------- informazioni sul programma (finestra Info) ----------
$AppName      = 'CSpect Launcher'
$AppVersion   = '1.0'
$AppCopyright = '(c) 2026 Giuseppe Papa - GPL-3.0'
$AppUrl       = 'https://github.com/Saxabar/CSpectLauncher'   # pagina per gli aggiornamenti
$CSpectUrl    = 'https://mdf200.itch.io/cspect'

$Root        = $PSScriptRoot
$IniPath     = Join-Path $Root 'games.ini'
$GameExts    = @('.nex', '.snx', '.sna')
$ImageExts   = @('.png', '.jpg', '.jpeg', '.gif', '.bmp')
$DefaultArgs = '-w2 -vsync -zxnext -mmc=.\'

# valori predefiniti, sovrascritti da [_default] in games.ini
$script:GamesDir       = Join-Path $Root 'GAMES'                # games=
$script:Emulator       = Join-Path $Root 'CSpect\CSpect.exe'    # cspect=
$script:GlobalArgs     = $DefaultArgs                           # args=
$script:Lang           = 'en'                                   # lang=  (en, it, es, fr, de)
$script:SortMode       = 'name'                                 # sort=  (name, rating)
$script:ListWidth      = 368                                    # listwidth=
$script:ShowHidden     = $false                                 # mostra anche i giochi nascosti (solo per la sessione)

# ============================================================
#  Traduzioni
# ============================================================
$LangNames = [ordered]@{ en = 'English'; it = 'Italiano'; es = 'Español'; fr = 'Français'; de = 'Deutsch' }

$script:Strings = @{
  en = @{
    argsMenu = 'Launch parameters...'; renameMenu = 'Rename title...'
    argsTitle = 'Launch parameters - {0}'
    argsLbl = "Custom CSpect parameters for this game.`nLeave empty to use the general ones:`n{0}"
    renameTitle = 'Rename - {0}'
    renameLbl = "Title shown in the list.`nLeave empty to use the folder name:`n{0}"
    setArgs = 'Other parameters:'; setWinSize = 'Window size:'; setFullscreen = 'Full screen'; dlCSpect = 'Download CSpect'; customTag = '(custom)'
    hideMenu = 'Hide game'; unhideMenu = 'Show game again'; showHiddenMenu = 'Show hidden games'
    hiddenTag = '(hidden)'; delSavMenu = 'Delete save files (.sav)...'
    delSavConfirm = "Delete {0} save file(s) of {1}?`n`n{2}`n`nThe files are moved to the Recycle Bin."
    delSavDone = 'Save files deleted: {0}'; delSavErr = "Cannot delete:`n{0}"
    info = 'Info'; aboutTitle = 'About'; aboutVersion = 'Version {0}'
    aboutUpdates = 'Updates and news:'; aboutEmu = 'Emulator: CSpect by Mike Dailly'
    search = 'Search:'; sortLbl = 'Sort:'; sortName = 'Name'; sortRating = 'Rating'
    sortTip = 'Sort the list by name or by rating'
    play = 'PLAY'; noRating = 'no rating'; unplayable = '(not launchable)'
    fileLine = "File: {0}`nParameters: {1}"
    fileChoose = "File: to be chosen on first launch ({0} executables)`nParameters: {1}"
    noFile = 'No .nex/.snx/.sna file - set it in games.ini'
    status = '{0} of {1} games   -   Enter/double-click: play   Ctrl+1..5: rating   F5: reload   Esc: exit'
    launched = 'Launched: {0}'; launchErr = "Launch error:`n{0}"
    chooseMenu = 'Choose executable...'; chooseTitle = 'Choose executable - {0}'
    chooseLbl = "Which executable do you want to use?`n(the choice is saved in games.ini)"
    ok = 'OK'; cancel = 'Cancel'
    saveErr = "Cannot save to games.ini:`n{0}"
    noExeMsg = "No .nex / .snx / .sna file found in:`n{0}`n`nSet the file to launch in games.ini (file= key)."
    emuNotFound = "CSpect.exe not found in:`n{0}`n`nDo you want to select the CSpect folder?"
    emuPick = 'Select the folder containing CSpect.exe'
    emuNotHere = 'CSpect.exe is not in this folder.'
    settings = 'Settings'; setTitle = 'Settings'
    welcome = 'Welcome! games.ini was not found: choose the language and the folders to start.'
    setLang = 'Language:'; setGames = 'Games folder:'; setCSpect = 'CSpect folder:'
    gamesPick = 'Select the folder containing the games (one subfolder per game)'
    gamesMissing = 'The games folder does not exist.'
  }
  it = @{
    argsMenu = 'Parametri di avvio...'; renameMenu = 'Rinomina titolo...'
    argsTitle = 'Parametri di avvio - {0}'
    argsLbl = "Parametri CSpect personalizzati per questo gioco.`nLascia vuoto per usare quelli generali:`n{0}"
    renameTitle = 'Rinomina - {0}'
    renameLbl = "Titolo mostrato nella lista.`nLascia vuoto per usare il nome della cartella:`n{0}"
    setArgs = 'Altri parametri:'; setWinSize = 'Grandezza finestra:'; setFullscreen = 'Schermo intero'; dlCSpect = 'Scarica CSpect'; customTag = '(personalizzati)'
    hideMenu = 'Nascondi gioco'; unhideMenu = 'Mostra di nuovo il gioco'; showHiddenMenu = 'Mostra giochi nascosti'
    hiddenTag = '(nascosto)'; delSavMenu = 'Elimina salvataggi (.sav)...'
    delSavConfirm = "Eliminare {0} file di salvataggio di {1}?`n`n{2}`n`nI file vengono spostati nel Cestino."
    delSavDone = 'Salvataggi eliminati: {0}'; delSavErr = "Impossibile eliminare:`n{0}"
    info = 'Info'; aboutTitle = 'Informazioni'; aboutVersion = 'Versione {0}'
    aboutUpdates = 'Aggiornamenti e novità:'; aboutEmu = 'Emulatore: CSpect di Mike Dailly'
    search = 'Cerca:'; sortLbl = 'Ordina:'; sortName = 'Nome'; sortRating = 'Voto'
    sortTip = 'Ordina la lista per nome o per voto'
    play = 'GIOCA'; noRating = 'nessun voto'; unplayable = '(non avviabile)'
    fileLine = "File: {0}`nParametri: {1}"
    fileChoose = "File: da scegliere al primo avvio ({0} eseguibili)`nParametri: {1}"
    noFile = 'Nessun file .nex/.snx/.sna - impostalo in games.ini'
    status = '{0} di {1} giochi   -   Invio/doppio clic: gioca   Ctrl+1..5: voto   F5: ricarica   Esc: esci'
    launched = 'Avviato: {0}'; launchErr = "Errore nell'avvio:`n{0}"
    chooseMenu = 'Scegli eseguibile...'; chooseTitle = "Scegli l'eseguibile - {0}"
    chooseLbl = "Quale eseguibile vuoi usare?`n(la scelta viene salvata in games.ini)"
    ok = 'OK'; cancel = 'Annulla'
    saveErr = "Impossibile salvare in games.ini:`n{0}"
    noExeMsg = "Nessun file .nex / .snx / .sna trovato in:`n{0}`n`nIndica il file da lanciare in games.ini (chiave file=)."
    emuNotFound = "CSpect.exe non trovato in:`n{0}`n`nVuoi indicare la cartella di CSpect?"
    emuPick = 'Seleziona la cartella che contiene CSpect.exe'
    emuNotHere = "In questa cartella non c'è CSpect.exe."
    settings = 'Impostazioni'; setTitle = 'Impostazioni'
    welcome = 'Benvenuto! games.ini non è stato trovato: scegli la lingua e le cartelle per iniziare.'
    setLang = 'Lingua:'; setGames = 'Cartella giochi:'; setCSpect = 'Cartella CSpect:'
    gamesPick = 'Seleziona la cartella che contiene i giochi (una sottocartella per gioco)'
    gamesMissing = 'La cartella dei giochi non esiste.'
  }
  es = @{
    argsMenu = 'Parámetros de inicio...'; renameMenu = 'Renombrar título...'
    argsTitle = 'Parámetros de inicio - {0}'
    argsLbl = "Parámetros de CSpect personalizados para este juego.`nDéjalo vacío para usar los generales:`n{0}"
    renameTitle = 'Renombrar - {0}'
    renameLbl = "Título mostrado en la lista.`nDéjalo vacío para usar el nombre de la carpeta:`n{0}"
    setArgs = 'Otros parámetros:'; setWinSize = 'Tamaño de ventana:'; setFullscreen = 'Pantalla completa'; dlCSpect = 'Descargar CSpect'; customTag = '(personalizados)'
    hideMenu = 'Ocultar juego'; unhideMenu = 'Volver a mostrar el juego'; showHiddenMenu = 'Mostrar juegos ocultos'
    hiddenTag = '(oculto)'; delSavMenu = 'Borrar partidas guardadas (.sav)...'
    delSavConfirm = "¿Borrar {0} archivo(s) de partida de {1}?`n`n{2}`n`nLos archivos se mueven a la Papelera de reciclaje."
    delSavDone = 'Partidas borradas: {0}'; delSavErr = "No se puede borrar:`n{0}"
    info = 'Info'; aboutTitle = 'Acerca de'; aboutVersion = 'Versión {0}'
    aboutUpdates = 'Actualizaciones y novedades:'; aboutEmu = 'Emulador: CSpect de Mike Dailly'
    search = 'Buscar:'; sortLbl = 'Ordenar:'; sortName = 'Nombre'; sortRating = 'Nota'
    sortTip = 'Ordenar la lista por nombre o por nota'
    play = 'JUGAR'; noRating = 'sin nota'; unplayable = '(no ejecutable)'
    fileLine = "Archivo: {0}`nParámetros: {1}"
    fileChoose = "Archivo: a elegir en el primer inicio ({0} ejecutables)`nParámetros: {1}"
    noFile = 'Ningún archivo .nex/.snx/.sna - indícalo en games.ini'
    status = '{0} de {1} juegos   -   Intro/doble clic: jugar   Ctrl+1..5: nota   F5: recargar   Esc: salir'
    launched = 'Iniciado: {0}'; launchErr = "Error al iniciar:`n{0}"
    chooseMenu = 'Elegir ejecutable...'; chooseTitle = 'Elegir ejecutable - {0}'
    chooseLbl = "¿Qué ejecutable quieres usar?`n(la elección se guarda en games.ini)"
    ok = 'Aceptar'; cancel = 'Cancelar'
    saveErr = "No se puede guardar en games.ini:`n{0}"
    noExeMsg = "No se encontró ningún archivo .nex / .snx / .sna en:`n{0}`n`nIndica el archivo a ejecutar en games.ini (clave file=)."
    emuNotFound = "No se encontró CSpect.exe en:`n{0}`n`n¿Quieres indicar la carpeta de CSpect?"
    emuPick = 'Selecciona la carpeta que contiene CSpect.exe'
    emuNotHere = 'CSpect.exe no está en esta carpeta.'
    settings = 'Ajustes'; setTitle = 'Ajustes'
    welcome = '¡Bienvenido! No se encontró games.ini: elige el idioma y las carpetas para empezar.'
    setLang = 'Idioma:'; setGames = 'Carpeta de juegos:'; setCSpect = 'Carpeta de CSpect:'
    gamesPick = 'Selecciona la carpeta que contiene los juegos (una subcarpeta por juego)'
    gamesMissing = 'La carpeta de juegos no existe.'
  }
  fr = @{
    argsMenu = 'Paramètres de lancement...'; renameMenu = 'Renommer le titre...'
    argsTitle = 'Paramètres de lancement - {0}'
    argsLbl = "Paramètres CSpect personnalisés pour ce jeu.`nLaissez vide pour utiliser les paramètres généraux :`n{0}"
    renameTitle = 'Renommer - {0}'
    renameLbl = "Titre affiché dans la liste.`nLaissez vide pour utiliser le nom du dossier :`n{0}"
    setArgs = 'Autres paramètres :'; setWinSize = 'Taille de la fenêtre :'; setFullscreen = 'Plein écran'; dlCSpect = 'Télécharger CSpect'; customTag = '(personnalisés)'
    hideMenu = 'Masquer le jeu'; unhideMenu = 'Afficher à nouveau le jeu'; showHiddenMenu = 'Afficher les jeux masqués'
    hiddenTag = '(masqué)'; delSavMenu = 'Supprimer les sauvegardes (.sav)...'
    delSavConfirm = "Supprimer {0} fichier(s) de sauvegarde de {1} ?`n`n{2}`n`nLes fichiers sont placés dans la Corbeille."
    delSavDone = 'Sauvegardes supprimées : {0}'; delSavErr = "Impossible de supprimer :`n{0}"
    info = 'Infos'; aboutTitle = 'À propos'; aboutVersion = 'Version {0}'
    aboutUpdates = 'Mises à jour et nouveautés :'; aboutEmu = 'Émulateur : CSpect de Mike Dailly'
    search = 'Rechercher :'; sortLbl = 'Trier :'; sortName = 'Nom'; sortRating = 'Note'
    sortTip = 'Trier la liste par nom ou par note'
    play = 'JOUER'; noRating = 'pas de note'; unplayable = '(non lançable)'
    fileLine = "Fichier : {0}`nParamètres : {1}"
    fileChoose = "Fichier : à choisir au premier lancement ({0} exécutables)`nParamètres : {1}"
    noFile = 'Aucun fichier .nex/.snx/.sna - indiquez-le dans games.ini'
    status = '{0} sur {1} jeux   -   Entrée/double-clic : jouer   Ctrl+1..5 : note   F5 : recharger   Échap : quitter'
    launched = 'Lancé : {0}'; launchErr = "Erreur au lancement :`n{0}"
    chooseMenu = "Choisir l'exécutable..."; chooseTitle = "Choisir l'exécutable - {0}"
    chooseLbl = "Quel exécutable voulez-vous utiliser ?`n(le choix est enregistré dans games.ini)"
    ok = 'OK'; cancel = 'Annuler'
    saveErr = "Impossible d'enregistrer dans games.ini :`n{0}"
    noExeMsg = "Aucun fichier .nex / .snx / .sna trouvé dans :`n{0}`n`nIndiquez le fichier à lancer dans games.ini (clé file=)."
    emuNotFound = "CSpect.exe introuvable dans :`n{0}`n`nVoulez-vous indiquer le dossier de CSpect ?"
    emuPick = 'Sélectionnez le dossier contenant CSpect.exe'
    emuNotHere = "CSpect.exe n'est pas dans ce dossier."
    settings = 'Paramètres'; setTitle = 'Paramètres'
    welcome = "Bienvenue ! games.ini est introuvable : choisissez la langue et les dossiers pour commencer."
    setLang = 'Langue :'; setGames = 'Dossier des jeux :'; setCSpect = 'Dossier de CSpect :'
    gamesPick = 'Sélectionnez le dossier contenant les jeux (un sous-dossier par jeu)'
    gamesMissing = "Le dossier des jeux n'existe pas."
  }
  de = @{
    argsMenu = 'Startparameter...'; renameMenu = 'Titel umbenennen...'
    argsTitle = 'Startparameter - {0}'
    argsLbl = "Eigene CSpect-Parameter für dieses Spiel.`nLeer lassen, um die allgemeinen zu verwenden:`n{0}"
    renameTitle = 'Umbenennen - {0}'
    renameLbl = "In der Liste angezeigter Titel.`nLeer lassen, um den Ordnernamen zu verwenden:`n{0}"
    setArgs = 'Weitere Parameter:'; setWinSize = 'Fenstergröße:'; setFullscreen = 'Vollbild'; dlCSpect = 'CSpect herunterladen'; customTag = '(eigene)'
    hideMenu = 'Spiel ausblenden'; unhideMenu = 'Spiel wieder anzeigen'; showHiddenMenu = 'Ausgeblendete Spiele anzeigen'
    hiddenTag = '(ausgeblendet)'; delSavMenu = 'Spielstände löschen (.sav)...'
    delSavConfirm = "{0} Spielstand-Datei(en) von {1} löschen?`n`n{2}`n`nDie Dateien werden in den Papierkorb verschoben."
    delSavDone = 'Spielstände gelöscht: {0}'; delSavErr = "Löschen nicht möglich:`n{0}"
    info = 'Info'; aboutTitle = 'Über'; aboutVersion = 'Version {0}'
    aboutUpdates = 'Updates und Neuigkeiten:'; aboutEmu = 'Emulator: CSpect von Mike Dailly'
    search = 'Suchen:'; sortLbl = 'Sortieren:'; sortName = 'Name'; sortRating = 'Wertung'
    sortTip = 'Liste nach Name oder Wertung sortieren'
    play = 'SPIELEN'; noRating = 'keine Wertung'; unplayable = '(nicht startbar)'
    fileLine = "Datei: {0}`nParameter: {1}"
    fileChoose = "Datei: wird beim ersten Start gewählt ({0} Programme)`nParameter: {1}"
    noFile = 'Keine .nex/.snx/.sna-Datei - in games.ini festlegen'
    status = '{0} von {1} Spielen   -   Enter/Doppelklick: spielen   Strg+1..5: Wertung   F5: neu laden   Esc: beenden'
    launched = 'Gestartet: {0}'; launchErr = "Fehler beim Start:`n{0}"
    chooseMenu = 'Programm wählen...'; chooseTitle = 'Programm wählen - {0}'
    chooseLbl = "Welches Programm möchtest du verwenden?`n(die Auswahl wird in games.ini gespeichert)"
    ok = 'OK'; cancel = 'Abbrechen'
    saveErr = "Speichern in games.ini nicht möglich:`n{0}"
    noExeMsg = "Keine .nex / .snx / .sna-Datei gefunden in:`n{0}`n`nLege die zu startende Datei in games.ini fest (Schlüssel file=)."
    emuNotFound = "CSpect.exe nicht gefunden in:`n{0}`n`nMöchtest du den CSpect-Ordner auswählen?"
    emuPick = 'Wähle den Ordner mit CSpect.exe'
    emuNotHere = 'CSpect.exe befindet sich nicht in diesem Ordner.'
    settings = 'Einstellungen'; setTitle = 'Einstellungen'
    welcome = 'Willkommen! games.ini wurde nicht gefunden: wähle Sprache und Ordner, um zu beginnen.'
    setLang = 'Sprache:'; setGames = 'Spieleordner:'; setCSpect = 'CSpect-Ordner:'
    gamesPick = 'Wähle den Ordner mit den Spielen (ein Unterordner pro Spiel)'
    gamesMissing = 'Der Spieleordner existiert nicht.'
  }
}

# testo tradotto; parametri opzionali per {0}, {1}...
function T([string]$key) {
    $s = $script:Strings[$script:Lang][$key]
    if (-not $s) { $s = $script:Strings['en'][$key] }
    if (-not $s) { $s = $key }
    if ($args.Count -gt 0) { $s = [string]::Format($s, [object[]]$args) }
    return $s
}

# ============================================================
#  games.ini
# ============================================================
function Read-Ini([string]$path) {
    $ini = @{}
    $sec = $null
    if (-not (Test-Path -LiteralPath $path)) { return $ini }
    foreach ($line in (Get-Content -LiteralPath $path -Encoding UTF8)) {
        $l = $line.Trim()
        if ($l -eq '' -or $l.StartsWith(';') -or $l.StartsWith('#')) { continue }
        if ($l -match '^\[(.+)\]$') { $sec = $Matches[1].Trim(); $ini[$sec] = @{}; continue }
        if ($sec -and $l -match '^([^=]+)=(.*)$') { $ini[$sec][$Matches[1].Trim()] = $Matches[2].Trim() }
    }
    return $ini
}

# scrive un valore mantenendo il resto del file
function Set-IniValue([string]$section, [string]$key, [string]$value) {
    $lines = New-Object System.Collections.Generic.List[string]
    if (Test-Path -LiteralPath $IniPath) {
        foreach ($l in [System.IO.File]::ReadAllLines($IniPath)) { $lines.Add($l) }
    }
    $start = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Trim() -eq "[$section]") { $start = $i; break }
    }
    if ($start -lt 0) {
        $lines.Add(''); $lines.Add("[$section]"); $lines.Add("$key=$value")
    } else {
        $end = $lines.Count
        for ($i = $start + 1; $i -lt $lines.Count; $i++) {
            if ($lines[$i].Trim() -match '^\[.+\]$') { $end = $i; break }
        }
        $done = $false
        for ($i = $start + 1; $i -lt $end; $i++) {
            if ($lines[$i] -match "^\s*$([regex]::Escape($key))\s*=") { $lines[$i] = "$key=$value"; $done = $true; break }
        }
        if (-not $done) { $lines.Insert($start + 1, "$key=$value") }
    }
    $enc = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($IniPath, ([string]::Join("`r`n", $lines) + "`r`n"), $enc)
}

# crea games.ini al primo avvio
function New-IniFile([string]$lang, [string]$games, [string]$cspect, [string]$gargs) {
    if (-not $gargs) { $gargs = $DefaultArgs }
    $txt = @(
        '; ============================================================'
        ';  CSpect Launcher settings'
        '; ============================================================'
        ';  games=          games folder (one subfolder per game),'
        ';                  absolute (D:\...) or relative to this folder (.\GAMES)'
        ';  cspect=         CSpect folder (or path of CSpect.exe), absolute or relative'
        ';  lang=           language: en, it, es, fr, de'
        ';  args=           CSpect parameters for all games'
        ';  sort=           list order: name or rating'
        ';  listwidth=      list width in pixels (also by dragging the divider)'
        ';'
        ';  Per game: file= (executable), rating=1..5, hidden=1 (hidden game),'
        ';  title= image= args= optional'
        '; ============================================================'
        ''
        '[_default]'
        "lang=$lang"
        "games=$games"
        "cspect=$cspect"
        "args=$gargs"
        'sort=name'
        'listwidth=368'
        ''
    ) -join "`r`n"
    $enc = New-Object System.Text.UTF8Encoding($true)
    [System.IO.File]::WriteAllText($IniPath, $txt, $enc)
}

# toglie le sezioni dei giochi la cui cartella non esiste piu'
function Remove-OrphanSections([string[]]$existing) {
    if (-not (Test-Path -LiteralPath $IniPath)) { return }
    if (-not $existing -or $existing.Count -eq 0) { return }   # cartella giochi vuota/irraggiungibile: non tocca nulla
    $names = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($n in $existing) { [void]$names.Add($n) }
    [void]$names.Add('_default')

    $lines = [System.IO.File]::ReadAllLines($IniPath)
    $out = New-Object System.Collections.Generic.List[string]
    $skip = $false; $removed = 0
    foreach ($l in $lines) {
        if ($l.Trim() -match '^\[(.+)\]$') {
            $skip = -not $names.Contains($Matches[1].Trim())
            if ($skip) {
                $removed++
                while ($out.Count -gt 0 -and $out[$out.Count - 1].Trim() -eq '') { $out.RemoveAt($out.Count - 1) }
                if ($out.Count -gt 0) { $out.Add('') }
                continue
            }
        }
        if (-not $skip) { $out.Add($l) }
    }
    if ($removed -gt 0) {
        try { Copy-Item -LiteralPath $IniPath -Destination ($IniPath + '.bak') -Force } catch {}
        while ($out.Count -gt 0 -and $out[$out.Count - 1].Trim() -eq '') { $out.RemoveAt($out.Count - 1) }
        $enc = New-Object System.Text.UTF8Encoding($true)
        [System.IO.File]::WriteAllText($IniPath, ([string]::Join("`r`n", $out) + "`r`n"), $enc)
    }
}

# ============================================================
#  Percorsi
# ============================================================
# cartella da impostazione (assoluta o relativa al launcher)
function Resolve-Dir([string]$value, [string]$default) {
    $p = "$value".Trim().Trim('"')
    if (-not $p) { $p = $default }
    if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path $Root $p }
    return [System.IO.Path]::GetFullPath($p).TrimEnd('\')
}

# CSpect.exe da cspect= (cartella o .exe)
function Resolve-Emulator([string]$value) {
    $p = "$value".Trim().Trim('"')
    if (-not $p) { $p = 'CSpect' }
    if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path $Root $p }
    if ($p -notmatch '\.exe$') { $p = Join-Path $p 'CSpect.exe' }
    return [System.IO.Path]::GetFullPath($p)
}

# se il percorso sta sotto la cartella del launcher lo salva come relativo (.\...)
function To-IniPath([string]$path) {
    $rootT = $Root.TrimEnd('\')
    $p = $path.TrimEnd('\')
    if ($p.Equals($rootT, [StringComparison]::OrdinalIgnoreCase)) { return '.' }
    if ($p.StartsWith($rootT + '\', [StringComparison]::OrdinalIgnoreCase)) { return '.' + $p.Substring($rootT.Length) }
    return $p
}

# legge [_default] e aggiorna le impostazioni; restituisce tutto l'ini
function Load-Settings {
    $ini = Read-Ini $IniPath
    $set = @{}
    if ($ini.ContainsKey('_default')) { $set = $ini['_default'] }
    $script:GlobalArgs = $DefaultArgs
    if ($set['args']) { $script:GlobalArgs = $set['args'] }
    $script:GamesDir = Resolve-Dir $set['games'] 'GAMES'
    $script:Emulator = Resolve-Emulator $set['cspect']
    $l = "$($set['lang'])".Trim().ToLower()
    if ($script:Strings.ContainsKey($l)) { $script:Lang = $l } else { $script:Lang = 'en' }
    if ($set['sort'] -match '^\s*(voto|rating)\s*$') { $script:SortMode = 'rating' } else { $script:SortMode = 'name' }
    if ($set['listwidth'] -match '^\s*(\d+)\s*$') { $script:ListWidth = [math]::Max(200, [math]::Min(1200, [int]$Matches[1])) }
    return $ini
}

# ============================================================
#  Colori e caratteri
# ============================================================
$cBack  = [System.Drawing.Color]::FromArgb(24, 24, 28)
$cPanel = [System.Drawing.Color]::FromArgb(36, 36, 42)
$cText  = [System.Drawing.Color]::FromArgb(230, 230, 230)
$cDim   = [System.Drawing.Color]::FromArgb(150, 150, 160)
$cGold  = [System.Drawing.Color]::FromArgb(255, 200, 0)
$font   = New-Object System.Drawing.Font('Segoe UI', 10)
$form   = $null

# ============================================================
#  Finestra impostazioni (anche al primo avvio)
# ============================================================
function Show-Settings([bool]$firstRun) {
    $dlg = New-Object System.Windows.Forms.Form
    $dlg.StartPosition = $(if ($form) { 'CenterParent' } else { 'CenterScreen' })
    $dlg.FormBorderStyle = 'FixedDialog'; $dlg.MaximizeBox = $false; $dlg.MinimizeBox = $false
    $dlg.BackColor = $cBack; $dlg.ForeColor = $cText; $dlg.Font = $font
    if ($form -and $form.Icon) { $dlg.Icon = $form.Icon }
    $linkColor = [System.Drawing.Color]::FromArgb(0, 200, 215)
    $openLink = { try { [System.Diagnostics.Process]::Start([string]$this.Tag) | Out-Null } catch {} }

    # dai parametri generali separa grandezza finestra (-wN) e schermo intero (-fullscreen)
    $curSize = 0; $curFull = $false
    $rest = " $($script:GlobalArgs) "
    if ($rest -match '\s-w(\d+)(?=\s)') { $curSize = [int]$Matches[1] }
    if ($rest -match '\s-fullscreen(?=\s)') { $curFull = $true }
    $rest = ($rest -replace '\s-w\d+(?=\s)', ' ' -replace '\s-fullscreen(?=\s)', ' ' -replace '\s+', ' ').Trim()
    if ($curSize -lt 1 -or $curSize -gt 4) { $curSize = 4 }    # CSpect: -w1..-w4, predefinito 4

    $y = 15
    $lblWelcome = New-Object System.Windows.Forms.Label
    $lblWelcome.Location = New-Object System.Drawing.Point(15, $y); $lblWelcome.Size = New-Object System.Drawing.Size(555, 44)
    $lblWelcome.ForeColor = $cGold
    if ($firstRun) { $dlg.Controls.Add($lblWelcome); $y += 52 }

    # lingua
    $lblLang = New-Object System.Windows.Forms.Label
    $lblLang.Location = New-Object System.Drawing.Point(15, ($y + 3)); $lblLang.Size = New-Object System.Drawing.Size(140, 22)
    $cmbLang = New-Object System.Windows.Forms.ComboBox
    $cmbLang.DropDownStyle = 'DropDownList'; $cmbLang.FlatStyle = 'Flat'
    $cmbLang.BackColor = $cPanel; $cmbLang.ForeColor = $cText
    $cmbLang.Location = New-Object System.Drawing.Point(160, $y); $cmbLang.Width = 180
    $codes = @($LangNames.Keys)
    foreach ($c in $codes) { [void]$cmbLang.Items.Add($LangNames[$c]) }
    $cmbLang.SelectedIndex = [math]::Max(0, [array]::IndexOf($codes, $script:Lang))
    $y += 40

    # cartella giochi
    $lblGames = New-Object System.Windows.Forms.Label
    $lblGames.Location = New-Object System.Drawing.Point(15, ($y + 3)); $lblGames.Size = New-Object System.Drawing.Size(140, 22)
    $txtGames = New-Object System.Windows.Forms.TextBox
    $txtGames.Location = New-Object System.Drawing.Point(160, $y); $txtGames.Width = 365
    $txtGames.BackColor = $cPanel; $txtGames.ForeColor = $cText; $txtGames.BorderStyle = 'FixedSingle'
    $txtGames.Text = $script:GamesDir
    $btnGames = New-Object System.Windows.Forms.Button
    $btnGames.Text = '...'; $btnGames.FlatStyle = 'Flat'
    $btnGames.Location = New-Object System.Drawing.Point(530, ($y - 1)); $btnGames.Size = New-Object System.Drawing.Size(40, 27)
    $y += 40

    # cartella CSpect
    $lblCs = New-Object System.Windows.Forms.Label
    $lblCs.Location = New-Object System.Drawing.Point(15, ($y + 3)); $lblCs.Size = New-Object System.Drawing.Size(140, 22)
    $txtCs = New-Object System.Windows.Forms.TextBox
    $txtCs.Location = New-Object System.Drawing.Point(160, $y); $txtCs.Width = 365
    $txtCs.BackColor = $cPanel; $txtCs.ForeColor = $cText; $txtCs.BorderStyle = 'FixedSingle'
    $txtCs.Text = Split-Path $script:Emulator -Parent
    $btnCs = New-Object System.Windows.Forms.Button
    $btnCs.Text = '...'; $btnCs.FlatStyle = 'Flat'
    $btnCs.Location = New-Object System.Drawing.Point(530, ($y - 1)); $btnCs.Size = New-Object System.Drawing.Size(40, 27)
    $y += 28
    $lnkDl = New-Object System.Windows.Forms.LinkLabel
    $lnkDl.Tag = $CSpectUrl; $lnkDl.LinkColor = $linkColor; $lnkDl.ActiveLinkColor = $cGold
    $lnkDl.Location = New-Object System.Drawing.Point(160, $y); $lnkDl.AutoSize = $true
    $lnkDl.Add_LinkClicked($openLink)
    $y += 32

    # grandezza finestra: 4 riquadri proporzionali (1x..4x)
    $lblWin = New-Object System.Windows.Forms.Label
    $lblWin.Location = New-Object System.Drawing.Point(15, ($y + 3)); $lblWin.Size = New-Object System.Drawing.Size(140, 22)
    $script:SizeButtons = @()
    $sx = 160
    for ($n = 1; $n -le 4; $n++) {
        $rb = New-Object System.Windows.Forms.RadioButton
        $rb.Appearance = 'Button'; $rb.FlatStyle = 'Flat'; $rb.TextAlign = 'MiddleCenter'
        $rb.Text = "${n}x"; $rb.Tag = $n
        $w = 30 + 14 * $n; $h = 22 + 10 * $n
        $rb.Size = New-Object System.Drawing.Size($w, $h)
        $rb.Location = New-Object System.Drawing.Point($sx, ($y + 62 - $h))
        $rb.BackColor = $cPanel
        $rb.FlatAppearance.CheckedBackColor = [System.Drawing.Color]::FromArgb(0, 150, 60)
        $rb.FlatAppearance.BorderColor = $cDim
        $rb.Checked = ($n -eq $curSize)
        $script:SizeButtons += $rb
        $sx += $w + 10
    }
    $chkFull = New-Object System.Windows.Forms.CheckBox
    $chkFull.Location = New-Object System.Drawing.Point(($sx + 15), ($y + 38)); $chkFull.AutoSize = $true
    $chkFull.Checked = $curFull
    $y += 74

    # parametri CSpect generali
    $lblArgs = New-Object System.Windows.Forms.Label
    $lblArgs.Location = New-Object System.Drawing.Point(15, ($y + 3)); $lblArgs.Size = New-Object System.Drawing.Size(140, 22)
    $txtArgs = New-Object System.Windows.Forms.TextBox
    $txtArgs.Location = New-Object System.Drawing.Point(160, $y); $txtArgs.Width = 410
    $txtArgs.BackColor = $cPanel; $txtArgs.ForeColor = $cText; $txtArgs.BorderStyle = 'FixedSingle'
    $txtArgs.Font = New-Object System.Drawing.Font('Consolas', 10)
    $txtArgs.Text = $rest
    $y += 48

    # informazioni: nome, versione, copyright, link
    $sep = New-Object System.Windows.Forms.Label
    $sep.Location = New-Object System.Drawing.Point(15, $y); $sep.Size = New-Object System.Drawing.Size(555, 1)
    $sep.BackColor = $cPanel
    $y += 10
    $lblApp = New-Object System.Windows.Forms.Label
    $lblApp.Location = New-Object System.Drawing.Point(15, $y); $lblApp.Size = New-Object System.Drawing.Size(555, 20)
    $lblApp.ForeColor = $cDim
    $y += 22
    $lblUpd = New-Object System.Windows.Forms.Label
    $lnkUpd = New-Object System.Windows.Forms.LinkLabel
    if ($AppUrl) {
        $lblUpd.Location = New-Object System.Drawing.Point(15, $y); $lblUpd.AutoSize = $true; $lblUpd.ForeColor = $cDim
        $lnkUpd.Text = $AppUrl; $lnkUpd.Tag = $AppUrl; $lnkUpd.LinkColor = $linkColor; $lnkUpd.ActiveLinkColor = $cGold
        $lnkUpd.Location = New-Object System.Drawing.Point(230, $y); $lnkUpd.AutoSize = $true
        $lnkUpd.Add_LinkClicked($openLink)
        $dlg.Controls.Add($lblUpd); $dlg.Controls.Add($lnkUpd)
        $y += 22
    }
    $lblEmu = New-Object System.Windows.Forms.Label
    $lblEmu.Location = New-Object System.Drawing.Point(15, $y); $lblEmu.AutoSize = $true; $lblEmu.ForeColor = $cDim
    $lnkEmu = New-Object System.Windows.Forms.LinkLabel
    $lnkEmu.Text = $CSpectUrl; $lnkEmu.Tag = $CSpectUrl; $lnkEmu.LinkColor = $linkColor; $lnkEmu.ActiveLinkColor = $cGold
    $lnkEmu.Location = New-Object System.Drawing.Point(300, $y); $lnkEmu.AutoSize = $true
    $lnkEmu.Add_LinkClicked($openLink)
    $y += 36

    $ok = New-Object System.Windows.Forms.Button
    $ok.FlatStyle = 'Flat'
    $ok.Location = New-Object System.Drawing.Point(370, $y); $ok.Size = New-Object System.Drawing.Size(95, 32)
    $cancel = New-Object System.Windows.Forms.Button
    $cancel.FlatStyle = 'Flat'; $cancel.DialogResult = 'Cancel'
    $cancel.Location = New-Object System.Drawing.Point(475, $y); $cancel.Size = New-Object System.Drawing.Size(95, 32)
    $dlg.ClientSize = New-Object System.Drawing.Size(585, ($y + 47))

    # testi nella lingua scelta (si aggiornano cambiando lingua)
    $applyTexts = {
        $dlg.Text = T 'setTitle'
        $lblWelcome.Text = T 'welcome'
        $lblLang.Text = T 'setLang'; $lblGames.Text = T 'setGames'; $lblCs.Text = T 'setCSpect'; $lblArgs.Text = T 'setArgs'
        $lblWin.Text = T 'setWinSize'; $chkFull.Text = T 'setFullscreen'; $lnkDl.Text = T 'dlCSpect'
        $lblApp.Text = "$AppName  -  " + (T 'aboutVersion' $AppVersion) + "  -  $AppCopyright"
        $lblUpd.Text = T 'aboutUpdates'
        $lblEmu.Text = T 'aboutEmu'
        $ok.Text = T 'ok'; $cancel.Text = T 'cancel'
    }
    $prevLang = $script:Lang
    $cmbLang.Add_SelectedIndexChanged({ $script:Lang = $codes[$cmbLang.SelectedIndex]; & $applyTexts })
    & $applyTexts

    $btnGames.Add_Click({
        $fb = New-Object System.Windows.Forms.FolderBrowserDialog
        $fb.Description = T 'gamesPick'
        if (Test-Path -LiteralPath $txtGames.Text) { $fb.SelectedPath = $txtGames.Text } else { $fb.SelectedPath = $Root }
        if ($fb.ShowDialog($dlg) -eq 'OK') { $txtGames.Text = $fb.SelectedPath }
    })
    $btnCs.Add_Click({
        $fb = New-Object System.Windows.Forms.FolderBrowserDialog
        $fb.Description = T 'emuPick'
        if (Test-Path -LiteralPath $txtCs.Text) { $fb.SelectedPath = $txtCs.Text } else { $fb.SelectedPath = $Root }
        if ($fb.ShowDialog($dlg) -eq 'OK') { $txtCs.Text = $fb.SelectedPath }
    })
    $ok.Add_Click({
        $g = Resolve-Dir $txtGames.Text 'GAMES'
        if (-not (Test-Path -LiteralPath $g -PathType Container)) {
            [System.Windows.Forms.MessageBox]::Show((T 'gamesMissing') + "`n$g", $AppName, 'OK', 'Warning') | Out-Null
            return
        }
        $e = Resolve-Emulator $txtCs.Text
        if (-not (Test-Path -LiteralPath $e)) {
            [System.Windows.Forms.MessageBox]::Show((T 'emuNotHere') + "`n$(Split-Path $e -Parent)", $AppName, 'OK', 'Warning') | Out-Null
            return
        }
        $dlg.DialogResult = 'OK'
        $dlg.Close()
    })

    $dlg.AcceptButton = $ok; $dlg.CancelButton = $cancel
    $dlg.Controls.AddRange(@($lblLang, $cmbLang, $lblGames, $txtGames, $btnGames, $lblCs, $txtCs, $btnCs,
                             $lnkDl, $lblWin, $chkFull, $lblArgs, $txtArgs, $sep, $lblApp, $lblEmu, $lnkEmu, $ok, $cancel))
    $dlg.Controls.AddRange($script:SizeButtons)
    $res = if ($form) { $dlg.ShowDialog($form) } else { $dlg.ShowDialog() }

    if ($res -ne 'OK') { $script:Lang = $prevLang; $dlg.Dispose(); return $false }

    $lang   = $codes[$cmbLang.SelectedIndex]
    $games  = To-IniPath (Resolve-Dir $txtGames.Text 'GAMES')
    $cspect = To-IniPath (Split-Path (Resolve-Emulator $txtCs.Text) -Parent)
    # ricompone i parametri: -wN + altri parametri + -fullscreen
    $size = 4
    foreach ($rb in $script:SizeButtons) { if ($rb.Checked) { $size = [int]$rb.Tag } }
    $other = (" " + $txtArgs.Text + " ") -replace '\s-w\d+(?=\s)', ' ' -replace '\s-fullscreen(?=\s)', ' '
    $other = ($other -replace '\s+', ' ').Trim()
    $gargs = "-w$size"
    if ($other) { $gargs += " $other" }
    if ($chkFull.Checked) { $gargs += ' -fullscreen' }
    $dlg.Dispose()
    try {
        if (-not (Test-Path -LiteralPath $IniPath)) {
            New-IniFile $lang $games $cspect $gargs
        } else {
            Set-IniValue '_default' 'lang' $lang
            Set-IniValue '_default' 'games' $games
            Set-IniValue '_default' 'cspect' $cspect
            Set-IniValue '_default' 'args' $gargs
        }
    } catch {
        [System.Windows.Forms.MessageBox]::Show((T 'saveErr' $_.Exception.Message), $AppName, 'OK', 'Warning') | Out-Null
    }
    [void](Load-Settings)
    return $true
}

# finestra con una casella di testo (rinomina, parametri del singolo gioco)
# restituisce il testo, oppure $null se annullata
function Show-InputBox([string]$title, [string]$label, [string]$value, [bool]$mono) {
    $dlg = New-Object System.Windows.Forms.Form
    $dlg.Text = $title
    $dlg.StartPosition = 'CenterParent'
    $dlg.FormBorderStyle = 'FixedDialog'; $dlg.MaximizeBox = $false; $dlg.MinimizeBox = $false
    $dlg.BackColor = $cBack; $dlg.ForeColor = $cText; $dlg.Font = $font
    $lbl = New-Object System.Windows.Forms.Label
    $lbl.Text = $label
    $lbl.Location = New-Object System.Drawing.Point(12, 12); $lbl.Size = New-Object System.Drawing.Size(500, 64)
    $txt = New-Object System.Windows.Forms.TextBox
    $txt.Location = New-Object System.Drawing.Point(12, 82); $txt.Width = 500
    $txt.BackColor = $cPanel; $txt.ForeColor = $cText; $txt.BorderStyle = 'FixedSingle'
    if ($mono) { $txt.Font = New-Object System.Drawing.Font('Consolas', 10) }
    $txt.Text = $value
    $ok = New-Object System.Windows.Forms.Button
    $ok.Text = T 'ok'; $ok.DialogResult = 'OK'; $ok.FlatStyle = 'Flat'
    $ok.Location = New-Object System.Drawing.Point(312, 122); $ok.Size = New-Object System.Drawing.Size(95, 32)
    $cancel = New-Object System.Windows.Forms.Button
    $cancel.Text = T 'cancel'; $cancel.DialogResult = 'Cancel'; $cancel.FlatStyle = 'Flat'
    $cancel.Location = New-Object System.Drawing.Point(417, 122); $cancel.Size = New-Object System.Drawing.Size(95, 32)
    $dlg.AcceptButton = $ok; $dlg.CancelButton = $cancel
    $dlg.Controls.AddRange(@($lbl, $txt, $ok, $cancel))
    $dlg.ClientSize = New-Object System.Drawing.Size(526, 168)
    $dlg.Add_Shown({ $txt.Focus(); $txt.SelectAll() })
    $res = $dlg.ShowDialog($form)
    $out = $txt.Text.Trim()
    $dlg.Dispose()
    if ($res -ne 'OK') { return $null }
    return $out
}

# ============================================================
#  Giochi
# ============================================================
# eseguibili nella cartella del gioco e nelle sottocartelle (percorsi relativi)
function Get-Candidates([string]$folder) {
    $base = $folder.TrimEnd('\', '/')
    Get-ChildItem -LiteralPath $folder -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $GameExts -contains $_.Extension.ToLower() } |
        ForEach-Object { $_.FullName.Substring($base.Length + 1) } |
        Sort-Object @{ Expression = { ($_ -split '[\\/]').Count } }, @{ Expression = { $_ } }
}

# finestra di scelta dell'eseguibile
function Select-Executable($game) {
    $dlg = New-Object System.Windows.Forms.Form
    $dlg.Text = T 'chooseTitle' $game.Title
    $dlg.Size = New-Object System.Drawing.Size(460, 320)
    $dlg.StartPosition = 'CenterParent'
    $dlg.FormBorderStyle = 'FixedDialog'; $dlg.MaximizeBox = $false; $dlg.MinimizeBox = $false
    $dlg.BackColor = $cBack; $dlg.ForeColor = $cText; $dlg.Font = $font

    $lbl = New-Object System.Windows.Forms.Label
    $lbl.Text = T 'chooseLbl'
    $lbl.Location = New-Object System.Drawing.Point(12, 10); $lbl.Size = New-Object System.Drawing.Size(420, 40)

    $lb = New-Object System.Windows.Forms.ListBox
    $lb.Location = New-Object System.Drawing.Point(12, 55); $lb.Size = New-Object System.Drawing.Size(420, 170)
    $lb.BackColor = $cPanel; $lb.ForeColor = $cText; $lb.BorderStyle = 'None'
    foreach ($c in $game.Candidates) { [void]$lb.Items.Add($c) }
    $idx = -1
    if ($game.File) {
        $cur = $game.File.Substring($game.Folder.TrimEnd('\').Length + 1)
        $idx = $lb.Items.IndexOf($cur)
    }
    $lb.SelectedIndex = [math]::Max(0, $idx)

    $ok = New-Object System.Windows.Forms.Button
    $ok.Text = T 'ok'; $ok.DialogResult = 'OK'; $ok.FlatStyle = 'Flat'
    $ok.Location = New-Object System.Drawing.Point(232, 235); $ok.Size = New-Object System.Drawing.Size(95, 32)
    $cancel = New-Object System.Windows.Forms.Button
    $cancel.Text = T 'cancel'; $cancel.DialogResult = 'Cancel'; $cancel.FlatStyle = 'Flat'
    $cancel.Location = New-Object System.Drawing.Point(337, 235); $cancel.Size = New-Object System.Drawing.Size(95, 32)
    $lb.Add_DoubleClick({ $dlg.DialogResult = 'OK'; $dlg.Close() })

    $dlg.AcceptButton = $ok; $dlg.CancelButton = $cancel
    $dlg.Controls.AddRange(@($lbl, $lb, $ok, $cancel))
    $res = $dlg.ShowDialog($form)
    $choice = $lb.SelectedItem
    $dlg.Dispose()
    if ($res -ne 'OK' -or -not $choice) { return $false }

    try { Set-IniValue $game.Section 'file' $choice } catch {
        [System.Windows.Forms.MessageBox]::Show((T 'saveErr' $_.Exception.Message), 'CSpect Launcher', 'OK', 'Warning') | Out-Null
    }
    $game.File = Join-Path $game.Folder $choice
    $game.Image = Find-Image $game.Folder $game.ImageCfg $game.File
    return $true
}

# testo nella lista (titolo + stelline)
$StarFull  = [string][char]0x2605
$StarEmpty = [string][char]0x2606
function Update-Display($g) {
    $d = $g.Title
    if (-not $g.File -and $g.Candidates.Count -eq 0) { $d += '  ' + (T 'unplayable') }
    if ($g.Hidden) { $d += '  ' + (T 'hiddenTag') }
    if ($g.Rating -gt 0) { $d += '   ' + ($StarFull * $g.Rating) }
    $g.Display = $d
}

# se CSpect non c'e', fa scegliere la cartella e la salva in games.ini
function Find-Emulator {
    if (Test-Path -LiteralPath $script:Emulator) { return $true }
    $r = [System.Windows.Forms.MessageBox]::Show((T 'emuNotFound' $script:Emulator), 'CSpect Launcher', 'YesNo', 'Warning')
    if ($r -ne 'Yes') { return $false }
    $fb = New-Object System.Windows.Forms.FolderBrowserDialog
    $fb.Description = T 'emuPick'
    $fb.SelectedPath = $Root
    while ($fb.ShowDialog($form) -eq 'OK') {
        $exe = Join-Path $fb.SelectedPath 'CSpect.exe'
        if (Test-Path -LiteralPath $exe) {
            try { Set-IniValue '_default' 'cspect' (To-IniPath $fb.SelectedPath) } catch {}
            $script:Emulator = $exe
            return $true
        }
        [System.Windows.Forms.MessageBox]::Show((T 'emuNotHere'), 'CSpect Launcher', 'OK', 'Warning') | Out-Null
    }
    return $false
}

# immagine del gioco
# priorita': image= > <nome eseguibile>*.png piu' recente (screenshot F5 di CSpect) > cover/copertina.*
# > altri screenshot CSpect > screen*/title* > prima immagine della cartella
function Find-Image([string]$folder, [string]$imageCfg, [string]$gameFile) {
    if ($imageCfg) {
        $p = Join-Path $folder $imageCfg
        if (Test-Path -LiteralPath $p) { return $p }
    }
    $imgs = @(Get-ChildItem -LiteralPath $folder -File | Where-Object { $ImageExts -contains $_.Extension.ToLower() } | Sort-Object Name)
    $shots = $imgs
    if ($gameFile) {
        $exeDir = [System.IO.Path]::GetDirectoryName($gameFile)
        if ($exeDir.TrimEnd('\', '/') -ne $folder.TrimEnd('\', '/')) {
            $shots = @(Get-ChildItem -LiteralPath $exeDir -File -ErrorAction SilentlyContinue | Where-Object { $ImageExts -contains $_.Extension.ToLower() })
        }
    }
    if ($imgs.Count -eq 0 -and $shots.Count -eq 0) { return $null }
    $c = $null
    if ($gameFile) {
        $exeBase = [System.IO.Path]::GetFileNameWithoutExtension($gameFile)
        $c = $shots | Where-Object { $_.Extension -ieq '.png' -and $_.BaseName.StartsWith($exeBase, [StringComparison]::OrdinalIgnoreCase) } |
             Sort-Object LastWriteTime -Descending | Select-Object -First 1
    }
    if (-not $c) { $c = $imgs | Where-Object { $_.BaseName -match '^(cover|copertina)' } | Select-Object -First 1 }
    if (-not $c) { $c = $imgs | Where-Object { $_.BaseName -match '_\d{4}_\d{2}_\d{2}___\d{2}_\d{2}_\d{2}$' } | Sort-Object LastWriteTime -Descending | Select-Object -First 1 }
    if (-not $c) { $c = $imgs | Where-Object { $_.BaseName -match '^(screen|screenshot|title)' } | Select-Object -First 1 }
    if (-not $c) { $c = $imgs | Select-Object -First 1 }
    if (-not $c) { $c = $shots | Select-Object -First 1 }
    if (-not $c) { return $null }
    return $c.FullName
}

# scansione della cartella giochi
function Get-Games {
    $ini = Load-Settings
    $list = New-Object System.Collections.ArrayList
    if (-not (Test-Path -LiteralPath $script:GamesDir)) { return $list }

    $dirs = @(Get-ChildItem -LiteralPath $script:GamesDir -Directory | Sort-Object Name)

    # cartelle sparite: via le loro impostazioni
    try { Remove-OrphanSections @($dirs | ForEach-Object { $_.Name }) } catch {}

    # giochi nuovi: aggiunti all'ini (file= solo se c'e' un unico eseguibile)
    $toAdd = ''
    foreach ($dir in $dirs) {
        if ($ini.ContainsKey($dir.Name)) { continue }
        $cands = @(Get-Candidates $dir.FullName)
        $fname = ''
        if ($cands.Count -eq 1) { $fname = $cands[0] }
        $toAdd += "`r`n[$($dir.Name)]`r`nfile=$fname`r`n"
        $ini[$dir.Name] = @{ file = $fname }
    }
    if ($toAdd -ne '') {
        try {
            $enc = New-Object System.Text.UTF8Encoding($true)
            if ((Test-Path -LiteralPath $IniPath) -and -not ([System.IO.File]::ReadAllText($IniPath).EndsWith("`n"))) { $toAdd = "`r`n" + $toAdd }
            [System.IO.File]::AppendAllText($IniPath, $toAdd, $enc)
        } catch {}
    }

    foreach ($dir in $dirs) {
        $cfg = @{}
        if ($ini.ContainsKey($dir.Name)) { $cfg = $ini[$dir.Name] }

        $cands = @(Get-Candidates $dir.FullName)
        $gameFile = $null
        if ($cfg['file']) {
            $p = Join-Path $dir.FullName $cfg['file']
            if (Test-Path -LiteralPath $p) { $gameFile = $p }
        } elseif ($cands.Count -eq 1) {
            $gameFile = Join-Path $dir.FullName $cands[0]
        }

        $title = $dir.Name
        if ($cfg['title']) { $title = $cfg['title'] }
        $gArgs = $script:GlobalArgs
        if ($cfg['args']) { $gArgs = $cfg['args'] }
        $rating = 0
        if ($cfg['rating'] -match '^\s*([0-5])\s*$') { $rating = [int]$Matches[1] }

        $g = [pscustomobject]@{
            Display    = ''
            Title      = $title
            Rating     = $rating
            Hidden     = ($cfg['hidden'] -match '^\s*(1|yes|true)\s*$')
            Section    = $dir.Name
            Folder     = $dir.FullName
            File       = $gameFile
            Candidates = $cands
            Args       = $gArgs
            Image      = (Find-Image $dir.FullName $cfg['image'] $gameFile)
            ImageCfg   = $cfg['image']
            TitleCfg   = $cfg['title']
            ArgsCfg    = $cfg['args']
        }
        Update-Display $g
        [void]$list.Add($g)
    }
    return $list
}

# avvio di un gioco
function Start-Game($game) {
    if (-not $game) { return }
    if (-not $game.File -and $game.Candidates.Count -gt 1) {
        if (-not (Select-Executable $game)) { return }
        Show-Game $game
    }
    if (-not $game.File) {
        [System.Windows.Forms.MessageBox]::Show((T 'noExeMsg' $game.Folder), 'CSpect Launcher', 'OK', 'Warning') | Out-Null
        return
    }
    if (-not (Find-Emulator)) { return }
    # cartella di lavoro = cartella dell'eseguibile: -mmc=.\ punta li',
    # salvataggi e screenshot finiscono accanto al gioco
    $exeDir = [System.IO.Path]::GetDirectoryName($game.File)
    $rel = '.\' + [System.IO.Path]::GetFileName($game.File)
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName         = $script:Emulator
    $psi.Arguments        = "$($game.Args) `"$rel`""
    $psi.WorkingDirectory = $exeDir
    $psi.UseShellExecute  = $false
    try {
        [System.Diagnostics.Process]::Start($psi) | Out-Null
        $status.Text = T 'launched' $game.Title
    } catch {
        [System.Windows.Forms.MessageBox]::Show((T 'launchErr' $_.Exception.Message), 'CSpect Launcher', 'OK', 'Error') | Out-Null
    }
}

# file di salvataggio .sav del gioco (cartella del gioco e sottocartelle)
function Get-SaveFiles($game) {
    Get-ChildItem -LiteralPath $game.Folder -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -ieq '.sav' } | Sort-Object FullName
}

function Load-ImageNoLock([string]$path) {
    try {
        $bytes = [System.IO.File]::ReadAllBytes($path)
        $ms = New-Object System.IO.MemoryStream(,$bytes)
        return [System.Drawing.Image]::FromStream($ms)
    } catch { return $null }
}

# ============================================================
#  Primo avvio: senza games.ini chiede lingua e cartelle
# ============================================================
if (-not (Test-Path -LiteralPath $IniPath)) {
    if (-not (Show-Settings $true)) { return }
} else {
    [void](Load-Settings)
}

# ============================================================
#  Interfaccia
# ============================================================
$form = New-Object System.Windows.Forms.Form
$form.Text = 'CSpect Launcher - ZX Spectrum Next'
$form.Size = New-Object System.Drawing.Size(960, 600)
$form.MinimumSize = New-Object System.Drawing.Size(700, 420)
$form.StartPosition = 'CenterScreen'
$form.BackColor = $cBack
$form.ForeColor = $cText
$form.Font = $font
$form.KeyPreview = $true

# striscia colorata stile Spectrum
$stripe = New-Object System.Windows.Forms.Panel
$stripe.Dock = 'Top'; $stripe.Height = 6
$stripe.Add_Paint({
    param($s, $e)
    $cols = @('#D70000', '#D7D700', '#00D700', '#00D7D7')
    $w = [math]::Ceiling($s.Width / $cols.Count)
    for ($i = 0; $i -lt $cols.Count; $i++) {
        $b = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($cols[$i]))
        $e.Graphics.FillRectangle($b, $i * $w, 0, $w, $s.Height); $b.Dispose()
    }
})

# pannello sinistro: ricerca, ordinamento, lista
$left = New-Object System.Windows.Forms.Panel
$left.Dock = 'Left'; $left.Width = 368; $left.Padding = New-Object System.Windows.Forms.Padding(10)

$lblFilter = New-Object System.Windows.Forms.Label
$lblFilter.Dock = 'Fill'; $lblFilter.ForeColor = $cDim
$lblSortT = New-Object System.Windows.Forms.Label
$lblSortT.ForeColor = $cDim; $lblSortT.Dock = 'Right'; $lblSortT.Width = 95
$labelRow = New-Object System.Windows.Forms.Panel
$labelRow.Dock = 'Top'; $labelRow.Height = 22
$labelRow.Controls.Add($lblFilter); $labelRow.Controls.Add($lblSortT)

$txtFilter = New-Object System.Windows.Forms.TextBox
$txtFilter.Dock = 'Fill'; $txtFilter.BackColor = $cPanel; $txtFilter.ForeColor = $cText; $txtFilter.BorderStyle = 'FixedSingle'
$cmbSort = New-Object System.Windows.Forms.ComboBox
$cmbSort.DropDownStyle = 'DropDownList'; $cmbSort.FlatStyle = 'Flat'
$cmbSort.BackColor = $cPanel; $cmbSort.ForeColor = $cText
$cmbSort.Dock = 'Right'; $cmbSort.Width = 95
[void]$cmbSort.Items.Add(''); [void]$cmbSort.Items.Add('')
$tip = New-Object System.Windows.Forms.ToolTip
$gap = New-Object System.Windows.Forms.Panel
$gap.Dock = 'Right'; $gap.Width = 6
$searchRow = New-Object System.Windows.Forms.Panel
$searchRow.Dock = 'Top'; $searchRow.Height = 26
$searchRow.Controls.Add($txtFilter); $searchRow.Controls.Add($gap); $searchRow.Controls.Add($cmbSort)

$spacer = New-Object System.Windows.Forms.Panel
$spacer.Dock = 'Top'; $spacer.Height = 8

$lst = New-Object System.Windows.Forms.ListBox
$lst.Dock = 'Fill'; $lst.BackColor = $cPanel; $lst.ForeColor = $cText; $lst.BorderStyle = 'None'
$lst.Font = New-Object System.Drawing.Font('Segoe UI', 11)
$lst.IntegralHeight = $false
$lst.DisplayMember = 'Display'

$left.Controls.Add($lst); $left.Controls.Add($spacer); $left.Controls.Add($searchRow); $left.Controls.Add($labelRow)

# pannello destro: titolo + stelline, immagine, file + pulsante
$right = New-Object System.Windows.Forms.Panel
$right.Dock = 'Fill'; $right.Padding = New-Object System.Windows.Forms.Padding(10)

$lblTitle = New-Object System.Windows.Forms.Label
$lblTitle.Dock = 'Fill'; $lblTitle.TextAlign = 'MiddleLeft'; $lblTitle.AutoEllipsis = $true
$lblTitle.Font = New-Object System.Drawing.Font('Segoe UI', 16, [System.Drawing.FontStyle]::Bold)

$pic = New-Object System.Windows.Forms.PictureBox
$pic.Dock = 'Fill'; $pic.SizeMode = 'Zoom'; $pic.BackColor = [System.Drawing.Color]::Black

$bottom = New-Object System.Windows.Forms.Panel
$bottom.Dock = 'Bottom'; $bottom.Height = 70
$lblFile = New-Object System.Windows.Forms.Label
$lblFile.Location = New-Object System.Drawing.Point(0, 12); $lblFile.AutoSize = $false
$lblFile.Size = New-Object System.Drawing.Size(420, 50); $lblFile.ForeColor = $cDim
$lblFile.Anchor = 'Left,Top,Right'
$btnPlay = New-Object System.Windows.Forms.Button
$btnPlay.Size = New-Object System.Drawing.Size(150, 46)
$btnPlay.Anchor = 'Top,Right'
$btnPlay.FlatStyle = 'Flat'; $btnPlay.BackColor = [System.Drawing.Color]::FromArgb(0, 150, 60)
$btnPlay.ForeColor = [System.Drawing.Color]::White
$btnPlay.Font = New-Object System.Drawing.Font('Segoe UI', 12, [System.Drawing.FontStyle]::Bold)
$bottom.Controls.Add($lblFile); $bottom.Controls.Add($btnPlay)
$bottom.Add_Resize({
    $btnPlay.Location = New-Object System.Drawing.Point(($bottom.Width - $btnPlay.Width), 12)
    $lblFile.Width = [math]::Max(50, $bottom.Width - $btnPlay.Width - 15)
})

# stelline del voto (clic = imposta, clic sulla stessa stella = azzera)
$starsPanel = New-Object System.Windows.Forms.FlowLayoutPanel
$starsPanel.Dock = 'Right'; $starsPanel.WrapContents = $false
$starFont = New-Object System.Drawing.Font('Segoe UI Symbol', 22)
$script:StarLabels = @()
$lblVoto = New-Object System.Windows.Forms.Label
$lblVoto.AutoSize = $false; $lblVoto.Size = New-Object System.Drawing.Size(110, 44)
$lblVoto.TextAlign = 'MiddleRight'; $lblVoto.ForeColor = $cDim
$lblVoto.Margin = New-Object System.Windows.Forms.Padding(0, 0, 6, 0)
[void]$starsPanel.Controls.Add($lblVoto)
for ($n = 1; $n -le 5; $n++) {
    $sl = New-Object System.Windows.Forms.Label
    $sl.Text = $StarEmpty; $sl.Font = $starFont; $sl.AutoSize = $false
    $sl.Size = New-Object System.Drawing.Size(38, 44); $sl.TextAlign = 'MiddleCenter'
    $sl.ForeColor = $cDim; $sl.Cursor = [System.Windows.Forms.Cursors]::Hand
    $sl.Margin = New-Object System.Windows.Forms.Padding(0, 0, 2, 0)
    $sl.Tag = $n
    $sl.Add_MouseEnter({ Paint-Stars ([int]$this.Tag) })
    $sl.Add_MouseLeave({ Paint-Stars $null })
    $sl.Add_Click({ Set-Rating ([int]$this.Tag) })
    $script:StarLabels += $sl
    [void]$starsPanel.Controls.Add($sl)
}
$starsPanel.Width = 116 + 5 * 40 + 4

$titleRow = New-Object System.Windows.Forms.Panel
$titleRow.Dock = 'Top'; $titleRow.Height = 48
$titleRow.Controls.Add($lblTitle); $titleRow.Controls.Add($starsPanel)

$right.Controls.Add($pic); $right.Controls.Add($bottom); $right.Controls.Add($titleRow)

# barra di stato con pulsante Impostazioni a destra
$statusStrip = New-Object System.Windows.Forms.StatusStrip
$statusStrip.BackColor = $cPanel; $statusStrip.SizingGrip = $false
$status = New-Object System.Windows.Forms.ToolStripStatusLabel
$status.ForeColor = $cDim; $status.Spring = $true; $status.TextAlign = 'MiddleLeft'
$btnSettings = New-Object System.Windows.Forms.ToolStripButton
$btnSettings.ForeColor = $cText
[void]$statusStrip.Items.Add($status)
[void]$statusStrip.Items.Add($btnSettings)

# divisore trascinabile tra lista e dettagli (larghezza salvata in listwidth=)
$splitter = New-Object System.Windows.Forms.Splitter
$splitter.Dock = 'Left'; $splitter.Width = 5; $splitter.MinSize = 200; $splitter.MinExtra = 300
$splitter.BackColor = $cPanel
$splitter.Add_SplitterMoved({
    $script:ListWidth = $left.Width
    try { Set-IniValue '_default' 'listwidth' "$($left.Width)" } catch {}
})

$form.Controls.Add($right); $form.Controls.Add($splitter); $form.Controls.Add($left); $form.Controls.Add($stripe); $form.Controls.Add($statusStrip)

# menu del clic destro
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$miChoose     = $menu.Items.Add('')
$miArgs       = $menu.Items.Add('')
$miRename     = $menu.Items.Add('')
$miHide       = $menu.Items.Add('')
$miDelSav     = $menu.Items.Add('')
[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
$miShowHidden = New-Object System.Windows.Forms.ToolStripMenuItem
$miShowHidden.CheckOnClick = $true
[void]$menu.Items.Add($miShowHidden)
$lst.ContextMenuStrip = $menu

# ============================================================
#  Logica
# ============================================================
# testi dell'interfaccia nella lingua corrente
function Apply-Language {
    $lblFilter.Text = T 'search'
    $lblSortT.Text  = T 'sortLbl'
    $script:SortChanging = $true
    $si = $cmbSort.SelectedIndex
    $cmbSort.Items[0] = T 'sortName'
    $cmbSort.Items[1] = T 'sortRating'
    $cmbSort.SelectedIndex = $si
    $script:SortChanging = $false
    $tip.SetToolTip($cmbSort, (T 'sortTip'))
    $btnPlay.Text   = T 'play'
    $miChoose.Text  = T 'chooseMenu'
    $miArgs.Text    = T 'argsMenu'
    $miRename.Text  = T 'renameMenu'
    $miDelSav.Text  = T 'delSavMenu'
    $miShowHidden.Text = T 'showHiddenMenu'
    $btnSettings.Text = [string][char]0x2699 + ' ' + (T 'settings')
}

function Refresh-List {
    $q = $txtFilter.Text.Trim()
    $keep = $lst.SelectedItem
    $items = @($script:AllGames | Where-Object {
        ($q -eq '' -or $_.Title.IndexOf($q, [StringComparison]::OrdinalIgnoreCase) -ge 0) -and
        ($script:ShowHidden -or -not $_.Hidden)
    })
    if ($script:SortMode -eq 'rating') {
        $items = @($items | Sort-Object @{ Expression = 'Rating'; Descending = $true }, @{ Expression = 'Title'; Descending = $false })
    } else {
        $items = @($items | Sort-Object Title)
    }
    $lst.BeginUpdate()
    $lst.Items.Clear()
    foreach ($g in $items) { [void]$lst.Items.Add($g) }
    $lst.EndUpdate()
    $idx = -1
    if ($keep) {
        for ($i = 0; $i -lt $lst.Items.Count; $i++) { if ($lst.Items[$i].Section -eq $keep.Section) { $idx = $i; break } }
    }
    if ($idx -lt 0 -and $lst.Items.Count -gt 0) { $idx = 0 }
    if ($idx -ge 0) { $lst.SelectedIndex = $idx; $lst.TopIndex = [math]::Max(0, $idx - 5) } else { Show-Game $null }
    $status.Text = T 'status' $lst.Items.Count $script:AllGames.Count
}

# ricarica tutto (giochi, impostazioni, testi)
function Reload-All {
    $script:AllGames = Get-Games
    Apply-Language
    $script:SortChanging = $true
    $cmbSort.SelectedIndex = $(if ($script:SortMode -eq 'rating') { 1 } else { 0 })
    $script:SortChanging = $false
    $icoPath = Join-Path (Split-Path $script:Emulator -Parent) 'ZXNext.ico'
    if (Test-Path -LiteralPath $icoPath) { try { $form.Icon = New-Object System.Drawing.Icon($icoPath) } catch {} }
    Refresh-List
}

# stelline: $hover = stella sotto il mouse, altrimenti il voto salvato
function Paint-Stars($hover) {
    $g = $lst.SelectedItem
    $starsPanel.Visible = [bool]$g
    if (-not $g) { return }
    $v = if ($hover) { $hover } else { $g.Rating }
    for ($i = 0; $i -lt 5; $i++) {
        $on = ($i -lt $v)
        $script:StarLabels[$i].Text = if ($on) { $StarFull } else { $StarEmpty }
        $script:StarLabels[$i].ForeColor = if ($on) { $cGold } else { $cDim }
    }
    $lblVoto.Text = if ($g.Rating -gt 0) { "$($g.Rating)/5" } else { T 'noRating' }
}

function Set-Rating([int]$n) {
    $g = $lst.SelectedItem
    if (-not $g) { return }
    if ($g.Rating -eq $n) { $n = 0 }          # clic sulla stessa stella = toglie il voto
    $g.Rating = $n
    try { Set-IniValue $g.Section 'rating' $(if ($n -gt 0) { "$n" } else { '' }) } catch {
        [System.Windows.Forms.MessageBox]::Show((T 'saveErr' $_.Exception.Message), 'CSpect Launcher', 'OK', 'Warning') | Out-Null
    }
    Update-Display $g
    if ($script:SortMode -eq 'rating') {
        Refresh-List
    } else {
        $idx = $lst.SelectedIndex
        if ($idx -ge 0) { $lst.Items[$idx] = $g }
    }
    Paint-Stars $null
}

function Show-Game($g) {
    if ($pic.Image) { $old = $pic.Image; $pic.Image = $null; $old.Dispose() }
    Paint-Stars $null
    if (-not $g) { $lblTitle.Text = ''; $lblFile.Text = ''; $btnPlay.Enabled = $false; return }
    $lblTitle.Text = $g.Title
    if ($g.File) {
        $argTxt = $g.Args
        if ($g.ArgsCfg) { $argTxt += '  ' + (T 'customTag') }
        $lblFile.Text = T 'fileLine' ($g.File.Substring($g.Folder.TrimEnd('\').Length + 1)) $argTxt
        $btnPlay.Enabled = $true
    } elseif ($g.Candidates.Count -gt 1) {
        $lblFile.Text = T 'fileChoose' $g.Candidates.Count $g.Args
        $btnPlay.Enabled = $true
    } else {
        $lblFile.Text = T 'noFile'
        $btnPlay.Enabled = $false
    }
    if ($g.Image) { $pic.Image = Load-ImageNoLock $g.Image }
}

# ---------- eventi ----------
$lst.Add_SelectedIndexChanged({ Show-Game $lst.SelectedItem })
$lst.Add_DoubleClick({ Start-Game $lst.SelectedItem })
$lst.Add_MouseDown({
    param($s, $e)
    if ($e.Button -eq 'Right') {
        $i = $lst.IndexFromPoint($e.Location)
        if ($i -ge 0) { $lst.SelectedIndex = $i }
    }
})
$miChoose.Add_Click({
    $g = $lst.SelectedItem
    if ($g -and $g.Candidates.Count -gt 0) { if (Select-Executable $g) { Show-Game $g } }
})
$menu.Add_Opening({
    $g = $lst.SelectedItem
    $miChoose.Enabled = ($g -and $g.Candidates.Count -gt 0)
    $miHide.Enabled   = [bool]$g
    $miArgs.Enabled   = [bool]$g
    $miRename.Enabled = [bool]$g
    $miHide.Text      = if ($g -and $g.Hidden) { T 'unhideMenu' } else { T 'hideMenu' }
    $miDelSav.Enabled = ($g -and @(Get-SaveFiles $g).Count -gt 0)
    $miShowHidden.Checked = $script:ShowHidden
})

# parametri di avvio del singolo gioco (args= nella sua sezione; vuoto = parametri generali)
$miArgs.Add_Click({
    $g = $lst.SelectedItem
    if (-not $g) { return }
    $v = Show-InputBox (T 'argsTitle' $g.Title) (T 'argsLbl' $script:GlobalArgs) "$($g.ArgsCfg)" $true
    if ($null -eq $v) { return }
    try { Set-IniValue $g.Section 'args' $v } catch {
        [System.Windows.Forms.MessageBox]::Show((T 'saveErr' $_.Exception.Message), $AppName, 'OK', 'Warning') | Out-Null
    }
    $g.ArgsCfg = $v
    $g.Args = if ($v) { $v } else { $script:GlobalArgs }
    Show-Game $g
})

# rinomina il titolo mostrato (title= nella sua sezione; vuoto = nome della cartella)
$miRename.Add_Click({
    $g = $lst.SelectedItem
    if (-not $g) { return }
    $cur = if ($g.TitleCfg) { $g.TitleCfg } else { $g.Section }
    $v = Show-InputBox (T 'renameTitle' $g.Title) (T 'renameLbl' $g.Section) $cur $false
    if ($null -eq $v) { return }
    if ($v -eq $g.Section) { $v = '' }
    try { Set-IniValue $g.Section 'title' $v } catch {
        [System.Windows.Forms.MessageBox]::Show((T 'saveErr' $_.Exception.Message), $AppName, 'OK', 'Warning') | Out-Null
    }
    $g.TitleCfg = $v
    $g.Title = if ($v) { $v } else { $g.Section }
    Update-Display $g
    Refresh-List
})

# nascondi / mostra di nuovo il singolo gioco (hidden=1 in games.ini)
$miHide.Add_Click({
    $g = $lst.SelectedItem
    if (-not $g) { return }
    $g.Hidden = -not $g.Hidden
    try { Set-IniValue $g.Section 'hidden' $(if ($g.Hidden) { '1' } else { '' }) } catch {
        [System.Windows.Forms.MessageBox]::Show((T 'saveErr' $_.Exception.Message), $AppName, 'OK', 'Warning') | Out-Null
    }
    Update-Display $g
    Refresh-List
})

# mostra/nasconde nella lista i giochi nascosti (per poterli ripristinare)
$miShowHidden.Add_CheckedChanged({
    $script:ShowHidden = $miShowHidden.Checked
    Refresh-List
})

# elimina i salvataggi .sav del gioco (nel Cestino, dopo conferma)
$miDelSav.Add_Click({
    $g = $lst.SelectedItem
    if (-not $g) { return }
    $files = @(Get-SaveFiles $g)
    if ($files.Count -eq 0) { return }
    $base = $g.Folder.TrimEnd('\').Length + 1
    $names = ($files | ForEach-Object { $_.FullName.Substring($base) }) -join "`n"
    $r = [System.Windows.Forms.MessageBox]::Show((T 'delSavConfirm' $files.Count $g.Title $names), $AppName, 'YesNo', 'Question', 'Button2')
    if ($r -ne 'Yes') { return }
    $n = 0
    foreach ($f in $files) {
        try {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($f.FullName, 'OnlyErrorDialogs', 'SendToRecycleBin')
            $n++
        } catch {
            [System.Windows.Forms.MessageBox]::Show((T 'delSavErr' "$($f.FullName)`n$($_.Exception.Message)"), $AppName, 'OK', 'Warning') | Out-Null
        }
    }
    $status.Text = T 'delSavDone' $n
})

$btnPlay.Add_Click({ Start-Game $lst.SelectedItem })
$txtFilter.Add_TextChanged({ Refresh-List })

$cmbSort.Add_SelectedIndexChanged({
    if ($script:SortChanging) { return }
    $script:SortMode = if ($cmbSort.SelectedIndex -eq 1) { 'rating' } else { 'name' }
    try { Set-IniValue '_default' 'sort' $script:SortMode } catch {}
    Refresh-List
    $lst.Focus()
})

$btnSettings.Add_Click({
    if (Show-Settings $false) { Reload-All }
})

$txtFilter.Add_KeyDown({
    param($s, $e)
    if ($e.KeyCode -eq 'Down' -or $e.KeyCode -eq 'Up') {
        if ($lst.Items.Count -gt 0) {
            $i = $lst.SelectedIndex + $(if ($e.KeyCode -eq 'Down') { 1 } else { -1 })
            $lst.SelectedIndex = [math]::Max(0, [math]::Min($lst.Items.Count - 1, $i))
        }
        $e.Handled = $true
    }
})

$form.Add_KeyDown({
    param($s, $e)
    if ($e.Control) {
        $k = [int]$e.KeyCode
        $n = -1
        if ($k -ge 48 -and $k -le 53)  { $n = $k - 48 }    # Ctrl+0..5
        if ($k -ge 96 -and $k -le 101) { $n = $k - 96 }    # Ctrl+tastierino 0..5
        if ($n -ge 0) {
            $g = $lst.SelectedItem
            if ($g) { $g.Rating = 0; Set-Rating $n }
            $e.Handled = $true; $e.SuppressKeyPress = $true
            return
        }
    }
    switch ($e.KeyCode) {
        'Enter'  { Start-Game $lst.SelectedItem; $e.Handled = $true; $e.SuppressKeyPress = $true }
        'Escape' { if ($txtFilter.Text -ne '') { $txtFilter.Text = '' } else { $form.Close() }; $e.Handled = $true }
        'F5'     { Reload-All; $e.Handled = $true }
    }
})

# tornando al launcher (es. dopo uno screenshot con F5 in CSpect) aggiorna l'immagine
$form.Add_Activated({
    $g = $lst.SelectedItem
    if (-not $g) { return }
    $new = Find-Image $g.Folder $g.ImageCfg $g.File
    if ($new -ne $g.Image) { $g.Image = $new; Show-Game $g }
})

# ---------- avvio ----------
$script:AllGames = Get-Games
Apply-Language
$script:SortChanging = $true
$cmbSort.SelectedIndex = $(if ($script:SortMode -eq 'rating') { 1 } else { 0 })
$script:SortChanging = $false
$left.Width = $script:ListWidth
if ($form.Width -lt $script:ListWidth + 600) { $form.Width = $script:ListWidth + 600 }
$icoPath = Join-Path (Split-Path $script:Emulator -Parent) 'ZXNext.ico'
if (Test-Path -LiteralPath $icoPath) { try { $form.Icon = New-Object System.Drawing.Icon($icoPath) } catch {} }

$form.Add_Shown({ Refresh-List; $txtFilter.Focus() })
[void]$form.ShowDialog()

# Changelog

All notable changes to CSpect Launcher.
Each version has a "## <version>" section, used as the text of the GitHub release.

## 1.6

- "Start with NextZXOS" also works for .sna games, loaded with the NextZXOS Snapshot Loader as the Browser does
- Games that load their files from a fixed folder of the SD card (e.g. TX-1696 from c:/tx-1696/) are put in that folder of the NextZXOS image, so they start
- "Start with NextZXOS" is now in the "CSpect 3 compatibility" submenu of the right-click menu

## 1.5

- Right-click menu: "Load in 48K mode" for .tap games that need the 48K Spectrum
- NextBASIC programs saved without extension (e.g. Vice City Blues) start automatically through NextZXOS like .bas files; a file named like the game folder is offered first
- BASIC programs saved without autostart (e.g. Orb Run) now start instead of only being loaded
- Right-click menu: "CSpect 3 compatibility" turns on, per game, the fixes of the CSpect Compat plugin for old games that crash in CSpect 3 (e.g. Montana Mike, Deltas Shadow, Elite Next, Spice Invaderz)

## 1.4

- Right-click menu: "Start with NextZXOS" loads a .nex/.snx through NextZXOS, for games that stay on a black screen in CSpect (e.g. The Lords of Midnight)
- NextZXOS games: files saved by the game (saved games, high scores) are copied back to the game folder when CSpect is closed
- Favorite games: add them with the right-click menu and show only them with the ♥ button next to the Sort menu
- .tap games are loaded with the NextZXOS Tape Loader in 128K mode, so games with custom loaders (e.g. Tokimal) now start

## 1.3.1

- The window size is remembered on exit and the last game started is selected when the launcher opens
- Right-click menu: "Open game folder" opens the game's folder with the executable selected
- Z-machine text adventures (.z3, .z4, .z5, .z7, .z8) start automatically through NextZXOS with the ZXZVM interpreter

## 1.3

- Experimental macOS support in the Linux version (start with cspect-launcher.command; not yet tested on a Mac)

## 1.2

- .bas/.tap games: F5 screenshots are saved next to the game (they ended up in the temporary folder)
- .bas/.tap games: SD card images of previous launches are deleted from the temporary folder

## 1.1

- NextBASIC (.bas) and tape (.tap) games start automatically: the launcher creates a small
  NextZXOS SD card image with the game and an autoexec.bas (needs zxnext.sd and hdfmonkey, both from CSpect)
- If zxnext.sd is missing, the launcher offers to download it with CSpect's ZXOS.bat / ZXOS.sh,
  shows a waiting window during the download and then starts the game
- New games.ini key nextzxos= (SD card image with NextZXOS, default zxnext.sd in the CSpect folder)

## 1.0

First release.

- Game list with search and sorting by name or rating, 1-5 star ratings
- Cover pictures from CSpect screenshots (F5)
- Executables found in the game folder and its subfolders (.nex, .snx, .sna)
- Per-game executable, launch parameters, custom title and hidden games
- Delete a game's .sav files (moved to the Recycle Bin / Trash)
- Settings: language, games and CSpect folders, window size 1x-4x, full screen
- Interface in English, Italian, Spanish, French and German
- Windows version (PowerShell) and Linux version (Python + Tkinter), sharing the same games.ini

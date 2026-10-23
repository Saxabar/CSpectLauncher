# Changelog

All notable changes to CSpect Launcher.
Each version has a "## <version>" section, used as the text of the GitHub release.

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

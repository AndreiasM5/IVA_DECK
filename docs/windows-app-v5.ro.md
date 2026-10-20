# Instalează IVA DECK V5

**Aplicația Windows pentru tastatura IVA DECK — fără instalare separată de Python.**

## Descarcă

Intră în **[Releases](https://github.com/AndreiasM5/IVA_DECK/releases/latest)** și descarcă **IVA-DECK-5.0.0-Setup-x64.exe** din Assets. Rulează installerul și deschide IVA DECK din Start sau de pe Desktop.

Sunt necesare Windows 10 21H2 sau mai nou / Windows 11, pe 64 de biți. Instalarea se face în profilul tău Windows și nu cere drepturi de administrator. Pentru varianta fără instalare, descarcă ZIP-ul Portable, extrage-l complet și deschide IVA-DECK.exe. Păstrează folderul _internal lângă executabil.

## Conectează tastatura

### Bluetooth

1. Pornește tastatura și asociază **IVA_Deck_FINAL** din Setările Windows → Bluetooth.
2. În IVA DECK, deschide **Conexiune** și apasă **Caută din nou porturile**.
3. Alege portul serial Bluetooth **de ieșire**, apoi **Conectează Bluetooth**.
4. Apasă o tastă fizică. Indicatorul de sus arată **date primite** după recepția unui mesaj.

**COM3 este doar un exemplu.** Pe alt calculator poate fi COM5, COM7 etc. Dacă există două porturi Bluetooth, identifică portul de ieșire pentru dispozitiv în setările avansate Bluetooth din Windows. Închide aplicațiile care folosesc același port.

### USB

Conectează cablul, caută din nou porturile, alege portul USB și apasă **Conectează USB**. Dacă portul nu apare în Windows, instalează driverul oficial pentru convertorul USB de pe placa folosită.

Bluetooth serial folosește **9600 baud**, USB **115200 baud**. Installerul nu schimbă firmware-ul și nu include drivere USB specifice plăcii.

## Folosește aplicația

![IVA DECK V5](media/app-v5-dashboard.png)

- **Taste & macro-uri:** vezi cele nouă taste și potențiometrele animate. Click pe o tastă pentru a-i atribui un macro.
- **Bibliotecă macro:** creezi și editezi combinații precum Ctrl+C sau Ctrl+Shift+S, plus comenzi media.
- **Volum:** alegi aplicația controlată de fiecare potențiometru. Pornește sunet în aplicația dorită și reîmprospătează lista.
- **Dispozitiv:** proximitate, buzzer și trimitere de text la LCD. Funcțiile de imagini SD sunt amânate.
- **Conexiune:** conectare, căutare porturi și deconectare. Ultimul port conectat este memorat și reîncercat la pornire.

## Setări, actualizare și depanare

Configurația se salvează în **%APPDATA%\IVA DECK**: `keybinds.json`, `settings.json` și `application.log`. Installerul și dezinstalarea păstrează aceste date. Pentru backup, copiază cele două fișiere JSON. O singură instanță rulează la un moment dat.

Dacă nu primești date, verifică portul de ieșire, alimentarea tastaturii și firmware-ul compatibil. Dacă alt program are portul deschis, închide-l înainte de reconectare. AI nu este inclus în interfața V5.

## Gratuit și cu sursa disponibilă

V5 este gratuită sub **[GPLv3](../SOFTWARE/APP/v5/LICENSE)**. Nu ai nevoie de cont sau abonament. [Sursa și instrucțiunile de build](../SOFTWARE/APP/v5/) sunt în repository.

Primul installer nu are certificat de semnare digitală. Windows poate afișa un publisher necunoscut. Verifică proveniența din acest repository și hash-ul SHA-256 din release; nu dezactiva antivirusul.

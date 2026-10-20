# IVA DECK V5.0.0 · Windows

Aplicația pentru tastatura IVA DECK, cu interfață mov–roz, macro-uri și control de volum. **Nu ai nevoie de Python instalat.**

## Descarcă

| Fișier | Utilizare |
| --- | --- |
| **[IVA-DECK-5.0.0-Setup-x64.exe](https://github.com/AndreiasM5/IVA_DECK/releases/download/v5.0.0/IVA-DECK-5.0.0-Setup-x64.exe)** | Recomandat: installer, scurtături în Start și pe Desktop, dezinstalare |
| **IVA-DECK-5.0.0-Portable-x64.zip** | Fără instalare: extrage tot folderul și pornește IVA-DECK.exe |
| **SHA256SUMS.txt** | Verificarea integrității fișierelor |

**Windows 10 21H2+ / Windows 11 x64.** Instalare pentru utilizatorul curent, fără drepturi de administrator.

![IVA DECK V5](https://raw.githubusercontent.com/AndreiasM5/IVA_DECK/v5.0.0/docs/media/app-v5-dashboard.png)

## Prima conectare

1. Pornește tastatura și asociază **IVA_Deck_FINAL** în Bluetooth din Windows, sau conectează USB.
2. În **Conexiune**, caută porturile și alege portul serial Bluetooth de ieșire sau USB.
3. Conectează și apasă o tastă fizică. Indicatorul arată **date primite** după recepție.

**Numărul COM diferă între calculatoare.** Închide Arduino Serial Monitor și alte programe care folosesc același port.

## Ce include

- Nouă taste cu numele macro-ului, combinația atribuită și feedback la apăsare.
- Atribuire prin click și bibliotecă pentru creare, captură, editare și ștergere de macro-uri.
- Trei potențiometre grafice animate pe prima pagină; țintele audio se aleg în **Volum**.
- Proximitate, buzzer și trimitere de text LCD.
- Macro-uri, atribuiri, ținte audio și ultimul port salvate în **%APPDATA%\IVA DECK**.
- Reconectare la ultimul port disponibil și o singură instanță a aplicației.

AI și imaginile de pe card SD nu sunt incluse în acest release. Installerul nu schimbă firmware-ul. V4 rămâne disponibilă separat.

## Ghid și sursă

[Ghid de instalare în română](https://github.com/AndreiasM5/IVA_DECK/blob/v5.0.0/docs/windows-app-v5.ro.md) · [Sursă și build Windows](https://github.com/AndreiasM5/IVA_DECK/tree/v5.0.0/SOFTWARE/APP/v5)

V5 este gratuită, sub **GPLv3**, cu notificările dependențelor incluse. Autor: **Ioan-Andrei Ivașcu**.

Verificările locale acoperă executabilul independent, evenimentele de taste/proximitate/volum, animațiile, salvarea setărilor, navigarea, instalarea, actualizarea, dezinstalarea și varianta portabilă. Testat pe Windows 11 x64; un test pe un calculator Windows separat rămâne recomandat.

**Installerul este nesemnat digital.** Windows poate afișa un publisher necunoscut. Verifică proveniența și SHA-256; nu dezactiva antivirusul.

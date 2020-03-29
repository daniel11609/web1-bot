# DuSchuldestMirBot

## Beschreibung des "DuSchuldestMirBot"

Bei dem Bot handelt es sich um einen Telegram-Bot, der im Rahmen eines Projektes vom Informatikkurs TIM19 der DHBW RV entwickelt wurde.  
Der „DuSchuldestMirBot“ soll ein Prototyp darstellen, der zur Erinnerung an Schulden jeglicher Art entwickelt wurde. 
  
  
## Installation

### Python

Für die Nutzung des Bots wird Python 3.8.2 und zusätzlich pip benötigt. 
https://www.python.org/downloads/

### Bibliothek

Um die Bibliothek zu installieren kann man folgenden Befehl benutzen: 

```bash
$ pip install python-telegram-bot -upgrade
```

### Telegramaccount

Um den Telegram-Bot in Betrieb zu nehmen, wird natürlich zu allererst ein TelegramAccount benötigt. 

## Botfather

Wenn die Accounterstellung abgeschlossen ist, sucht man mit der Suchfunktion von Telegram nach dem „Botfather“. 
Diesen kann man mit 
```bash
/start
```
starten. 

Mit dem Befehl 
```bash
/newbot 
```
erstellt man nun seinen eigenen Bot und folgt den Anweisungen des „Botfather“. 

### Token ersetzen

Nach erfolgreicher Erstellung eines Bots erhält man einen Token, mit dem man die http API ansprechen kann. 
Dieser Token wird nun in Zeile 40 der „main.py“ als Variable in „BOT_HTTP_TOKEN“ gespeichert.  

### Registrierung

Mit dem Befehl
```bash
/start
```
nimmt man den Chatbot in Betrieb. Dieser fragt bei der Erstbenutzung, ob man sich registrieren will.
Hier kann man mit 'ja' oder 'nein' antworten. 

Nach der Registrierung ist der Bot startklar. 
 
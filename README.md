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

Um den Telegram-Bot in Betrieb zu nehmen, wird zu allererst ein TelegramAccount benötigt. 

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

Nach der Registrierung ist der Bot startbereit. 

### Befehle

Mit dem Befehl 
```bash
/schuld 
```
kann man einem registrierten User Schulden zuweisen. Hierfür wählt man die Art, Menge und das Datum, zu der die Schuld spätestens beglichen sein soll. 
Der Schuldner bekommt daraufhin eine Bestätigungsbenachrichtigung, in der er die Schuld bestätigen/ablehnen kann. 
Wenn die Schuld bestätigt wurde, bekommen Schuldner und Gläubiger in regelmäßigen Abständen eine Benachrichtigung, welche an die Schuld erinnern soll.   

Mit dem Befehl 
```bash
/ichBekomme 
```
kann sich der User alle seine ausstehenden Forderungen anzeigen lassen. 
Durch Auswahl einer Schuld kann der Gläubiger diese jederzeit als beglichen markieren.   

Mit dem Befehl 
```bash
/ichSchulde 
```
kann sich der User alle seine ausstehenden Schulden anzeigen lassen. Durch Auswahl einer Schuld kann die Begleichung angefragt werden. 
Der Gläubiger bekommt in diesem Fall eine Benachrichtigung, um zu bestätigen, ob die Schuld wirklich beglichen wurde. 
Erst nachdem es bestätigt wurde, gilt die Schuld als beglichen und wird auch so gespeichert.   

 
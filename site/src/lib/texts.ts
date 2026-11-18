// Reading: one short paragraph per language, written for this page. The section shows those whose
// language the font build lists as supported (all of them while that list is empty).
export const texts: Record<string, string> = {
  da: "Biblioteket i Fjordby åbnede i 1962 med fire tusind bøger og en kartoteksskuffe for hvert bogstav. I dag står der over halvtreds tusind bind på hylderne, men systemet er det samme: hver bog har sin plads, og hver plads har sit nummer. Når en bog kommer tilbage, sætter bibliotekaren den ind, hvor den hører hjemme, så den næste, der leder, kan finde den uden at spørge.",
  no: "Toget mot Ålund går fra spor sju hver halve time. Rutetabellen henger ved inngangen og har knapt endret seg på tjue år, og folk her stoler på den. En tabell som er satt opp med omhu, sparer leseren for både tid og bekymring: tallene står under hverandre, og øyet finner raden det leter etter uten å telle.",
  sv: "På apoteket i Sölvberg står burkarna i bokstavsordning, från acetylsalicylsyra till zink. Etiketterna är små, men de måste gå att läsa i dåligt ljus och med en darrande hand. Därför trycks de med tydliga siffror och gott om luft mellan raderna. Ordning är här inte en fråga om smak, utan om säkerhet.",
  fi: "Kirjaston kortisto on järjestetty aakkosjärjestykseen. Jokaisella kirjalla on oma korttinsa, ja jokaisella kortilla on oma paikkansa laatikossa. Kun kortti palaa paikalleen, seuraava etsijä löytää sen ilman apua. Järjestys ei ole sinänsä kaunis, mutta se säästää aikaa.",
  is: "Á bókasafninu í Fjarðabæ á hver bók sinn stað. Þegar bók kemur til baka er henni raðað aftur í hilluna þar sem hún á heima, svo að næsti lesandi finni hana án þess að spyrja. Kerfið er gamalt, en það virkar.",
  de: "Im Archiv der Stadt Fjordby liegt jede Akte in einer grauen Mappe, jede Mappe in einem Karton und jeder Karton auf einem nummerierten Regalboden. Wer etwas sucht, braucht nur die Signatur; für alles Übrige sorgt das Verzeichnis. Ordnung ist hier keine Frage des Geschmacks, sondern eine Abmachung zwischen dem, der ablegt, und dem, der später sucht.",
  en: "Orderly is meant for things that have to be found again: timetables, catalogue cards, labels on shelves and bottles. Its letters are built from one circle and one stem, so that a page of them looks even, and its Text design opens up at small sizes, so that a label set very small can still be read.",
};

/** Paragraph sizes in px, largest first: one at 20, two at 16, three at 13, the rest at 11. */
export const tiers = [20, 16, 16, 13, 13, 13, 11];

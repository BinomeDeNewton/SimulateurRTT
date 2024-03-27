import calendar
from datetime import date, timedelta, datetime
from calendar import monthrange
import webbrowser
import os

def sauvegarder_et_ouvrir_html(contenu_html, nom_fichier="calendrier.html"):
    chemin_complet = os.path.join(os.getcwd(), nom_fichier)
    # Spécifier l'encodage UTF-8 lors de la sauvegarde du fichier
    with open(chemin_complet, 'w', encoding='utf-8') as fichier:
        # Ajouter la balise meta pour spécifier l'encodage UTF-8 dans le HTML
        fichier.write('<meta charset="UTF-8">\n' + contenu_html)
    webbrowser.open('file://' + os.path.realpath(chemin_complet))
    
    
class CustomHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, calendrier_optimise, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calendrier_optimise = calendrier_optimise
        
    def formatday(self, day, weekday, theyear, themonth):
        # Début modifié pour ajouter des couleurs
        if day == 0:
            return '<td class="%s">&nbsp;</td>' % (self.cssclass_noday)
        else:
            cssclasses = self.cssclasses[weekday]
            css_style = "padding: 10px;"  # Style de base pour chaque jour
            if theyear and themonth and day:
                jour_type = self.calendrier_optimise[themonth-1][day-1]
                if jour_type == 'G':
                    css_style += "background-color: #cccccc;"  # Gris pour les week-ends
                elif jour_type == 'B':
                    css_style += "background-color: #add8e6;"  # Bleu pour les jours fériés
                elif jour_type == 'R':
                    css_style += "background-color: #ffcccc;"  # Rouge pour les jours de congé
            return f'<td class="{cssclasses}" style="{css_style}">{day}</td>'
        
    def formatweek(self, theweek, theyear, themonth):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, theyear, themonth) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s
    
    def formatmonth(self, theyear, themonth, withyear=True):
        jours_conge_recommandes = self.calculer_jours_conge_recommandes(themonth - 1)  # Calcul pour le mois actuel
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(f'<tr><th colspan="7" class="month-name">Congés recommandés: {jours_conge_recommandes} jours</th></tr>')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, theyear, themonth))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def calculer_jours_conge_recommandes(self, mois):
            compteur = 0
            periodes_de_repos = []  # Cette ligne peut être retirée si vous ne stockez pas les périodes
            debut_periode = None
        
            for jour, statut in enumerate(self.calendrier_optimise[mois]):
                if statut in ['G', 'B', 'R']:
                    compteur += 1
                    if compteur == 1:
                        debut_periode = jour
                else:
                    if compteur >= 3:  # Cette condition vérifie la longueur de la période de repos
                        fin_periode = jour - 1
                        periodes_de_repos.append((debut_periode, fin_periode))  # Stockage optionnel
                    compteur = 0
                    debut_periode = None
                    
            # Vérifier et compter la dernière période si nécessaire
            if compteur >= 3:
                fin_periode = jour
                periodes_de_repos.append((debut_periode, fin_periode))  # Stockage optionnel
                
            # Calculer les jours de congé recommandés en comptant simplement les 'R' dans le mois
            jours_conge_recommandes = sum(1 for jour in self.calendrier_optimise[mois] if jour == 'R')
            return jours_conge_recommandes
    
def generer_calendrier_html(calendrier_optimise, annee):
    # Update the calendar's CSS classes if needed
    CustomHTMLCalendar.cssclasses_weekday_head = ["mon-head", "tue-head", "wed-head", "thu-head", "fri-head", "sat-head", "sun-head"]
    CustomHTMLCalendar.cssclass_month_head = "month-head"
    CustomHTMLCalendar.cssclass_month = "month"
    CustomHTMLCalendar.cssclass_year = "year"
    CustomHTMLCalendar.cssclass_year_head = "year-head"
    
    # Instantiate custom HTMLCalendar
    cal = CustomHTMLCalendar(calendrier_optimise)
    return cal.formatyear(annee)
    
def calculer_paques(annee):
    "Retourne la date de Pâques pour une année donnée."
    a = annee % 19
    b = annee // 100
    c = annee % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mois = (h + l - 7 * m + 114) // 31
    jour = ((h + l - 7 * m + 114) % 31) + 1
    return date(annee, mois, jour)

def ajouter_jours_feries_mobiles(jours_feries, annee):
    paques = calculer_paques(annee)
    jours_feries[paques.month].append(paques.day)  # Pâques
    jours_feries[(paques + timedelta(days=1)).month].append((paques + timedelta(days=1)).day)  # Lundi de Pâques
    jours_feries[(paques + timedelta(days=39)).month].append((paques + timedelta(days=39)).day)  # Ascension
    jours_feries[(paques + timedelta(days=50)).month].append((paques + timedelta(days=50)).day)  # Pentecôte
    
def demander_annee_et_conges():
    annee = int(input("Quelle année sommes-nous ? "))
    conges = int(input("Combien de jours de congés pouvez-vous poser ? "))
    return annee, conges

def generer_calendrier(annee):
    calendrier = [[0 for _ in range(31)] for _ in range(12)]  # Matrice calendrier [mois][jour]
    
    for mois in range(12):
        for jour in range(31):
            try:
                if date(annee, mois+1, jour+1).weekday() >= 5:  # 5 pour samedi, 6 pour dimanche
                    calendrier[mois][jour] = 'G'  # Gris pour les week-ends
            except ValueError:
                break  # Mois avec moins de 31 jours
            
    # Liste simplifiée des jours fériés fixes, plus préparation pour l'ajout des jours fériés mobiles
    jours_feries = {
        1: [1],  # 1er janvier
        3: [],  # Préparation pour Pâques et Lundi de Pâques qui peuvent tomber en mars
        4: [],  # Préparation pour Pâques et Lundi de Pâques qui peuvent tomber en avril
        5: [1, 8],  # Fête du Travail et Victoire 1945, plus préparation pour Ascension et Pentecôte
        7: [14],  # Fête nationale
        8: [15],  # Assomption
        11: [1, 11],  # Toussaint et Armistice
        12: [25],  # Noël
    }
    
    ajouter_jours_feries_mobiles(jours_feries, annee)
    
    # Marquer les jours fériés et compter les jours fériés par mois
    for mois, jours in jours_feries.items():
        for jour in jours:
            calendrier[mois-1][jour-1] = 'B'  # Bleu pour les jours fériés
            
    return calendrier

def optimiser_conges(annee, calendrier, conges_total):
    jours_conges_poses = 0
    conges_par_mois_limite = conges_total // 4 + 1 # Pas plus du quart du nombre total de congés à poser par mois
    
    def peut_poser_conge(mois, jour):
        # Vérifie si un jour est ouvrable (ni week-end, ni jour férié, ni déjà posé comme congé)
        if jour < len(calendrier[mois]):  # S'assurer que le jour existe dans le mois
            return calendrier[mois][jour] == 0
        return False
    
    def poser_conge(mois, jour):
        nonlocal jours_conges_poses
        if peut_poser_conge(mois, jour) and jours_conges_poses < conges_total:
            calendrier[mois][jour] = 'R'  # Marque le jour comme posé en congé
            jours_conges_poses += 1
            
    def jour_de_la_semaine(jour, mois, annee):
        # Crée une date avec l'année, le mois et le jour
        date = datetime(annee, mois+1, jour+1)
        # Retourne le jour de la semaine sous forme d'entier, où Lundi=0, Mardi=1, ..., Dimanche=6
        return date.weekday()

    # Vérifier si Noël tombe un mercredi et poser le congé pour le jeudi et le vendredi si c'est le cas
    if jour_de_la_semaine(24, 11, annee) == 2:  # Noël est le 25 décembre, mois=11 car janvier est mois=0
        for i in [1, 2]:  # Poser les jours pour le 26 et 27 décembre
            if jours_conges_poses < conges_total and peut_poser_conge(11, 24 + i):
                poser_conge(11, 24 + i)
                
    for mois, jours in enumerate(calendrier):
        conges_poses_ce_mois = 0
        for jour, status in enumerate(jours):
            if status == 'B':  # Jour férié trouvé
                jour_semaine = jour_de_la_semaine(jour, mois, annee) # Simuler le jour de la semaine (1 pour Lundi, 7 pour Dimanche)
                if jour_semaine == 0:  # Si le jour férié est un Lundi
                    for i in range(1, 5):  # Poser le reste de la semaine en congé
                        if jours_conges_poses < conges_total and conges_poses_ce_mois < conges_par_mois_limite and peut_poser_conge(mois, jour + i):
                            poser_conge(mois, jour + i)
                            conges_poses_ce_mois += 1
                elif jour_semaine == 3:  # Si le jour férié est un Jeudi
                    faire_le_pont = input(f"Faire le pont pour le jour férié le {jour + 1}/{mois + 1} (o/n)? ") == 'o'
                    if faire_le_pont :
                        jours_a_poser = [-3, -2, -1]
                        calendrier[mois][jour + 1] = 'G'
                    else :
                        jours_a_poser = [-3, -2, -1, 1]  # Poser Vendredi aussi si on ne fait pas le pont
                    for i in jours_a_poser:
                        if jours_conges_poses < conges_total and conges_poses_ce_mois < conges_par_mois_limite and peut_poser_conge(mois, jour + i):
                            poser_conge(mois, jour + i)
                            conges_poses_ce_mois += 1
            # Limite de conges par mois
            if conges_poses_ce_mois >= conges_par_mois_limite:
                break
            
    return calendrier, conges_total - jours_conges_poses



def trouver_periodes_de_repos(calendrier_optimise, annee):
    nombre_de_periodes = 0
    total_jours_de_repos = 0
    
    for mois in range(12):
        compteur_de_jours = 0
        periode_en_cours = []
        
        for jour in range(31):
            try:
                if calendrier_optimise[mois][jour] in ['G', 'B', 'R']:
                    compteur_de_jours += 1
                    periode_en_cours.append(date(annee, mois + 1, jour + 1))
                elif compteur_de_jours >= 3:
                    nombre_de_periodes += 1
                    total_jours_de_repos += len(periode_en_cours)
                    print(f"Période #{nombre_de_periodes} ({len(periode_en_cours)} jours) : {periode_en_cours[0]} - {periode_en_cours[-1]}")
                    compteur_de_jours = 0
                    periode_en_cours = []
                else:
                    compteur_de_jours = 0
                    periode_en_cours = []
            except ValueError:  # Jour hors du mois
                break
        
        # Vérifier si le mois se termine par une période de repos
        if compteur_de_jours >= 3:
            nombre_de_periodes += 1
            total_jours_de_repos += len(periode_en_cours)
            print(f"Période #{nombre_de_periodes} ({len(periode_en_cours)} jours) : {periode_en_cours[0]} - {periode_en_cours[-1]}")
            
    print(f"\nNombre total de périodes de repos : {nombre_de_periodes}")
    print(f"Nombre total de jours de repos : {total_jours_de_repos}")
        

annee, conges = demander_annee_et_conges()
calendrier = generer_calendrier(annee)
calendrier_optimise, jours_conges_utilises = optimiser_conges(annee, calendrier, conges)

html_calendar = generer_calendrier_html(calendrier_optimise, annee)
sauvegarder_et_ouvrir_html(html_calendar)

# Après avoir optimisé les congés, appeler cette fonction pour afficher les résultats
trouver_periodes_de_repos(calendrier_optimise, annee)
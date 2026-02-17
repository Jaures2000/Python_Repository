from fpdf import FPDF
from datetime import datetime

class PatrimoinePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Liste des Patrimoines', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        date = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f'Page {self.page_no()} - Généré le {date}', 0, 0, 'C')


def generer_pdf_utilisateur(patrimoines, nom_utilisateur, nom_fichier="rapport.pdf"): #Genere un pdf avec la liste des patrimoines d'un utilisateur
    pdf = PatrimoinePDF()
    pdf.add_page()
    
    # Infos utilisateur
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Propriétaire : {nom_utilisateur}', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f'Nombre de patrimoines : {len(patrimoines)}', 0, 1)
    pdf.ln(8)
    
    # Liste des patrimoines
    for i, p in enumerate(patrimoines, 1):
        # Numéro et nom
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f"{i}. {p['nom_patrimoine']}", 0, 1)
        
        # Coordonnées GPS
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 6, '', 0, 0)  # Indentation
        pdf.cell(0, 6, f"Latitude  : {p['latitude']}", 0, 1)
        
        pdf.cell(30, 6, '', 0, 0)  # Indentation
        pdf.cell(0, 6, f"Longitude : {p['longitude']}", 0, 1)
        
        pdf.ln(6)
    
    pdf.output(nom_fichier)
    return nom_fichier


def generer_pdf_tous_patrimoines(tous_patrimoines, nom_fichier="rapport_complet.pdf"): #Genere un pdf avec tous les patrimoines de la base(uniquement pour l'admin)    
    pdf = PatrimoinePDF()
    pdf.add_page()
    
    # Titre
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'RAPPORT COMPLET - TOUS LES PATRIMOINES', 0, 1, 'C')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f'Total : {len(tous_patrimoines)} patrimoines', 0, 1, 'C')
    pdf.ln(8)
    
    # Grouper par utilisateur
    patrimoines_par_user = {}
    for p in tous_patrimoines:
        user = p['nom_utilisateur']
        if user not in patrimoines_par_user:
            patrimoines_par_user[user] = []
        patrimoines_par_user[user].append(p)
    
    # Afficher par utilisateur
    for nom_user, patrimoines in patrimoines_par_user.items():
        # Nom de l'utilisateur
        pdf.set_font('Arial', 'B', 13)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 8, f'{nom_user} ({len(patrimoines)} patrimoine(s))', 0, 1, 'L', 1)
        pdf.ln(3)
        
        # Ses patrimoines
        for i, p in enumerate(patrimoines, 1):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(20, 6, '', 0, 0)  # Indentation
            pdf.cell(0, 6, f"{i}. {p['nom_patrimoine']}", 0, 1)
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(40, 5, '', 0, 0)  # Indentation
            pdf.cell(0, 5, f"Lat: {p['latitude']} | Lon: {p['longitude']}", 0, 1)
            pdf.ln(2)
        
        pdf.ln(5)
    
    pdf.output(nom_fichier)
    return nom_fichier

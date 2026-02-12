from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
import folium
from typing import Dict, Any
from models.patrimoine import Patrimoine
from database.mysql_db import inserer_patrimoine, recuperer_patrimoines, inserer_utilisateur, get_utilisateur, recuperer_patrimoines_par_user
from models.utilisateur import Utilisateur


app = Flask(__name__)

# Clé secrète nécessaire pour :
# gérer les sessions
# stocker l'identité de l'utilisateur connecté
app.secret_key = "secret_key_simple"


# Page principale
@app.route("/")
def index():
    
    # Sécurité : si aucun utilisateur n'est connecté,
    # on redirige vers la page de connexion
    if "id_user" not in session:
        return redirect(url_for("login"))

    # Récupération de l'identifiant de l'utilisateur connecté
    id_user = session["id_user"]

    # Récupération des patrimoines liés à cet utilisateur
    patrimoines = recuperer_patrimoines_par_user(id_user)

    # Création de la carte centrée sur une position par défaut
    # calculer le centroïde des points pour afficher la zone moyenne qui contient tous les patrimoines
    m = folium.Map(location=[6.13, 1.22], zoom_start=12)

    # Ajout des marqueurs pour chaque patrimoine
    for p in patrimoines:
        # évitons les erreurs Folium
        lat = float(p["latitude"])
        lon = float(p["longitude"])
        
        # Création d'un marqueur avec un popup personnalisé
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"""
                <div style="font-size:14px">
                    <b>🏠 Patrimoine :</b> {p['nom_patrimoine']}<br>
                    <b>👤 Propriétaire :</b> {p['nom_utilisateur']}<br>
                    <b>📍 Coordonnées :</b><br>
                    Lat : {p['latitude']}<br>
                    Lon : {p['longitude']}
                </div>
                """,
                max_width=250
            )
        ).add_to(m)

    # Sauvegarde de la carte générée dans un fichier HTML
    m.save("maps/carte.html")

    # Affichage de la page principale
    return render_template("index.html")

"""
# Génération de la carte
@app.route("/carte")
def carte():
    patrimoines = recuperer_patrimoines()

    m = folium.Map(location=[6.13, 1.22], zoom_start=12)

    for p in patrimoines: # type: ignore
        p: Dict[str, Any]

        lat = float(p["latitude"])
        lon = float(p["longitude"])


    folium.Marker(
        location=[lat, lon],
        popup=f"{p['nom_patrimoine']} - {p['nom_utilisateur']}"
    ).add_to(m)


    m.save("maps/carte.html")
    return "Carte générée"
"""


# ==========================
# Accès aux cartes Folium
# ==========================
@app.route("/maps/<path:filename>")
def maps(filename):
    
    # l'accès aux cartes est réservé aux utilisateurs connectés
    if "id_user" not in session:
        return redirect(url_for("login"))

    # Envoi du fichier HTML demandé depuis le dossier maps
    return send_from_directory("maps", filename)

# Route, ajouter un patrimoine à la base de données.
@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    """
    Ajout d'un patrimoine pour l'utilisateur connecté.
    """
    if "id_user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nom = request.form["nom"]

        # Normalisation (évite que "6.1000" et "6.100000" soient différents)
        latitude = f"{float(request.form['latitude']):.6f}"
        longitude = f"{float(request.form['longitude']):.6f}"

        id_user = session["id_user"]

        p = Patrimoine(nom, latitude, longitude, id_user)

        # inserer_patrimoine doit renvoyer True/False (ou lever une erreur)
        ok = inserer_patrimoine(p)

        if not ok:
            flash("Ces coordonnées existent déjà. Choisis un autre point.", "error")
            return redirect(url_for("ajouter"))

        flash("Patrimoine enregistré avec succès ✅", "success")
        return redirect(url_for("index"))

    return render_template("ajouter.html")



@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    """
    Permet à un utilisateur de s'inscrire.
    """
    if request.method == "POST":
        nom = request.form["nom_utilisateur"]
        mot_de_passe = request.form["mot_de_passe"]

        # Création de l'objet Utilisateur (id généré par MySQL)
        user = Utilisateur(None, nom, mot_de_passe)

        # Insertion en base de données
        inserer_utilisateur(user)

        return redirect(url_for("login"))

    return render_template("inscription.html")



# ==========================
# Carte de sélection
# ==========================
@app.route("/carte_selection")
def carte_selection():
    """
    Cette carte est utilisée lors de l'ajout d'un patrimoine
    afin de récupérer automatiquement la latitude et
    la longitude par clic sur la carte.
    """
    if "id_user" not in session:
        return redirect(url_for("login"))

    m = folium.Map(location=[6.13, 1.22], zoom_start=12)

    # Ajout d'un popup affichant les coordonnées
    m.add_child(folium.LatLngPopup())

    m.save("maps/selection.html")

    return "Carte de sélection générée"

# Connexion utilisateur
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Gère la connexion d'un utilisateur.
    - Vérifie les identifiants saisis
    - Crée une session utilisateur
    - Redirige vers la page principale en cas de succès
    """

    # Si le formulaire est soumis
    if request.method == "POST":
        # Récupération des données du formulaire
        nom = request.form["nom_utilisateur"]
        mot_de_passe = request.form["mot_de_passe"]

        # Vérification des identifiants en base de données
        user = get_utilisateur(nom, mot_de_passe)

        if user:
            # Stockage des informations essentielles
            # dans la session utilisateur
            session["id_user"] = user["id_user"]
            session["nom_utilisateur"] = user["nom_utilisateur"]

            # Redirection vers la page principale
            return redirect(url_for("index"))

        return "Identifiants incorrects"

    return render_template("login.html")


# Déconnexion utilisateur
@app.route("/logout")
def logout():
    """
    Déconnecte l'utilisateur courant.

    - Supprime toutes les données stockées en session
    - Affiche un message de confirmation
    - Redirige vers la page de connexion
    """

    # Suppression complète des données de session
    session.clear()

    # Message flash affiché après redirection
    flash("Déconnecté avec succès ✅", "success")

    # Redirection vers la page de connexion
    return redirect(url_for("login"))




if __name__ == "__main__":
    app.run(debug=True)

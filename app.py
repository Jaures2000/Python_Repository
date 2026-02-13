from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    redirect,
    url_for,
    session,
    flash,
)
import folium
import os
import math
from typing import List

from models.patrimoine import Patrimoine
from models.utilisateur import Utilisateur
from database.mysql_db import (
    inserer_patrimoine,
    inserer_utilisateur,
    get_utilisateur,
    recuperer_patrimoines_par_user,
)

app = Flask(__name__)

app.secret_key = "secret_key_simple"


# =========================
# OUTILS GEO
# =========================
def polygone_cercle_autour_point(
    lat: float,
    lon: float,
    rayon_m: float = 50.0,   # ✅ taille type GPS (zone/accuracy plus réaliste)
    nb_points: int = 28
) -> List[List[float]]:
    """
    Retourne un polygone (liste de points) qui approxime un cercle autour d'un point.
    rayon_m : rayon en mètres (ex: 50m)
    nb_points : nombre de sommets (plus grand = plus rond)
    """
    points = []
    # Conversion m -> degrés (approx, suffisant pour ~50m)
    # 1° lat ≈ 111_320m
    for i in range(nb_points):
        angle = 2 * math.pi * (i / nb_points)
        dlat = (rayon_m / 111_320.0) * math.sin(angle)
        dlon = (rayon_m / (111_320.0 * math.cos(math.radians(lat)))) * math.cos(angle)
        points.append([lat + dlat, lon + dlon])
    return points


# =========================
# PAGE PRINCIPALE
# =========================
@app.route("/")
def index():
    if "id_user" not in session:
        return redirect(url_for("login"))

    id_user = session["id_user"]
    patrimoines = recuperer_patrimoines_par_user(id_user)

    coords = []
    for p in patrimoines:
        coords.append([float(p["latitude"]), float(p["longitude"])])

    if coords:
        lat_c = sum(c[0] for c in coords) / len(coords)
        lon_c = sum(c[1] for c in coords) / len(coords)

        zoom = 16 if len(coords) == 1 else 13
        m = folium.Map(location=[lat_c, lon_c], zoom_start=zoom)

        # ✅ zone moyenne contenant tous les points
        if len(coords) >= 2:
            m.fit_bounds(coords)
    else:
        m = folium.Map(location=[6.13, 1.22], zoom_start=12)

    for p in patrimoines:
        lat = float(p["latitude"])
        lon = float(p["longitude"])

        itineraire_url = url_for(
            "itineraire",
            lat=lat,
            lon=lon,
            nom=p.get("nom_patrimoine", "Patrimoine"),
        )

        # ✅ popup plus clean (bouton itinéraire)
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"""
                <div style="
                    font-family: Arial, sans-serif;
                    font-size: 13.5px;
                    line-height: 1.35;
                    min-width: 230px;
                ">
                    <div style="font-size:14px;margin-bottom:6px;">
                        <b>🏠 {p['nom_patrimoine']}</b>
                    </div>

                    <div style="color:#444;">
                        <b>👤 Propriétaire :</b> {p['nom_utilisateur']}<br>
                        <b>📍 Coordonnées :</b> {p['latitude']}, {p['longitude']}
                    </div>

                    <div style="margin-top:10px;">
                        <a href="{itineraire_url}" target="_top"
                           style="
                             display:inline-block;
                             padding:8px 12px;
                             border-radius:12px;
                             background:#111;
                             color:#fff;
                             text-decoration:none;
                             font-weight:700;
                           ">
                           🧭 Itinéraire
                        </a>
                    </div>

                    <div style="margin-top:8px;color:#777;font-size:12px;">
                      Astuce : ouvre l’itinéraire et choisis ton point de départ.
                    </div>
                </div>
                """,
                max_width=280,
            ),
        ).add_to(m)

        # ✅ Zone GPS autour du point (polygone cercle ~ 50m)
        zone = polygone_cercle_autour_point(lat, lon, rayon_m=50.0, nb_points=28)
        folium.Polygon(
            locations=zone,
            color="blue",
            weight=2,
            fill=True,
            fill_opacity=0.18,
        ).add_to(m)

    os.makedirs("maps", exist_ok=True)
    m.save("maps/carte.html")

    return render_template("index.html")


# ==========================
# ACCÈS AUX CARTES FOLIUM
# ==========================
@app.route("/maps/<path:filename>")
def maps(filename):
    if "id_user" not in session:
        return redirect(url_for("login"))

    return send_from_directory("maps", filename)


# ==========================
# AJOUT D'UN PATRIMOINE
# ==========================
@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    if "id_user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nom = request.form["nom"]

        latitude = f"{float(request.form['latitude']):.6f}"
        longitude = f"{float(request.form['longitude']):.6f}"

        id_user = session["id_user"]
        p = Patrimoine(nom, latitude, longitude, id_user)

        ok = inserer_patrimoine(p)
        if not ok:
            flash("Ces coordonnées existent déjà. Choisis un autre point.", "error")
            return redirect(url_for("ajouter"))

        flash("Patrimoine enregistré avec succès ✅", "success")
        return redirect(url_for("index"))

    return render_template("ajouter.html")


# ==========================
# INSCRIPTION
# ==========================
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form["nom_utilisateur"]
        mot_de_passe = request.form["mot_de_passe"]

        user = Utilisateur(None, nom, mot_de_passe)
        inserer_utilisateur(user)

        flash("Compte créé ✅ Vous pouvez vous connecter.", "success")
        return redirect(url_for("login"))

    return render_template("inscription.html")


# ==========================
# ITINÉRAIRE
# ==========================
@app.route("/itineraire")
def itineraire():
    if "id_user" not in session:
        return redirect(url_for("login"))

    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    nom = request.args.get("nom", default="Patrimoine")

    if lat is None or lon is None:
        flash("Patrimoine introuvable (coordonnées manquantes).", "error")
        return redirect(url_for("index"))

    return render_template("itineraire.html", dest_lat=lat, dest_lon=lon, dest_nom=nom)


# ==========================
# CONNEXION
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nom = request.form["nom_utilisateur"]
        mot_de_passe = request.form["mot_de_passe"]

        user = get_utilisateur(nom, mot_de_passe)

        if user:
            session["id_user"] = user["id_user"]
            session["nom_utilisateur"] = user["nom_utilisateur"]
            flash("Connecté ✅", "success")
            return redirect(url_for("index"))

        flash("Identifiants incorrects ❌", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ==========================
# DÉCONNEXION
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté avec succès ✅", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

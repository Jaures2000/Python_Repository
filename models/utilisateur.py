class Utilisateur:
    """
    Représente un utilisateur de l'application.

    Cette classe correspond directement à la table `utilisateur`
    dans la base de données MySQL.
    """

    def __init__(self, id_user, nom_utilisateur, mot_de_passe):
        """
        Constructeur de l'utilisateur.
        """
        self.id_user = id_user
        self.nom_utilisateur = nom_utilisateur
        self.mot_de_passe = mot_de_passe

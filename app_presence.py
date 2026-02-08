import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Présences",
    page_icon="🏫",
    layout="wide"
)

# Définition des matières par jour avec leurs professeurs
matieres_par_jour = {
    "Lundi": [
        {"nom": "Mathématiques", "prof": "M. Dupont", "tel": "01 23 45 67 89"},
        {"nom": "Français", "prof": "Mme. Martin", "tel": "01 34 56 78 90"},
        {"nom": "TPA-concept", "prof": "M. Leroy", "tel": "01 45 67 89 01"}
    ],
    "Mardi": [
        {"nom": "Physique-Chimie", "prof": "Mme. Bernard", "tel": "01 56 78 90 12"},
        {"nom": "Mathématiques", "prof": "M. Dupont", "tel": "01 23 45 67 89"},
        {"nom": "TPA-cao", "prof": "M. Petit", "tel": "01 67 89 01 23"},
        {"nom": "EPS", "prof": "M. Robert", "tel": "01 78 90 12 34"}
    ],
    "Mercredi": [
        {"nom": "Technologie", "prof": "M. Richard", "tel": "01 89 01 23 45"},
        {"nom": "Informatique", "prof": "Mme. Durand", "tel": "01 90 12 34 56"},
        {"nom": "Physique-Chimie", "prof": "Mme. Bernard", "tel": "01 56 78 90 12"}
    ],
    "Jeudi": [
        {"nom": "Construction mécanique", "prof": "M. Simon", "tel": "02 12 34 56 78"},
        {"nom": "Histoire-Géo", "prof": "Mme. Laurent", "tel": "02 23 45 67 89"},
        {"nom": "Dessin", "prof": "M. Michel", "tel": "02 34 56 78 90"}
    ],
    "Vendredi": [
        {"nom": "Électronique", "prof": "M. Moreau", "tel": "02 45 67 89 01"},
        {"nom": "Anglais", "prof": "Mme. Thomas", "tel": "02 56 78 90 12"}
    ]
}

jours = list(matieres_par_jour.keys())
heures_par_matiere = 3

# Fonction pour hacher les mots de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialisation des données
if 'donnees_chargees' not in st.session_state:
    st.session_state.donnees_chargees = False
    st.session_state.eleves = []
    st.session_state.presences = {}
    st.session_state.mot_de_passe_hash = ""
    st.session_state.authentifie = False
    st.session_state.professeurs = {}

# Chargement des données
def charger_donnees():
    try:
        with open('presences_data.json', 'r') as f:
            data = json.load(f)
            st.session_state.eleves = data.get('eleves', [f"Élève {i+1}" for i in range(31)])
            st.session_state.presences = data.get('presences', {})
            st.session_state.mot_de_passe_hash = data.get('mot_de_passe_hash', hash_password("admin123"))
            st.session_state.professeurs = data.get('professeurs', {})
            st.session_state.donnees_chargees = True
    except FileNotFoundError:
        # Initialisation par défaut
        st.session_state.eleves = [f"Élève {i+1}" for i in range(31)]
        st.session_state.mot_de_passe_hash = hash_password("admin123")
        
        # Initialiser les professeurs depuis la structure matieres_par_jour
        st.session_state.professeurs = {}
        for jour in matieres_par_jour:
            for matiere_info in matieres_par_jour[jour]:
                matiere_nom = matiere_info["nom"]
                if matiere_nom not in st.session_state.professeurs:
                    st.session_state.professeurs[matiere_nom] = {
                        "nom": matiere_info["prof"],
                        "telephone": matiere_info["tel"]
                    }
        
        st.session_state.donnees_chargees = True
        sauvegarder_donnees()

def sauvegarder_donnees():
    data = {
        'eleves': st.session_state.eleves,
        'presences': st.session_state.presences,
        'mot_de_passe_hash': st.session_state.mot_de_passe_hash,
        'professeurs': st.session_state.professeurs
    }
    with open('presences_data.json', 'w') as f:
        json.dump(data, f, indent=4)

def initialiser_semaine():
    date_actuelle = datetime.now().strftime("%Y-%m-%d")
    
    if date_actuelle not in st.session_state.presences:
        st.session_state.presences[date_actuelle] = {}
        for jour in jours:
            st.session_state.presences[date_actuelle][jour] = {}
            for matiere_info in matieres_par_jour[jour]:
                matiere_nom = matiere_info["nom"]
                st.session_state.presences[date_actuelle][jour][matiere_nom] = {}
                for eleve in st.session_state.eleves:
                    st.session_state.presences[date_actuelle][jour][matiere_nom][eleve] = ""

def obtenir_info_professeur(matiere_nom):
    """Récupère les informations du professeur pour une matière"""
    if matiere_nom in st.session_state.professeurs:
        prof_info = st.session_state.professeurs[matiere_nom]
        return f"{prof_info['nom']} - 📞 {prof_info['telephone']}"
    
    # Fallback : chercher dans matieres_par_jour
    for jour in matieres_par_jour:
        for matiere_info in matieres_par_jour[jour]:
            if matiere_info["nom"] == matiere_nom:
                return f"{matiere_info['prof']} - 📞 {matiere_info['tel']}"
    
    return "Professeur non défini"

# Charger les données au démarrage
if not st.session_state.donnees_chargees:
    charger_donnees()

# Page de connexion
if not st.session_state.authentifie:
    st.title("🔐 Connexion - Gestion des Présences")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_connexion"):
            st.subheader("Authentification")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Se connecter"):
                if hash_password(mot_de_passe) == st.session_state.mot_de_passe_hash:
                    st.session_state.authentifie = True
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")
        st.info("Mot de passe par défaut : admin123")
    
    st.stop()

# ============================================
# PAGE PRINCIPALE - Après authentification
# ============================================

st.sidebar.title("🏫 Navigation")
page = st.sidebar.selectbox(
    "Menu",
    ["📋 Tableau de bord", "👥 Gérer les élèves", "👨‍🏫 Gérer les professeurs", 
     "📝 Saisir les présences", "✏️ Modifier une présence", "📊 Statistiques", 
     "📅 Emploi du temps", "⚙️ Paramètres"]
)

# Initialiser la semaine si nécessaire
initialiser_semaine()

# Page 1 : Tableau de bord
if page == "📋 Tableau de bord":
    st.title("📋 Tableau de bord")
    
    # Afficher l'emploi du temps récapitulatif
    st.subheader("📅 Emploi du temps de la semaine")
    
    # Créer un dataframe pour l'emploi du temps
    edt_data = []
    for jour in jours:
        for matiere_info in matieres_par_jour[jour]:
            prof_info = obtenir_info_professeur(matiere_info["nom"])
            edt_data.append({
                "Jour": jour,
                "Matière": matiere_info["nom"],
                "Professeur": prof_info.split(" - 📞")[0],
                "Téléphone": prof_info.split("📞 ")[1] if "📞" in prof_info else "",
                "Heures": heures_par_matiere
            })
    
    edt_df = pd.DataFrame(edt_data)
    st.dataframe(edt_df, use_container_width=True, hide_index=True)
    
    # Stats rapides
    col1, col2, col3 = st.columns(3)
    with col1:
        total_matieres = sum(len(matieres) for matieres in matieres_par_jour.values())
        st.metric("Total matières", total_matieres)
    with col2:
        st.metric("Nombre d'élèves", len(st.session_state.eleves))
    with col3:
        total_heures = total_matieres * heures_par_matiere
        st.metric("Heures/semaine", f"{total_heures}h")
    
    # Actions rapides
    st.subheader("Actions rapides")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Saisir présences", use_container_width=True):
            st.session_state.page = "📝 Saisir les présences"
            st.rerun()
    
    with col2:
        if st.button("👨‍🏫 Gérer professeurs", use_container_width=True):
            st.session_state.page = "👨‍🏫 Gérer les professeurs"
            st.rerun()
    
    with col3:
        if st.button("📊 Voir statistiques", use_container_width=True):
            st.session_state.page = "📊 Statistiques"
            st.rerun()

# Page 2 : Gérer les élèves
elif page == "👥 Gérer les élèves":
    st.title("👥 Gestion des élèves")
    
    tab1, tab2 = st.tabs(["📋 Liste des élèves", "✏️ Modifier les noms"])
    
    with tab1:
        st.subheader("Liste des élèves")
        for i, eleve in enumerate(st.session_state.eleves, 1):
            st.write(f"{i}. {eleve}")
    
    with tab2:
        st.subheader("Modifier les noms des élèves")
        st.warning("Cette action nécessite une confirmation du mot de passe")
        
        with st.form("form_modifier_noms"):
            mot_de_passe = st.text_input("Confirmez avec le mot de passe", type="password")
            
            if st.form_submit_button("Continuer"):
                if hash_password(mot_de_passe) == st.session_state.mot_de_passe_hash:
                    st.session_state.modification_active = True
                    st.success("Mot de passe correct. Vous pouvez maintenant modifier les noms.")
                else:
                    st.error("Mot de passe incorrect")
        
        if st.session_state.get('modification_active', False):
            with st.form("form_noms"):
                nouveaux_noms = []
                for i in range(31):
                    nom_actuel = st.session_state.eleves[i] if i < len(st.session_state.eleves) else f"Élève {i+1}"
                    nouveau_nom = st.text_input(f"Élève {i+1}", value=nom_actuel, key=f"eleve_{i}")
                    nouveaux_noms.append(nouveau_nom)
                
                if st.form_submit_button("Enregistrer les modifications"):
                    st.session_state.eleves = nouveaux_noms
                    sauvegarder_donnees()
                    st.session_state.modification_active = False
                    st.success("Noms mis à jour avec succès !")
                    st.rerun()

# NOUVELLE PAGE : Gérer les professeurs
elif page == "👨‍🏫 Gérer les professeurs":
    st.title("👨‍🏫 Gestion des professeurs")
    
    tab1, tab2 = st.tabs(["📋 Liste des professeurs", "✏️ Modifier les professeurs"])
    
    with tab1:
        st.subheader("Liste des professeurs par matière")
        
        # Créer un dataframe des professeurs
        prof_data = []
        for jour in jours:
            for matiere_info in matieres_par_jour[jour]:
                matiere_nom = matiere_info["nom"]
                prof_info = st.session_state.professeurs.get(matiere_nom, {
                    "nom": matiere_info["prof"],
                    "telephone": matiere_info["tel"]
                })
                prof_data.append({
                    "Matière": matiere_nom,
                    "Professeur": prof_info["nom"],
                    "Téléphone": prof_info["telephone"],
                    "Jour(s)": jour
                })
        
        # Supprimer les doublons
        df_prof = pd.DataFrame(prof_data)
        df_prof_unique = df_prof.drop_duplicates(subset=["Matière"])
        
        st.dataframe(df_prof_unique[["Matière", "Professeur", "Téléphone"]], 
                    use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Modifier les informations des professeurs")
        st.warning("Cette action nécessite une confirmation du mot de passe")
        
        with st.form("form_auth_prof"):
            mot_de_passe = st.text_input("Confirmez avec le mot de passe", type="password")
            
            if st.form_submit_button("Continuer"):
                if hash_password(mot_de_passe) == st.session_state.mot_de_passe_hash:
                    st.session_state.modif_prof_active = True
                    st.success("Accès autorisé. Vous pouvez modifier les informations.")
                else:
                    st.error("Mot de passe incorrect")
        
        if st.session_state.get('modif_prof_active', False):
            # Liste de toutes les matières uniques
            toutes_matieres = []
            for jour in matieres_par_jour:
                for matiere_info in matieres_par_jour[jour]:
                    if matiere_info["nom"] not in toutes_matieres:
                        toutes_matieres.append(matiere_info["nom"])
            
            with st.form("form_modif_prof"):
                st.subheader("Modifier les informations")
                
                matiere_selectionnee = st.selectbox("Sélectionnez une matière", toutes_matieres)
                
                # Récupérer les informations actuelles
                prof_info_actuel = st.session_state.professeurs.get(matiere_selectionnee, {})
                nom_actuel = prof_info_actuel.get("nom", "")
                tel_actuel = prof_info_actuel.get("telephone", "")
                
                # Champs de modification
                nouveau_nom = st.text_input("Nom du professeur", value=nom_actuel)
                nouveau_tel = st.text_input("Numéro de téléphone", value=tel_actuel)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Enregistrer les modifications"):
                        if nouveau_nom and nouveau_tel:
                            st.session_state.professeurs[matiere_selectionnee] = {
                                "nom": nouveau_nom,
                                "telephone": nouveau_tel
                            }
                            sauvegarder_donnees()
                            st.success(f"✅ Informations mises à jour pour {matiere_selectionnee}")
                            st.rerun()
                        else:
                            st.error("Veuillez remplir tous les champs")
                
                with col2:
                    if st.form_submit_button("↩️ Annuler"):
                        st.session_state.modif_prof_active = False
                        st.rerun()

# Page 4 : Saisir les présences (MODIFIÉE pour afficher prof)
elif page == "📝 Saisir les présences":
    st.title("📝 Saisie des présences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jour = st.selectbox("Sélectionnez le jour", jours)
    
    with col2:
        # Afficher uniquement les matières du jour sélectionné
        matieres_du_jour = [m["nom"] for m in matieres_par_jour[jour]]
        matiere_selectionnee = st.selectbox("Sélectionnez la matière", matieres_du_jour)
    
    # Récupérer les informations du professeur
    prof_info = obtenir_info_professeur(matiere_selectionnee)
    
    # Afficher les informations de la matière et du professeur
    st.subheader(f"Présences pour le {jour}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Matière:** {matiere_selectionnee}")
    with col2:
        st.info(f"**Professeur:** {prof_info.split(' - 📞')[0]}")
    with col3:
        if "📞" in prof_info:
            st.info(f"**Téléphone:** {prof_info.split('📞 ')[1]}")
    
    date_actuelle = datetime.now().strftime("%Y-%m-%d")
    
    # Créer un formulaire pour les présences
    with st.form("form_presences"):
        presences_data = {}
        
        # Diviser les élèves en deux colonnes pour plus de lisibilité
        col1, col2 = st.columns(2)
        
        for i, eleve in enumerate(st.session_state.eleves):
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                valeur_actuelle = st.session_state.presences.get(date_actuelle, {}).get(jour, {}).get(matiere_selectionnee, {}).get(eleve, "")
                statut_initial = valeur_actuelle == "yes"
                
                presence = st.checkbox(
                    eleve,
                    value=statut_initial,
                    key=f"presence_{jour}_{matiere_selectionnee}_{eleve}"
                )
                presences_data[eleve] = "yes" if presence else "no"
        
        # Bouton de soumission
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            soumettre = st.form_submit_button("💾 Enregistrer les présences", use_container_width=True)
        
        if soumettre:
            # Initialiser la structure si nécessaire
            if date_actuelle not in st.session_state.presences:
                st.session_state.presences[date_actuelle] = {}
            if jour not in st.session_state.presences[date_actuelle]:
                st.session_state.presences[date_actuelle][jour] = {}
            if matiere_selectionnee not in st.session_state.presences[date_actuelle][jour]:
                st.session_state.presences[date_actuelle][jour][matiere_selectionnee] = {}
            
            # Mettre à jour les données
            for eleve, statut in presences_data.items():
                st.session_state.presences[date_actuelle][jour][matiere_selectionnee][eleve] = statut
            
            sauvegarder_donnees()
            st.success(f"✅ Présences enregistrées pour le {jour} en {matiere_selectionnee} !")
            
            # Afficher un récapitulatif
            st.subheader("📊 Récapitulatif")
            presents = list(presences_data.values()).count("yes")
            absents = list(presences_data.values()).count("no")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Présents", f"{presents} élèves")
            with col2:
                st.metric("Absents", f"{absents} élèves")
            with col3:
                taux = (presents / len(st.session_state.eleves)) * 100 if st.session_state.eleves else 0
                st.metric("Taux présence", f"{taux:.1f}%")
            with col4:
                st.metric("Professeur", prof_info.split(" - 📞")[0])

# Page 5 : Modifier une présence (MODIFIÉE pour afficher prof)
elif page == "✏️ Modifier une présence":
    st.title("✏️ Modification individuelle")
    
    st.warning("Cette action nécessite une confirmation du mot de passe")
    
    with st.form("form_auth_modification"):
        mot_de_passe = st.text_input("Confirmez avec le mot de passe", type="password")
        
        if st.form_submit_button("Vérifier le mot de passe"):
            if hash_password(mot_de_passe) == st.session_state.mot_de_passe_hash:
                st.session_state.modif_autorisee = True
                st.success("Accès autorisé")
            else:
                st.error("Mot de passe incorrect")
    
    if st.session_state.get('modif_autorisee', False):
        date_actuelle = datetime.now().strftime("%Y-%m-%d")
        
        if date_actuelle not in st.session_state.presences:
            st.warning("Aucune donnée de présence pour cette semaine.")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                eleve = st.selectbox("Sélectionnez l'élève", st.session_state.eleves, key="modif_eleve")
            
            with col2:
                jour = st.selectbox("Sélectionnez le jour", jours, key="modif_jour")
            
            with col3:
                matieres_du_jour = [m["nom"] for m in matieres_par_jour[jour]]
                matiere = st.selectbox("Sélectionnez la matière", matieres_du_jour, key="modif_matiere")
            
            # Récupérer les informations du professeur
            prof_info = obtenir_info_professeur(matiere)
            
            # Afficher les informations
            st.info(f"**Matière:** {matiere} | **Professeur:** {prof_info}")
            
            # Récupérer le statut actuel
            statut_actuel = st.session_state.presences[date_actuelle][jour][matiere].get(eleve, "non défini")
            
            st.info(f"Statut actuel de **{eleve}** : **{statut_actuel}**")
            
            # Boutons pour modifier
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✅ Présent", use_container_width=True, key="btn_present"):
                    st.session_state.presences[date_actuelle][jour][matiere][eleve] = "yes"
                    sauvegarder_donnees()
                    st.success(f"✅ {eleve} marqué comme présent en {matiere}")
                    st.rerun()
            
            with col2:
                if st.button("❌ Absent", use_container_width=True, key="btn_absent"):
                    st.session_state.presences[date_actuelle][jour][matiere][eleve] = "no"
                    sauvegarder_donnees()
                    st.success(f"✅ {eleve} marqué comme absent en {matiere}")
                    st.rerun()
            
            with col3:
                if st.button("🔄 Effacer", use_container_width=True, key="btn_effacer"):
                    st.session_state.presences[date_actuelle][jour][matiere][eleve] = ""
                    sauvegarder_donnees()
                    st.success(f"✅ Présence effacée pour {eleve}")
                    st.rerun()
            
            with col4:
                if st.button("📋 Voir toutes les présences", use_container_width=True, key="btn_voir_toutes"):
                    data = []
                    for j in jours:
                        for m_info in matieres_par_jour[j]:
                            m_nom = m_info["nom"]
                            statut = st.session_state.presences[date_actuelle][j][m_nom].get(eleve, "")
                            prof = obtenir_info_professeur(m_nom)
                            data.append({
                                "Jour": j,
                                "Matière": m_nom,
                                "Professeur": prof.split(" - 📞")[0],
                                "Statut": "✅ Présent" if statut == "yes" else "❌ Absent" if statut == "no" else "⚪ Non défini"
                            })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)

# Page 6 : Statistiques (MODIFIÉE pour inclure professeurs)
elif page == "📊 Statistiques":
    st.title("📊 Statistiques de présence")
    
    date_actuelle = datetime.now().strftime("%Y-%m-%d")
    
    if date_actuelle not in st.session_state.presences:
        st.warning("Aucune donnée de présence pour cette semaine.")
    else:
        tab1, tab2, tab3 = st.tabs(["📈 Par élève", "📚 Par matière", "👨‍🏫 Par professeur"])
        
        with tab1:
            # Statistiques par élève
            stats_eleves = []
            
            for eleve in st.session_state.eleves:
                total_present = 0
                total_absent = 0
                
                for jour in jours:
                    for matiere_info in matieres_par_jour[jour]:
                        matiere_nom = matiere_info["nom"]
                        statut = st.session_state.presences[date_actuelle][jour][matiere_nom].get(eleve, "")
                        if statut == "yes":
                            total_present += heures_par_matiere
                        elif statut == "no":
                            total_absent += heures_par_matiere
                
                total_heures = total_present + total_absent
                taux = (total_present / total_heures * 100) if total_heures > 0 else 0
                
                stats_eleves.append({
                    "Élève": eleve,
                    "Heures présentes": total_present,
                    "Heures absentes": total_absent,
                    "Taux de présence": f"{taux:.1f}%"
                })
            
            df_eleves = pd.DataFrame(stats_eleves)
            st.dataframe(df_eleves, use_container_width=True)
            
            # Graphique
            df_chart = df_eleves.copy()
            df_chart["Taux numérique"] = df_chart["Taux de présence"].str.replace('%', '').astype(float)
            st.bar_chart(df_chart.set_index("Élève")["Taux numérique"])
        
        with tab2:
            # Statistiques par matière
            stats_matieres = []
            for jour in jours:
                for matiere_info in matieres_par_jour[jour]:
                    matiere_nom = matiere_info["nom"]
                    prof_info = obtenir_info_professeur(matiere_nom)
                    
                    total_present_matiere = 0
                    total_absent_matiere = 0
                    
                    for eleve in st.session_state.eleves:
                        statut = st.session_state.presences[date_actuelle][jour][matiere_nom].get(eleve, "")
                        if statut == "yes":
                            total_present_matiere += 1
                        elif statut == "no":
                            total_absent_matiere += 1
                    
                    total_eleves_matiere = total_present_matiere + total_absent_matiere
                    taux_matiere = (total_present_matiere / total_eleves_matiere * 100) if total_eleves_matiere > 0 else 0
                    
                    stats_matieres.append({
                        "Jour": jour,
                        "Matière": matiere_nom,
                        "Professeur": prof_info.split(" - 📞")[0],
                        "Présents": total_present_matiere,
                        "Absents": total_absent_matiere,
                        "Taux": f"{taux_matiere:.1f}%"
                    })
            
            df_matieres = pd.DataFrame(stats_matieres)
            st.dataframe(df_matieres, use_container_width=True)
        
        with tab3:
            # Statistiques par professeur
            stats_profs = {}
            
            for jour in jours:
                for matiere_info in matieres_par_jour[jour]:
                    matiere_nom = matiere_info["nom"]
                    prof_info = obtenir_info_professeur(matiere_nom)
                    prof_nom = prof_info.split(" - 📞")[0]
                    
                    if prof_nom not in stats_profs:
                        stats_profs[prof_nom] = {
                            "matieres": [],
                            "total_presents": 0,
                            "total_absents": 0
                        }
                    
                    if matiere_nom not in stats_profs[prof_nom]["matieres"]:
                        stats_profs[prof_nom]["matieres"].append(matiere_nom)
                    
                    for eleve in st.session_state.eleves:
                        statut = st.session_state.presences[date_actuelle][jour][matiere_nom].get(eleve, "")
                        if statut == "yes":
                            stats_profs[prof_nom]["total_presents"] += 1
                        elif statut == "no":
                            stats_profs[prof_nom]["total_absents"] += 1
            
            # Créer le dataframe
            prof_data = []
            for prof_nom, data in stats_profs.items():
                total = data["total_presents"] + data["total_absents"]
                taux = (data["total_presents"] / total * 100) if total > 0 else 0
                prof_data.append({
                    "Professeur": prof_nom,
                    "Matières": ", ".join(data["matieres"]),
                    "Séances avec présence": data["total_presents"],
                    "Séances avec absence": data["total_absents"],
                    "Taux présence": f"{taux:.1f}%"
                })
            
            df_profs = pd.DataFrame(prof_data)
            st.dataframe(df_profs, use_container_width=True)

# Page 7 : Emploi du temps (MODIFIÉE pour inclure professeurs)
elif page == "📅 Emploi du temps":
    st.title("📅 Emploi du temps complet")
    
    tab1, tab2 = st.tabs(["📋 Vue par jour", "👨‍🏫 Vue par professeur"])
    
    with tab1:
        st.subheader("Emploi du temps par jour")
        
        for jour in jours:
            with st.expander(f"📌 {jour}", expanded=True):
                col1, col2, col3, col4 = st.columns([3, 4, 3, 2])
                with col1:
                    st.markdown("**Matière**")
                with col2:
                    st.markdown("**Professeur**")
                with col3:
                    st.markdown("**Téléphone**")
                with col4:
                    st.markdown("**Heures**")
                
                for matiere_info in matieres_par_jour[jour]:
                    prof_info = obtenir_info_professeur(matiere_info["nom"])
                    prof_nom = prof_info.split(" - 📞")[0]
                    prof_tel = prof_info.split("📞 ")[1] if "📞" in prof_info else ""
                    
                    col1, col2, col3, col4 = st.columns([3, 4, 3, 2])
                    with col1:
                        st.write(matiere_info["nom"])
                    with col2:
                        st.write(prof_nom)
                    with col3:
                        st.write(prof_tel)
                    with col4:
                        st.write(f"{heures_par_matiere}h")
    
    with tab2:
        st.subheader("Emploi du temps par professeur")
        
        # Regrouper par professeur
        profs_matieres = {}
        for jour in jours:
            for matiere_info in matieres_par_jour[jour]:
                prof_info = obtenir_info_professeur(matiere_info["nom"])
                prof_nom = prof_info.split(" - 📞")[0]
                
                if prof_nom not in profs_matieres:
                    profs_matieres[prof_nom] = []
                
                profs_matieres[prof_nom].append({
                    "jour": jour,
                    "matiere": matiere_info["nom"],
                    "telephone": prof_info.split("📞 ")[1] if "📞" in prof_info else ""
                })
        
        for prof_nom, matieres in profs_matieres.items():
            with st.expander(f"👨‍🏫 {prof_nom}", expanded=True):
                for item in matieres:
                    col1, col2, col3 = st.columns([2, 3, 3])
                    with col1:
                        st.write(f"**{item['jour']}**")
                    with col2:
                        st.write(item['matiere'])
                    with col3:
                        if item['telephone']:
                            st.write(f"📞 {item['telephone']}")

# Page 8 : Paramètres
elif page == "⚙️ Paramètres":
    st.title("⚙️ Paramètres")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Mot de passe", "💾 Données", "ℹ️ Informations"])
    
    with tab1:
        st.subheader("Modifier le mot de passe")
        
        with st.form("form_changer_mdp"):
            ancien_mdp = st.text_input("Ancien mot de passe", type="password")
            nouveau_mdp = st.text_input("Nouveau mot de passe", type="password")
            confirmation = st.text_input("Confirmez le nouveau mot de passe", type="password")
            
            if st.form_submit_button("Modifier le mot de passe"):
                if hash_password(ancien_mdp) != st.session_state.mot_de_passe_hash:
                    st.error("Ancien mot de passe incorrect")
                elif nouveau_mdp != confirmation:
                    st.error("Les nouveaux mots de passe ne correspondent pas")
                elif len(nouveau_mdp) < 4:
                    st.error("Le mot de passe doit faire au moins 4 caractères")
                else:
                    st.session_state.mot_de_passe_hash = hash_password(nouveau_mdp)
                    sauvegarder_donnees()
                    st.success("✅ Mot de passe modifié avec succès !")
    
    with tab2:
        st.subheader("Gestion des données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Sauvegarder maintenant", use_container_width=True):
                sauvegarder_donnees()
                st.success("✅ Données sauvegardées !")
        
        with col2:
            if st.button("🔄 Réinitialiser la semaine", use_container_width=True):
                st.warning("Cette action va effacer toutes les présences de la semaine en cours")
                confirmation = st.text_input("Tapez 'CONFIRMER' pour continuer")
                if confirmation == "CONFIRMER":
                    date_actuelle = datetime.now().strftime("%Y-%m-%d")
                    if date_actuelle in st.session_state.presences:
                        del st.session_state.presences[date_actuelle]
                    initialiser_semaine()
                    sauvegarder_donnees()
                    st.success("✅ Semaine réinitialisée !")
                    st.rerun()
    
    with tab3:
        st.subheader("Informations système")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre d'élèves", len(st.session_state.eleves))
        
        with col2:
            total_matieres = sum(len(matieres_par_jour[jour]) for jour in jours)
            st.metric("Nombre de matières", total_matieres)
        
        with col3:
            unique_profs = len(set(
                obtenir_info_professeur(m["nom"]).split(" - 📞")[0]
                for jour in jours
                for m in matieres_par_jour[jour]
            ))
            st.metric("Nombre de professeurs", unique_profs)
        
        st.info(f"📅 Semaine du {datetime.now().strftime('%d/%m/%Y')}")
        st.info(f"🗃️ Données sauvegardées dans: presences_data.json")

# Pied de page
st.sidebar.markdown("---")
st.sidebar.info(f"📅 {datetime.now().strftime('%A %d %B %Y')}")

if st.sidebar.button("🚪 Déconnexion", use_container_width=True):
    st.session_state.authentifie = False
    st.rerun()

# Afficher les crédits
st.sidebar.markdown("---")
st.sidebar.caption("🏫 Gestion des Présences v2.0")
st.sidebar.caption("Avec gestion des professeurs")

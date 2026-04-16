import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

# Configuration de la page
st.set_page_config(page_title="Tuteur IA - Spécial CNC", layout="centered")

st.title("🎓 Ton Tuteur IA Universel")
st.markdown("### Résous tes exercices en utilisant uniquement TON cours.")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Entre ta clé API Google Gemini :", type="password")
    st.info("Obtiens ta clé gratuite sur [aistudio.google.com](https://aistudio.google.com/)")

# --- ÉTAPE 1 : COURS ---
st.subheader("1. Dépose ton support de cours")
course_file = st.file_uploader("Upload ton cours (PDF ou Image)", type=["pdf", "png", "jpg", "jpeg"])

course_context = ""
if course_file:
    if course_file.type == "application/pdf":
        reader = PdfReader(course_file)
        for page in reader.pages:
            course_context += page.extract_text()
        st.success("Cours PDF chargé avec succès !")
    else:
        st.success("Image du cours chargée !")

# --- ÉTAPE 2 : EXERCICE ---
st.subheader("2. Ton exercice")
exercise_text = st.text_area("Colle l'énoncé ici...")
exercise_image = st.file_uploader("Ou prends une photo de l'exercice", type=["png", "jpg", "jpeg"])

# --- ÉTAPE 3 : RÉSOLUTION ---
if st.button("🚀 Résoudre avec mon cours"):
    if not api_key:
        st.error("Veuillez entrer votre clé API dans la barre latérale.")
    elif not course_file:
        st.error("Veuillez d'abord télécharger un cours.")
    elif not (exercise_text or exercise_image):
        st.error("Veuillez fournir un exercice (texte ou photo).")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # ---> LE CODE ANTI-ERREUR EST ICI <---
            # On demande à Google la liste des modèles exacts autorisés pour votre clé
            model_name = "gemini-2.0-flash" # Sécurité par défaut
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if '1.5-flash' in m.name:
                        model_name = m.name
                        break
                    elif '1.5-pro' in m.name:
                        model_name = m.name
                        
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            Tu es un tuteur pédagogique expert. 
            Voici un extrait de cours : {course_context if course_context else "L'utilisateur a fourni une image de cours."}
            
            Ta mission :
            1. Résoudre l'exercice fourni.
            2. Utiliser UNIQUEMENT les méthodes, les formules et les notations du cours.
            3. Expliquer chaque étape en citant le cours.
            4. Si une info manque, dis-le clairement.
            
            L'exercice est : {exercise_text if exercise_text else "Voir l'image de l'exercice jointe."}
            """
            
            inputs = [prompt]
            if not course_context: 
                inputs.append(Image.open(course_file))
            if exercise_image:
                inputs.append(Image.open(exercise_image))
            
            with st.spinner(f"Analyse en cours avec le modèle autorisé..."):
                response = model.generate_content(inputs)
                st.markdown("---")
                st.markdown("### ✅ Solution proposée :")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Erreur technique détaillée : {e}")

st.markdown("---")
st.caption("Projet créé pour les étudiants de tous les niveaux scolaires.")

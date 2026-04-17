import os
from dotenv import load_dotenv
from openai import OpenAI
from models import QuestionList

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_smart_questions(level, topic):
    # On définit les piliers du Data Analyst pour guider l'IA
    da_pillars = "SQL, Data Visualization, Nettoyage de données (Pandas), Statistiques descriptives, et Interprétation Business."
    topic_context = f"concentrées sur : {topic}" if topic else f"équilibrées entre {da_pillars}"
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o", 
        messages=[
            {
                "role": "system", 
                "content": f"""Tu es un coach expert en recrutement de Data Analysts.
                MISSION : Génère 10 questions d'entretien pour un profil {level.upper()}.
                
                CONSIGNES MÉTIER :
                1. CŒUR DE MÉTIER : Priorise le SQL, l'analyse de données, la manipulation avec Python/Pandas et la communication de résultats. 
                2. MACHINE LEARNING : Ne propose PAS de questions sur le ML (modèles prédictifs, entraînement, etc.) sauf si l'utilisateur l'a explicitement demandé dans le sujet.
                3. RÉPONSE EXPERT : Très technique et orientée méthodologie.
                4. LANGAGE CLAIR : Vulgarisation de haut niveau pour adulte, expliquant l'impact business (3-4 phrases).
                5. DIFFICULTÉ : Strictement adaptée au niveau {level}."""
            },
            {"role": "user", "content": f"Génère 10 fiches de révision {level} sur {topic_context}."}
        ],
        response_format=QuestionList,
        temperature=0.7 
    )
    return response.choices[0].message.parsed
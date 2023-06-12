import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup


# Fonction pour afficher la page d'accueil
st.set_page_config(page_title="Votre brief de redaction", page_icon="📝", layout="wide", initial_sidebar_state="expanded", menu_items=None)


# Définir la clé d'accès API d'OpenAI
openai.api_key = "VOTRE_CLÉ_D'ACCÈS_API"

# Fonction pour appeler l'API OpenAI
def call_openai_api(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Tu es un redacteur SEO avec 20 années d'expérience. Tu proposes des réponses de qualité et professionnelles en prenant toujours en compte la notion de référencement naturel"},{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
    except openai.error.AuthenticationError:
        st.error("Erreur d'authentification OpenAI. Veuillez vérifier votre clé d'accès API.")
        return ""


# Fonction pour effectuer la recherche sur Google et parser les résultats
def search_google(keyword):
    url = f"https://www.google.com/search?q={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_search_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = soup.select(".g")
    search_results = []
    for result in results:
        title_element = result.select_one("h3")
        if title_element is not None:
            title = title_element.text
            link = result.select_one("a")["href"]
            search_results.append({"title": title, "link": link})

    return search_results

# Interface utilisateur avec Streamlit
st.sidebar.header("Générateur de brief")

# Récupérer la clé d'accès API d'OpenAI
api_key = st.sidebar.text_input("Clé d'accès API OpenAI")

# Récupérer le mot-clé à analyser
keyword = st.sidebar.text_input("Mot-clé à analyser")

# Bouton "Générer le brief"
if st.sidebar.button("Générer le brief"):
    # Vérifier si la clé d'accès API est fournie
    if api_key:

        st.title(f"Brief de redaction de la requête : \"{keyword}\"")
        # Définir la clé d'accès API d'OpenAI
        openai.api_key = api_key

        # Récupérer les résultats de la SERP de Google
        html = search_google(keyword)
        search_results = parse_search_results(html)

        # Extraire les titres et les URLs
        ndd = [result["link"] for result in search_results]
        title = [result["title"] for result in search_results]

        # Afficher les résultats de la SERP
        st.subheader("Voici l'analyse de la SERP")
        for i in range(len(ndd)):
            st.write(f"{i+1}. {ndd[i]} - {title[i]}")

        # Appeler l'API OpenAI pour obtenir des idées de sujets
        prompt_idee_sujets = f"Propose moi une liste de sujets complémentaires autour de la thématique : {keyword}"
        idee_sujets = call_openai_api(prompt_idee_sujets)

        # Afficher la liste des idées de sujets
        st.subheader("\nVoici une liste d'idées de sujet :")
        st.write(idee_sujets)

         # Construction de l'intention de recherche
        prompt_search_intent=f"Voici la définition de l'intention de recherche : La recherche informationnelle concerne les internautes ayant un besoin d'information. Ce type d'intention est très large car il concerne des milliers de thématiques allant de la météo aux sites internet d'éducation ou de jardinage. La recherche navigationnelle concerne les internautes qui souhaitent visiter un site web bien particulier. C'est notamment le cas lorsqu'ils tapent le nom du site ou une marque. La recherche transactionnelle concerne les internautes désireux d'acheter sur le web. Ils sont donc à la recherche d'un produit, d'un service ou d'une marque spécifique. En général, les requêtes sont assez courtes et elles ne sont jamais tournées sous forme de question. L'intention de recherche commerciale concerne les personnes en cours de réflexion en vue d'un achat prochain. Ces dernières utilisent le web pour comparer, trouver des bons plans, conseils et avis d'internautes. La recherche commerciale intervient en général juste avant l'intention transactionnelle. Sur la base de cette définition, analyse l'intention de recherche pour le mot-clé '{keyword}' en prenant en compte les sujets en lien, le titre et le nom de domaine de la concurrence. Identifiez l'intention derrière cette requête en tenant compte des éléments suivants : Sujets en lien : voici une liste de sujet en lien avec le mot clé '{keyword}'.\n {idee_sujets}\nQuels sont les sujets connexes ou les termes associés qui peuvent donner des indications sur l'intention de recherche ? Notez-les et considérez leur pertinence par rapport au mot-clé principal.\nTitre : Voici  les titres associés à '{keyword}'.\n {title}\nQuelles sont les informations fournies dans le titre ? Est-ce une question, une demande d'informations, une recherche de comparaison ou autre ? Le titre peut fournir des indices sur l'intention de recherche.\nNom de domaine de la concurrence : Voici les sites concurrents qui apparaissent dans les résultats de recherche pour '{keyword}'.\n {ndd}\nQuels types de sites ou d'entreprises sont présents ? S'agit-il de sites de vente en ligne, de blogs d'informations, de sites éducatifs ou d'autres types ? Le type de sites concurrents peut révéler l'intention de recherche.\nEn utilisant ces informations, identifiez l'intention de recherche pour le mot-clé '{keyword}'. Est-ce une intention informative, transactionnelle, navigationelle ou comemrciale ? Expliquez votre raisonnement en prenant en compte les sujets en lien, le titre et le nom de domaine de la concurrence. Adoptez un ton pragamatique, bienveillant et didactique"
        search_intent = call_openai_api(prompt_search_intent)

        # Afficher l'intention de recherche
        st.subheader("\nVoici l'intention de recherche du texte :")
        st.write(search_intent)  


        # Générer un title et une meta-description
        prompt_title = f"Je souhaite créer un titre efficace sur le sujet {keyword} pour ma page web. Le contenu de ma page concerne les suejts suivants : {idee_sujets}. J'aimerais que le titre soit à la fois pertinent, accrocheur et optimisé pour le SEO. Peux-tu m'aider à générer un titre attractif qui incite les utilisateurs à cliquer tout en étant optimisé pour les moteurs de recherche ? Propose moi une liste de 5 titres si possible dans des styles assez differents les uns des autres. Attention, il faut impérativement que le titre ne dépasse pas les 11 mots"
        prompt_md = f"Je souhaite créer une méta-description convaincante sur le sujet {keyword} pour ma page web. Ma page traite des sujets suivants : {idee_sujets}. J'aimerais une méta-description qui donne aux utilisateurs une idée claire et attrayante du contenu de ma page, tout en étant optimisée pour le référencement. Peux-tu me proposer une méta-description pertinente et engageante ? Attention, il faut impérativement que la meta-description ne dépasse pas les 40 mots"
        title = call_openai_api(prompt_title)
        metadesc = call_openai_api(prompt_md)

        # Afficher le titre et la méta-description
        st.subheader("\nVoici des titres possible :")
        st.write(title)
        st.subheader("\nVoici une meta-description possible :")
        st.write(metadesc)

        # Appeler l'API OpenAI pour générer un plan de site
        prompt_article_plan = f"Je veux que tu fasses un plan complet en français en suivant la méthode MECE avec 1 H1 puis tous les H2 et H3 nécessaires en te basant sur les idées de sujets que je vais te donner, et les titres de mes concurrents. Sous chaque Hn tu dois décrire en 1 à 2 phrases le contenu de la partie et les éléments hors texte à intégrer (tableau, liste à puce, schéma, outil en ligne...). Attention il faut iméprativement effectuer un saut de ligne entre les Hn, la description et les éléments hors contextes afin d'améliorer la visibilité du rendu.\nVoici les titres :\nBalise title : {title}\n\nEt voici les idées de sujets complémentaires : {idee_sujets}"
        article_plan = call_openai_api(prompt_article_plan)

        # Afficher le plan de site
        st.subheader("\nVoici un plan de site possible :")
        st.write(article_plan)
        
        
    else:
        st.error("Veuillez entrer la clé d'accès API OpenAI.")

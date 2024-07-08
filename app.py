import streamlit as st
import pandas as pd
from googlesearch import search
import requests

# Fonction pour nettoyer l'URL
def clean_url(url):
    if isinstance(url, str):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        return url.rstrip('/')
    return url

# Fonction pour compléter l'URL
def get_complete_url(simplified_url):
    full_url = clean_url(simplified_url)
    try:
        query = f"{simplified_url}"
        for url in search(query, num_results=1):
            return url
    except Exception as e:
        return f"Error: {str(e)}"
    return full_url

# Fonction principale pour Streamlit
def main():
    st.title('URL Finder for Investment Funds and Start-ups')
    st.write("Upload an Excel file with company names in the first column to retrieve their official websites.")

    # Choix de la fonction
    function_choice = st.radio(
        "Choose the function you want to use:",
        ('Import to Affinity', 'Import Pitchbook')
    )

    # Téléchargement du fichier
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("File uploaded successfully. Here are the first few rows:")
        st.write(df.head())

        if function_choice == 'Import to Affinity':
            # Ajouter une colonne pour les URLs en fonction des noms de sociétés dans la colonne A
            df['URL'] = df.iloc[:, 0].apply(get_complete_url)
            
            # Nettoyer les URLs
            df['URL'] = df['URL'].apply(clean_url)
            
            # Renommer les colonnes
            df.columns = ['Organization Name', 'Organization Website']
            
            st.write("URLs have been fetched. Here are the first few results:")
            st.write(df.head())
            
            # Sauvegarder les résultats
            output_file = 'output_with_urls.csv'
            df.to_csv(output_file, index=False, sep=',')
            
            with open(output_file, "rb") as file:
                btn = st.download_button(
                    label="Download updated CSV file",
                    data=file,
                    file_name=output_file,
                    mime="text/csv"
                )

        elif function_choice == 'Import Pitchbook':
            # Vérifier que la colonne B contient des URLs valides
            if 'Unnamed: 1' in df.columns:
                df['Complete URL'] = df['Website'].apply(lambda x: get_complete_url(x) if isinstance(x, str) else x)
                
                st.write("Completing URLs for each simplified URL...")
                st.write(df.head())
                
                # Sauvegarder les résultats
                output_file = 'completed_urls.csv'
                df.to_csv(output_file, index=False, sep=',')
                
                with open(output_file, "rb") as file:
                    btn = st.download_button(
                        label="Download completed URLs CSV file",
                        data=file,
                        file_name=output_file,
                        mime="text/csv"
                    )
            else:
                st.error("The uploaded file does not contain a second column with URLs.")

if __name__ == '__main__':
    main()
from flask import Flask, jsonify
from riotwatcher import LolWatcher, ApiError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ⚠️ REMETTEZ VOTRE CLÉ ICI
api_key = 'RGAPI-5b3ecf31-efc5-4710-b7e3-dc9ee175a2f0' 
watcher = LolWatcher(api_key)

# Configuration des régions
# "europe" sert à trouver le Riot ID (Account V1)
# "euw1" sert à trouver les stats LoL (League V4)
REGION_ACCOUNT = 'europe' 
REGION_LOL = 'euw1'

@app.route('/recherche/<gameName>/<tagLine>')
def search_player(gameName, tagLine):
    try:
        # 1. On cherche le COMPTE RIOT (pour avoir le PUUID)
        # Attention : Riot ID est sensible aux majuscules/minuscules parfois, mais l'API gère assez bien.
        account = watcher.account.by_riot_id(REGION_ACCOUNT, gameName, tagLine)
        puuid = account['puuid']
        
        # 2. Avec le PUUID, on récupère le profil LoL
        summoner = watcher.summoner.by_puuid(REGION_LOL, puuid)
        
        # 3. Avec l'ID d'invocateur, on récupère le Rang (Ranked)
        ranked_stats = watcher.league.by_summoner(REGION_LOL, summoner['id'])
        
        return jsonify({
            "account": account, # Contient le Nom#Tag officiel
            "profil": summoner, # Contient le niveau
            "rangs": ranked_stats # Contient le rang (Gold, Plat, etc.)
        })
        
    except ApiError as err:
        if err.response.status_code == 404:
            return jsonify({"error": "Joueur introuvable (Vérifiez le #Tag)"}), 404
        elif err.response.status_code == 403:
            return jsonify({"error": "Clé API expirée !"}), 403
        else:
            print(err) # Affiche l'erreur dans votre terminal pour debug
            return jsonify({"error": "Erreur serveur"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
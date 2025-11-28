import redis
import json
import sys

def attribuer_course_directement(id_livreur, id_commande, host='localhost', port=6379):
    """
    Envoie directement une notification d'attribution à un livreur spécifique
    
    Args:
        id_livreur (str): Identifiant du livreur
        id_commande (str): Identifiant de la commande
    """
    redis_client = redis.Redis(host=host, port=port, decode_responses=True)
    
    canal_prive = f"notifications-livreur:{id_livreur}"
    
    notification = {
        "type": "attribution",
        "id_commande": id_commande,
        "message": f"🎉 Course {id_commande} attribuée ! Rendez-vous au restaurant."
    }
    
    message_json = json.dumps(notification, ensure_ascii=False)
    nb_destinataires = redis_client.publish(canal_prive, message_json)
    
    if nb_destinataires > 0:
        print(f"✅ Notification envoyée au livreur {id_livreur}")
    else:
        print(f"⚠️ Aucun livreur connecté sur le canal {canal_prive}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python attribution.py <id_livreur> <id_commande>")
        print("Exemple: python attribution.py livreur-001 CMD-001")
        sys.exit(1)
    
    id_livreur = sys.argv[1]
    id_commande = sys.argv[2]
    
    attribuer_course_directement(id_livreur, id_commande)

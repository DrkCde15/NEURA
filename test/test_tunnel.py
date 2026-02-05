import requests

# URL gerada pelo localtunnel (agora fixa pelo PM2)
TUNNEL_URL = "https://neura-ai.loca.lt/api/tags"

# O LocalTunnel exige esse cabeçalho para pular a tela de aviso em APIs
headers = {
    "Bypass-Tunnel-Reminder": "true"
}

try:
    response = requests.get(TUNNEL_URL, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Modelos:", response.json())
    else:
        print("Corpo da resposta:", response.text[:500])
except Exception as e:
    print(f"Erro: {e}")
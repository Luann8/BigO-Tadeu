import time
from typing import Any, Dict, List, Optional

import requests

try:
    import folium
except ImportError:
    folium = None

try:
    from IPython.display import display
except ImportError:
    display = None


def buscar_localizacao(ip: str) -> Optional[Dict[str, Any]]:
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}",
            headers=headers,
            timeout=6
        )

        if response.status_code == 200:
            dados = response.json()
            if dados.get("status") == "success":
                return {
                    "ip": ip,
                    "cidade": dados.get("city", "Desconhecida"),
                    "pais": dados.get("country", ""),
                    "lat": dados["lat"],
                    "lon": dados["lon"],
                }
    except requests.RequestException:
        pass

    return None


def processar_ips_e_gerar_mapa(lista_ips: List[str]):
    """Complexidade O(N)"""
    localizacoes = []

    print("\nBuscando localizações...\n")
    inicio = time.time()

    for ip in lista_ips:  # O(N)
        info = buscar_localizacao(ip)
        if info:
            localizacoes.append(info)
            print(f"✓ {ip} → {info['cidade']}, {info['pais']}")
        else:
            print(f"✗ {ip} → Não encontrado")

    fim = time.time()
    print(f"\nTempo total: {fim - inicio:.2f} segundos")
    print(f"Complexidade: O(N) — processou {len(lista_ips)} IPs")

    if not localizacoes:
        print("Nenhuma localização encontrada.")
        return None

    if folium is None:
        print("A biblioteca folium não está instalada. Execute: pip install folium requests")
        return None

    mapa = folium.Map(
        location=[localizacoes[0]["lat"], localizacoes[0]["lon"]],
        zoom_start=2,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
    )

    for loc in localizacoes:
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=f"<b>{loc['ip']}</b><br>{loc['cidade']} - {loc['pais']}",
            tooltip=loc["ip"],
            icon=folium.Icon(color="red", icon="home"),
        ).add_to(mapa)

    return mapa


if __name__ == "__main__":
    meu_ip = input("Digite seu IP: ").strip()

    if meu_ip:
        mapa = processar_ips_e_gerar_mapa([meu_ip])

        if mapa:
            if display is not None:
                display(mapa)
            else:
                mapa.save("mapa_ips.html")
                print("Mapa salvo em mapa_ips.html")
    else:
        print("Você não digitou nenhum IP.")
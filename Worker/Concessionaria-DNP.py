import urllib3
import urllib.parse
from lxml import html
import unicodedata
import json
from datetime import datetime



def collectFromCEEE(httpClient):
    print("Acessando site para monitoramento...")


    dados_coletados = []

    try:
        
        HOST = "https://ceee.equatorialenergia.com.br/api-etr/ocorrencias?estado=RS"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }

        r = httpClient.request('GET', HOST, headers=headers)

        if r.status !=200:
            print(f"Erro na requisição para a API: {r.status}")
            return []

        payload = json.loads(r.data.decode('utf-8'))

        listaOcorrencias = payload.get("ocorrencias", [])

        for oc in listaOcorrencias:

            if oc.get("municipality", "").upper() == "PORTO ALEGRE":

                dados_coletados.append({
                    "bairro": oc.get("neighborhood", "Não informado"),
                    "interrupcoes": 1,
                    "consumidores_afetados": oc.get("affected_units", 0),
                    "tipo": oc.get("occurrence_type", "Não programado"),
                    "duracao_minutos": oc.get("duration_minutes", 1),
                    "reparo_estimado": oc.get("etr", "Não informado")
                })

        return dados_coletados
    
    except Exception as e:
        print(f"Erro ao buscar dados de interrupção: {e}")
        return []
    
def normalizar_nome(nome):
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = nome.replace('-', ' ')
    return nome.strip().upper()

def mapear_bairros(cidade, httpClient):
    print(f"Mapeando ids da cidade ${cidade} para Overpass...")

    query = f"""
    [out:json];
    area["name"="{cidade}"]["admin_level"="8"]->.searchArea;
    (
        relation["admin_level"="10"](area.searchArea);
        way["admin_level"="10"](area.searchArea);
    );
    out tags;
    """

    url = f"https://overpass-api.de/api/interpreter?data={urllib.parse.quote(query)}"

    mapa_bairros = {}

    try:
        r = httpClient.request('GET',url)
        dados = json.loads(r.data.decode('utf-8'))

        if "elements" in dados:
            for el in dados["elements"]:
                nome = el["tags"].get("name", "")
                if nome:
                    nome_limpo = normalizar_nome(nome)
                    mapa_bairros[nome_limpo] = el["id"]
        return mapa_bairros
    except Exception as e:
        print(f"Erro ao buscar ID no Overpass: {e}")
        return {}

def exportarJson(novosDados):
    if not novosDados:
        print("Nenhum dado encontrado para salvar")
        return

    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    novoArquivo = f"CEEE_Report_DNP_{timestamp}.json"

    with open(novoArquivo, "w", encoding="utf-8") as f:
        json.dump(novosDados, f, indent=4, ensure_ascii=False)
    print(f"Novo arquivo criado: {novoArquivo}")

def enviarParaAPI(district_id, httpclient):
    
    API_URL = "http://localhost:5176/homepage/cities/1"
    url = f"{API_URL}/districts/{district_id}/reports"


    payload = {
        "Is_Fixed": False,
        "Problem_Category_id": 1
    }

    headers = {
        'Content-Type': 'application/json'
    }

    dados_json = json.dumps(payload).encode('utf-8')

    try:
        r = httpclient.request('POST', url, body=dados_json, headers=headers)
        print(f"{r.status}. Reportado o bairro {district_id}")
    except Exception as e:
        print(f"Erro de conexão com o bando de dados: {e}")


def main():
    http = urllib3.PoolManager()

    cidade_alvo = "Porto Alegre"
    dicionario_bairros = mapear_bairros(cidade_alvo, http)

    if not dicionario_bairros:
        print("Falha ao carregar dicionario de bairros.")
        return

    dadosColetados = collectFromCEEE(http)

    for queda in dadosColetados:
        nome_limpo = normalizar_nome(queda["bairro"])

        district_id = dicionario_bairros.get(nome_limpo)

        if district_id:
            print(f"Reportando: {queda['bairro']} -> ID {district_id}")
            enviarParaAPI(district_id, http)
        else:
            print(f"Aviso: Bairro {queda['bairro']} não foi encontrado no dicionario!")

    
    exportarJson(dadosColetados)

if __name__ == "__main__":
    main()



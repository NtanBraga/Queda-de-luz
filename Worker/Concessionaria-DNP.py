import urllib3
import urllib.parse
import unicodedata
import json
from datetime import datetime
import os
import time
import re

CORRECOES_CEEE = {
    "TRES FIQUEIRAS": "TRES FIGUEIRAS",
    "SAO JOSE": "VILA SAO JOSE",
    "CENTRO": "CENTRO HISTRICO",
    "M. DE VENTO": "MOINHOS DE VENTO",
    "M DE VENTO": "MOINHOS DE VENTO",
    "SANTA TERESA": "SANTA TEREZA",
    "APARICIO BORGES": "CORONEL APARICIO BORGES",
    "ABERTA MORROS": "ABERTA DOS MORROS",
    "JARDIM ITU SABARA": "JARDIM ITU",
    "PROTASIO ALVES": "MORRO SANTANA"
}

ARQUIVO_ESTADO = "estado_quedas.json"

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

    if not nome:
        return ""
    
    nome = re.sub(r'\(.*?\)', '', nome)
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = nome.replace('-', ' ')
    return nome.strip().upper()

def mapear_bairros(cidade, httpClient):
    print(f"Mapeando ids da cidade ${cidade} para Overpass...")

    pastaDados = "Cidade_Dicionario_Bairros"
    if not os.path.exists(pastaDados):
        os.makedirs(pastaDados)
        print(f"Pasta {pastaDados} foi criada.")
    
    nomeArquivo = f"bairros_{cidade.replace(' ', '_').lower()}.json"
    caminhoArquivo = os.path.join(pastaDados, nomeArquivo)

    if os.path.exists(caminhoArquivo):
        print(f"Carregando dicionario de bairros pelo arquivo: {nomeArquivo}")
        with open(caminhoArquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"Arquivo inexistente. Fazendo download pelo Overpass...")

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
        if mapa_bairros:
            with open(caminhoArquivo, "w", encoding="utf-8") as f:
                json.dump(mapa_bairros, f, ensure_ascii=False, indent=4)
            print(f"Download concluido! Dicionario salvo em: {caminhoArquivo}")
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

def enviarParaAPI(district_id, httpclient, Is_Fixed=False):
    
    API_URL = "http://localhost:5176/homepage/cities/1"
    url = f"{API_URL}/districts/{district_id}/reports"


    payload = {
        "Is_Fixed": Is_Fixed,
        "Problem_Category_id": 1
    }

    headers = {
        'Content-Type': 'application/json'
    }

    dados_json = json.dumps(payload).encode('utf-8')

    try:
        r = httpclient.request('POST', url, body=dados_json, headers=headers)
        statusMsg = "Luz voltou." if Is_Fixed else "Falta de luz reportada"
        
        if r.status in [200, 201]:
            print(f"{r.status}. {statusMsg} o bairro {district_id}")
        else:
            print(f"Erro ao enviar status do bairro {district_id}")
    except Exception as e:
        print(f"Erro de conexão com o bando de dados: {e}")

def carregarEstadoAnterior():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def salvarEstadoAtual(quedasAtuais):
    with open(ARQUIVO_ESTADO, 'w', encoding='utf-8') as f:
        json.dump(list(quedasAtuais), f)

def main():
    http = urllib3.PoolManager()

    cidade_alvo = "Porto Alegre"
    dicionario_bairros = mapear_bairros(cidade_alvo, http)

    if not dicionario_bairros:
        print("Falha ao carregar dicionario de bairros.")
        return

    quedasAnteriores = carregarEstadoAnterior()
    quedasAtuais = set()

    dadosColetados = collectFromCEEE(http)

    for queda in dadosColetados:

        bairros_separados = [b.strip() for b in queda["bairro"].split('/') if b.strip()]

        for bairro_bruto in bairros_separados:

            nome_limpo = normalizar_nome(bairro_bruto)
            district_id = None

            if nome_limpo in CORRECOES_CEEE:
                nome_limpo = CORRECOES_CEEE[nome_limpo]

            if nome_limpo in dicionario_bairros:
                district_id = dicionario_bairros.get(nome_limpo)

            if not district_id:
                for b_json, d_id in dicionario_bairros.items():
                    if b_json in nome_limpo:
                        district_id = d_id
                        break

            if district_id:
                quedasAtuais.add(district_id)
            else:
                print(f"Aviso: Bairro {bairro_bruto} não foi encontrado no dicionario!")


    bairrosResolvidos = quedasAnteriores - quedasAtuais
    for resolvedId in bairrosResolvidos:
        enviarParaAPI(resolvedId, http, Is_Fixed=True)

    novasQuedas = quedasAtuais - quedasAnteriores
    for brokenId in novasQuedas:
        enviarParaAPI(brokenId, http, Is_Fixed=False)

    salvarEstadoAtual(quedasAtuais)
    exportarJson(dadosColetados)

if __name__ == "__main__":
    #Colocar no agendador de tarefas depois.
    while True:
        try:
            print(f"\n Nova varredura: {datetime.now().strftime('%H:%M:%S')}")
            main()
        except Exception as e:
            print(f"Erro fatal durante a varredura:{e}")
        time.sleep(30)


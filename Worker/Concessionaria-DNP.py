import urllib3
import urllib.parse
import unicodedata
import json
from datetime import datetime
import os
import time
import re
import difflib

CORRECOES_CEEE = {
    "TRES FIQUEIRAS": ["TRES FIGUEIRAS"],
    "SAO JOSE": ["VILA SAO JOSE"],
    "CENTRO": ["CENTRO HISTORICO"],
    "M. DE VENTO": ["MOINHOS DE VENTO"],
    "M DE VENTO": ["MOINHOS DE VENTO"],
    "SANTA TERESA": ["SANTA TEREZA"],
    "APARICIO BORGES": ["CORONEL APARICIO BORGES"],
    "ABERTA MORROS": ["ABERTA DOS MORROS"],
    "JARDIM ITU SABARA": ["JARDIM ITU", "JARDIM SABARA"],
    "PROTASIO ALVES": ["MORRO SANTANA"]
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
    nome = nome.replace('-', ' ').replace('.', ' ')
    nome = ' '.join(nome.split()).upper()

    abreviacoes = {
        r'\bSTA\b': 'SANTA',
        r'\bSTO\b': 'SANTO',
        r'\bSRA\b': 'SENHORA',
        r'\bJD\b': 'JARDIM',
        r'\bVIL\b': 'VILA',
        r'\bCONJ\b': 'CONJUNTO',
        r'\bLOT\b': 'LOTEAMENTO'
    }

    for abrev, completo in abreviacoes.items():
        nome = re.sub(abrev, completo, nome)

    return nome.strip()

def motor_bairro_nome(nome_sujo, dicionario_bairro):
    nome_limpo = normalizar_nome(nome_sujo)

    bairros_processar = []

    if nome_limpo in CORRECOES_CEEE:
        bairros_processar = CORRECOES_CEEE[nome_limpo]
    else:
        encontrou_erro = False
        for erro, correcao in CORRECOES_CEEE.items():
            if erro in nome_limpo:
                bairros_processar = correcao
                encontrou_erro = True
                break
        if not encontrou_erro:
            bairros_processar = [nome_limpo]
    resultados = []
    nome_oficiais = list(dicionario_bairro.keys())


    for b_nome in bairros_processar:
        if b_nome in dicionario_bairro:
            resultados.append((dicionario_bairro[b_nome], b_nome))
            continue
        matches = difflib.get_close_matches(nome_limpo, nome_oficiais, n=1, cutoff=0.75)
        if matches:
            resultados.append((dicionario_bairro[matches[0]], matches[0]))
            continue

        encontrou_parcial = False
        for bairros_osm, d_id in dicionario_bairro.items():
            if bairros_osm in nome_limpo:
                resultados.append((d_id, bairros_osm))
                encontrou_parcial = True
                break
        if not encontrou_parcial:
            resultados.append((None, b_nome))

    return resultados

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
            dados = json.load(f)

            if isinstance(dados, dict):
                return dados
    return {}

def salvarEstadoAtual(quedasAtuais):
    with open(ARQUIVO_ESTADO, 'w', encoding='utf-8') as f:
        json.dump(quedasAtuais, f, indent=4)

def main():
    http = urllib3.PoolManager()

    cidade_alvo = "Porto Alegre"
    dicionario_bairros = mapear_bairros(cidade_alvo, http)

    if not dicionario_bairros:
        print("Falha ao carregar dicionario de bairros.")
        return

    quedasAnteriores = carregarEstadoAnterior()
    quedasAtuais = {}

    dadosColetados = collectFromCEEE(http)

    for queda in dadosColetados:

        bairros_separados = [b.strip() for b in queda["bairro"].split('/') if b.strip()]

        for bairro_bruto in bairros_separados:

            resultados = motor_bairro_nome(bairro_bruto, dicionario_bairros)

            for district_id, nome_oficial in resultados:
                if district_id:
                    district_id_string = str(district_id)
                    quedasAtuais[district_id_string] = quedasAtuais.get(district_id_string, 0) + 1
                else:
                    print(f"Aviso: Bairro {bairro_bruto} (Limpo {nome_oficial}) não foi encontrado no dicionario!")


    todos_ids = set(quedasAnteriores.keys()).union(set(quedasAtuais.keys()))

    for d_id in todos_ids:
        qtd_antes = quedasAnteriores.get(d_id, 0)
        qtd_agora = quedasAtuais.get(d_id, 0)

        diferenca = qtd_agora - qtd_antes

        if diferenca > 0:
            for _ in range(diferenca):
                enviarParaAPI(d_id, http, Is_Fixed=False)
        elif diferenca < 0:
            for _ in range(abs(diferenca)):
                enviarParaAPI(d_id, http, Is_Fixed=True)

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
        time.sleep(1800)


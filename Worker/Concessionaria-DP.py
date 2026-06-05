import urllib3
from lxml import html
import io
import os
import pdfplumber
import re
import json
from datetime import datetime, timedelta
import time

LOG_FILE = "log.txt"
ARQUIVO_AGENDADOS = '../Frontend/public/data/agendamentos_ativos.json'
ARQUIVO_ENVIAR_FRONTEND = '../Frontend/public/data/agendamentos_futuros.json'

def collectFromCEEE(httpClient):

    print("Iniciando busca de dados em CEEE....")

    #Capturar os pdfs com datas e horarios programados da CEEE
    try:
        HOST = 'https://ceee.equatorialenergia.com.br/desligamento-programado/'

        r = httpClient.request('GET', HOST)

        data_string = r.data.decode('utf-8', errors='ignore')

        tree = html.fromstring(data_string)

        links = tree.xpath('//a[@href]')

        getPDF = [link.get('href') for link in links if link.get('href').lower().endswith('.pdf')]

        return getPDF
    except Exception as e:
        print(f"Erro ao tentar buscar dados em CEEE: {e}")
        return []

def tratamentoHorarios(horarioBruto):
    horarioLimpo = re.sub(r'[^0-9: \-]', '', horarioBruto).strip()

    horarioLimpo = horarioLimpo.replace(' ', '-')

    dividir = [p.strip() for p in horarioLimpo.split('-') if p.strip()]

    inicio = ""
    fim = ""

    if len(dividir) >= 2:
        inicio = dividir[0]
        fim = dividir[1]

        if ':' not in inicio and len(inicio) == 4:
            inicio = f"{inicio[:2]}:{inicio[2:]}"
        if ':' not in fim and len(fim) == 4:
            fim = f"{fim[:2]}:{fim[2:]}"
    return inicio,fim

def FormatacaoDeDadosPDF(PDFUrl, httpClient):
    print("Baixando e analisando dados de pdf...")

    dadosFinais = []

    try:
        r = httpClient.request('GET', PDFUrl)

        pdfFile = io.BytesIO(r.data)

        with pdfplumber.open(pdfFile) as pdf:
            for i, page in enumerate(pdf.pages):

                table = page.extract_table()

                if table:
                    for linha in table:
                        if not linha or "Município" in str(linha[0]):
                            continue
                        dados_limpos = [str(coluna).strip().replace('\n', ' ') if coluna else "" for coluna in linha]

                        if len(dados_limpos) >=7:
                            if dados_limpos[0].upper() == "PORTO ALEGRE":
                                horaInicio, horaFim = tratamentoHorarios(dados_limpos[3])
                                dadosFinais.append({
                                    "municipio": dados_limpos[0],
                                    "data": dados_limpos[1],
                                    "horario_inicio": horaInicio,
                                    "horario_fim": horaFim,
                                    "servico": dados_limpos[4],
                                    "bairro": dados_limpos[6].upper()
                                })
        return dadosFinais
    except Exception as e:
        print(f"Erro ao processar PDF {PDFUrl}: {e}")
        return []

def gerenciarAgendamentos(agendamentos):
    agora = datetime.now()
    agendamentosRetidos = []
    bairrosManutencaoAgora = set()

    for evento in agendamentos:
        try:
            inicioStr = f"{evento['data']} {evento['horario_inicio']}"
            fimStr = f"{evento['data']} {evento['horario_fim']}"

            inicioDate = datetime.strptime(inicioStr, "%d/%m/%Y %H:%M")
            fimDate = datetime.strptime(fimStr, "%d/%m/%Y %H:%M")

            bairroNome = evento['bairro']

            if agora < fimDate:
                agendamentosRetidos.append(evento)

            if inicioDate <= agora < fimDate:
                bairrosManutencaoAgora.add(bairroNome)

        except Exception as e:
            pass

    diretorioFuturo = os.path.dirname(ARQUIVO_AGENDADOS)
    if not os.path.exists(diretorioFuturo):
        os.makedirs(diretorioFuturo, exist_ok=True)

    with open(ARQUIVO_AGENDADOS, "w", encoding="utf-8") as f:
        json.dump(agendamentosRetidos, f, ensure_ascii=False, indent=4)


    diretorioAgendado = os.path.dirname(ARQUIVO_AGENDADOS)
    if not os.path.exists(diretorioAgendado):
        os.makedirs(diretorioAgendado, exist_ok=True)
    with open(ARQUIVO_ENVIAR_FRONTEND, "w", encoding="utf-8") as f:
        json.dump(list(bairrosManutencaoAgora), f, ensure_ascii=False, indent=4)
    
    return agendamentosRetidos

def calcularProximaVerificacao(agendamentos):
    maiorDate = None
    for evento in agendamentos:
        try:
            stringFim = f"{evento['data']} {evento['horario_fim']}"
            dateFim = datetime.strptime(stringFim, "%d/%m/%Y %H:%M")
            if maiorDate is None or dateFim > maiorDate:
                maiorDate = dateFim
        except:
            pass
    return maiorDate

def carregarLinksTXT():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f.readlines() if linha.strip()]
    
def guardarLinksTXT(link):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def exportarJson(novosDados):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    novoArquivo = f"CEEE_Report_DP_{timestamp}.json"

    with open(novoArquivo, "w", encoding="utf-8") as f:
        json.dump(novosDados, f, indent=4, ensure_ascii=False)
    print(f"Novo arquivo criado: {novoArquivo}")

def main():
    http = urllib3.PoolManager()

    proximaVerificacao = datetime.now() - timedelta(minutes=1)


    while True:
        agora = datetime.now()

        agendamentos = []
        
        if os.path.exists(ARQUIVO_AGENDADOS):
            with open(ARQUIVO_AGENDADOS, "r", encoding="utf-8") as f:
                agendamentos = json.load(f)


        if agora >= proximaVerificacao:
            print(f"\n[{agora.strftime('%H:%M:%S')}] Iniciando buscas no site da CEEE...")

            pdfs = collectFromCEEE(http)
            linkGuardados = []

            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    linkGuardados = [l.strip() for l in f.readlines()]

            for pdf in pdfs:
                if pdf.startswith('/'):
                    pdf = 'https://ceee.equatorialenergia.com.br' + pdf
                if pdf not in linkGuardados:
                    novosDados = FormatacaoDeDadosPDF(pdf, http)
                    if novosDados:
                        agendamentos.extend(novosDados)
                    with open(LOG_FILE, "a") as f:
                        f.write(pdf + "\n")

            dataLimite = calcularProximaVerificacao(agendamentos)

            if dataLimite and dataLimite > agora:
                proximaVerificacao = dataLimite
                print(f"Agendamentos encotrados. Entrando em hibernação...")
            else:
                proximaVerificacao = agora + timedelta(days=1)
                print(f"Sem agendamentos. Cooldown ativado até o próximo dia...")

        gerenciarAgendamentos(agendamentos)
        
        time.sleep(60)

if __name__ == "__main__":
    main()
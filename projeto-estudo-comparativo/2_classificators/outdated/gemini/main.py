import os
import io
import pandas as pd
from google.cloud import vision
from google.oauth2 import service_account
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================

CAMINHO_CHAVE_JSON = "chave-google-vision.json"
NOME_ARQUIVO_SAIDA = "resultado_gemini.csv"
MODELO_NOME = "gemini"

# CAMINHO BASE onde estão as pastas sim01, sim02...
BASE_PATH = "projeto-estudo-comparativo/datasets"

CLASS_MAPPING = {
    'JOY': 'alegria',
    'ANGER': 'raiva'
}

MIN_THRESHOLD = vision.Likelihood.LIKELY

class EmotionArchitect:
    def __init__(self):
        # Validação da chave
        if not os.path.exists(CAMINHO_CHAVE_JSON):
            print(f"ERRO CRÍTICO: Chave {CAMINHO_CHAVE_JSON} não encontrada.")
            exit()
            
        credentials = service_account.Credentials.from_service_account_file(CAMINHO_CHAVE_JSON)
        self.client = vision.ImageAnnotatorClient(credentials=credentials)

    def _get_likelihood_score(self, likelihood_enum):
        return int(likelihood_enum)

    def detect_emotion(self, file_path: str) -> str:
        try:
            with io.open(file_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.client.face_detection(image=image)
            
            if response.error.message: return "API_ERROR"
            if not response.face_annotations: return "NO_FACE"

            face = response.face_annotations[0]
            
            joy_score = self._get_likelihood_score(face.joy_likelihood)
            anger_score = self._get_likelihood_score(face.anger_likelihood)
            threshold_score = self._get_likelihood_score(MIN_THRESHOLD)

            # Lógica de Decisão
            if joy_score < threshold_score and anger_score < threshold_score:
                return "BAIXA_CONFIANCA"

            if joy_score > anger_score:
                return CLASS_MAPPING['JOY']
            elif anger_score > joy_score:
                return CLASS_MAPPING['ANGER']
            else:
                return CLASS_MAPPING['JOY']

        except Exception as e:
            print(f" [ERRO I/O] {os.path.basename(file_path)}: {e}")
            return "SYSTEM_ERROR"

    def run_simulation_folder(self, sim_folder_path: str):
        """
        Processa APENAS a pasta de simulação específica recebida.
        Retorna listas y_true e y_pred para aquela simulação.
        """
        y_true = []
        y_pred = []
        valid_extensions = ('.jpg', '.jpeg', '.png')
        target_folders = list(CLASS_MAPPING.values()) # ['alegria', 'raiva']
        
        sim_name = os.path.basename(sim_folder_path)
        
        # Caminha apenas dentro desta simulação
        for root, dirs, files in os.walk(sim_folder_path):
            folder_name = os.path.basename(root)
            
            # Só processa se estivermos nas pastas alvo
            if folder_name in target_folders:
                for file in files:
                    if file.lower().endswith(valid_extensions):
                        full_path = os.path.join(root, file)
                        
                        # Processamento
                        print(f" -> {sim_name} | Analisando: {file}...", end='\r')
                        pred = self.detect_emotion(full_path)
                        
                        y_true.append(folder_name)
                        y_pred.append(pred)
        
        return sim_name, y_true, y_pred

# ==========================================
# EXECUÇÃO DO LOOP (BATCH)
# ==========================================
if __name__ == "__main__":
    try:
        app = EmotionArchitect()
        
        # 1. Limpeza opcional: Se quiser começar um arquivo novo a cada execução geral
        # Se preferir manter histórico antigo, comente as 3 linhas abaixo.
        if os.path.exists(NOME_ARQUIVO_SAIDA):
             print(f"AVISO: Removendo arquivo antigo {NOME_ARQUIVO_SAIDA} para nova bateria.")
             os.remove(NOME_ARQUIVO_SAIDA)

        # 2. Descobrir todas as pastas 'sim...'
        if not os.path.exists(BASE_PATH):
            print(f"ERRO: Caminho base não encontrado: {BASE_PATH}")
            exit()

        # Lista e ordena as pastas (sim01, sim02, ..., sim30)
        pastas_simulacao = sorted([
            f for f in os.listdir(BASE_PATH) 
            if os.path.isdir(os.path.join(BASE_PATH, f)) and f.lower().startswith("sim")
        ])

        if not pastas_simulacao:
            print("Nenhuma pasta começando com 'sim' encontrada.")
            exit()

        print(f"--> Iniciando processamento de {len(pastas_simulacao)} simulações.")
        print("-" * 60)

        # 3. LOOP PRINCIPAL - Aqui está o segredo
        for pasta in pastas_simulacao:
            caminho_simulacao = os.path.join(BASE_PATH, pasta)
            
            # A. Processa a pasta
            sim_name, y_true, y_pred = app.run_simulation_folder(caminho_simulacao)
            
            if not y_true:
                print(f"\n[AVISO] {sim_name} está vazia ou sem estrutura correta. Pulando.")
                continue

            # B. Calcula Métricas daquela simulação
            labels = ['alegria', 'raiva']
            acuracia = accuracy_score(y_true, y_pred)
            
            # Matriz de Confusão para contagem
            cm = confusion_matrix(y_true, y_pred, labels=labels)
            try:
                qtd_alegria = cm[0][0]
                qtd_raiva = cm[1][1]
            except:
                qtd_alegria = 0
                qtd_raiva = 0

            # Relatório detalhado
            report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
            
            # C. Monta o dicionário de dados (LINHA DO CSV)
            dados_linha = {
                'simulacao': [sim_name],
                'modelo': [MODELO_NOME],
                'qtd_sucesso_alegria': [qtd_alegria],
                'qtd_sucesso_raiva': [qtd_raiva],
                'acuracia': [round(acuracia, 4)],
                'precisao': [round(report['weighted avg']['precision'], 4)],
                'recall': [round(report['weighted avg']['recall'], 4)],
                'f1-score': [round(report['weighted avg']['f1-score'], 4)]
            }

            # D. GRAVAÇÃO IMEDIATA (APPEND)
            df_resultado = pd.DataFrame(dados_linha)
            
            # Verifica se o arquivo já existe para decidir se escreve o cabeçalho
            arquivo_existe = os.path.isfile(NOME_ARQUIVO_SAIDA)
            
            df_resultado.to_csv(
                NOME_ARQUIVO_SAIDA, 
                mode='a',              # 'a' = Append (Adicionar ao final)
                header=not arquivo_existe, # Só escreve header se arquivo não existe
                index=False
            )
            
            print(f"\n [OK] {sim_name} processada e salva. Acurácia: {acuracia:.2%}")

        print("\n" + "="*60)
        print(f"Processamento Completo! Arquivo gerado: {os.path.abspath(NOME_ARQUIVO_SAIDA)}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nERRO FATAL: {e}")
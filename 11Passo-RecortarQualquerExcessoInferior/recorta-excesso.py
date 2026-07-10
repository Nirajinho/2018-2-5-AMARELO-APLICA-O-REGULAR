"""
Propósito: recortar excessos inferiores que possam ter ficado nas imagens, usando a faixa de rascunho como referência
Autor: Alexandre Nassar de Peder / Adaptado para padrão específico de rascunho
Criação: 02/10/2025
Atualização: 03/06/2026 (Modificado em 10/07/2026)

OBS1: puxe a pasta "questoes" do passo 10 para este passo 11
OBS2: este código vai criar uma pasta de saída chamada "finalizadas", vai percorrer o pixel central de baixo para cima procurando pelo padrão visual, e vai recortar as imagens que tem rascunho analisando, salvando as imagens recortadas nessa pasta criada.
OBS3: Padrão configurado para 4px de altura e 5px de largura com a cor RGB(35, 31, 32), limitado até a metade da imagem.
OBS4: execute o código e abra as imagens para conferir se os excessos inferiores foram recortados corretamente.
"""

from PIL import Image
import os
import shutil

def encontrar_faixa_rascunho(imagem, cor_alvo, tolerancia=15):
    """
    Encontra a faixa de início do rascunho de baixo para cima.
    Procura por um padrão de 4 pixels de altura por 5 pixels de largura.
    Para no máximo na metade da altura da imagem.
    Retorna a posição Y onde deve ser feito o corte (acima da faixa) ou None se não encontrar.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    x_centro = largura // 2
    # Limita a busca para não passar da metade da imagem (de baixo para cima)
    limite_superior = altura // 2
    
    # Percorre de baixo para cima, garantindo espaço para os 4 pixels de altura do padrão (dy de 0 a 3)
    for y in range(altura - 1, limite_superior + 3, -1):
        faixa_encontrada = True
        
        # Verifica o bloco de 4 pixels de altura (y-3 até y) por 5 pixels de largura (x-2 até x+2)
        for dy in range(4):
            pixel_y = y - 3 + dy
            
            for dx in range(-2, 3):
                pixel_x = x_centro + dx
                
                # Garante que não está fora das bordas da imagem
                if pixel_x < 0 or pixel_x >= largura or pixel_y < 0 or pixel_y >= altura:
                    faixa_encontrada = False
                    break
                
                pixel = pixels[pixel_x, pixel_y]
                if len(pixel) == 4:  # RGBA
                    r, g, b, a = pixel
                else:  # RGB
                    r, g, b = pixel[:3]
                
                # Verifica se o pixel está dentro da tolerância da cor alvo (35, 31, 32)
                if (abs(r - cor_alvo[0]) > tolerancia or 
                    abs(g - cor_alvo[1]) > tolerancia or 
                    abs(b - cor_alvo[2]) > tolerancia):
                    faixa_encontrada = False
                    break
            
            if not faixa_encontrada:
                break
                
        if faixa_encontrada:
            # Encontrou o padrão! O rascunho começa em (y-3).
            # Cortamos imediatamente acima dele para remover a faixa e tudo que está abaixo.
            posicao_corte = y - 3
            print(f"Faixa de rascunho encontrada! Cortando na posição y={posicao_corte}")
            return posicao_corte
            
    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    """
    Processa todas as imagens da pasta origem, recortando as que têm a faixa de rascunho
    e copiando todas para a pasta destino.
    """
    # Cria a pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todos os arquivos da pasta origem
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            # Abre a imagem
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # Procura pela faixa de rascunho
                posicao_corte = encontrar_faixa_rascunho(imagem, cor_alvo)
                
                if posicao_corte is not None and posicao_corte > 0:
                    # Se encontrou o início do rascunho, recorta mantendo apenas a parte de cima (0 até posicao_corte)
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    # Se não encontrou o padrão, copia a imagem original intacta
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (rascunho não detectado)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            # Tenta copiar o arquivo mesmo com erro para não perder dados
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado original devido ao erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

# Função principal
if __name__ == "__main__":
    # Configurações
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    
    # Nova cor alvo baseada na especificação: RGB(35, 31, 32)
    cor_alvo = (35, 31, 32)  
    
    print("Iniciando processamento de imagens (Foco: Remoção de Rascunho)...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo do rascunho: RGB{cor_alvo}")
    
    # Verifica se a pasta origem existe
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    # Executa o processamento
    processar_imagens(pasta_origem, pasta_destino, cor_alvo)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram processadas e salvas em: {pasta_destino}")
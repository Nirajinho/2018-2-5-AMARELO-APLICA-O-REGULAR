from PIL import Image
import os

def encontrar_faixa_cinza(imagem, cor_alvo=(209, 210, 212), tolerancia=15, altura_base=28, margem_erro=3):
    """
    Encontra as posições da faixa cinza e define o corte 8 pixels acima dela.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    altura_minima = altura_base - margem_erro  # 25 pixels
    altura_maxima = altura_base + margem_erro  # 31 pixels
    
    y = 0
    while y < altura:
        def pixel_correta(px_x, px_y):
            if px_y >= altura:
                return False
            pixel = pixels[px_x, px_y]
            r, g, b = pixel[:3]
            return (abs(r - cor_alvo[0]) <= tolerancia and 
                    abs(g - cor_alvo[1]) <= tolerancia and 
                    abs(b - cor_alvo[2]) <= tolerancia)

        if pixel_correta(largura - 2, y) or pixel_correta(largura - 1, y):
            inicio_faixa = y
            
            while y < altura and (pixel_correta(largura - 2, y) or pixel_correta(largura - 1, y)):
                y += 1
                
            altura_detectada = y - inicio_faixa
            
            if altura_minima <= altura_detectada <= altura_maxima:
                # Define o ponto de divisão 8 pixels acima do início da faixa
                posicao_corte = inicio_faixa - 10
                if posicao_corte < 0:
                    posicao_corte = 0
                    
                posicoes_corte.append(posicao_corte)
                print(f"Faixa cinza detectada em y={inicio_faixa}. Corte definido em y={posicao_corte}")
            else:
                continue
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem garantindo que a faixa cinza e a margem fiquem no topo da próxima imagem.
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: Imagem {caminho_imagem} não encontrada.")
        return
        
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    posicoes_corte = encontrar_faixa_cinza(imagem)
    
    if not posicoes_corte:
        print("Nenhuma faixa cinza dentro do padrão esperado foi encontrada!")
        return
        
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a parte de cima (questão anterior) terminando logo antes da margem da nova questão
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # O pulo do gato: A próxima imagem começa do exato ponto onde a outra terminou.
        # Isso faz com que os 8px de respiro + a faixa cinza entrem no topo do próximo bloco.
        posicao_anterior = posicao_corte
    
    # Corta a última seção (que já começa com a última faixa no topo)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "inteiras_concatenadas_verticalmente.png"  
    pasta_saida = "questoes_divididas" 
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída! Os padrões visuais agora estão no topo de cada imagem correspondente.")
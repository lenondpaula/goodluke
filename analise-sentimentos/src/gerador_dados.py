"""
Gerador de Dados Sintéticos - TechNova
Simula comentários de redes sociais para análise de sentimentos
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Inicializa Faker com locale brasileiro
fake = Faker('pt_BR')
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Templates de comentários por categoria
ELOGIOS_SUPORTE = [
    "O suporte da TechNova é incrível! Resolveram meu problema em minutos 🙌",
    "Atendimento nota 10! A equipe da TechNova é muito prestativa",
    "Nunca vi suporte tão rápido. TechNova mandou bem demais!",
    "Parabéns @TechNova pelo atendimento excepcional! Super recomendo",
    "A TechNova tem o melhor suporte que já vi. Equipe 100%!",
    "Problema resolvido em 5 minutos! Obrigado TechNova 👏",
    "Adorei o atendimento da TechNova, muito profissionais!",
    "Suporte TechNova salvou meu dia! Muito obrigado! ❤️",
    "Impressionado com a agilidade do suporte TechNova",
    "TechNova respondeu minha dúvida em segundos, top demais!",
    "Equipe de suporte da TechNova é extremamente competente!",
    "Melhor experiência de suporte que tive! Valeu TechNova!",
    "SAC da TechNova funciona de verdade! Raridade hoje em dia",
    "Atendente super educado e resolveu tudo! Parabéns TechNova",
    "TechNova entrega o que promete no pós-venda 💯",
]

RECLAMACOES_BATERIA = [
    "A bateria do produto TechNova está durando muito pouco 😡",
    "Decepcionado com a bateria do TechNova, não dura nem 4 horas",
    "Bateria péssima! TechNova precisa melhorar urgente isso",
    "Terceira vez que reclamo da bateria e nada muda @TechNova",
    "Produto TechNova é bom, mas a bateria é uma vergonha",
    "Não comprem TechNova se precisam de bateria boa, frustrante",
    "Bateria descarrega do nada! TechNova precisa resolver isso",
    "Estou arrependido da compra, bateria TechNova é muito fraca",
    "A bateria superaquece e dura pouco. Péssimo TechNova!",
    "TechNova ignorando os problemas de bateria? Inadmissível!",
    "Comprei ontem e a bateria já deu problema. TechNova fail",
    "Bateria viciada em menos de 3 meses. TechNova explica?",
    "Pior bateria do mercado! TechNova decepcionou demais",
    "A bateria não aguenta um dia de uso normal. Triste com TechNova",
    "Propaganda enganosa! Bateria TechNova não dura o prometido",
]

DUVIDAS_PRECO = [
    "Alguém sabe se a TechNova vai fazer promoção na Black Friday?",
    "Qual o preço do modelo novo da TechNova?",
    "TechNova tem desconto pra estudante?",
    "Vale a pena pagar mais caro no TechNova Pro?",
    "Onde encontro TechNova mais barato?",
    "TechNova aceita parcelamento em quantas vezes?",
    "Qual a diferença de preço entre os modelos TechNova?",
    "TechNova está caro ou é preço justo pelo que oferece?",
    "Alguém comprou TechNova no site oficial? É seguro?",
    "Tem cupom de desconto pra TechNova?",
    "TechNova Premium vale o investimento extra?",
    "Preço subiu ou sempre foi assim? Quero comprar TechNova",
    "Qual loja tem melhor preço de TechNova?",
    "Compensa esperar promoção ou compro agora o TechNova?",
    "TechNova oferece cashback?",
]

COMENTARIOS_GERAIS = [
    "Design do TechNova é muito bonito, adorei a cor!",
    "TechNova chegou antes do prazo, embalagem perfeita 📦",
    "Usando TechNova há 6 meses e estou satisfeito",
    "Qualidade do TechNova superou minhas expectativas!",
    "TechNova é bom mas poderia ser melhor no preço",
    "Recomendo TechNova pra quem busca qualidade",
    "Meu TechNova parou de funcionar depois de 1 ano 😢",
    "Tela do TechNova é linda, cores vibrantes!",
    "TechNova tem boa performance no geral",
    "Produto ok, nada de especial. TechNova mediano",
    "Comprei TechNova e não me arrependo!",
    "TechNova entregou menos do que eu esperava",
    "Som do TechNova é excelente, surpreendente!",
    "Câmera do TechNova é boa para o preço",
    "TechNova vs concorrentes? TechNova ganha fácil!",
]

PLATAFORMAS = ['Twitter', 'Instagram', 'Facebook']
PESOS_PLATAFORMAS = [0.5, 0.3, 0.2]  # Twitter mais frequente

def gerar_comentarios(n_comentarios: int = 500) -> pd.DataFrame:
    """
    Gera DataFrame com comentários sintéticos de redes sociais.
    
    Args:
        n_comentarios: Número de comentários a gerar
        
    Returns:
        DataFrame com colunas: data, plataforma, usuario, texto, likes
    """
    
    # Distribui comentários por categoria
    categorias = {
        'elogio': ELOGIOS_SUPORTE,
        'reclamacao': RECLAMACOES_BATERIA,
        'duvida': DUVIDAS_PRECO,
        'geral': COMENTARIOS_GERAIS
    }
    pesos_categorias = [0.25, 0.25, 0.20, 0.30]
    
    dados = []
    data_base = datetime.now()
    
    for _ in range(n_comentarios):
        # Seleciona categoria e comentário
        categoria = random.choices(list(categorias.keys()), weights=pesos_categorias)[0]
        texto = random.choice(categorias[categoria])
        
        # Adiciona variação ao texto
        if random.random() > 0.7:
            texto = texto + " " + fake.sentence(nb_words=3)
        
        # Gera data nos últimos 30 dias
        dias_atras = random.randint(0, 30)
        hora = random.randint(0, 23)
        minuto = random.randint(0, 59)
        data = data_base - timedelta(days=dias_atras, hours=hora, minutes=minuto)
        
        # Seleciona plataforma
        plataforma = random.choices(PLATAFORMAS, weights=PESOS_PLATAFORMAS)[0]
        
        # Gera usuário
        usuario = f"@{fake.user_name()}"
        
        # Gera likes (distribuição exponencial para simular viralidade)
        if categoria == 'reclamacao':
            # Reclamações tendem a viralizar mais
            likes = int(np.random.exponential(scale=150))
        elif categoria == 'elogio':
            likes = int(np.random.exponential(scale=80))
        else:
            likes = int(np.random.exponential(scale=40))
        
        dados.append({
            'data': data,
            'plataforma': plataforma,
            'usuario': usuario,
            'texto': texto,
            'likes': min(likes, 10000)  # Cap em 10k
        })
    
    df = pd.DataFrame(dados)
    df = df.sort_values('data', ascending=False).reset_index(drop=True)
    
    return df

def main():
    """Função principal para gerar e salvar os dados."""
    print("🚀 Gerando comentários sintéticos para TechNova...")
    
    # Gera 500 comentários
    df = gerar_comentarios(500)
    
    # Cria diretório se não existir
    os.makedirs('data', exist_ok=True)
    
    # Salva CSV
    caminho = 'data/comentarios_social.csv'
    df.to_csv(caminho, index=False)
    
    print(f"✅ {len(df)} comentários gerados e salvos em '{caminho}'")
    print(f"\n📊 Distribuição por plataforma:")
    print(df['plataforma'].value_counts())
    print(f"\n📅 Período: {df['data'].min().date()} a {df['data'].max().date()}")
    print(f"❤️ Média de likes: {df['likes'].mean():.1f}")
    
    return df

if __name__ == "__main__":
    main()

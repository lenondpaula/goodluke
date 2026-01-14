"""
PoA-Insight Explorer - Gerador de Locais de Porto Alegre
Base de dados georreferenciada com pontos turísticos reais
"""

from pathlib import Path
import pandas as pd

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def gerar_locais_poa() -> pd.DataFrame:
    """
    Gera dataset com 30 pontos turísticos reais de Porto Alegre.
    
    Categorias:
    - Parque: Áreas verdes e espaços ao ar livre
    - Museu: Espaços culturais e exposições
    - Gastronomia: Restaurantes, cafés e mercados
    - Vida Noturna: Bares, pubs e casas noturnas
    - Cultura: Teatros, centros culturais e patrimônios
    
    Tipo:
    - Indoor: Ambientes fechados (funcionam com chuva)
    - Outdoor: Ao ar livre (dependem do clima)
    
    Horário_Pico:
    - Manhã: 6h-12h
    - Tarde: 12h-18h
    - Noite: 18h-00h
    """
    
    locais = [
        # ═══════════════════════════════════════════════════════════════════════
        # PARQUES (Outdoor) - Verde e natureza
        # ═══════════════════════════════════════════════════════════════════════
        {
            "ID": 1, "Nome": "Parque da Redenção (Farroupilha)",
            "Categoria": "Parque", "Lat": -30.0392, "Lon": -51.2172,
            "Preco_Medio": 1, "Tipo": "Outdoor", "Popularidade_Base": 95,
            "Horario_Pico": "Tarde", "Descricao": "Principal parque urbano, com lago, Brique aos domingos"
        },
        {
            "ID": 2, "Nome": "Orla do Guaíba (Gasômetro)",
            "Categoria": "Parque", "Lat": -30.0345, "Lon": -51.2420,
            "Preco_Medio": 1, "Tipo": "Outdoor", "Popularidade_Base": 98,
            "Horario_Pico": "Tarde", "Descricao": "Pôr do sol mais famoso de POA, vista para o Guaíba"
        },
        {
            "ID": 3, "Nome": "Parque Moinhos de Vento (Parcão)",
            "Categoria": "Parque", "Lat": -30.0275, "Lon": -51.2005,
            "Preco_Medio": 1, "Tipo": "Outdoor", "Popularidade_Base": 88,
            "Horario_Pico": "Tarde", "Descricao": "Parque nobre com lago, patos e área para pets"
        },
        {
            "ID": 4, "Nome": "Parque Marinha do Brasil",
            "Categoria": "Parque", "Lat": -30.0505, "Lon": -51.2340,
            "Preco_Medio": 1, "Tipo": "Outdoor", "Popularidade_Base": 75,
            "Horario_Pico": "Manhã", "Descricao": "Extenso parque com pistas de caminhada e ciclismo"
        },
        {
            "ID": 5, "Nome": "Jardim Botânico",
            "Categoria": "Parque", "Lat": -30.0540, "Lon": -51.1770,
            "Preco_Medio": 1, "Tipo": "Outdoor", "Popularidade_Base": 82,
            "Horario_Pico": "Manhã", "Descricao": "Jardim científico com mata nativa e trilhas"
        },
        
        # ═══════════════════════════════════════════════════════════════════════
        # MUSEUS (Indoor) - Arte e história
        # ═══════════════════════════════════════════════════════════════════════
        {
            "ID": 6, "Nome": "Fundação Iberê Camargo",
            "Categoria": "Museu", "Lat": -30.0710, "Lon": -51.2580,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 90,
            "Horario_Pico": "Tarde", "Descricao": "Arquitetura icônica de Álvaro Siza, arte contemporânea"
        },
        {
            "ID": 7, "Nome": "MARGS - Museu de Arte do RS",
            "Categoria": "Museu", "Lat": -30.0329, "Lon": -51.2290,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 85,
            "Horario_Pico": "Tarde", "Descricao": "Acervo de arte gaúcha e brasileira na Praça da Alfândega"
        },
        {
            "ID": 8, "Nome": "Museu de Ciências e Tecnologia (PUCRS)",
            "Categoria": "Museu", "Lat": -30.0595, "Lon": -51.1740,
            "Preco_Medio": 3, "Tipo": "Indoor", "Popularidade_Base": 92,
            "Horario_Pico": "Tarde", "Descricao": "Maior museu interativo da América Latina"
        },
        {
            "ID": 9, "Nome": "Memorial do RS",
            "Categoria": "Museu", "Lat": -30.0350, "Lon": -51.2305,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 70,
            "Horario_Pico": "Tarde", "Descricao": "História e cultura gaúcha no centro histórico"
        },
        {
            "ID": 10, "Nome": "Museu Júlio de Castilhos",
            "Categoria": "Museu", "Lat": -30.0340, "Lon": -51.2220,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 65,
            "Horario_Pico": "Manhã", "Descricao": "Museu histórico mais antigo do estado"
        },
        
        # ═══════════════════════════════════════════════════════════════════════
        # GASTRONOMIA (Indoor/Outdoor) - Sabores de POA
        # ═══════════════════════════════════════════════════════════════════════
        {
            "ID": 11, "Nome": "Mercado Público",
            "Categoria": "Gastronomia", "Lat": -30.0280, "Lon": -51.2280,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 95,
            "Horario_Pico": "Manhã", "Descricao": "Mercado histórico, bancas tradicionais e Banca 40"
        },
        {
            "ID": 12, "Nome": "Rua Padre Chagas",
            "Categoria": "Gastronomia", "Lat": -30.0265, "Lon": -51.2025,
            "Preco_Medio": 4, "Tipo": "Outdoor", "Popularidade_Base": 88,
            "Horario_Pico": "Noite", "Descricao": "Corredor gastronômico de Moinhos de Vento"
        },
        {
            "ID": 13, "Nome": "Gambrinus (Cidade Baixa)",
            "Categoria": "Gastronomia", "Lat": -30.0435, "Lon": -51.2155,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 80,
            "Horario_Pico": "Noite", "Descricao": "Bar tradicional com cerveja artesanal e petiscos"
        },
        {
            "ID": 14, "Nome": "Chalé da Praça XV",
            "Categoria": "Gastronomia", "Lat": -30.0295, "Lon": -51.2295,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 75,
            "Horario_Pico": "Tarde", "Descricao": "Café histórico no centro, arquitetura de 1885"
        },
        {
            "ID": 15, "Nome": "Banca 40 (Mercado Público)",
            "Categoria": "Gastronomia", "Lat": -30.0280, "Lon": -51.2282,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 85,
            "Horario_Pico": "Manhã", "Descricao": "Lendária banca de temperos e simpatias"
        },
        {
            "ID": 16, "Nome": "Oliva Restaurante",
            "Categoria": "Gastronomia", "Lat": -30.0250, "Lon": -51.2040,
            "Preco_Medio": 5, "Tipo": "Indoor", "Popularidade_Base": 78,
            "Horario_Pico": "Noite", "Descricao": "Alta gastronomia com ingredientes locais"
        },
        
        # ═══════════════════════════════════════════════════════════════════════
        # VIDA NOTURNA (Indoor) - Festas e bares
        # ═══════════════════════════════════════════════════════════════════════
        {
            "ID": 17, "Nome": "Cidade Baixa (Polo Gastronômico)",
            "Categoria": "Vida Noturna", "Lat": -30.0420, "Lon": -51.2180,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 98,
            "Horario_Pico": "Noite", "Descricao": "Boemia porto-alegrense, dezenas de bares"
        },
        {
            "ID": 18, "Nome": "Ocidente Bar",
            "Categoria": "Vida Noturna", "Lat": -30.0410, "Lon": -51.2190,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 85,
            "Horario_Pico": "Noite", "Descricao": "Bar cult com shows ao vivo e ambiente alternativo"
        },
        {
            "ID": 19, "Nome": "Opinião (Casa de Shows)",
            "Categoria": "Vida Noturna", "Lat": -30.0415, "Lon": -51.2170,
            "Preco_Medio": 3, "Tipo": "Indoor", "Popularidade_Base": 88,
            "Horario_Pico": "Noite", "Descricao": "Palco histórico da música gaúcha e nacional"
        },
        {
            "ID": 20, "Nome": "Beco do Espelho",
            "Categoria": "Vida Noturna", "Lat": -30.0425, "Lon": -51.2165,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 75,
            "Horario_Pico": "Noite", "Descricao": "Bar descolado em beco decorado com espelhos"
        },
        {
            "ID": 21, "Nome": "Agulha Bar",
            "Categoria": "Vida Noturna", "Lat": -30.0430, "Lon": -51.2155,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 82,
            "Horario_Pico": "Noite", "Descricao": "DJ sets e ambiente jovem na Cidade Baixa"
        },
        
        # ═══════════════════════════════════════════════════════════════════════
        # CULTURA (Indoor) - Teatros e patrimônio
        # ═══════════════════════════════════════════════════════════════════════
        {
            "ID": 22, "Nome": "Casa de Cultura Mario Quintana",
            "Categoria": "Cultura", "Lat": -30.0330, "Lon": -51.2260,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 92,
            "Horario_Pico": "Tarde", "Descricao": "Centro cultural no antigo Hotel Majestic"
        },
        {
            "ID": 23, "Nome": "Theatro São Pedro",
            "Categoria": "Cultura", "Lat": -30.0318, "Lon": -51.2270,
            "Preco_Medio": 3, "Tipo": "Indoor", "Popularidade_Base": 85,
            "Horario_Pico": "Noite", "Descricao": "Teatro histórico de 1858, óperas e concertos"
        },
        {
            "ID": 24, "Nome": "Santander Cultural",
            "Categoria": "Cultura", "Lat": -30.0290, "Lon": -51.2295,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 88,
            "Horario_Pico": "Tarde", "Descricao": "Exposições de arte em prédio art déco"
        },
        {
            "ID": 25, "Nome": "Catedral Metropolitana",
            "Categoria": "Cultura", "Lat": -30.0305, "Lon": -51.2275,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 80,
            "Horario_Pico": "Manhã", "Descricao": "Arquitetura renascentista, vista panorâmica do mirante"
        },
        {
            "ID": 26, "Nome": "Usina do Gasômetro",
            "Categoria": "Cultura", "Lat": -30.0340, "Lon": -51.2425,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 90,
            "Horario_Pico": "Tarde", "Descricao": "Centro cultural na antiga usina, cinema e exposições"
        },
        {
            "ID": 27, "Nome": "Praça da Alfândega",
            "Categoria": "Cultura", "Lat": -30.0300, "Lon": -51.2290,
            "Preco_Medio": 1, "Tipo": "Outdoor", "Popularidade_Base": 85,
            "Horario_Pico": "Tarde", "Descricao": "Praça histórica, Feira do Livro anual"
        },
        {
            "ID": 28, "Nome": "Centro Histórico",
            "Categoria": "Cultura", "Lat": -30.0320, "Lon": -51.2280,
            "Preco_Medio": 1, "Tipo": "Outdoor", "Popularidade_Base": 82,
            "Horario_Pico": "Manhã", "Descricao": "Caminhada por prédios históricos e ruas antigas"
        },
        {
            "ID": 29, "Nome": "Biblioteca Pública do Estado",
            "Categoria": "Cultura", "Lat": -30.0335, "Lon": -51.2255,
            "Preco_Medio": 1, "Tipo": "Indoor", "Popularidade_Base": 68,
            "Horario_Pico": "Manhã", "Descricao": "Acervo histórico e arquitetura neoclássica"
        },
        {
            "ID": 30, "Nome": "Cinemateca Capitólio",
            "Categoria": "Cultura", "Lat": -30.0410, "Lon": -51.2215,
            "Preco_Medio": 2, "Tipo": "Indoor", "Popularidade_Base": 78,
            "Horario_Pico": "Noite", "Descricao": "Cinema de arte e festivais de filmes"
        },
    ]
    
    df = pd.DataFrame(locais)
    return df


def main():
    """Gera o dataset de locais de Porto Alegre."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🗺️  PoA-Insight Explorer - Gerador de Locais")
    print("=" * 50)
    
    # Gerar locais
    print("\n📍 Gerando base de pontos turísticos...")
    df = gerar_locais_poa()
    
    # Salvar CSV
    csv_path = DATA_DIR / "locais_poa.csv"
    df.to_csv(csv_path, index=False)
    print(f"   ✓ Salvo em {csv_path}")
    print(f"   → {len(df)} locais cadastrados")
    
    # Resumo por categoria
    print("\n📊 Distribuição por Categoria:")
    for cat in df["Categoria"].unique():
        count = len(df[df["Categoria"] == cat])
        indoor = len(df[(df["Categoria"] == cat) & (df["Tipo"] == "Indoor")])
        print(f"   {cat}: {count} locais ({indoor} indoor, {count-indoor} outdoor)")
    
    # Resumo por horário pico
    print("\n⏰ Distribuição por Horário de Pico:")
    for horario in ["Manhã", "Tarde", "Noite"]:
        count = len(df[df["Horario_Pico"] == horario])
        print(f"   {horario}: {count} locais")
    
    print("\n✅ Base de locais gerada com sucesso!")


if __name__ == "__main__":
    main()

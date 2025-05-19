import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# CONFIGURAÇÕES DA PÁGINA
st.set_page_config(
    page_title="Operacional",
    page_icon="🛠",
    layout="wide"
)

# CARREGANDO DADOS
df = pd.read_excel("opracionalTratado.xlsx")
df.columns = df.columns.str.strip()

# CONVERSÕES
df['Custo Manutenção'] = pd.to_numeric(df['Custo Manutenção'], errors='coerce')
df['Tempo Parado (dias)'] = pd.to_numeric(df['Tempo Parado (dias)'], errors='coerce')
df['Data Manutenção'] = pd.to_datetime(df['Data Manutenção'], errors='coerce')

# DICIONÁRIO DE FILTROS
filtros = {
    "setor": "Setor",
    "status": "Status Atual",
    "modelo": "Modelo",
    "tipo_manutencao": "Tipo Manutenção",
    "custo_manutencao": "Custo Manutenção",
    "tempo_parado": "Tempo Parado (dias)"
}

# FUNÇÃO PARA APLICAR FILTROS
def aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    st.sidebar.header("Filtros")
    df_filtrado = df.copy()

    for chave, coluna in filtros.items():
        if coluna not in df.columns:
            continue

        usar_filtro = st.sidebar.checkbox(f"Filtrar por: {coluna}", key=f"{chave}_checkbox")

        if usar_filtro:
            if pd.api.types.is_numeric_dtype(df[coluna]):
                minimo = int(df[coluna].min(skipna=True))
                maximo = int(df[coluna].max(skipna=True))
                faixa = st.sidebar.slider(
                    label=coluna,
                    min_value=minimo,
                    max_value=maximo,
                    value=(minimo, maximo),
                    key=chave
                )
                df_filtrado = df_filtrado[df_filtrado[coluna].between(faixa[0], faixa[1])]
            else:
                opcoes = sorted(df[coluna].dropna().unique())
                selecao = st.sidebar.multiselect(
                    label=coluna,
                    options=opcoes,
                    default=opcoes,
                    key=chave
                )
                if selecao:
                    df_filtrado = df_filtrado[df_filtrado[coluna].isin(selecao)]

    return df_filtrado

# Aplicar filtros
df_filtrado = aplicar_filtros(df, filtros)

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# Página Home
def pagina_home():
    st.title("📊 Visão Geral")

    total_custo = df_filtrado["Custo Manutenção"].sum()
    media_parado = df_filtrado["Tempo Parado (dias)"].mean()
    unicos_modelos = df_filtrado["Modelo"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Custo Total de Manutenção", f"R$ {total_custo:,.2f}")
    col2.metric("⏱️ Média Tempo Parado (dias)", f"{media_parado:.1f}")
    col3.metric("🔧 Modelos Únicos", unicos_modelos)

    st.markdown("---")
    st.title("📌 Indicadores Setoriais")

    setores = df_filtrado["Setor"].unique()
    cols = st.columns(len(setores))
    for i, setor in enumerate(setores):
        subtotal = df_filtrado[df_filtrado["Setor"] == setor]["Custo Manutenção"].sum()
        cols[i].metric(setor, f"R$ {subtotal:,.0f}")

# Página Gráficos
def pagina_graficos():
    st.title("📈 Análise Gráfica")

    # Gráfico 1: Status por Setor
    status_por_setor = df_filtrado.groupby(['Setor', 'Status Atual']).size().reset_index(name='Quantidade')
    fig1 = px.bar(status_por_setor, x='Setor', y='Quantidade', color='Status Atual',
                  title='Status dos Equipamentos por Setor', barmode='group')
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Tipo de Manutenção
    manutencao_contagem = df_filtrado['Tipo Manutenção'].value_counts().reset_index()
    manutencao_contagem.columns = ['Tipo Manutenção', 'Quantidade']
    fig2 = px.pie(manutencao_contagem, names='Tipo Manutenção', values='Quantidade',
                  title='Distribuição dos Tipos de Manutenção')
    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3: Custo por Setor
    custo_por_setor = df_filtrado.groupby('Setor')['Custo Manutenção'].sum().reset_index()
    fig3 = px.bar(custo_por_setor, x='Setor', y='Custo Manutenção',
                  title='Custo Total de Manutenção por Setor', text_auto='.2s')
    st.plotly_chart(fig3, use_container_width=True)

    # Gráfico 6: Setores com mais tempo parado
    tempo_parado = df_filtrado.sort_values('Tempo Parado (dias)', ascending=False).head(10)
    fig6 = px.bar(tempo_parado, x='Tempo Parado (dias)', y='Setor', color='Setor',
                  title='Setores com mais tempo parado para manutenção', hover_data=['Setor'])
    st.plotly_chart(fig6, use_container_width=True)

    # Gráfico 8: Top 10 Tipos de Manutenção com Maior Tempo Parado por Setor
    tempo_parado_por_tipo_setor = df_filtrado.groupby(['Tipo Manutenção', 'Setor'])['Tempo Parado (dias)'].sum().reset_index()

    # Filtra os 10 tipos de manutenção com maior tempo parado total
    top_tipos_parado = df_filtrado.groupby('Tipo Manutenção')['Tempo Parado (dias)'].sum().nlargest(10).index
    tempo_parado_por_tipo_setor = tempo_parado_por_tipo_setor[tempo_parado_por_tipo_setor['Tipo Manutenção'].isin(top_tipos_parado)]

    fig8 = px.bar(
        tempo_parado_por_tipo_setor,
        x='Tempo Parado (dias)',
        y='Tipo Manutenção',
        color='Setor',
        orientation='h',
        title='Tipos de Manutenção com Maior Tempo Parado por Setor',
        text_auto='.2s',
        barmode='stack'
    )
    st.plotly_chart(fig8, use_container_width=True)

# Navegação no menu lateral
with st.sidebar:
    pagina = option_menu(
        menu_title="Navegação",
        options=["Home", "Gráficos"],
        icons=["house", "bar-chart"],
        default_index=0
    )

if pagina == "Home":
    pagina_home()
elif pagina == "Gráficos":
    pagina_graficos()

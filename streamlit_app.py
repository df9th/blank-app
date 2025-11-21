import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from math import erf

st.set_page_config(page_title="Gráfico de controle – Cumbucas de Uva", layout="wide")



def normal_cdf(z: float) -> float:
    return 0.5 * (1 + erf(z / np.sqrt(2)))

def obter_constantes_xbar_r(n: int):
    tabela = {
        2: {"A2": 1.880, "D3": 0.000, "D4": 3.267, "d2": 1.128},
        3: {"A2": 1.023, "D3": 0.000, "D4": 2.574, "d2": 1.693},
        4: {"A2": 0.729, "D3": 0.000, "D4": 2.282, "d2": 2.059},
        5: {"A2": 0.577, "D3": 0.000, "D4": 2.115, "d2": 2.326},
        6: {"A2": 0.483, "D3": 0.000, "D4": 2.004, "d2": 2.534},
        7: {"A2": 0.419, "D3": 0.076, "D4": 1.924, "d2": 2.704},
        8: {"A2": 0.373, "D3": 0.136, "D4": 1.864, "d2": 2.847},
        9: {"A2": 0.337, "D3": 0.184, "D4": 1.816, "d2": 2.970},
        10: {"A2": 0.308, "D3": 0.223, "D4": 1.777, "d2": 3.078},
    }
    if n not in tabela:
        st.error(f"Não tenho constantes para subgrupo n = {n}. Use entre 2 e 10.")
        st.stop()
    return tabela[n]["A2"], tabela[n]["D3"], tabela[n]["D4"], tabela[n]["d2"]



st.title("Gráfico de controle – Cumbucas de Uva")
st.write("Ferramenta para o projeto final de Controle Estatístico da Qualidade.")
st.write("___")



file = st.file_uploader("Envie o arquivo CSV ou XLSX (formato: Amostra | x1 | x2 | ...)", type=["csv", "xlsx"])

if file is not None:
    
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    
    df.rename(columns={df.columns[0]: "Amostra"}, inplace=True)
    measure_cols = df.columns[1:].tolist()
    n = len(measure_cols)

   
    df[measure_cols] = df[measure_cols].apply(pd.to_numeric, errors="coerce")

    
    df["Xbar"] = df[measure_cols].mean(axis=1)
    df["R"] = df[measure_cols].max(axis=1) - df[measure_cols].min(axis=1)

    Xbar_bar = float(df["Xbar"].mean())
    R_bar = float(df["R"].mean())

    
    valores = df[measure_cols].values.flatten()
    valores = valores[~np.isnan(valores)]  

    media = float(np.mean(valores))
    desvio = float(np.std(valores, ddof=1))
    variancia = float(np.var(valores, ddof=1))
    minimo = float(np.min(valores))
    maximo = float(np.max(valores))
    amplitude = maximo - minimo

   
    A2, D3, D4, d2 = obter_constantes_xbar_r(n)

    
    UCL_X = Xbar_bar + A2 * R_bar
    LCL_X = Xbar_bar - A2 * R_bar

    UCL_R = D4 * R_bar
    LCL_R = D3 * R_bar

  

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Visão Geral",
        "Estatísticas Descritivas",
        "Histograma e Boxplot",
        "Gráficos de Controle",
        "Capacidade e Performance"
    ])

   
    with tab1:
        st.subheader("Visão Geral dos Dados")

        c1, c2, c3 = st.columns(3)
        c1.metric("Nº de Amostras (subgrupos)", df.shape[0])
        c2.metric("Tamanho do Subgrupo (n)", n)
        c3.metric("Total de Observações", len(valores))

        st.write("___")
        st.dataframe(df, use_container_width=True)


    with tab2:
        st.subheader("Estatísticas Descritivas – Todas as Observações")

        c1, c2, c3 = st.columns(3)
        c1.metric("Média Geral", f"{media:.2f} g")
        c2.metric("Desvio Padrão Amostral", f"{desvio:.2f} g")
        c3.metric("Variância", f"{variancia:.2f} g²")

        c4, c5, c6 = st.columns(3)
        c4.metric("Mínimo", f"{minimo:.2f} g")
        c5.metric("Máximo", f"{maximo:.2f} g")
        c6.metric("Amplitude", f"{amplitude:.2f} g")

        st.write("___")
        st.write("Estas estatísticas são calculadas considerando todas as medições individuais (x1, x2, ..., xn).")

 
    with tab3:
        st.subheader("Histograma da Distribuição das Medições")

    
   
        min_val = np.floor(valores.min())
        max_val = np.ceil(valores.max())

     
        bins = np.arange(min_val, max_val + 1, 1)

        hist = px.histogram(
            x=valores,
            nbins=len(bins),
            labels={"x": "Peso (g)", "y": "Frequência"},
            title="Histograma com Faixas de 1 g",
            opacity=0.75,
        )

        
        hist.update_traces(xbins=dict(
            start=min_val,
            end=max_val,
            size=1  
        ))

      
        hist.add_vline(
            x=media,
            line_color="red",
            line_dash="dash",
            annotation_text=f"Média = {media:.2f}",
            annotation_position="top right",
            annotation=dict(font=dict(color="black"), yshift=20),
        )

        st.plotly_chart(hist, use_container_width=True)


        st.subheader("Boxplot dos Pesos")
            box = px.box(
                y=valores,
                labels={"y": "Peso (g)"},
                title="Boxplot dos Pesos",
            )
            st.plotly_chart(box, use_container_width=True)

   
    with tab4:
        
        st.subheader("Gráfico de Controle – X̄")
        st.write("Limites do Gráfico de Controle – X̄")
        cx1, cx2, cx3 = st.columns(3)
        cx1.metric("LCL (Inferior)", f"{LCL_X:.3f}")
        cx2.metric("CL (Média)", f"{Xbar_bar:.3f}")
        cx3.metric("UCL (Superior)", f"{UCL_X:.3f}")
        st.write("___")

  
        fig_x = go.Figure()
        fig_x.add_trace(go.Scatter(
            x=df["Amostra"],
            y=df["Xbar"],
            mode="lines+markers",
            name="X̄ por subgrupo",
            line=dict(color="blue"),          
            marker=dict(size=8,color="blue"),        
        ))
        fig_x.add_hline(
            y=Xbar_bar,
            line_color="green",
            annotation_text=f"CL = {Xbar_bar:.3f}",
            annotation_position="top left",
            annotation=dict(font=dict(color="black"), yshift=12),
        )
        fig_x.add_hline(
            y=UCL_X,
            line_color="red",
            line_dash="dash",
            annotation_text=f"UCL = {UCL_X:.3f}",
            annotation_position="top left",
            annotation=dict(font=dict(color="black"), yshift=12),
        )
        fig_x.add_hline(
            y=LCL_X,
            line_color="red",
            line_dash="dash",
            annotation_text=f"LCL = {LCL_X:.3f}",
            annotation_position="bottom left",
            annotation=dict(font=dict(color="black"), yshift=-12),
        )

        fig_x.update_layout(
            height=450,
            xaxis_title="Amostra",
            yaxis_title="Média (X̄)",
            title="Gráfico de Controle de Médias (X̄)",
        )
        st.plotly_chart(fig_x, use_container_width=True)

        st.write("___")

        
        st.subheader("Gráfico de Controle – R")
        st.write("Limites do Gráfico de Controle – R")
        cr1, cr2, cr3 = st.columns(3)
        cr1.metric("LCL (Inferior)", f"{LCL_R:.3f}")
        cr2.metric("CL (Média)", f"{R_bar:.3f}")
        cr3.metric("UCL (Superior)", f"{UCL_R:.3f}")
        st.write("___")

      
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(
            x=df["Amostra"],
            y=df["R"],
            mode="lines+markers",
            name="Amplitude (R)",
            line=dict(color="blue"),          # cor da linha
            marker=dict(size=8,color="blue"),
        ))
        fig_r.add_hline(
            y=R_bar,
            line_color="green",
            annotation_text=f"CL = {R_bar:.3f}",
            annotation_position="top left",
            annotation=dict(font=dict(color="black"), yshift=12),
        )
        fig_r.add_hline(
            y=UCL_R,
            line_color="red",
            line_dash="dash",
            annotation_text=f"UCL = {UCL_R:.3f}",
            annotation_position="top left",
            annotation=dict(font=dict(color="black"), yshift=12),
        )
        fig_r.add_hline(
            y=LCL_R,
            line_color="red",
            line_dash="dash",
            annotation_text=f"LCL = {LCL_R:.3f}",
            annotation_position="bottom left",
            annotation=dict(font=dict(color="black"), yshift=-12),
        )

        fig_r.update_layout(
            height=450,
            xaxis_title="Amostra",
            yaxis_title="Amplitude (R)",
            title="Gráfico de Controle de Amplitudes (R)",
        )
        st.plotly_chart(fig_r, use_container_width=True)


        # ======= CÁLCULOS DETALHADOS – Xbar e R =======
        st.markdown(f"""
<div class="calc-box">
<div class="calc-title">Cálculo dos Limites – Gráfico X̄</div>

**CL = X̄̄ = {Xbar_bar:.3f}**

---

**UCL = X̄̄ + A₂ × R̄**  
UCL = {Xbar_bar:.3f} + {A2:.3f} × {R_bar:.3f}  
**UCL = {UCL_X:.3f}**

---

**LCL = X̄̄ − A₂ × R̄**  
LCL = {Xbar_bar:.3f} − {A2:.3f} × {R_bar:.3f}  
**LCL = {LCL_X:.3f}**

</div>
""", unsafe_allow_html=True)


        st.markdown(f"""
<div class="calc-box">
<div class="calc-title">Cálculo dos Limites – Gráfico R</div>

**CL = R̄ = {R_bar:.3f}**

---

**UCL_R = D₄ × R̄**  
UCL_R = {D4:.3f} × {R_bar:.3f}  
**UCL_R = {UCL_R:.3f}**

---

**LCL_R = D₃ × R̄**  
LCL_R = {D3:.3f} × {R_bar:.3f}  
**LCL_R = {LCL_R:.3f}**

</div>
""", unsafe_allow_html=True)



    with tab5:
        st.subheader("Capacidade do Processo e Performance")

        st.write("Defina os limites de especificação (LSL e USL):")

        col_lsl, col_usl = st.columns(2)
        LSL = col_lsl.number_input("LSL (Limite Inferior)", value=495.0)
        USL = col_usl.number_input("USL (Limite Superior)", value=505.0)

        st.write(f"LSL = {LSL:.2f} g")
        st.write(f"USL = {USL:.2f} g")
        st.write("___")


        sigma_est = R_bar / d2 if d2 != 0 else np.nan

        Cp = (USL - LSL) / (6 * sigma_est) if sigma_est > 0 else np.nan
        Cpu = (USL - Xbar_bar) / (3 * sigma_est) if sigma_est > 0 else np.nan
        Cpl = (Xbar_bar - LSL) / (3 * sigma_est) if sigma_est > 0 else np.nan
        Cpk = min(Cpu, Cpl) if sigma_est > 0 else np.nan

    
        Z_sup = (USL - Xbar_bar) / sigma_est if sigma_est > 0 else np.nan
        Z_inf = (Xbar_bar - LSL) / sigma_est if sigma_est > 0 else np.nan

     
        p_acima = 1 - normal_cdf(Z_sup) if sigma_est > 0 else np.nan
        p_abaixo = 1 - normal_cdf(Z_inf) if sigma_est > 0 else np.nan
        p_total = p_acima + p_abaixo if sigma_est > 0 else np.nan

        st.write("___")

        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("σ estimado (R̄/d2)", f"{sigma_est:.3f}")
        cc2.metric("Cp", f"{Cp:.3f}")
        cc3.metric("Cpk", f"{Cpk:.3f}")

        cc4, cc5, cc6 = st.columns(3)
        cc4.metric("Z superior", f"{Z_sup:.3f}")
        cc5.metric("Z inferior", f"{Z_inf:.3f}")
        cc6.metric("% Total fora", f"{p_total * 100:.4f} %")

        st.write("___")
        st.subheader("Histograma com LSL e USL")

# Define o range dos bins baseado nos valores reais
        min_val = np.floor(valores.min())
        max_val = np.ceil(valores.max())

        fig_cap = px.histogram(
            x=valores,
            labels={"x": "Peso (g)", "y": "Frequência"},
            title="Histograma com LSL e USL (faixas de 1 g)",
            opacity=0.75,
        )

        # bins de 1 g
        fig_cap.update_traces(
            xbins=dict(
                start=min_val,
                end=max_val,
                size=1  # largura = 1 g
            )
        )

        # LSL
        fig_cap.add_vline(
            x=LSL,
            line_color="red",
            line_dash="dash",
            annotation_text=f"LSL = {LSL:.2f}",
            annotation_position="top left",
            annotation=dict(font=dict(color="black"), yshift=20),
        )

        # USL
        fig_cap.add_vline(
            x=USL,
            line_color="red",
            line_dash="dash",
            annotation_text=f"USL = {USL:.2f}",
            annotation_position="top right",
            annotation=dict(font=dict(color="black"), yshift=20),
        )

        # Média
        fig_cap.add_vline(
            x=Xbar_bar,
            line_color="black",
            line_dash="dash",
            annotation_text=f"Média = {Xbar_bar:.2f}",
            annotation_position="bottom right",
            annotation=dict(
                font=dict(color="black", size=12),
                yshift=-40,
                xshift=30
            ),
        )

        st.plotly_chart(fig_cap, use_container_width=True)



        # ======== CÁLCULOS DETALHADOS – CAPACIDADE =========

        st.markdown(f"""
<div class="calc-box">
<div class="calc-title">Estimativa do Desvio Padrão (σ)</div>

σ = R̄ / d₂  
σ = {R_bar:.3f} / {d2:.3f}  
**σ = {sigma_est:.3f}**

</div>
""", unsafe_allow_html=True)

        st.markdown(f"""
<div class="calc-box">
<div class="calc-title">Índices Cp, Cpu, Cpl e Cpk</div>

**Cp = (USL - LSL) / (6σ)**  
Cp = ({USL:.2f} - {LSL:.2f}) / (6 × {sigma_est:.3f})  
**Cp = {Cp:.3f}**

---

**Cpu = (USL - X̄̄) / (3σ)**  
Cpu = ({USL:.2f} - {Xbar_bar:.3f}) / (3 × {sigma_est:.3f})  
**Cpu = {Cpu:.3f}**

---

**Cpl = (X̄̄ - LSL) / (3σ)**  
Cpl = ({Xbar_bar:.3f} - {LSL:.2f}) / (3 × {sigma_est:.3f})  
**Cpl = {Cpl:.3f}**

---

Cpk = min(Cpu, Cpl)  
Cpk = min({Cpu:.3f}, {Cpl:.3f})  
**Cpk = {Cpk:.3f}**

</div>
""", unsafe_allow_html=True)

        st.markdown(f"""
<div class="calc-box">
<div class="calc-title">Probabilidade de Peças Fora da Especificação</div>

**Acima do USL:**  
p_acima = 1 − Φ(Zₛ)  
p_acima = 1 − Φ({Z_sup:.3f})  
**p_acima = {p_acima*100:.4f}%**

---

**Abaixo do LSL:**  
p_abaixo = 1 − Φ(Zᵢ)  
p_abaixo = 1 − Φ({Z_inf:.3f})  
**p_abaixo = {p_abaixo*100:.4f}%**

---

**Total Fora:**  
p_total = p_acima + p_abaixo  
p_total = {p_acima*100:.4f}% + {p_abaixo*100:.4f}%  
**p_total = {p_total*100:.4f}%**

</div>
""", unsafe_allow_html=True)

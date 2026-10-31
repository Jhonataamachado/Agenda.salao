import streamlit as st
import json
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Agendamento Salão", page_icon="💇‍♀️", layout="centered")

# Nome do arquivo de banco de dados local
DB_FILE = "agendamentos.json"

# Serviços e horários expandidos (08h às 21h)
SERVICOS = {
    "Corte Feminino": 60.0,
    "Corte Masculino": 40.0,
    "Manicure & Pedicure": 50.0,
    "Coloração / Luzes": 150.0,
    "Escova / Hidratação": 70.0
}
HORARIOS = [f"{str(h).zfill(2)}:00" for h in range(8, 22)]

# Função para carregar agendamentos
def carregar_dados():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# Função para salvar agendamentos
def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Carrega os dados no início do app
agendamentos = carregar_dados()

# Sidebar de navegação
st.sidebar.title("💇‍♀️ Salão & Beleza")
menu = st.sidebar.radio("Navegar", ["Agendar Horário", "Painel da Administração"])

# --- MENU: AGENDAR HORÁRIO ---
if menu == "Agendar Horário":
    st.title("📅 Agendamento Online")
    st.markdown("Reserve o seu horário de forma rápida e prática!")

    with st.form("form_agendamento", clear_on_submit=True):
        nome = st.text_input("Seu Nome completo*", placeholder="Digite seu nome")
        telefone = st.text_input("Seu Telefone / WhatsApp*", placeholder="(11) 99999-9999")
        servico = st.selectbox("Escolha o Serviço", list(SERVICOS.keys()))
        data = st.date_input("Escolha a Data", min_value=datetime.today())
        horario = st.selectbox("Escolha o Horário", HORARIOS)
        
        # Detalhes adicionais
        data_str = data.strftime("%Y-%m-%d")
        preco = SERVICOS[servico]
        
        st.info(f"💰 Valor estimado do serviço: R$ {preco:.2f}")
        
        submetido = st.form_submit_button("Confirmar Agendamento 🔒")
        
        if submetido:
            if not nome or not telefone:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                # Verificar se o horário e data já estão ocupados
                conflito = any(
                    a["data"] == data_str and a["horario"] == horario 
                    for a in agendamentos
                )
                
                if conflito:
                    st.error(f"❌ Desculpe, o horário das {horario} no dia {data_str} já está reservado. Escolha outro!")
                else:
                    # Registrar o agendamento
                    novo_agendamento = {
                        "nome": nome,
                        "telefone": telefone,
                        "servico": servico,
                        "data": data_str,
                        "horario": horario,
                        "preco": preco,
                        "status": "Pendente"
                    }
                    agendamentos.append(novo_agendamento)
                    salvar_dados(agendamentos)
                    
                    st.success(f"🎉 Maravilha, {nome}! Seu horário para {servico} no dia {data_str} às {horario} foi reservado com sucesso!")
                    st.balloons()

# --- MENU: ADMINISTRAÇÃO ---
elif menu == "Painel da Administração":
    st.title("💼 Painel de Controle - Salão")
    st.markdown("Gerencie a agenda de atendimentos e veja o faturamento diário.")

    if not agendamentos:
        st.info("Nenhum agendamento realizado até o momento.")
    else:
        # Estatísticas Rápidas
        faturamento_total = sum(a["preco"] for a in agendamentos)
        total_agendamentos = len(agendamentos)
        
        col1, col2 = st.columns(2)
        col1.metric("Total de Agendamentos", total_agendamentos)
        col2.metric("Faturamento Estimado", f"R$ {faturamento_total:.2f}")

        # Filtro de Data
        datas_disponiveis = sorted(list(set(a["data"] for a in agendamentos)))
        data_filtro = st.selectbox("Filtrar por data", ["Todos"] + datas_disponiveis)

        # Filtrar a lista
        agendamentos_exibidos = agendamentos
        if data_filtro != "Todos":
            agendamentos_exibidos = [a for a in agendamentos if a["data"] == data_filtro]

        # Tabela de Agendamentos
        st.subheader(f"Agenda: {data_filtro}")
        for idx, a in enumerate(agendamentos_exibidos):
            status_color = "🟢" if a.get("status") == "Confirmado" else "🟡"
            with st.expander(f"{status_color} {a['horario']} - {a['nome']} ({a['servico']})"):
                st.write(f"📞 WhatsApp: {a['telefone']}")
                st.write(f"📅 Data: {a['data']}")
                st.write(f"💰 Valor: R$ {a['preco']:.2f}")
                
                # Botões de Ação divididos em duas colunas
                col_btn1, col_btn2 = st.columns(2)
                
                # Confirmar
                if col_btn1.button("Confirmar", key=f"conf_{idx}"):
                    for ag in agendamentos:
                        if ag["data"] == a["data"] and ag["horario"] == a["horario"]:
                            ag["status"] = "Confirmado"
                    salvar_dados(agendamentos)
                    st.rerun()
                
                # Excluir
                if col_btn2.button("🗑️ Excluir", key=f"del_{idx}"):
                    # Remove da lista principal mantendo apenas os que são diferentes
                    agendamentos = [ag for ag in agendamentos if not (ag["data"] == a["data"] and ag["horario"] == a["horario"])]
                    salvar_dados(agendamentos)
                    st.rerun()
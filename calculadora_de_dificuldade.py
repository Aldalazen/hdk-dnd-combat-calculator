import math
import streamlit as st

st.set_page_config(page_title="Calculadora de Dificuldade D&D 5e", layout="centered")

# XP por CR oficial de D&D 5e
CR_TO_XP = {
    "0": 10,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5000,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000,
}

# Limiares por personagem, por nível
XP_THRESHOLDS = {
    1: {"Fácil": 25, "Médio": 50, "Difícil": 75, "Mortal": 100},
    2: {"Fácil": 50, "Médio": 100, "Difícil": 150, "Mortal": 200},
    3: {"Fácil": 75, "Médio": 150, "Difícil": 225, "Mortal": 400},
    4: {"Fácil": 125, "Médio": 250, "Difícil": 375, "Mortal": 500},
    5: {"Fácil": 250, "Médio": 500, "Difícil": 750, "Mortal": 1100},
    6: {"Fácil": 300, "Médio": 600, "Difícil": 900, "Mortal": 1400},
    7: {"Fácil": 350, "Médio": 750, "Difícil": 1100, "Mortal": 1700},
    8: {"Fácil": 450, "Médio": 900, "Difícil": 1400, "Mortal": 2100},
    9: {"Fácil": 550, "Médio": 1100, "Difícil": 1600, "Mortal": 2400},
    10: {"Fácil": 600, "Médio": 1200, "Difícil": 1900, "Mortal": 2800},
    11: {"Fácil": 800, "Médio": 1600, "Difícil": 2400, "Mortal": 3600},
    12: {"Fácil": 1000, "Médio": 2000, "Difícil": 3000, "Mortal": 4500},
    13: {"Fácil": 1100, "Médio": 2200, "Difícil": 3400, "Mortal": 5100},
    14: {"Fácil": 1250, "Médio": 2500, "Difícil": 3800, "Mortal": 5700},
    15: {"Fácil": 1400, "Médio": 2800, "Difícil": 4300, "Mortal": 6400},
    16: {"Fácil": 1600, "Médio": 3200, "Difícil": 4800, "Mortal": 7200},
    17: {"Fácil": 2000, "Médio": 3900, "Difícil": 5900, "Mortal": 8800},
    18: {"Fácil": 2100, "Médio": 4200, "Difícil": 6300, "Mortal": 9500},
    19: {"Fácil": 2400, "Médio": 4900, "Difícil": 7300, "Mortal": 10900},
    20: {"Fácil": 2800, "Médio": 5700, "Difícil": 8500, "Mortal": 12700},
}


def monster_multiplier(monster_count: int, player_count: int) -> float:
    if monster_count <= 0:
        return 1.0

    if monster_count == 1:
        base = 1.0
    elif monster_count == 2:
        base = 1.5
    elif 3 <= monster_count <= 6:
        base = 2.0
    elif 7 <= monster_count <= 10:
        base = 2.5
    elif 11 <= monster_count <= 14:
        base = 3.0
    else:
        base = 4.0

    # Ajuste do DMG para grupos pequenos ou grandes
    if player_count < 3:
        if base == 1.0:
            return 1.5
        if base == 1.5:
            return 2.0
        if base == 2.0:
            return 2.5
        if base == 2.5:
            return 3.0
        if base == 3.0:
            return 4.0
        return 5.0

    if player_count >= 6:
        if base == 1.5:
            return 1.0
        if base == 2.0:
            return 1.5
        if base == 2.5:
            return 2.0
        if base == 3.0:
            return 2.5
        if base == 4.0:
            return 3.0
        return 1.0

    return base



def classify_difficulty(adjusted_xp: int, thresholds: dict[str, int]) -> str:
    if adjusted_xp == 0:
        return "Sem inimigos"
    if adjusted_xp < thresholds["Fácil"]:
        return "Abaixo de Fácil"
    if adjusted_xp < thresholds["Médio"]:
        return "Fácil"
    if adjusted_xp < thresholds["Difícil"]:
        return "Médio"
    if adjusted_xp < thresholds["Mortal"]:
        return "Difícil"
    return "Mortal"


st.title("Calculadora de Dificuldade de Combate - D&D 5e")
st.caption("Baseado no método de XP ajustado do Dungeon Master's Guide.")

with st.form("encounter_form"):
    st.subheader("Grupo")
    col1, col2 = st.columns(2)
    with col1:
        player_count = st.number_input("Número de jogadores", min_value=1, max_value=10, value=4, step=1)
    with col2:
        avg_level = st.number_input("Nível médio do grupo", min_value=1, max_value=20, value=5, step=1)

    st.subheader("Monstros")
    monster_rows = []
    for i in range(1, 6):
        c1, c2 = st.columns([2, 1])
        with c1:
            cr = st.selectbox(f"CR do grupo de monstros {i}", options=list(CR_TO_XP.keys()), index=0, key=f"cr_{i}")
        with c2:
            qty = st.number_input(f"Qtd. {i}", min_value=0, max_value=50, value=0, step=1, key=f"qty_{i}")
        monster_rows.append((cr, qty))

    submitted = st.form_submit_button("Calcular dificuldade")

if submitted:
    thresholds_per_character = XP_THRESHOLDS[int(avg_level)]
    group_thresholds = {
        label: value * int(player_count)
        for label, value in thresholds_per_character.items()
    }

    total_monsters = sum(int(qty) for _, qty in monster_rows)
    base_xp = sum(CR_TO_XP[cr] * int(qty) for cr, qty in monster_rows)
    multiplier = monster_multiplier(total_monsters, int(player_count))
    adjusted_xp = math.floor(base_xp * multiplier)
    difficulty = classify_difficulty(adjusted_xp, group_thresholds)

    st.subheader("Resultado")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("XP base", f"{base_xp:,}".replace(",", "."))
    m2.metric("Multiplicador", f"x{multiplier}")
    m3.metric("XP ajustado", f"{adjusted_xp:,}".replace(",", "."))
    m4.metric("Dificuldade", difficulty)

    st.subheader("Limiares do grupo")
    st.table(
        {
            "Dificuldade": list(group_thresholds.keys()),
            "XP": [f"{xp:,}".replace(",", ".") for xp in group_thresholds.values()],
        }
    )

    st.subheader("Detalhamento dos monstros")
    detail_rows = []
    for cr, qty in monster_rows:
        if int(qty) > 0:
            detail_rows.append(
                {
                    "CR": cr,
                    "Quantidade": int(qty),
                    "XP por monstro": CR_TO_XP[cr],
                    "XP subtotal": CR_TO_XP[cr] * int(qty),
                }
            )

    if detail_rows:
        st.table(detail_rows)
    else:
        st.info("Nenhum monstro foi informado.")

    st.markdown(
        """
        ### Leitura rápida
        - **Abaixo de Fácil**: encontro trivial.
        - **Fácil**: baixo consumo de recursos.
        - **Médio**: encontro padrão.
        - **Difícil**: chance real de derrubar personagens.
        - **Mortal**: alto risco de derrota do grupo.
        """
    )
else:
    st.info("Preencha o grupo e os monstros, depois clique em calcular.")

from PPlay.window import *
from PPlay.gameimage import *
from PPlay.sprite import *
import random
import os

# --- 1. CONFIGURAÇÕES INICIAIS ---
janela = Window(1440, 900)
janela.set_title("Futuro space invaders")
mouse = janela.get_mouse()
teclado = janela.get_keyboard()

# Variáveis do Jogo
distancia = 40
nova_dist = 120
tam = 17 # Tamanho da fonte
pulo = 50 # Distância que inimigos descem
pts = 0
q_linha, q_coluna = 8, 8 # Tamanho da matriz de inimigos

# Cores
branco = (255, 255, 255)
preto = (0, 0, 0)
vermelho = (255, 0, 0)
verde = (0, 255, 0) 
amarelo = (255, 255, 0)

# Variáveis de Velocidade e Dificuldade
vel_jog = 350
vel_tiro = 400
vel_ini = 50
tempo_dif = 0.4 # Cadência inicial de tiro do jogador (corrigida)
vida = 3

# Timers
delta_time = janela.delta_time()
timer = 0.0 # Timer do tiro do jogador
timer_tiro_ini = 0.0 # Timer do tiro do inimigo
intervalo_tiro_ini = 2.0 
timer_invencibilidade = 0.0
duracao_invencibilidade = 5.0 # Invencibilidade de 5 segundos
invencivel = False
pisca_timer = 0.0
pisca_intervalo = 0.1

# Estados
state = "string" # Estado inicial: Menu
mouse_livre = True
esc_press = False
inimigos_criados = False

# --- RANKING GLOBAL ---
HIGHSCORE_FILE = "ranking.txt"
pontuacao_maxima = 0 

# --- FPS ---
frames = 0.0
n_frames = 0
fps = 0

# --- 2. CRIAÇÃO DE SPRITES ---
Titulo = Sprite("titulo.png")
Titulo.set_position((janela.width / 2 - Titulo.width / 2), (0 - 40))

# Botões (usando "ranking.png" como placeholder para botões)
Botao_jogar = Sprite("ranking.png")
Botao_jogar.set_position(janela.width / 2 - Botao_jogar.width / 2, janela.height / 2 + nova_dist)
Botao_dificuldade = Sprite("ranking.png")
Botao_dificuldade.set_position(janela.width / 2 - Botao_jogar.width / 2, janela.height / 2 + distancia + nova_dist)
Botao_rank = Sprite("ranking.png")
Botao_rank.set_position(janela.width / 2 - Botao_jogar.width / 2, janela.height / 2 + (distancia * 2) + nova_dist)
Botao_sair = Sprite("ranking.png")
Botao_sair.set_position(janela.width / 2 - Botao_jogar.width / 2, janela.height / 2 + (distancia * 3) + nova_dist)

# Botões de Dificuldade
Facil = Sprite("ranking.png")
Facil.set_position(janela.width / 2 - Botao_jogar.width / 2 - 300, janela.height / 2 - (distancia * 0) + nova_dist)
Medio = Sprite("ranking.png")
Medio.set_position(janela.width / 2 - Botao_jogar.width / 2 - 300, janela.height / 2 - (distancia * 1) + nova_dist)
Dificil = Sprite("ranking.png")
Dificil.set_position(janela.width / 2 - Botao_jogar.width / 2 - 300, janela.height / 2 - (distancia * 2) + nova_dist)
Impossivel = Sprite("ranking.png")
Impossivel.set_position(janela.width / 2 - Botao_jogar.width / 2 - 300, janela.height / 2 - (distancia * 3) + nova_dist)

# Jogador
jogador = Sprite("jogador.xcf")
jogador.set_position(janela.width / 2 - jogador.width / 2, janela.height * 7 / 8)
jogador.visivel = True # Correção de AttributeError

# Listas
tiros = []
tiros_inimigos = [] 
matriz_de_mons = []

# --- 3. FUNÇÕES DE RANKING ---
def carregar_ranking():
    """Carrega a pontuação máxima do arquivo."""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as file:
                return int(file.read().strip())
        except:
            return 0
    return 0 

def salvar_ranking(nova_pontuacao):
    """Salva a nova pontuação máxima no arquivo."""
    global pontuacao_maxima
    if nova_pontuacao > pontuacao_maxima:
        pontuacao_maxima = nova_pontuacao
        with open(HIGHSCORE_FILE, "w") as file:
            file.write(str(pontuacao_maxima))

pontuacao_maxima = carregar_ranking()

# --- 4. FUNÇÕES DE JOGO ---
def reset_jogo():
    """Reinicia variáveis para um novo jogo."""
    global vida, pts, timer_tiro_ini, tiros_inimigos, invencivel, timer_invencibilidade, inimigos_criados, tempo_dif, vel_ini, timer
    
    # Correção: Permite tiro imediato ao reiniciar
    timer = tempo_dif 
    
    vida = 3
    pts = 0
    timer_tiro_ini = 0.0
    tiros_inimigos.clear()
    tiros.clear()
    matriz_de_mons.clear()
    inimigos_criados = False
    invencivel = False
    timer_invencibilidade = 0.0
    jogador.set_position(janela.width / 2 - jogador.width / 2, janela.height * 7 / 8)
    jogador.visivel = True

def preenche_inimigos(n, m):
    """Cria e posiciona a matriz de inimigos."""
    matriz_de_mons.clear()
    for i in range(n):
        linha = []
        for c in range(m):
            inimigo = Sprite("inimigo.xcf", 2)
            distancia_ini = inimigo.width*3/2
            inimigo.set_total_duration(800)
            inimigo.set_position(janela.width / 2 - 500 + (distancia_ini * c), janela.height * 1 / 12 + (distancia_ini * i))
            linha.append(inimigo)
        matriz_de_mons.append(linha)

def escolher_inimigo_aleatorio():
    """Retorna um inimigo aleatório da matriz que ainda esteja 'vivo'."""
    inimigos_ativos = []
    for linha in matriz_de_mons:
        for inimigo in linha:
            inimigos_ativos.append(inimigo)
    
    if inimigos_ativos:
        return random.choice(inimigos_ativos)
    return None

def da_tiro_ini():
    """Cria e adiciona um tiro inimigo."""
    inimigo_atirador = escolher_inimigo_aleatorio()
    
    if inimigo_atirador:
        tiro_ini = Sprite("tiro_ini.png") 
        vel_tiro_ini = 250 
        
        tiro_ini.set_position(inimigo_atirador.x + inimigo_atirador.width / 2 - tiro_ini.width / 2, inimigo_atirador.y + inimigo_atirador.height)
        tiro_ini.dir_x = 0
        tiro_ini.dir_y = 1
        tiro_ini.vel = vel_tiro_ini
               
        tiros_inimigos.append(tiro_ini)

def da_tiro():
    """Cria e adiciona um tiro do jogador."""
    tiro = Sprite("projetil.xcf")
    tiro.set_position(jogador.x + jogador.width / 2 - tiro.width / 2, jogador.y)
    tiros.append(tiro)

def tomar_dano():
    """Processa o dano ao jogador e a invencibilidade temporária."""
    global vida, invencivel, timer_invencibilidade, state, pts

    # Lógica que impede o dano enquanto invencivel for True (piscando)
    if invencivel:
        return 

    vida -= 1
    
    if vida <= 0:
        salvar_ranking(int(pts))
        state = "game_over"
        return
    
    # Reseta a posição e ativa invencibilidade
    #jogador.set_position(janela.width / 2 - jogador.width / 2, janela.height * 7 / 8)
    invencivel = True
    timer_invencibilidade = 0.0

# --- 5. LOOP PRINCIPAL DO JOGO ---
while True:
    
    # Atualização do Delta Time
    if state != "pausa":
        delta_time = janela.delta_time()
    else:
        delta_time = 0.0
        
    timer += delta_time
    timer_tiro_ini += delta_time
    
    # Controle de FPS
    frames += delta_time
    n_frames += 1
    if frames >= 1:
        fps = n_frames/frames
        frames = 0.0
        n_frames = 0
    
    # --- Lógica de Invencibilidade e Piscada ---
    if invencivel:
        timer_invencibilidade += delta_time
        pisca_timer += delta_time
        
        if timer_invencibilidade >= duracao_invencibilidade:
            invencivel = False
            pisca_timer = 0.0
            jogador.visivel = True
        
        if pisca_timer >= pisca_intervalo:
            pisca_timer = 0.0
            jogador.visivel = not jogador.visivel
    else:
        jogador.visivel = True

    # --- MENU PRINCIPAL ---
    if state == "string":
        janela.set_background_color(preto)
        vida = 3
        if mouse.is_over_object(Botao_jogar) and mouse.is_button_pressed(1) and mouse_livre:
            reset_jogo()
            state = "jogando"
            mouse_livre = False
        if mouse.is_over_object(Botao_dificuldade) and mouse.is_button_pressed(1) and mouse_livre:
            state = "dificuldades"
            mouse_livre = False
        if mouse.is_over_object(Botao_rank) and mouse.is_button_pressed(1) and mouse_livre:
            pontuacao_maxima = carregar_ranking()
            state = "rank"
            mouse_livre = False
        if mouse.is_over_object(Botao_sair) and mouse.is_button_pressed(1) and mouse_livre:
            state = "saiu"
            mouse_livre = False

        # Desenho dos botões do menu
        Botao_jogar.draw(); janela.draw_text("JOGAR", Botao_jogar.x + 63, Botao_jogar.y, tam, preto, "Calibri", True)
        Botao_dificuldade.draw(); janela.draw_text("DIFICULDADE", Botao_dificuldade.x + 40, Botao_dificuldade.y, tam, preto, "Calibri", True)
        Botao_rank.draw(); janela.draw_text("RANK", Botao_rank.x + 68, Botao_rank.y, tam, preto, "Calibri", True)
        Botao_sair.draw(); janela.draw_text("SAIR", Botao_sair.x + 68, Botao_sair.y, tam, preto, "Calibri", True)
        Titulo.draw()
    
    # --- MENU DE PAUSA ---
    elif state == "pausa":
        menu_pausa = Sprite("pausa.xcf")
        menu_pausa.set_position(janela.width / 2 - menu_pausa.width / 2, janela.height / 2 - menu_pausa.height / 2)
        menu_pausa.draw()
        janela.draw_text("Esc para voltar ao jogo", janela.width / 2 - 100, janela.height / 2 + 100, tam, branco, "Calibri", True)
        janela.draw_text("Espaço para voltar ao menu", janela.width / 2 - 120, janela.height / 2 + 150, tam, branco, "Calibri", True)

        if teclado.key_pressed("esc") and not esc_press:
            state = "jogando"
        if teclado.key_pressed("space"):
            state = "string"
        esc_press = teclado.key_pressed("esc")
    
    # --- GAME OVER (DERROTA) ---
    elif state == "game_over":
        janela.set_background_color(preto)
        recorde_atual = carregar_ranking()

        janela.draw_text("DERROTA! GAME OVER", janela.width / 2 - 250, janela.height / 2 - 50, 60, vermelho, "Calibri", True)
        janela.draw_text(f"PONTUAÇÃO FINAL: {int(pts)}", janela.width / 2 - 150, janela.height / 2 + 50, 30, branco, "Calibri", True)
        janela.draw_text(f"RECORDE ATUAL: {recorde_atual}", janela.width / 2 - 150, janela.height / 2 + 100, 30, verde, "Calibri", True)
        janela.draw_text("Pressione ESPAÇO para o Menu", janela.width / 2 - 150, janela.height / 2 + 200, tam, verde, "Calibri", True)
        
        if teclado.key_pressed("space"):
            state = "string"
            
    # --- VITÓRIA ---
    elif state == "vitoria":
        janela.set_background_color(preto)
        
        salvar_ranking(int(pts)) 
        recorde_atual = carregar_ranking()
        
        janela.draw_text("VITÓRIA!", janela.width / 2 - 150, janela.height / 2 - 50, 60, verde, "Calibri", True)
        janela.draw_text("TODOS OS INIMIGOS DESTRUIDOS!", janela.width / 2 - 250, janela.height / 2 + 20, 30, branco, "Calibri", True)
        janela.draw_text(f"PONTUAÇÃO FINAL: {int(pts)}", janela.width / 2 - 150, janela.height / 2 + 100, 30, branco, "Calibri", True)
        janela.draw_text(f"RECORDE ATUAL: {recorde_atual}", janela.width / 2 - 150, janela.height / 2 + 150, 30, verde, "Calibri", True)
        janela.draw_text("Pressione ESPAÇO para o Menu", janela.width / 2 - 150, janela.height / 2 + 250, tam, verde, "Calibri", True)
        
        if teclado.key_pressed("space"):
            state = "string"
    
    # --- JOGANDO ---
    elif state == "jogando":
        janela.set_background_color(preto)
        
        # 1. Criação dos Inimigos
        if not inimigos_criados:
            preenche_inimigos(q_linha, q_coluna)
            inimigos_criados = True

        # 2. LÓGICA DE VITÓRIA (Corrigido: Verifica matriz vazia após criação)
        if inimigos_criados and not any(any(linha) for linha in matriz_de_mons):
            salvar_ranking(int(pts))
            state = "vitoria"
            continue 

        # Pausa
        if teclado.key_pressed("esc") and not esc_press:
            state = "pausa"
        esc_press = teclado.key_pressed("esc")

        # Movimento do Jogador
        if teclado.key_pressed("RIGHT"):
            jogador.x += vel_jog * delta_time
        if teclado.key_pressed("LEFT"):
            jogador.x -= vel_jog * delta_time
            
        # Limites do Jogador
        if jogador.x < 0:
            jogador.x = 0
        if jogador.x > janela.width - jogador.width:
            jogador.x = janela.width - jogador.width

        # Tiro do Jogador (Cadência)
        if teclado.key_pressed("space"):
            if timer >= tempo_dif:
                timer = 0.0
                da_tiro()

        # Tiro Inimigo
        if timer_tiro_ini >= intervalo_tiro_ini:
            intervalo_tiro_ini = 2.0 + random.uniform(-0.5, 1.5) / (vel_ini / 50) 
            timer_tiro_ini = 0.0
            da_tiro_ini()

        # Movimento e Colisão dos Tiros do Jogador
        tiros_a_manter = []
        for tiro in tiros[:]:
            tiro.y -= vel_tiro * delta_time
            
            colidiu = False
            # Colisão: tiro contra matriz de inimigos
            for f in range(len(matriz_de_mons) - 1, -1, -1):
                for t in range(len(matriz_de_mons[f]) - 1, -1, -1):
                    inimigo = matriz_de_mons[f][t]
                    if tiro.collided(inimigo):
                        matriz_de_mons[f].remove(inimigo) 
                        pts += 5
                        colidiu = True
                        break 
                if colidiu:
                    break 

            if not colidiu and tiro.y > -tiro.height: 
                tiros_a_manter.append(tiro)
        tiros = tiros_a_manter

        # Movimento e Colisão dos Tiros Inimigos
        tiros_inimigos_a_manter = []
        for tiro_ini in tiros_inimigos[:]:
            tiro_ini.x += tiro_ini.dir_x * tiro_ini.vel * delta_time
            tiro_ini.y += tiro_ini.dir_y * tiro_ini.vel * delta_time 
            tiro_ini.draw()

            # Colisão: tiro inimigo contra jogador (usa tomar_dano que checa invencibilidade)
            if tiro_ini.collided(jogador):
                tomar_dano() 
            elif tiro_ini.y < janela.height and tiro_ini.y > -tiro_ini.height: 
                tiros_inimigos_a_manter.append(tiro_ini)
        
        tiros_inimigos = tiros_inimigos_a_manter

        # Movimento e Colisão da Matriz de Inimigos
        inverter = False
        for f in range(len(matriz_de_mons)):
            for t in range(len(matriz_de_mons[f])):
                inimigo = matriz_de_mons[f][t]
                
                # LÓGICA DE DERROTA: Checa se inimigo cruzou a linha
                if inimigo.y + inimigo.height >= janela.height * 8/10:
                    salvar_ranking(int(pts))
                    state = "game_over"
                    break
                
                if inimigo.x <= 0 or inimigo.x + inimigo.width >= janela.width:
                    inverter = True
                    break
            if state == "game_over" or inverter:
                break
        
        # Inversão e Descida
        if inverter:
            ajuste_x = 0
            if vel_ini > 0:
                ajuste_x = -1
            else:
                ajuste_x = 1
            
            vel_ini *= -1
            
            for f in range(len(matriz_de_mons)):
                for t in range(len(matriz_de_mons[f])):
                    matriz_de_mons[f][t].y += pulo
                    matriz_de_mons[f][t].x += ajuste_x

        # Desenho
        for f in range(len(matriz_de_mons)):
            for t in range(len(matriz_de_mons[f])):
                inimigo = matriz_de_mons[f][t]
                inimigo.draw()
                inimigo.update()
                inimigo.x += vel_ini * delta_time 

        for tiro in tiros_a_manter:
            tiro.draw()
        
        # Desenho do Jogador (Apenas se visivel for True)
        if jogador.visivel:
            jogador.draw()

    # --- DIFICULDADES ---
    elif state == "dificuldades":
        janela.set_background_color((0, 0, 0))

        # Desenho dos botões de dificuldade
        Facil.draw(); janela.draw_text("FÁCIL", Facil.x + 63, Facil.y, tam, preto, "Calibri", True)
        Medio.draw(); janela.draw_text("MÉDIO", Medio.x + 63, Medio.y, tam, preto, "Calibri", True)
        Dificil.draw(); janela.draw_text("DIFÍCIL", Dificil.x + 63, Dificil.y, tam, preto, "Calibri", True)
        Impossivel.draw(); janela.draw_text("IMPOSSÍVEL", Impossivel.x + 40, Impossivel.y, tam, preto, "Calibri", True)

        # Lógica de seleção de dificuldade
        if mouse.is_over_object(Facil) and mouse.is_button_pressed(1) and mouse_livre:
            tempo_dif = 1.0; vel_ini = 100; reset_jogo(); state = "jogando"; mouse_livre = False; intervalo_tiro_ini = 2.0; duracao_invencibilidade = 5.0
        if mouse.is_over_object(Medio) and mouse.is_button_pressed(1) and mouse_livre:
            tempo_dif = 0.7; vel_ini = 150; reset_jogo(); state = "jogando"; mouse_livre = False; intervalo_tiro_ini = 1.5; duracao_invencibilidade = 3.0
        if mouse.is_over_object(Dificil) and mouse.is_button_pressed(1) and mouse_livre:
            tempo_dif = 0.5; vel_ini = 200; reset_jogo(); state = "jogando"; mouse_livre = False; intervalo_tiro_ini = 1.0; duracao_invencibilidade = 2.5
        if mouse.is_over_object(Impossivel) and mouse.is_button_pressed(1) and mouse_livre:
            tempo_dif = 0.3; vel_ini = 300; reset_jogo(); state = "jogando"; mouse_livre = False; intervalo_tiro_ini = 0.5; duracao_invencibilidade = 1.5
            
        if teclado.key_pressed("esc"):
            state = "string"

    # --- RANK ---
    elif state == "rank":
        janela.set_background_color((0, 0, 0))
        
        janela.draw_text("RANK", janela.width / 2 - 80, 20, 50, branco, "Calibri", True)
        janela.draw_text(f"PONTUAÇÃO MÁXIMA: {pontuacao_maxima}", 
                         janela.width / 2 - 150, janela.height / 2, 40, verde, "Calibri", True)
        janela.draw_text("Pressione ESC para o Menu", 
                         janela.width / 2 - 120, janela.height - 100, tam, branco, "Calibri", True)
        
        if teclado.key_pressed("esc"):
            state = "string"

    # --- Mouse Livre e Saída ---
    if not mouse.is_button_pressed(1):
        mouse_livre = True

    if state == "saiu":
        break
        
    # --- Desenho de HUD ---
    if state == "jogando" or state == "pausa":
        linha = "========================="* 10
        janela.draw_text(linha, 0, janela.height*8/10, tam, vermelho, "Calibri", True)
    
    if state != "saiu":
        janela.draw_text(f"PTS: {int(pts)}", 10, 35, size=24, color=(branco), bold=True)
        janela.draw_text(f"FPS: {int(fps)}", 10, 10, size=24, color=(amarelo), bold=True)
        janela.draw_text(f"VIDA: {int(vida)}", 10, 60, size=24, color=(verde), bold=True)
    if timer_invencibilidade > 0.0 and state == "jogando" and invencivel:
        tempo = float(duracao_invencibilidade - timer_invencibilidade)
        tempo = tempo * 100
        tempo = int(tempo)
        tempo = tempo / 100
        janela.draw_text(f"INV: {tempo}", 10, 85, size=24, color=(vermelho), bold=True)
    janela.update()

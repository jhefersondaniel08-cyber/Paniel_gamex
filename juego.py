import os
import sys
import math
import random
import pygame

from configuracion import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    VIRTUAL_WIDTH,
    VIRTUAL_HEIGHT,
    FPS,
    COLOR_BLACK,
)
from sonido import SoundFX
from camara import Camera, SceneTransition
from personaje import CharacterSpriteManager, Player
from escenarios import InteriorScene
from interfaz import DialogueBox, PanielMentalHUD, RetroHUD, UndertaleMenu, DeltaruneTitleScreen, DeltaruneShopMenu
from enemigos import OverworldEnemy
from combate import DeltaruneBattle

# ==========================================================
# BUCLE PRINCIPAL DEL JUEGO
# ==========================================================
def main():
    pygame.init()
    pygame.font.init()

    # Ventana escalable visible (960x720, tamaño más grande y cómodo, con soporte de redimensionado y F4 para pantalla completa)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("UnderBread")
    clock = pygame.time.Clock()
    is_fullscreen = False

    def present_screen():
        sw, sh = screen.get_size()
        scale = min(sw / float(VIRTUAL_WIDTH), sh / float(VIRTUAL_HEIGHT))
        tw = int(VIRTUAL_WIDTH * scale)
        th = int(VIRTUAL_HEIGHT * scale)
        if tw == sw and th == sh:
            pygame.transform.scale(virtual_screen, (sw, sh), screen)
        else:
            scaled = pygame.transform.scale(virtual_screen, (tw, th))
            screen.fill(COLOR_BLACK)
            screen.blit(scaled, ((sw - tw) // 2, (sh - th) // 2))
        pygame.display.flip()

    # Pantalla virtual 400x300 (escalado retro a resolución de ventana para máxima nitidez pixel-perfect)
    virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    camera = Camera(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

    # Fuentes retro (un poco más grandes y legibles para estadísticas y HUD)
    font_dialogue = pygame.font.SysFont("Lucida Console", 11) or pygame.font.SysFont("Courier New", 11)
    font_hud = pygame.font.SysFont("Lucida Console", 11, bold=True)
    font_hud_small = pygame.font.SysFont("Lucida Console", 9, bold=True)
    font_prompt = pygame.font.SysFont("Lucida Console", 10, bold=True)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sound_fx = SoundFX()

    # 1. Cargar sprites de Paniel en 4 direcciones a resolución 1:1 original intacta
    sprite_mgr = CharacterSpriteManager(base_dir)

    # 2. Inicializar escenas (nombres cortos para que nunca se salgan del HUD ni de los carteles)
    interiors = {
        "tutorial_grounds": InteriorScene("tutorial_grounds", "Tutorial"),
        "cemetery": InteriorScene("cemetery", "Cementerio"),
        "cemetery_church_section": InteriorScene("cemetery_church_section", "Atrio Iglesia"),
        "cemetery_depths": InteriorScene("cemetery_depths", "Abismo"),
        "eclipse_sanctuary": InteriorScene("eclipse_sanctuary", "Cristal Negro"),
        "church": InteriorScene("church", "Iglesia"),
        "church_basement": InteriorScene("church_basement", "Sótano"),
        "dark_world": InteriorScene("dark_world", "Dark World"),
        "dark_world_throne": InteriorScene("dark_world_throne", "Trono Oscuro"),
    }

    dialogue_box = DialogueBox(font_dialogue, sound_fx)
    hud = RetroHUD(font_hud, font_prompt)
    mental_hud = PanielMentalHUD(font_hud, font_hud_small)
    undertale_menu = UndertaleMenu(font_hud, font_hud_small, font_dialogue, sound_fx)
    shop_menu = DeltaruneShopMenu(font_hud, font_hud_small, font_dialogue, sound_fx)
    title_screen = DeltaruneTitleScreen(sound_fx, sprite_mgr)
    transition = SceneTransition()

    # Estado del mundo (inicia en la introducción ilustrada y despierta dentro del Cementerio)
    current_scene_type = "TITLE"  # TITLE, EXPLORATION o BATTLE
    current_map_id = "cemetery"
    battle_instance = None
    engaged_enemy = None
    battle_grace_timer = 0.0
    wakeup_timer = 0.0
    wakeup_duration = 2.6
    wakeup_dialogue_pending = False

    # Posición inicial dentro del Cementerio (junto a la reja sur cerrada con candado)
    player = Player(x=388, y=496, sprite_manager=sprite_mgr)
    player.facing = "DOWN"

    # Centrar la cámara de inmediato en Paniel
    active_map = interiors[current_map_id]
    camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, active_map.pixel_w, active_map.pixel_h)

    # 3 Instructores de Combate centrados en sus 3 Bahías Simétricas de la Sala 4 (1: Esquiva 4/4, 2: Parry [Z] 4/4, 3: Dash [X] 4/4)
    tutorial_enemies = [
        OverworldEnemy(185, 318, "maniqui_esquiva"),
        OverworldEnemy(389, 318, "maniqui_parry"),
        OverworldEnemy(593, 318, "maniqui_dash"),
    ]
    completed_tutorial_trainers = set()

    # Enemigos patrullando en el cementerio (distribuidos simétricamente en los senderos del mapa de 800x600 con el Jefe custodiando el Mausoleo)
    cemetery_enemies = [
        OverworldEnemy(383, 195, "sepulturero"),  # ¡EL JEFE MORVATH EL SEPULTURERO CUSTODIANDO EL GRAN MAUSOLEO!
        OverworldEnemy(185, 224, "sombra"),
        OverworldEnemy(590, 224, "fantasmino"),
        OverworldEnemy(185, 474, "sombra"),
        OverworldEnemy(590, 474, "sectario"),
    ]

    # Jefe y acólitos encapuchados en la parte más profunda del cementerio (Abismo del Cementerio)
    depths_enemies = [
        OverworldEnemy(383, 215, "sepulturero"),
        OverworldEnemy(250, 330, "sectario"),
        OverworldEnemy(535, 330, "sectario"),
    ]

    # Jefe Supremo más difícil en la nueva zona (Santuario del Cristal Quebrado)
    sanctuary_enemies = [
        OverworldEnemy(383, 210, "arconte"),
        OverworldEnemy(245, 335, "sectario"),
        OverworldEnemy(540, 335, "sectario"),
    ]

    # Enemigos diferentes exclusivos del Dark World (distribuidos en la Plaza Central y el Ala Este, dejando libre el Bazar Oeste)
    dark_world_enemies = [
        OverworldEnemy(500, 210, "bufon_caos"),
        OverworldEnemy(590, 275, "centinela_neon"),
        OverworldEnemy(300, 355, "bufon_caos"),
        OverworldEnemy(390, 175, "centinela_neon"),
    ]

    # Jefe Secreto del Dark World en la zona extra Trono Oscuro
    dark_throne_enemies = [
        OverworldEnemy(383, 240, "nyxar"),
    ]

    def spawn_dark_world_enemy():
        """Genera enemigos exclusivos del Dark World si hay menos de 4."""
        if len(dark_world_enemies) >= 4:
            return
        dw = interiors.get("dark_world")
        if not dw:
            return
        ex = random.uniform(180, dw.pixel_w - 140)
        ey = random.uniform(150, dw.pixel_h - 120)
        etype = random.choice(["bufon_caos", "centinela_neon"])
        dark_world_enemies.append(OverworldEnemy(ex, ey, etype))

    def spawn_cemetery_enemy():
        """Genera un enemigo patrullando en el cementerio con probabilidad 1/50 por paso."""
        if len(cemetery_enemies) >= 5:
            return
        cem = interiors.get("cemetery")
        if not cem:
            return
        for _ in range(16):
            ex = random.uniform(50, cem.pixel_w - 50)
            ey = random.uniform(110, cem.pixel_h - 60)
            # Evitar el mausoleo central y el cruce del punto de guardado
            if 310 <= ex <= 490 and 50 <= ey <= 160:
                continue
            if 370 <= ex <= 430 and 315 <= ey <= 365:
                continue
            # Conforme sube de nivel Paniel, aparecen más Acólitos del Eclipse (sectarios)
            pool = ["sombra", "fantasmino", "sectario"]
            if player.lv >= 2:
                pool.append("sectario")
            if player.lv >= 3:
                pool.append("rudinn")
            etype = random.choice(pool)
            cemetery_enemies.append(OverworldEnemy(ex, ey, etype))
            break

    def on_player_step():
        if current_scene_type == "EXPLORATION":
            if current_map_id == "cemetery" and random.randint(1, 50) == 1:
                spawn_cemetery_enemy()
            elif current_map_id == "dark_world" and random.randint(1, 45) == 1:
                spawn_dark_world_enemy()

    player.on_step_callback = on_player_step

    def start_combat(enemy):
        nonlocal current_scene_type, battle_instance, engaged_enemy
        sound_fx.play_encounter()
        engaged_enemy = enemy
        current_scene_type = "BATTLE"

        def on_battle_finish(victory, revived=False):
            nonlocal current_scene_type, current_map_id, battle_instance, engaged_enemy, battle_grace_timer
            tid = getattr(engaged_enemy, "template_id", "") if engaged_enemy is not None else ""
            was_boss = tid in ("sepulturero", "arconte", "nyxar")
            if engaged_enemy in cemetery_enemies:
                if victory:
                    cemetery_enemies.remove(engaged_enemy)
                else:
                    if tid == "sepulturero":
                        engaged_enemy.x = 383.0
                        engaged_enemy.y = 195.0
                        engaged_enemy.state = "WANDER"
                    else:
                        cemetery_enemies.remove(engaged_enemy)
            if victory and engaged_enemy in depths_enemies:
                depths_enemies.remove(engaged_enemy)
            elif not victory and engaged_enemy in depths_enemies:
                if tid == "sepulturero":
                    engaged_enemy.x = 383.0
                    engaged_enemy.y = 215.0
                engaged_enemy.state = "WANDER"
            if victory and engaged_enemy in sanctuary_enemies:
                sanctuary_enemies.remove(engaged_enemy)
            elif not victory and engaged_enemy in sanctuary_enemies:
                if tid == "arconte":
                    engaged_enemy.x = 383.0
                    engaged_enemy.y = 210.0
                engaged_enemy.state = "WANDER"
            if victory and engaged_enemy in dark_world_enemies:
                dark_world_enemies.remove(engaged_enemy)
            elif not victory and engaged_enemy in dark_world_enemies:
                engaged_enemy.state = "WANDER"
            if victory and engaged_enemy in dark_throne_enemies:
                dark_throne_enemies.remove(engaged_enemy)
            elif not victory and engaged_enemy in dark_throne_enemies:
                if tid == "nyxar":
                    engaged_enemy.x = 383.0
                    engaged_enemy.y = 240.0
                engaged_enemy.state = "WANDER"
            completed_all_tutorial = False
            if engaged_enemy in tutorial_enemies:
                # Los entrenadores no pueden morir ni desaparecer del mapa: se quedan en su pedestal
                player.y = max(player.y, engaged_enemy.y + 34.0)
                player.depth_y = player.y + player.h - 1
                if victory and tid:
                    completed_tutorial_trainers.add(tid)
                    if len(completed_tutorial_trainers) >= 3:
                        completed_all_tutorial = True
            engaged_enemy = None
            battle_instance = None
            battle_grace_timer = 1.0

            if revived:
                current_scene_type = "EXPLORATION"
                current_map_id = "cemetery"
                player.x = 388.0
                player.y = 496.0
                player.facing = "UP"
                player.depth_y = player.y + player.h - 1
                cem_map = interiors["cemetery"]
                camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, cem_map.pixel_w, cem_map.pixel_h)
                dc = player.death_count
                if dc == 1:
                    revival_lines = [
                        "* ...",
                        "* Paniel abre los ojos jadeando sobre los adoquines del cementerio.",
                        "* '¿Qué... demonios fue eso? Sentí cómo mi alma se hacía trizas.'",
                        "* 'Sigo atrapado aquí... Pero el frío no se va de mis huesos.'",
                    ]
                elif dc <= 3:
                    revival_lines = [
                        f"* Despiertas de nuevo junto a la reja cerrada. Muerte número {dc}.",
                        "* 'Recuerdo el golpe. Recuerdo el dolor con total nitidez.'",
                        "* Paniel aprieta los puños mientras un escalofrío recorre su espalda.",
                    ]
                elif dc <= 6:
                    revival_lines = [
                        f"* {dc} muertes. El suelo helado del cementerio ya es como un viejo conocido.",
                        "* 'Vuelvo una y otra vez... ¿Acaso este camposanto es una prisión eterna?'",
                        "* (Tu mirada se torna más oscura y distante)",
                    ]
                else:
                    revival_lines = [
                        f"* ¡¡DESPIERTAS OTRA VEZ!! Muerte número {dc}.",
                        "* 'JAJAJAJA... ¡¡NI LA MUERTE PUEDE MANTENERME ENTERRADO AQUÍ!!'",
                        "* Paniel se levanta con una carcajada siniestra y una sonrisa desquiciada.",
                    ]
                dialogue_box.start_dialogue(revival_lines)
            else:
                current_scene_type = "EXPLORATION"
                if completed_all_tutorial:
                    start_cemetery_wakeup(from_tutorial=True)
                elif was_boss and victory:
                    if tid == "nyxar":
                        dialogue_box.start_dialogue([
                            "* ¡¡La Fuente Oscura se aquieta y las alas de neón de Nyxar se disipan en luz!!",
                            "* Nyxar inclina su corona quebrada reconociendo la fuerza de tu Alma Roja.",
                            "* Paniel: 'Ese combate fue una locura... ¡Mira, el Cofre Real detrás del trono está libre!'",
                        ])
                    elif tid == "arconte":
                        dialogue_box.start_dialogue([
                            "* ¡¡El Cristal Negro se ha hecho añicos y el Fuego Oscuro se disipa!!",
                            "* Vaelkor se desvanece en fragmentos oscuros reconociendo tu poder.",
                            "* Paniel: 'Ni siquiera el núcleo del Eclipse pudo resistir mi BlackFlash.'",
                        ])
                    else:
                        dialogue_box.start_dialogue([
                            "* ¡El silencio regresa al camposanto!",
                            "* Morvath baja su guadaña y se desvanece en paz.",
                            "* Paniel: 'Su vigilia ha terminado... El camino al Mausoleo ha quedado libre.'",
                        ])

        battle_instance = DeltaruneBattle(player, enemy.template_id, sound_fx, font_hud, font_dialogue, on_battle_finish)

    def start_cemetery_wakeup(from_tutorial=False):
        nonlocal current_scene_type, current_map_id, wakeup_timer, wakeup_dialogue_pending, battle_grace_timer
        current_scene_type = "EXPLORATION"
        current_map_id = "cemetery"
        player.x = 388.0
        player.y = 496.0
        player.facing = "DOWN"
        player.depth_y = player.y + player.h - 1
        cem_map = interiors["cemetery"]
        camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, cem_map.pixel_w, cem_map.pixel_h)
        wakeup_timer = wakeup_duration
        wakeup_dialogue_pending = True
        battle_grace_timer = 4.5

    def execute_scene_switch(target_scene_id, target_spawn):
        nonlocal current_map_id, wakeup_timer, wakeup_dialogue_pending, battle_grace_timer
        prev_map = current_map_id
        current_map_id = target_scene_id
        player.x = float(target_spawn[0])
        player.y = float(target_spawn[1])
        player.depth_y = player.y + player.h - 1
        next_map = interiors[current_map_id]
        camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, next_map.pixel_w, next_map.pixel_h)
        sound_fx.play_door()
        if prev_map == "tutorial_grounds" and target_scene_id == "cemetery":
            player.facing = "DOWN"
            wakeup_timer = wakeup_duration
            wakeup_dialogue_pending = True
            battle_grace_timer = 4.5

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        # ------------------------------------------------------
        # MODO PANTALLA DE TÍTULO E INTRO (DELTARUNE STYLE)
        # ------------------------------------------------------
        if current_scene_type == "TITLE":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN and (event.key == pygame.K_F4 or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT))):
                    is_fullscreen = not is_fullscreen
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if is_fullscreen else pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                else:
                    res = title_screen.handle_input(event)
                    if res == "START_GAME":
                        start_cemetery_wakeup(from_tutorial=False)
                    elif res == "START_TUTORIAL":
                        current_scene_type = "EXPLORATION"
                        current_map_id = "tutorial_grounds"
                        player.x = 388.0
                        player.y = 825.0
                        player.facing = "UP"
                        player.depth_y = player.y + player.h - 1
                        tut_map = interiors["tutorial_grounds"]
                        camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, tut_map.pixel_w, tut_map.pixel_h)
                        dialogue_box.start_dialogue([
                            "* ¡Bienvenido al TUTORIAL de UnderBread!",
                            "* 1) Junto a ti tienes la Estrella Amarilla de GUARDADO (cura tu HP al 100%, +25% Cordura y guarda tu progreso).",
                            "* 2) Lee los carteles con [Z] para conocer FIGHT, ACT (BlackFlash), ITEM, SPARE, DEFEND y la Tienda.",
                            "* 3) Practica con los 3 Instructores (Esquiva, Parry [Z] verde y Dash [X]) o cruza el Portal Norte para despertar en el Cementerio."
                        ])
                    elif res == "QUIT":
                        running = False

            if current_scene_type == "TITLE":
                title_screen.update(dt)
                virtual_screen.fill(COLOR_BLACK)
                title_screen.draw(virtual_screen)
                present_screen()
                continue

        # ------------------------------------------------------
        # MODO COMBATE (DELTARUNE BATTLE SYSTEM)
        # ------------------------------------------------------
        if current_scene_type == "BATTLE" and battle_instance:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN and (event.key == pygame.K_F4 or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT))):
                    is_fullscreen = not is_fullscreen
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if is_fullscreen else pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                elif battle_instance:
                    battle_instance.handle_input(event)

            if current_scene_type == "BATTLE" and battle_instance:
                battle_instance.update(dt)

                virtual_screen.fill(COLOR_BLACK)
                battle_instance.draw(virtual_screen)

                present_screen()
                continue

        # ------------------------------------------------------
        # MODO EXPLORACIÓN (CEMENTERIO Y ENTRADA)
        # ------------------------------------------------------
        if battle_grace_timer > 0:
            battle_grace_timer = max(0.0, battle_grace_timer - dt)

        active_world = interiors[current_map_id]
        player.in_dark_world = current_map_id in ("dark_world", "dark_world_throne")
        area_name = active_world.name
        map_w, map_h = active_world.pixel_w, active_world.pixel_h

        # ------------------------------------------------------
        # EVENTOS
        # ------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                continue

            if event.type == pygame.KEYDOWN and (event.key == pygame.K_F4 or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT))):
                is_fullscreen = not is_fullscreen
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if is_fullscreen else pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                continue

            if dialogue_box.active:
                dialogue_box.handle_input(event)
                continue

            if shop_menu.active:
                shop_menu.handle_input(event, player)
                continue

            if undertale_menu.active:
                undertale_menu.handle_input(event, player, dialogue_box)
                continue

            if transition.state != "IDLE":
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Menú pausado estilo Undertale con tecla [C] (Objetos, Estadísticas, Mente, Muertes)
                elif event.key == pygame.K_c and not dialogue_box.active:
                    undertale_menu.open()

                # Atajos rápidos [1, 2, 3, 4] para probar los estados emocionales de Paniel y sus sprites
                elif event.key == pygame.K_1:
                    player.sanity = 100.0  # FELIZ
                    sound_fx.play_select()
                elif event.key == pygame.K_2:
                    player.sanity = 60.0   # TRISTE
                    sound_fx.play_select()
                elif event.key == pygame.K_3:
                    player.sanity = 30.0   # TRAUMADO
                    sound_fx.play_select()
                elif event.key == pygame.K_4:
                    player.sanity = 5.0    # LOCO
                    sound_fx.play_select()

                # Interacción con tecla [Z], [ENTER] o [ESPACIO]
                elif event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                    interact_reach = 26
                    check_x = player.x + player.w / 2
                    check_y = player.y + player.h - 5

                    if player.facing == "UP":
                        check_y -= interact_reach
                    elif player.facing == "DOWN":
                        check_y += interact_reach
                    elif player.facing == "LEFT":
                        check_x -= interact_reach
                    elif player.facing == "RIGHT":
                        check_x += interact_reach

                    check_rect = pygame.Rect(check_x - 14, check_y - 14, 28, 28)
                    for obj in active_world.world_objects:
                        if obj.interactable:
                            obj_box = obj.solid_rect if obj.solid_rect else pygame.Rect(obj.x, obj.y, getattr(obj, "w", 24), getattr(obj, "h", 24))
                            if check_rect.colliderect(obj_box) or math.hypot(check_x - obj_box.centerx, check_y - obj_box.centery) < 34:
                                try:
                                    obj.interact(dialogue_box, sound_fx, player=player, shop_menu=shop_menu)
                                except TypeError:
                                    try:
                                        obj.interact(dialogue_box, sound_fx, player=player)
                                    except TypeError:
                                        obj.interact(dialogue_box, sound_fx)
                                break

        # ------------------------------------------------------
        # ACTUALIZACIÓN DE LÓGICA
        # ------------------------------------------------------
        dialogue_box.update(dt)
        transition.update(dt, execute_scene_switch, sound_fx=sound_fx)

        # Cinemática inicial de despertar dentro del Cementerio
        if wakeup_timer > 0.0:
            wakeup_timer = max(0.0, wakeup_timer - dt)
            if wakeup_timer <= 0.0 and wakeup_dialogue_pending:
                wakeup_dialogue_pending = False
                player.facing = "DOWN"
                sound_fx.play_select()
                dialogue_box.start_dialogue([
                    "* ...Mmmh... ¿Qué hora es...?",
                    "* Paniel abre los ojos tiritando sobre los adoquines fríos del cementerio.",
                    "* Paniel: '¿Me quedé dormido aquí...? Solo vine al atardecer a dejar esas flores celestes.'",
                    "* Paniel: 'Llevaba noches sin dormir por el cansancio... y esta niebla dulce me venció.'",
                    "* (Miras atrás: la gran reja sur tiene cadena y candado por fuera.)",
                    "* Paniel: '¡El guardia cerró conmigo adentro! Y esos encapuchados entre las tumbas...'",
                    "* Paniel: 'Debo buscar otra salida... quizá por la Iglesia al Este o el Mausoleo al Norte.'"
                ])

        # Movimiento del personaje y menús Undertale / Tienda Deltarune
        undertale_menu.update(dt)
        shop_menu.update(dt)
        can_move = (wakeup_timer <= 0.0) and (not dialogue_box.active) and (not undertale_menu.active) and (not shop_menu.active) and (transition.state == "IDLE")
        player.handle_input_and_move(dt, active_world.solid_rects, disabled=not can_move)

        # Actualizar enemigos sueltos en el Tutorial, Cementerio, Abismo, Santuario, Dark World o Trono Oscuro
        if wakeup_timer <= 0.0 and current_map_id in ("tutorial_grounds", "cemetery", "cemetery_depths", "eclipse_sanctuary", "dark_world", "dark_world_throne"):
            if current_map_id == "tutorial_grounds":
                active_enemies = tutorial_enemies
            elif current_map_id == "cemetery":
                active_enemies = cemetery_enemies
            elif current_map_id == "cemetery_depths":
                active_enemies = depths_enemies
            elif current_map_id == "eclipse_sanctuary":
                active_enemies = sanctuary_enemies
            elif current_map_id == "dark_world":
                active_enemies = dark_world_enemies
            else:
                active_enemies = dark_throne_enemies
            p_center = (player.x + player.w / 2, player.y + player.h / 2)
            lv_chase_bonus = max(0, player.lv - 1) * 4.5
            for enm in list(active_enemies):
                if not getattr(enm, "is_tutorial_dummy", False):
                    enm.speed_chase = 64.0 + lv_chase_bonus
                enm.update(dt, p_center, active_world.solid_rects)
                if can_move and battle_grace_timer <= 0 and player.hitbox.colliderect(enm.hitbox):
                    start_combat(enm)
                    break

        if current_scene_type == "BATTLE":
            continue

        # Transición de pantallas
        if can_move:
            # 0. Tutorial -> Interior del Cementerio (al cruzar el Portal Dorado del Norte tras superar los 3 Instructores)
            if current_map_id == "tutorial_grounds":
                tut_scene = interiors["tutorial_grounds"]
                if hasattr(tut_scene, "tutorial_exit_gate_rect") and player.hitbox.colliderect(tut_scene.tutorial_exit_gate_rect):
                    if len(completed_tutorial_trainers) < 3:
                        player.y = 132.0
                        player.depth_y = player.y + player.h - 1
                        missing_names = []
                        for req_id, req_lbl in [
                            ("maniqui_esquiva", "Guía Esquiva (4/4)"),
                            ("maniqui_parry", "Guía Parry [Z] (4/4)"),
                            ("maniqui_dash", "Guía Dash [X] (4/4)"),
                        ]:
                            if req_id not in completed_tutorial_trainers:
                                missing_names.append(req_lbl)
                        sound_fx.play_hurt()
                        dialogue_box.start_dialogue([
                            f"* ¡EL PORTAL DORADO ESTÁ SELLADO! (Instructores superados: {len(completed_tutorial_trainers)}/3).",
                            f"* Aún debes superar la prueba (4/4) y usar SPARE con: {', '.join(missing_names)}.",
                        ])
                    else:
                        transition.start(
                            target_scene_id="cemetery",
                            target_spawn=(388, 496),
                            banner_text="Cementerio",
                        )
            # 1. Interior del Cementerio -> Abismo (norte) o Atrio de la Iglesia (este) [Reja sur cerrada con candado]
            elif current_map_id == "cemetery":
                cem_scene = interiors["cemetery"]
                if hasattr(cem_scene, "depths_gate_rect") and player.hitbox.colliderect(cem_scene.depths_gate_rect):
                    transition.start(
                        target_scene_id="cemetery_depths",
                        target_spawn=(400, 520),
                        banner_text="Abismo"
                    )
                elif hasattr(cem_scene, "church_section_gate_rect") and player.hitbox.colliderect(cem_scene.church_section_gate_rect):
                    transition.start(
                        target_scene_id="cemetery_church_section",
                        target_spawn=(44, 336),
                        banner_text="Atrio Iglesia"
                    )
            # 2. Atrio de la Iglesia -> Regreso al Cementerio (oeste) o Entrar a la Iglesia (norte)
            elif current_map_id == "cemetery_church_section":
                csec_scene = interiors["cemetery_church_section"]
                if csec_scene.exit_rect and player.hitbox.colliderect(csec_scene.exit_rect) and player.facing == "LEFT":
                    transition.start(
                        target_scene_id="cemetery",
                        target_spawn=(735, 336),
                        banner_text="Cementerio"
                    )
                elif hasattr(csec_scene, "church_gate_rect") and player.hitbox.colliderect(csec_scene.church_gate_rect):
                    transition.start(
                        target_scene_id="church",
                        target_spawn=(400, 520),
                        banner_text="Iglesia"
                    )
            # 3. Abismo -> Regreso al Cementerio (sur) o Cristal Negro (norte)
            elif current_map_id == "cemetery_depths":
                depths_scene = interiors["cemetery_depths"]
                if depths_scene.exit_rect and player.hitbox.colliderect(depths_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="cemetery",
                        target_spawn=(400, 162),
                        banner_text="Cementerio"
                    )
                elif hasattr(depths_scene, "sanctuary_gate_rect") and player.hitbox.colliderect(depths_scene.sanctuary_gate_rect):
                    transition.start(
                        target_scene_id="eclipse_sanctuary",
                        target_spawn=(400, 520),
                        banner_text="Cristal Negro"
                    )
            # 4. Cristal Negro -> Regreso al Abismo (salida al sur)
            elif current_map_id == "eclipse_sanctuary":
                sanc_scene = interiors["eclipse_sanctuary"]
                if sanc_scene.exit_rect and player.hitbox.colliderect(sanc_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="cemetery_depths",
                        target_spawn=(400, 145),
                        banner_text="Abismo"
                    )
            # 5. Iglesia -> Salida al Atrio (sur) o Sótano (puerta norte)
            elif current_map_id == "church":
                ch_scene = interiors["church"]
                if ch_scene.exit_rect and player.hitbox.colliderect(ch_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="cemetery_church_section",
                        target_spawn=(400, 272),
                        banner_text="Atrio Iglesia",
                    )
                elif hasattr(ch_scene, "basement_gate_rect") and player.hitbox.colliderect(ch_scene.basement_gate_rect):
                    transition.start(
                        target_scene_id="church_basement",
                        target_spawn=(400, 520),
                        banner_text="Sótano",
                    )
            # 6. Sótano -> Regreso a la Iglesia (sur) o Caída al Dark World (portal norte)
            elif current_map_id == "church_basement":
                bs_scene = interiors["church_basement"]
                if bs_scene.exit_rect and player.hitbox.colliderect(bs_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="church",
                        target_spawn=(400, 145),
                        banner_text="Iglesia",
                    )
                elif hasattr(bs_scene, "dark_world_gate_rect") and player.hitbox.colliderect(bs_scene.dark_world_gate_rect):
                    transition.start(
                        target_scene_id="dark_world",
                        target_spawn=(400, 520),
                        banner_text="★ DARK WORLD ★",
                    )
            # 7. Dark World -> Regreso al Sótano (portal sur) o Zona Extra Trono Oscuro (portal norte)
            elif current_map_id == "dark_world":
                dw_scene = interiors["dark_world"]
                if dw_scene.exit_rect and player.hitbox.colliderect(dw_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="church_basement",
                        target_spawn=(400, 150),
                        banner_text="Sótano",
                    )
                elif hasattr(dw_scene, "throne_gate_rect") and player.hitbox.colliderect(dw_scene.throne_gate_rect):
                    transition.start(
                        target_scene_id="dark_world_throne",
                        target_spawn=(388, 520),
                        banner_text="Trono Oscuro",
                    )
            # 8. Trono Oscuro (Zona Extra del Dark World) -> Regreso al Dark World (portal sur)
            elif current_map_id == "dark_world_throne":
                dwt_scene = interiors["dark_world_throne"]
                if dwt_scene.exit_rect and player.hitbox.colliderect(dwt_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="dark_world",
                        target_spawn=(388, 126),
                        banner_text="★ DARK WORLD ★",
                    )

        # Actualizar objetos animados (incluyendo fuegos fatuos, faroles, pebeteros y atmósfera del cementerio)
        for obj in active_world.world_objects:
            obj.update(dt)
        if hasattr(active_world, "update_ambient"):
            active_world.update_ambient(dt)

        # Actualizar cámara siguiendo a Paniel
        player_cx = player.x + player.w / 2.0
        player_cy = player.y + player.h / 2.0
        camera.update(player_cx, player_cy, map_w, map_h)

        # ------------------------------------------------------
        # RENDERIZADO PIXEL-PERFECT (100% CALIDAD NATIVA SIN REESCALADO)
        # ------------------------------------------------------
        virtual_screen.fill(COLOR_BLACK)

        # 1. Capa de suelo / fondo
        active_world.draw_ground(virtual_screen, camera)

        # 2. Profundidad 2.5D (Y-SORTING)
        render_queue = list(active_world.world_objects)
        if current_map_id == "tutorial_grounds":
            render_queue.extend(tutorial_enemies)
        elif current_map_id == "cemetery":
            render_queue.extend(cemetery_enemies)
        elif current_map_id == "cemetery_depths":
            render_queue.extend(depths_enemies)
        elif current_map_id == "eclipse_sanctuary":
            render_queue.extend(sanctuary_enemies)
        elif current_map_id == "dark_world":
            render_queue.extend(dark_world_enemies)
        elif current_map_id == "dark_world_throne":
            render_queue.extend(dark_throne_enemies)
        render_queue.append(player)
        render_queue.sort(key=lambda item: item.depth_y)

        for entity in render_queue:
            entity.draw(virtual_screen, camera)

        # 2.5 Capa atmosférica animada (niebla, luciérnagas, pétalos nocturnos o Miasma de la Bruja)
        if hasattr(active_world, "draw_overlay"):
            active_world.draw_overlay(virtual_screen, camera)

        # 2.8 Cinemática de despertar dentro del cementerio (Zzz -> sobresalto ! + apertura de párpados)
        if wakeup_timer > 0.0:
            prog = 1.0 - (wakeup_timer / wakeup_duration)
            px_s, py_s = camera.apply((player.x + player.w / 2.0, player.y))
            if prog < 0.56:
                for zi, ch in enumerate(["z", "Z", "z"]):
                    z_rise = ((prog * 2.6 + zi * 0.35) % 1.0) * 20.0
                    zx = int(px_s + 8 + zi * 6)
                    zy = int(py_s - 4 - z_rise)
                    zs = font_hud_small.render(ch, False, (185, 225, 255))
                    virtual_screen.blit(zs, (zx, zy))
            elif prog < 0.90:
                bx_b, by_b = int(px_s - 6), int(py_s - 22)
                pygame.draw.rect(virtual_screen, (255, 255, 255), (bx_b, by_b, 12, 14), border_radius=3)
                pygame.draw.rect(virtual_screen, (20, 20, 32), (bx_b, by_b, 12, 14), 1, border_radius=3)
                exc = font_hud.render("!", False, (220, 40, 60))
                virtual_screen.blit(exc, (bx_b + 3, by_b + 1))

            # Parpadeo cinematográfico al abrir los ojos en el cementerio
            if prog < 0.22:
                open_ratio = (prog / 0.22) * 0.34
            elif prog < 0.36:
                open_ratio = 0.34 - ((prog - 0.22) / 0.14) * 0.22
            elif prog < 0.88:
                open_ratio = 0.12 + ((prog - 0.36) / 0.52) * 0.88
            else:
                open_ratio = 1.0
            lid_h = int((VIRTUAL_HEIGHT / 2.0) * (1.0 - open_ratio))
            if lid_h > 0:
                pygame.draw.rect(virtual_screen, (4, 5, 12), (0, 0, VIRTUAL_WIDTH, lid_h))
                pygame.draw.rect(virtual_screen, (4, 5, 12), (0, VIRTUAL_HEIGHT - lid_h, VIRTUAL_WIDTH, lid_h))

        # 3. Cuadro de diálogo
        dialogue_box.draw(virtual_screen, player=player)

        # 4. HUD de estado inferior
        if wakeup_timer <= 0.0 and not dialogue_box.active and not undertale_menu.active and not shop_menu.active:
            hud.draw(virtual_screen, player=player, is_running=player.is_running and player.is_moving, area_name=area_name, door_prompt=None)

        # 5. Medidor de Locura / HUD de salud mental en la esquina inferior derecha
        mental_hud.update(dt)
        if wakeup_timer <= 0.0 and not dialogue_box.active and not undertale_menu.active and not shop_menu.active:
            mental_hud.draw(virtual_screen, player)

        # 6. Menú estilo Undertale con tecla [C] o Menú de Tienda Dinámico estilo Deltarune
        if undertale_menu.active:
            undertale_menu.draw(virtual_screen, player, mental_hud)
        if shop_menu.active:
            shop_menu.draw(virtual_screen, player)

        # 6. Efecto de transición, animación de caída al Dark World estilo Kris y títulos flotantes
        transition.draw(virtual_screen, font_hud, player=player, camera=camera)

        # 7. Escalado retro a la resolución de ventana (960x720) manteniendo proporción
        present_screen()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

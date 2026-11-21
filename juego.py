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
from interfaz import DialogueBox, PanielMentalHUD, RetroHUD, UndertaleMenu, DeltaruneTitleScreen
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
    pygame.display.set_caption("Paniel - El Cementerio")
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

    # 2. Inicializar escenas del Cementerio (incluyendo el Abismo y el Santuario del Cristal Quebrado)
    interiors = {
        "cemetery_entrance": InteriorScene("cemetery_entrance", "Entrada del Cementerio"),
        "cemetery": InteriorScene("cemetery", "Cementerio"),
        "cemetery_depths": InteriorScene("cemetery_depths", "Abismo del Cementerio"),
        "eclipse_sanctuary": InteriorScene("eclipse_sanctuary", "Santuario del Cristal Quebrado"),
    }

    dialogue_box = DialogueBox(font_dialogue, sound_fx)
    hud = RetroHUD(font_hud, font_prompt)
    mental_hud = PanielMentalHUD(font_hud, font_hud_small)
    undertale_menu = UndertaleMenu(font_hud, font_hud_small, font_dialogue, sound_fx)
    title_screen = DeltaruneTitleScreen(sound_fx, sprite_mgr)
    transition = SceneTransition()

    # Estado del mundo (inicia en la introducción/título estilo Deltarune)
    current_scene_type = "TITLE"  # TITLE, EXPLORATION o BATTLE
    current_map_id = "cemetery_entrance"
    battle_instance = None
    engaged_enemy = None
    battle_grace_timer = 0.0

    # Iniciar jugador en la acera frente a la puerta del cementerio con sus sprites 1:1 originales
    player = Player(x=237, y=390, sprite_manager=sprite_mgr)
    player.facing = "UP"

    # Centrar la cámara de inmediato en Paniel
    active_map = interiors[current_map_id]
    camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, active_map.pixel_w, active_map.pixel_h)

    # Enemigos patrullando en el cementerio (distribuidos en el mapa de 800x600 con el Jefe custodiando el Mausoleo)
    cemetery_enemies = [
        OverworldEnemy(383, 195, "sepulturero"),  # ¡EL JEFE MORVATH EL SEPULTURERO CUSTODIANDO EL GRAN MAUSOLEO!
        OverworldEnemy(180, 240, "sombra"),
        OverworldEnemy(620, 240, "fantasmino"),
        OverworldEnemy(400, 395, "sectario"),
        OverworldEnemy(260, 480, "sombra"),
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
        if current_scene_type == "EXPLORATION" and current_map_id == "cemetery":
            if random.randint(1, 50) == 1:
                spawn_cemetery_enemy()

    player.on_step_callback = on_player_step

    def start_combat(enemy):
        nonlocal current_scene_type, battle_instance, engaged_enemy
        sound_fx.play_encounter()
        engaged_enemy = enemy
        current_scene_type = "BATTLE"

        def on_battle_finish(victory, revived=False):
            nonlocal current_scene_type, current_map_id, battle_instance, engaged_enemy, battle_grace_timer
            tid = getattr(engaged_enemy, "template_id", "") if engaged_enemy is not None else ""
            was_boss = tid in ("sepulturero", "arconte")
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
            engaged_enemy = None
            battle_instance = None
            battle_grace_timer = 1.0

            if revived:
                current_scene_type = "EXPLORATION"
                current_map_id = "cemetery_entrance"
                player.x = 237.0
                player.y = 390.0
                player.facing = "UP"
                player.depth_y = player.y + player.h - 1
                cem_ent = interiors["cemetery_entrance"]
                camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, cem_ent.pixel_w, cem_ent.pixel_h)
                dc = player.death_count
                if dc == 1:
                    revival_lines = [
                        "* ...",
                        "* Paniel abre los ojos jadeando en la hierba del cementerio.",
                        "* '¿Qué... demonios fue eso? Sentí cómo mi alma se hacía trizas.'",
                        "* 'Sigo vivo... Pero el frío no se va de mis huesos.'",
                    ]
                elif dc <= 3:
                    revival_lines = [
                        f"* Despiertas de nuevo ante la verja. Muerte número {dc}.",
                        "* 'Recuerdo el golpe. Recuerdo el dolor con total nitidez.'",
                        "* Paniel aprieta los puños mientras un escalofrío recorre su espalda.",
                    ]
                elif dc <= 6:
                    revival_lines = [
                        f"* {dc} muertes. El suelo de la entrada del cementerio ya es como un viejo conocido.",
                        "* 'Vuelvo una y otra vez... ¿Acaso este cementerio es una prisión eterna?'",
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
                if was_boss and victory:
                    if tid == "arconte":
                        dialogue_box.start_dialogue([
                            "* ¡¡El Cristal Negro se ha hecho añicos y el Fuego Oscuro se disipa!!",
                            "* Vaelkor, Rey del Cristal Negro, se desvanece reconociendo tu poder.",
                            "* Paniel: 'Ni siquiera el núcleo del Eclipse pudo resistir mi BlackFlash.'",
                        ])
                    else:
                        dialogue_box.start_dialogue([
                            "* ¡El silencio regresa al camposanto!",
                            "* Morvath el Sepulturero baja su guadaña y se desvanece en paz.",
                            "* Paniel: 'Su vigilia ha terminado... El camino al Mausoleo ancestral ha quedado libre.'",
                        ])

        battle_instance = DeltaruneBattle(player, enemy.template_id, sound_fx, font_hud, font_dialogue, on_battle_finish)

    def execute_scene_switch(target_scene_id, target_spawn):
        nonlocal current_map_id
        current_map_id = target_scene_id
        player.x = float(target_spawn[0])
        player.y = float(target_spawn[1])
        player.depth_y = player.y + player.h - 1
        next_map = interiors[current_map_id]
        camera.snap(player.x + player.w / 2.0, player.y + player.h / 2.0, next_map.pixel_w, next_map.pixel_h)
        sound_fx.play_door()

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
                        current_scene_type = "EXPLORATION"
                        dialogue_box.start_dialogue([
                            "* (El aire frío de la noche rodea la Entrada del Cementerio).",
                            "* Paniel: 'Así que este es el lugar... La verja de hierro está entreabierta.'",
                            "* (Usa las FLECHAS para moverte, [Z] para interactuar y [C] para abrir el menú)."
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
                                    obj.interact(dialogue_box, sound_fx, player=player)
                                except TypeError:
                                    obj.interact(dialogue_box, sound_fx)
                                break

        # ------------------------------------------------------
        # ACTUALIZACIÓN DE LÓGICA
        # ------------------------------------------------------
        dialogue_box.update(dt)
        transition.update(dt, execute_scene_switch)

        # Movimiento del personaje y menú Undertale
        undertale_menu.update(dt)
        can_move = (not dialogue_box.active) and (not undertale_menu.active) and (transition.state == "IDLE")
        player.handle_input_and_move(dt, active_world.solid_rects, disabled=not can_move)

        # Actualizar enemigos sueltos en el cementerio, el Abismo o el Santuario del Cristal Quebrado
        if current_map_id in ("cemetery", "cemetery_depths", "eclipse_sanctuary"):
            if current_map_id == "cemetery":
                active_enemies = cemetery_enemies
            elif current_map_id == "cemetery_depths":
                active_enemies = depths_enemies
            else:
                active_enemies = sanctuary_enemies
            p_center = (player.x + player.w / 2, player.y + player.h / 2)
            lv_chase_bonus = max(0, player.lv - 1) * 4.5
            for enm in list(active_enemies):
                enm.speed_chase = 64.0 + lv_chase_bonus
                enm.update(dt, p_center, active_world.solid_rects)
                if can_move and battle_grace_timer <= 0 and player.hitbox.colliderect(enm.hitbox):
                    start_combat(enm)
                    break

        if current_scene_type == "BATTLE":
            continue

        # Transición de pantallas
        if can_move:
            # 1. Entrada del Cementerio -> Interior (marco de la puerta)
            if current_map_id == "cemetery_entrance":
                cent_scene = interiors["cemetery_entrance"]
                if hasattr(cent_scene, 'cemetery_gate_rect') and player.hitbox.colliderect(cent_scene.cemetery_gate_rect):
                    transition.start(
                        target_scene_id="cemetery",
                        target_spawn=(400, 520),
                        banner_text="Cementerio"
                    )
            # 2. Interior del Cementerio -> Entrada (sur) o Abismo del Cementerio (norte por el Mausoleo)
            elif current_map_id == "cemetery":
                cem_scene = interiors["cemetery"]
                if cem_scene.exit_rect and player.hitbox.colliderect(cem_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="cemetery_entrance",
                        target_spawn=(237, 390),
                        banner_text="Entrada del Cementerio"
                    )
                elif hasattr(cem_scene, "depths_gate_rect") and player.hitbox.colliderect(cem_scene.depths_gate_rect):
                    transition.start(
                        target_scene_id="cemetery_depths",
                        target_spawn=(400, 520),
                        banner_text="Abismo del Cementerio"
                    )
            # 3. Abismo del Cementerio -> Regreso al Cementerio (sur) o Santuario del Cristal Quebrado (norte)
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
                        banner_text="Santuario del Cristal Quebrado"
                    )
            # 4. Santuario del Cristal Quebrado -> Regreso al Abismo del Cementerio (salida al sur)
            elif current_map_id == "eclipse_sanctuary":
                sanc_scene = interiors["eclipse_sanctuary"]
                if sanc_scene.exit_rect and player.hitbox.colliderect(sanc_scene.exit_rect) and player.facing == "DOWN":
                    transition.start(
                        target_scene_id="cemetery_depths",
                        target_spawn=(400, 145),
                        banner_text="Abismo del Cementerio"
                    )

        # Actualizar objetos animados (incluyendo fuegos fatuos y árboles con faroles)
        for obj in active_world.world_objects:
            obj.update(dt)

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
        if current_map_id == "cemetery":
            render_queue.extend(cemetery_enemies)
        elif current_map_id == "cemetery_depths":
            render_queue.extend(depths_enemies)
        elif current_map_id == "eclipse_sanctuary":
            render_queue.extend(sanctuary_enemies)
        render_queue.append(player)
        render_queue.sort(key=lambda item: item.depth_y)

        for entity in render_queue:
            entity.draw(virtual_screen, camera)

        # 3. Cuadro de diálogo
        dialogue_box.draw(virtual_screen, player=player)

        # 4. HUD de estado inferior
        if not dialogue_box.active and not undertale_menu.active:
            hud.draw(virtual_screen, player=player, is_running=player.is_running and player.is_moving, area_name=area_name, door_prompt=None)

        # 5. Medidor de Locura / HUD de salud mental en la esquina inferior derecha
        mental_hud.update(dt)
        if not dialogue_box.active and not undertale_menu.active:
            mental_hud.draw(virtual_screen, player)

        # 6. Menú estilo Undertale con tecla [C]
        if undertale_menu.active:
            undertale_menu.draw(virtual_screen, player, mental_hud)

        # 6. Efecto de transición y títulos flotantes
        transition.draw(virtual_screen, font_hud)

        # 7. Escalado retro a la resolución de ventana (960x720) manteniendo proporción
        present_screen()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

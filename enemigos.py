import math
import random
import pygame
from objetos_mundo import WorldObject

# ==========================================================
# SISTEMA DE COMBATE Y ENEMIGOS ESTILO DELTARUNE
# ==========================================================

# 1. PLANTILLAS DE ENEMIGOS INVENTADOS (Con estadísticas similares o superiores)
ENEMY_TEMPLATES = {
    "sombra": {
        "id": "sombra",
        "name": "Acechador",
        "hp": 24,
        "max_hp": 24,
        "attack": 11,
        "defense": 2,
        "exp": 25,
        "color": (165, 75, 240),
        "intro_text": "* ¡Un Acechador de la Gula emerge del miasma oscuro con dagas gemelas y sonrisa vendada!",
        "quotes": [
            "* ¡Qué delicioso aroma tienen tus recuerdos...!",
            "* ¡Dame tu nombre, viajero del camposanto!",
            "* ¡El miasma de la Bruja devorará tu sombra!",
            "* ¡Qué festín tan exquisito nos promete el Evangelio!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* ACECHADOR (GULA) - ATK 11 DEF 2\n* Secuaz sigiloso del Culto de la Bruja envuelto en vendas y miasma.\n* Atraviesa sus muros dorados de filo pulsando Dash [X].",
                "mercy": 0,
            },
            {
                "name": "Contar Recuerdo",
                "text": "* Compartes en voz alta un recuerdo cálido de tu infancia.\n* ¡El Acechador escucha embelesado y baja sus dagas sombrías!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Disipar Miasma",
                "text": "* Proyectas la luz serena de tu Alma para purificar la niebla a su alrededor.\n* Sus ojos rasgados se calman al sentir alivio del hambre eterna.\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["shadow_rain", "shadow_spiral", "crystal_dash_sweep"],
    },
    "rudinn": {
        "id": "rudinn",
        "name": "Heraldo",
        "hp": 26,
        "max_hp": 26,
        "attack": 12,
        "defense": 3,
        "exp": 32,
        "color": (225, 210, 255),
        "intro_text": "* ¡Un Heraldo de la Codicia ajusta su abrigo impecable mientras congela el aire a su alrededor!",
        "quotes": [
            "* ¡¿Cómo te atreves a violar mis derechos mirando mi rostro?!",
            "* ¡Mi túnica inmaculada no tolerará ni una mota de polvo!",
            "* ¡Soy un ser completo y perfecto; tu presencia es una ofensa!",
            "* ¡El tiempo mismo se inclina ante la voluntad del Culto!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* HERALDO (CODICIA) - ATK 12 DEF 3\n* Secuaz aristocrático del Culto de la Bruja con máscara de porcelana.\n* Sus lanzas de cristal flotan detenidas en un halo temporal.",
                "mercy": 0,
            },
            {
                "name": "Respetar Derechos",
                "text": "* Te disculpas formalmente por haber interrumpido su paseo nocturno.\n* ¡El Heraldo asiente satisfecho con aire de superioridad!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Elogiar Túnica",
                "text": "* Alabas la perfección impecable de su abrigo blanco y dorado.\n* Su mirada gélida se suaviza y baja su estoque ritual.\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["diamond_swords", "crossfire_diamonds", "crystal_dash_sweep"],
    },
    "fantasmino": {
        "id": "fantasmino",
        "name": "Lamento",
        "hp": 22,
        "max_hp": 22,
        "attack": 10,
        "defense": 2,
        "exp": 22,
        "color": (255, 115, 165),
        "intro_text": "* ¡Un Lamento de la Ira flota envuelto en vendas ardientes haciendo girar sus cadenas de fuego!",
        "quotes": [
            "* ¡Siente mi dolor! ¡Compartamos nuestras almas en llamas!",
            "* ¡¿No escuchas el latido ardiente que nos une a todos?!",
            "* ¡El amor de la Bruja arde con una pasión abrasadora!",
            "* ¡Llora conmigo bajo la luna del cementerio!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* LAMENTO (IRA) - ATK 10 DEF 2\n* Espectro vendado del Culto de la Bruja atado a incensarios ardientes.\n* Contagia sus emociones intensas a través de cadenas llameantes.",
                "mercy": 0,
            },
            {
                "name": "Escuchar Lamento",
                "text": "* Escuchas su llanto en silencio sin juzgar su sufrimiento.\n* ¡Sus cadenas en llamas dejan de girar frenéticamente!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Apaciguar Alma",
                "text": "* Ofreces una palabra serena para aliviar la furia que la consume.\n* Su ojo ardiente destella con calma y lágrimas luminosas.\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["bouncing_notes", "sound_arcs", "miasma_dash_waves"],
    },
    "sectario": {
        "id": "sectario",
        "name": "Dedo Pereza",
        "hp": 30,
        "max_hp": 30,
        "attack": 12,
        "defense": 3,
        "exp": 36,
        "color": (195, 55, 245),
        "intro_text": "* ¡Un Dedo de la Pereza retuerce la cabeza mientras Manos Invisibles brotan de su manto negro!",
        "quotes": [
            "* ¡Qué... PEREZOSO eres! ¡Mi cerebro tiembla!",
            "* ¡El Evangelio Negro dictó nuestro encuentro!",
            "* ¡Contempla las Manos Invisibles del amor de la Bruja!",
            "* ¡Diligencia! ¡Debemos ser DILIGENTES en el rito!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* DEDO PEREZA - ATK 12 DEF 3\n* Secuaz fanático del Culto de la Bruja que porta un Evangelio Negro.\n* Invoca Manos Invisibles y oleadas de miasma que debes cruzar con Dash [X].",
                "mercy": 0,
            },
            {
                "name": "Mostrar Diligencia",
                "text": "* Te mantienes firme y demuestras una disciplina intachable.\n* ¡El Cultista aplaude con lágrimas fanáticas admirando tu diligencia!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Leer Evangelio",
                "text": "* Observas en silencio los símbolos arcanos de su libro oscuro.\n* El secuaz inclina su capucha con devota reverencia.\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["cult_daggers", "blood_sigil", "miasma_dash_waves"],
    },
    "sepulturero": {
        "id": "sepulturero",
        "name": "Morvath",
        "is_boss": True,
        "hp": 110,
        "max_hp": 110,
        "attack": 15,
        "defense": 4,
        "exp": 180,
        "color": (235, 65, 90),
        "intro_text": "* ¡¡MORVATH, EL SEPULTURERO ETERNO, blande su guadaña fúnebre ante el Mausoleo!!",
        "quotes": [
            "* ¡Tu tumba lleva siglos esperando!",
            "* ¡Cada muerte tuya alimenta mi farol!",
            "* ¡¡Siente el corte de mi guadaña bumerán!!",
            "* ¡Las campanas fúnebres doblan por tu alma!",
            "* ¡¡Nadie escapa del Juicio del Sepulturero!!",
            "* ¡La tierra remueve los huesos de los caídos!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* MORVATH EL SEPULTURERO - ATK 15 DEF 4 (JEFE DEL CEMENTERIO)\n* Guardián ancestral que custodia las puertas del Mausoleo.\n* Blande guadañas bumerán, ondas de campana fúnebre y lluvia de ánimas.",
                "mercy": 0,
            },
            {
                "name": "Recordar Nombre",
                "text": "* Pronuncias su antiguo nombre con solemne respeto.\n* ¡La llama del farol de Morvath tiembla con nostalgia!\n* (Piedad +25%)",
                "mercy": 25,
            },
            {
                "name": "Ofrecer Paz",
                "text": "* Le dices que su vigilia eterna ya ha cumplido su deber.\n* Morvath baja lentamente su guadaña-pala ancestral.\n* (Piedad +35%)",
                "mercy": 35,
            },
        ],
        "patterns": [
            "scythe_sweep",
            "soul_lantern_ring",
            "grave_pillars",
            "death_scythe_boomerang",
            "funeral_bell_toll",
            "graveyard_cataclysm",
            "frenzy_soul_hunt",
            "reaper_dash_shockwave",
        ],
    },
    "arconte": {
        "id": "arconte",
        "name": "Vaelkor",
        "is_boss": True,
        "hp": 165,
        "max_hp": 165,
        "attack": 19,
        "defense": 5,
        "exp": 350,
        "color": (255, 35, 95),
        "intro_text": "* ¡¡VAELKOR, REY DEL CRISTAL NEGRO, quiebra el espacio con Fuego Oscuro!!",
        "quotes": [
            "* ¡El cristal de esta realidad ya se ha roto!",
            "* ¡¡Arde en el Vórtice del Fuego Oscuro!!",
            "* ¡¡Ni tu BlackFlash podrá salvar tu alma!!",
            "* ¡¡Las esquirlas dimensionales te consumirán!!",
            "* ¡¡Siente la gravedad del Eclipse Supremo!!",
            "* ¡La realidad se fragmenta ante tu mirada!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* VAELKOR, REY DEL CRISTAL NEGRO - ATK 19 DEF 5 (JEFE SUPREMO)\n* Soberano del Santuario del Cristal Quebrado.\n* Domina vórtices gravitacionales, láseres cruzados y fracturas de cristal negro.",
                "mercy": 0,
            },
            {
                "name": "Desafiar Destino",
                "text": "* Mantienes la mirada firme frente a las grietas de cristal oscuro.\n* ¡Vaelkor reconoce tu determinación inquebrantable!\n* (Piedad +20%)",
                "mercy": 20,
            },
            {
                "name": "Sellar Grieta",
                "text": "* Canalizas el brillo de tu Alma para apaciguar el Fuego Oscuro.\n* Las esquirlas de cristal alrededor de Vaelkor dejan de vibrar.\n* (Piedad +30%)",
                "mercy": 30,
            },
        ],
        "patterns": [
            "black_flame_barrage",
            "crystal_shatter_storm",
            "void_cleave_laser",
            "eclipse_gravity_vortex",
            "fractured_mirror_barrage",
            "abyssal_cross_lasers",
            "apocalypse_crystal_rain",
            "eclipse_dash_fracture",
        ],
    },
    "bufon_caos": {
        "id": "bufon_caos",
        "name": "Jevix",
        "hp": 48,
        "max_hp": 48,
        "attack": 14,
        "defense": 3,
        "exp": 68,
        "color": (210, 95, 255),
        "intro_text": "* ¡Jevix, Bufón del Caos, salta haciendo malabares con naipes en el Dark World!",
        "quotes": [
            "* ¡¡PUEDO HACER CUALQUIER COSA, CAOS, CAOS!!",
            "* ¡A ver si tu escudo de Parry adivina este giro!",
            "* ¡Mis cartas nunca viajan en línea recta!",
            "* ¡La vida en el Dark World es una ruleta loca!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* JEVIX, BUFÓN DEL CAOS - ATK 14 DEF 3 (DARK WORLD)\n* Habitante travieso del Dark World debajo de la iglesia.\n* Sus ataques cambian de dirección de forma totalmente errática.",
                "mercy": 0,
            },
            {
                "name": "Seguir Juego",
                "text": "* Das una pirueta caótica siguiendo el ritmo de sus cascabeles.\n* ¡Jevix ríe encantado con tu locura!\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Adivinar Carta",
                "text": "* Señalas el As de Diamantes antes de que termine de barajar.\n* ¡Jevix aplaude sorprendido!\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["erratic_chaos_cards", "jester_ricochet_scythes", "neon_firewall_dash"],
    },
    "centinela_neon": {
        "id": "centinela_neon",
        "name": "Viro-Neón",
        "hp": 54,
        "max_hp": 54,
        "attack": 15,
        "defense": 4,
        "exp": 76,
        "color": (75, 245, 255),
        "intro_text": "* ¡Viro-Neón despliega sus alas holográficas con interferencia digital!",
        "quotes": [
            "* >> PROTOCOLO DE ATAQUE ERRÁTICO: ACTIVO <<",
            "* ¡Mis paquetes de datos esquivarán tu guardia!",
            "* ¡ERROR 404: PIEDAD NO ENCONTRADA!",
            "* ¡Siente el voltaje del Cyber Dark World!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* VIRO-NEÓN - ATK 15 DEF 4 (DARK WORLD)\n* Guardián cibernético del Dark World subterráneo.\n* Sus proyectiles sufren 'glitch' y dan saltos laterales impredecibles.",
                "mercy": 0,
            },
            {
                "name": "Depurar Código",
                "text": "* Reordenas sus paquetes de datos con un comando amistoso.\n* ¡El visor de Viro-Neón muestra un icono feliz ^_^\n* (Piedad +50%)",
                "mercy": 50,
            },
            {
                "name": "Sincronizar",
                "text": "* Sincronizas el brillo de tu Alma con su frecuencia de neón.\n* ¡Sus alas holográficas bajan en señal de paz!\n* (Piedad +50%)",
                "mercy": 50,
            },
        ],
        "patterns": ["erratic_cyber_viruses", "erratic_chaos_cards", "neon_firewall_dash"],
    },
    "nyxar": {
        "id": "nyxar",
        "name": "Nyxar",
        "is_boss": True,
        "hp": 195,
        "max_hp": 195,
        "attack": 20,
        "defense": 5,
        "exp": 420,
        "color": (85, 245, 255),
        "intro_text": "* ¡¡NYXAR, SOBERANO DE LA FUENTE OSCURA, despliega sus alas de neón en el Trono Oscuro!!",
        "quotes": [
            "* ¡¡ESTA FUENTE OSCURA ME OBEDECE SOLO A MÍ!!",
            "* ¡Cruza mis muros de neón con [X] si puedes!",
            "* ¡Tus recuerdos brillan como código roto!",
            "* ¡¡LÁSERES, CAOS Y GRAVEDAD DEL DARK WORLD!!",
            "* ¡Ni la luz del cementerio alcanzará este trono!",
            "* ¡¡MUÉSTRAME TU VERDADERA DETERMINACIÓN!!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* NYXAR - ATK 20 DEF 5 (JEFE DEL DARK WORLD)\n* Soberano cibernético-abismal del Trono Oscuro.\n* Combina muros de Dash [X], láseres cruzados, vórtices y tormentas glitch.",
                "mercy": 0,
            },
            {
                "name": "Sintonizar Alma",
                "text": "* Resuenas con la frecuencia de la Fuente Oscura sin retroceder.\n* ¡La corona holográfica de Nyxar vibra con respeto!\n* (Piedad +25%)",
                "mercy": 25,
            },
            {
                "name": "Desafiar Fuente",
                "text": "* Apuntas tu Alma Roja directo hacia la Fuente Oscura a sus espaldas.\n* ¡Nyxar ríe complacido y modera su furia un instante!\n* (Piedad +25%)",
                "mercy": 25,
            },
        ],
        "patterns": [
            "nyx_neon_dash_gauntlet",
            "nyx_fountain_crossfire",
            "nyx_abyssal_pendulum",
            "nyx_glitch_storm",
            "nyx_black_sun_collapse",
        ],
    },
    "maniqui_esquiva": {
        "id": "maniqui_esquiva",
        "name": "Esquiva",
        "is_tutorial_dummy": True,
        "hp": 20,
        "max_hp": 20,
        "attack": 4,
        "defense": 1,
        "exp": 15,
        "color": (95, 225, 255),
        "intro_text": "* ¡GUÍA ESQUIVA (Prueba 1/3): '¡Debes cruzar 4 BARRERAS por el HUECO VERDE sin ser golpeado (0/4)! SPARE está bloqueado hasta que logres 4/4.'",
        "quotes": [
            "* ¡Muévete al HUECO VERDE de la barrera!",
            "* ¡Si te golpeo no cuenta: esquiva 4 veces!",
            "* ¡Cada barrera esquivada da +25% MERCY!",
            "* ¡Completa 4/4 esquivas limpias para usar SPARE!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* GUÍA ESQUIVA - PRUEBA OBLIGATORIA (4 ESQUIVAS LIMPIAS)\n* Lanza barreras con un recuadro verde indicando el HUECO SEGURO.\n* ¡Cruza 4 barreras por el hueco sin recibir daño para desbloquear SPARE!",
                "mercy": 0,
            },
            {
                "name": "Guía: Esquiva",
                "text": "* PASO 1: Mira dónde aparece el recuadro verde en la barrera.\n* PASO 2: Mueve tu corazón con [Flechas / WASD] hasta alinearte con el hueco.\n* PASO 3: Cruza 4 barreras sin ser golpeado (4/4 = 100% MERCY).",
                "mercy": 0,
            },
            {
                "name": "Iniciar Prueba",
                "text": "* ¡El Guía lanza su tanda de barreras!\n* '¡Recuerda: ni ACT ni FIGHT suben mi MERCY! ¡Solo esquivar 4 barreras por el hueco!'",
                "mercy": 0,
            },
        ],
        "patterns": ["tutorial_dodge_corridor"],
    },
    "maniqui_parry": {
        "id": "maniqui_parry",
        "name": "Parry",
        "is_tutorial_dummy": True,
        "hp": 22,
        "max_hp": 22,
        "attack": 4,
        "defense": 1,
        "exp": 15,
        "color": (65, 250, 130),
        "intro_text": "* ¡GUÍA PARRY (Prueba 2/3): '¡Debes bloquear 4 ESFERAS VERDES pulsando [Z] (Escudo Verde) antes del impacto (0/4) para desbloquear SPARE!'",
        "quotes": [
            "* ¡Cuando el anillo brille en amarillo, pulsa [Z]!",
            "* ¡Bloquea 4 esferas con tu Escudo Verde [Z]!",
            "* ¡Cada PARRY exitoso suma 1/4 (+25% MERCY)!",
            "* ¡Sin 4/4 Parrys no podrás usar SPARE!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* GUÍA PARRY - PRUEBA OBLIGATORIA (4 PARRYS CON [Z])\n* Lanza esferas verdes guiadas directamente a tu corazón.\n* ¡Pulsa [Z] justo antes de que te toquen para bloquear 4 esferas y desbloquear SPARE!",
                "mercy": 0,
            },
            {
                "name": "Guía: Parry [Z]",
                "text": "* PASO 1: Espera a que la esfera verde se acerque a tu corazón (su anillo cambia a amarillo).\n* PASO 2: Pulsa [Z] para activar el Escudo Verde durante 0.36s.\n* PASO 3: Haz 4 Parrys exitosos (4/4 = 100% MERCY y +16% TP por Parry).",
                "mercy": 0,
            },
            {
                "name": "Iniciar Prueba",
                "text": "* ¡El Guía apunta sus esferas guiadas hacia tu corazón!\n* '¡Pulsa [Z] en el momento justo 4 veces para superar mi entrenamiento!'",
                "mercy": 0,
            },
        ],
        "patterns": ["tutorial_parry_orbs"],
    },
    "maniqui_dash": {
        "id": "maniqui_dash",
        "name": "Dash",
        "is_tutorial_dummy": True,
        "hp": 24,
        "max_hp": 24,
        "attack": 4,
        "defense": 1,
        "exp": 20,
        "color": (255, 215, 80),
        "intro_text": "* ¡GUÍA DASH (Prueba 3/3): '¡Debes ATRAVESAR 4 MUROS DORADOS pulsando [X] (DASH) al cruzarlos (0/4)! Hacer Dash lejos del muro no cuenta.'",
        "quotes": [
            "* ¡Camina hacia el muro dorado y pulsa [X] para cruzarlo!",
            "* ¡Hacer Dash en el aire vacío no cuenta: cruza el muro!",
            "* ¡Atraviesa 4 muros con [X] para llegar a 100% MERCY!",
            "* ¡El Dash [X] te vuelve invulnerable al cruzar el láser!",
        ],
        "acts": [
            {
                "name": "Examinar",
                "text": "* GUÍA DASH - PRUEBA OBLIGATORIA (ATRAVESAR 4 MUROS CON [X])\n* Lanza muros láser dorados de ancho/alto completo sin huecos.\n* ¡Debes cruzar a través de 4 muros usando [X] (DASH) para desbloquear SPARE!",
                "mercy": 0,
            },
            {
                "name": "Guía: Dash [X]",
                "text": "* PASO 1: Mantén presionada la dirección hacia donde viene el muro dorado.\n* PASO 2: Justo al llegar al muro, pulsa [X] para impulsarte y atravesarlo sin daño.\n* PASO 3: Atraviesa 4 muros dorados (4/4 = 100% MERCY).",
                "mercy": 0,
            },
            {
                "name": "Iniciar Prueba",
                "text": "* ¡El Guía activa los muros láser de barrido completo!\n* '¡Demuestra que sabes atravesar 4 muros con [X] para graduarte del tutorial!'",
                "mercy": 0,
            },
        ],
        "patterns": ["tutorial_dash_walls"],
    },
}


# 2. ENEMIGO SUELTO EN EL MAPA (Overworld) CON PATRULLA, ALERTA Y PERSECUCIÓN
class OverworldEnemy(WorldObject):
    def __init__(self, x, y, template_id):
        super().__init__(x, y, depth_y=y + 26)
        self.template_id = template_id
        self.template = ENEMY_TEMPLATES[template_id]
        self.is_boss = self.template.get("is_boss", False)
        self.w = 34 if self.is_boss else 22
        self.h = 42 if self.is_boss else 28
        self.hitbox_w = 24 if self.is_boss else 16
        self.hitbox_h = 14 if self.is_boss else 10

        self.state = "WANDER"  # WANDER, ALERT, CHASE
        self.is_tutorial_dummy = self.template.get("is_tutorial_dummy", False)
        self.speed_wander = 0.0 if self.is_tutorial_dummy else (22.0 if self.is_boss else 38.0)
        self.speed_chase = 0.0 if self.is_tutorial_dummy else (66.0 if self.is_boss else 74.0)

        self.move_dir = [0.0, 0.0]
        self.move_timer = random.uniform(0.5, 2.0)
        self.pause_timer = 0.0

        self.alert_timer = 0.0
        self.anim_timer = 0.0
        self.anim_frame = 0

    @property
    def hitbox(self):
        return pygame.Rect(
            int(self.x + (self.w - self.hitbox_w) / 2),
            int(self.y + self.h - self.hitbox_h - 1),
            self.hitbox_w,
            self.hitbox_h,
        )

    def update(self, dt, player_center, solid_rects, is_void_func=None):
        self.depth_y = self.y + self.h
        self.anim_timer += dt
        if self.anim_timer >= 0.16:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 4

        pcx, pcy = player_center
        my_cx = self.x + self.w / 2
        my_cy = self.y + self.h / 2
        dist_to_player = math.hypot(pcx - my_cx, pcy - my_cy)

        # Transición de estados de IA
        if self.state == "WANDER":
            if dist_to_player < 78:
                self.state = "ALERT"
                self.alert_timer = 0.38
                self.move_dir = [0.0, 0.0]
        elif self.state == "ALERT":
            self.alert_timer -= dt
            if self.alert_timer <= 0:
                self.state = "CHASE"
        elif self.state == "CHASE":
            if dist_to_player > 145:
                self.state = "WANDER"
                self.move_timer = random.uniform(1.0, 2.2)

        # Movimiento
        dx, dy = 0.0, 0.0
        if self.state == "CHASE":
            if dist_to_player > 2:
                dx = (pcx - my_cx) / dist_to_player * self.speed_chase * dt
                dy = (pcy - my_cy) / dist_to_player * self.speed_chase * dt
        elif self.state == "WANDER":
            if self.pause_timer > 0:
                self.pause_timer -= dt
            else:
                self.move_timer -= dt
                if self.move_timer <= 0:
                    if random.random() < 0.35:
                        self.pause_timer = random.uniform(0.6, 1.4)
                        self.move_dir = [0.0, 0.0]
                    else:
                        angle = random.uniform(0, 2 * math.pi)
                        self.move_dir = [math.cos(angle), math.sin(angle)]
                        self.move_timer = random.uniform(1.2, 2.8)
                dx = self.move_dir[0] * self.speed_wander * dt
                dy = self.move_dir[1] * self.speed_wander * dt

        if dx != 0 or dy != 0:
            old_x = self.x
            self.x += dx
            rx = self.hitbox
            col_x = any(rx.colliderect(s) for s in solid_rects)
            if col_x or (is_void_func and is_void_func(self.hitbox.centerx, self.hitbox.bottom - 2)):
                self.x = old_x
                if self.state == "WANDER":
                    self.move_dir[0] *= -1

            old_y = self.y
            self.y += dy
            ry = self.hitbox
            col_y = any(ry.colliderect(s) for s in solid_rects)
            if col_y or (is_void_func and is_void_func(self.hitbox.centerx, self.hitbox.bottom - 2)):
                self.y = old_y
                if self.state == "WANDER":
                    self.move_dir[1] *= -1

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        shadow = pygame.Surface((16, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 95), (0, 0, 16, 6))
        surface.blit(shadow, (cx + (self.w - 16) // 2, cy + self.h - 5))

        bob = int(math.sin(self.anim_frame * math.pi / 2) * 2)
        if self.template_id == "sombra":
            self._draw_sombra_overworld(surface, cx, cy + bob)
        elif self.template_id == "rudinn":
            self._draw_rudinn_overworld(surface, cx, cy + bob)
        elif self.template_id == "fantasmino":
            self._draw_fantasmino_overworld(surface, cx, cy + bob)
        elif self.template_id == "sectario":
            self._draw_sectario_overworld(surface, cx, cy + bob)
        elif self.template_id == "sepulturero":
            self._draw_sepulturero_overworld(surface, cx, cy + bob)
        elif self.template_id == "arconte":
            self._draw_arconte_overworld(surface, cx, cy + bob)
        elif self.template_id == "bufon_caos":
            self._draw_bufon_caos_overworld(surface, cx, cy + bob)
        elif self.template_id == "centinela_neon":
            self._draw_centinela_neon_overworld(surface, cx, cy + bob)
        elif self.template_id == "nyxar":
            self._draw_nyxar_overworld(surface, cx, cy + bob)
        elif self.template_id in ("maniqui_esquiva", "maniqui_parry", "maniqui_dash"):
            self._draw_tutorial_dummy_overworld(surface, cx, cy + bob)

        # Burbuja de exclamación [!] estilo Deltarune
        if self.state == "ALERT" or (self.state == "CHASE" and self.alert_timer > -0.3):
            self._draw_alert_bubble(surface, cx + self.w // 2, cy - 8)

    def _draw_alert_bubble(self, surface, bx, by):
        pygame.draw.circle(surface, (255, 50, 50), (bx, by), 7)
        pygame.draw.circle(surface, (255, 255, 255), (bx, by), 7, 1)
        pygame.draw.line(surface, (255, 255, 255), (bx, by - 4), (bx, by + 1), 2)
        pygame.draw.circle(surface, (255, 255, 255), (bx, by + 3), 1)

    def _draw_mini_unseen_hand(self, surface, sx, sy, ex, ey, aura=(185, 55, 245)):
        """Dibuja una Mano Invisible compacta estilo Re:Zero (Autoridad de la Pereza) en el mapa."""
        mx = int((sx + ex) / 2 + (ey - sy) * 0.25)
        my = int((sy + ey) / 2 - (ex - sx) * 0.25)
        pygame.draw.lines(surface, aura, False, [(sx, sy), (mx, my), (ex, ey)], 3)
        pygame.draw.lines(surface, (12, 5, 20), False, [(sx, sy), (mx, my), (ex, ey)], 1)
        pygame.draw.circle(surface, aura, (ex, ey), 3)
        pygame.draw.circle(surface, (12, 5, 20), (ex, ey), 2)
        for dx, dy in [(-2, -3), (0, -3), (2, -2)]:
            pygame.draw.line(surface, aura, (ex, ey), (ex + dx, ey + dy), 1)

    def _draw_sombra_overworld(self, surface, cx, cy):
        """Dibuja al Acechador de la Gula (Secuaz vendado del Culto de la Bruja con dagas sombrías)."""
        t = pygame.time.get_ticks() * 0.005 + self.x * 0.05
        # Sello miasmático en el suelo
        aura = pygame.Surface((24, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (125, 35, 195, 80), (0, 1, 24, 8))
        surface.blit(aura, (cx - 1, cy + 20))
        # Túnica negra desgarrada del Culto con ribete púrpura-vino
        sway = int(math.sin(t) * 1.5)
        robe = [(cx + 5, cy + 8), (cx + 17, cy + 8), (cx + 21 + sway, cy + 25), (cx + 11, cy + 23), (cx + 1 + sway, cy + 25)]
        pygame.draw.polygon(surface, (20, 10, 28), robe)
        pygame.draw.polygon(surface, (165, 55, 235), robe, 1)
        # Bufanda de vendas grises cubriendo cuello y boca
        pygame.draw.rect(surface, (215, 210, 224), (cx + 6, cy + 8, 10, 4), border_radius=1)
        pygame.draw.line(surface, (135, 125, 150), (cx + 6, cy + 10), (cx + 16, cy + 10), 1)
        # Capucha puntiaguda profunda y ojos rasgados ámbar/violeta
        hood = [(cx + 11, cy - 2), (cx + 18, cy + 5), (cx + 16, cy + 10), (cx + 6, cy + 10), (cx + 4, cy + 5)]
        pygame.draw.polygon(surface, (16, 8, 24), hood)
        pygame.draw.polygon(surface, (185, 70, 245), hood, 1)
        pygame.draw.circle(surface, (6, 3, 10), (cx + 11, cy + 6), 4)
        pygame.draw.rect(surface, (245, 175, 255), (cx + 8, cy + 5, 2, 2))
        pygame.draw.rect(surface, (245, 175, 255), (cx + 12, cy + 5, 2, 2))
        # Dagas gemelas oscuras
        pygame.draw.line(surface, (215, 75, 245), (cx + 3, cy + 15), (cx - 2, cy + 20), 2)
        pygame.draw.line(surface, (215, 75, 245), (cx + 19, cy + 15), (cx + 24, cy + 20), 2)

    def _draw_rudinn_overworld(self, surface, cx, cy):
        """Dibuja al Heraldo de la Codicia (Secuaz aristocrático inspirado en Regulus Corneas)."""
        t = pygame.time.get_ticks() * 0.004 + self.y * 0.03
        # Anillo sutil dorado-violeta en el suelo
        aura = pygame.Surface((24, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (230, 200, 105, 80), (1, 1, 22, 8), 1)
        surface.blit(aura, (cx - 1, cy + 21))
        # Cristales/estrellas detenidas orbitando detrás
        for side in (-1, 1):
            ox = cx + 11 + int(side * 10)
            oy = cy + 9 + int(math.sin(t + side) * 2)
            pygame.draw.polygon(surface, (235, 245, 255), [(ox, oy - 4), (ox + 2, oy), (ox, oy + 4), (ox - 2, oy)])
            pygame.draw.polygon(surface, (230, 195, 85), [(ox, oy - 4), (ox + 2, oy), (ox, oy + 4), (ox - 2, oy)], 1)
        # Abrigo ceremonial blanco marfil con solapas negras y ribete dorado
        coat = [(cx + 5, cy + 8), (cx + 17, cy + 8), (cx + 19, cy + 25), (cx + 3, cy + 25)]
        pygame.draw.polygon(surface, (238, 236, 246), coat)
        pygame.draw.polygon(surface, (36, 22, 54), [(cx + 9, cy + 9), (cx + 13, cy + 9), (cx + 13, cy + 24), (cx + 9, cy + 24)])
        pygame.draw.polygon(surface, (215, 185, 85), coat, 1)
        # Cabeza con cabello plateado y máscara de porcelana agrietada
        pygame.draw.circle(surface, (245, 242, 252), (cx + 11, cy + 5), 5)
        pygame.draw.circle(surface, (42, 34, 58), (cx + 11, cy + 5), 5, 1)
        pygame.draw.rect(surface, (115, 195, 255), (cx + 8, cy + 4, 2, 2))
        pygame.draw.rect(surface, (115, 195, 255), (cx + 12, cy + 4, 2, 2))
        # Estoque ceremonial dorado
        pygame.draw.line(surface, (230, 245, 255), (cx + 18, cy + 16), (cx + 23, cy + 5), 2)
        pygame.draw.circle(surface, (240, 205, 85), (cx + 18, cy + 16), 2)

    def _draw_fantasmino_overworld(self, surface, cx, cy):
        """Dibuja al Lamento de la Ira (Espectro vendado inspirado en Sirius con cadenas ardientes)."""
        t = pygame.time.get_ticks() * 0.006 + self.x * 0.04
        # Túnica espectral oscura con vendas flotantes
        robe = [(cx + 6, cy + 8), (cx + 16, cy + 8), (cx + 19, cy + 24), (cx + 11, cy + 21), (cx + 3, cy + 24)]
        pygame.draw.polygon(surface, (32, 16, 42), robe)
        pygame.draw.polygon(surface, (235, 95, 130), robe, 1)
        # Vendas blancas largas ondeando
        w_off = int(math.sin(t) * 3)
        pygame.draw.line(surface, (235, 228, 236), (cx + 6, cy + 10), (cx - 1, cy + 16 + w_off), 2)
        pygame.draw.line(surface, (235, 228, 236), (cx + 16, cy + 10), (cx + 23, cy + 16 - w_off), 2)
        # Cabeza vendada con un solo ojo ardiente en llamas ámbar-carmesí
        pygame.draw.circle(surface, (236, 228, 234), (cx + 11, cy + 5), 5)
        pygame.draw.line(surface, (165, 150, 168), (cx + 7, cy + 4), (cx + 15, cy + 6), 1)
        pygame.draw.line(surface, (165, 150, 168), (cx + 7, cy + 7), (cx + 14, cy + 3), 1)
        pygame.draw.circle(surface, (255, 75, 95), (cx + 12, cy + 5), 2)
        pygame.draw.circle(surface, (255, 235, 110), (cx + 12, cy + 5), 1)
        # Cadenas con incensarios en llamas a los lados
        for side in (-1, 1):
            fx = cx + 11 + side * 10
            fy = cy + 18 + int(math.sin(t * 1.4 + side) * 2)
            pygame.draw.line(surface, (110, 105, 125), (cx + 11 + side * 5, cy + 12), (fx, fy), 1)
            pygame.draw.circle(surface, (255, 120, 60), (fx, fy), 3)
            pygame.draw.circle(surface, (255, 235, 130), (fx, fy), 1)

    def _draw_sectario_overworld(self, surface, cx, cy):
        """Dibuja al Dedo de la Pereza (Cultista de la Bruja con Manos Invisibles y Evangelio Negro)."""
        t = pygame.time.get_ticks() * 0.005 + self.x * 0.03
        # Manos Invisibles retorciéndose detrás del cultista
        w1 = int(math.sin(t * 1.5) * 3)
        w2 = int(math.cos(t * 1.3) * 3)
        self._draw_mini_unseen_hand(surface, cx + 6, cy + 11, cx - 4, cy + 4 + w1, aura=(185, 55, 245))
        self._draw_mini_unseen_hand(surface, cx + 16, cy + 11, cx + 26, cy + 5 + w2, aura=(185, 55, 245))

        # Túnica negra clásica del Culto de la Bruja con ribetes púrpura y oro
        robe_pts = [(cx + 5, cy + 8), (cx + 17, cy + 8), (cx + 21, cy + 26), (cx + 1, cy + 26)]
        pygame.draw.polygon(surface, (18, 10, 26), robe_pts)
        pygame.draw.polygon(surface, (185, 55, 240), robe_pts, 1)
        # Estola púrpura y dorada con el sello del Culto
        pygame.draw.line(surface, (135, 35, 185), (cx + 11, cy + 10), (cx + 11, cy + 25), 3)
        pygame.draw.line(surface, (235, 200, 95), (cx + 11, cy + 10), (cx + 11, cy + 25), 1)
        # Capucha gótica puntiaguda profunda con ojos verdes/violeta maniáticos
        hood_pts = [(cx + 11, cy - 3), (cx + 18, cy + 5), (cx + 17, cy + 11), (cx + 5, cy + 11), (cx + 4, cy + 5)]
        pygame.draw.polygon(surface, (14, 7, 22), hood_pts)
        pygame.draw.polygon(surface, (205, 70, 250), hood_pts, 1)
        pygame.draw.circle(surface, (6, 2, 10), (cx + 11, cy + 7), 4)
        pygame.draw.rect(surface, (125, 255, 130), (cx + 8, cy + 6, 2, 2))
        pygame.draw.rect(surface, (125, 255, 130), (cx + 12, cy + 5, 2, 3))
        # Pequeño Evangelio Negro flotando a la izquierda
        pygame.draw.rect(surface, (28, 12, 42), (cx - 3, cy + 14 + w1 // 2, 5, 6))
        pygame.draw.rect(surface, (225, 195, 90), (cx - 3, cy + 14 + w1 // 2, 5, 6), 1)

    def _draw_sepulturero_overworld(self, surface, cx, cy):
        """Dibuja al Jefe Morvath el Sepulturero (Arzobispo del Osario con Manos Invisibles y Farol)."""
        t = pygame.time.get_ticks() * 0.0045
        # Sello ritual del Culto en el suelo
        aura = pygame.Surface((48, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (150, 30, 195, 95), (0, 0, 48, 18))
        pygame.draw.ellipse(aura, (245, 85, 155, 170), (2, 2, 44, 14), 1)
        surface.blit(aura, (cx - 7, cy + 27))

        # 2 Manos Invisibles monumentales brotando detrás de su espalda
        w1 = int(math.sin(t * 1.4) * 4)
        self._draw_mini_unseen_hand(surface, cx + 7, cy + 14, cx - 8, cy + 4 + w1, aura=(205, 55, 250))
        self._draw_mini_unseen_hand(surface, cx + 27, cy + 14, cx + 42, cy + 5 - w1, aura=(205, 55, 250))

        # Manto arzobispal negro con capas púrpura y borde carmesí/dorado
        cloak_pts = [(cx + 7, cy + 10), (cx + 27, cy + 10), (cx + 33, cy + 39), (cx + 17, cy + 41), (cx + 1, cy + 39)]
        pygame.draw.polygon(surface, (18, 10, 28), cloak_pts)
        pygame.draw.polygon(surface, (195, 50, 145), cloak_pts, 1)
        pygame.draw.rect(surface, (95, 22, 135), (cx + 14, cy + 12, 6, 26))
        pygame.draw.line(surface, (235, 200, 95), (cx + 17, cy + 12), (cx + 17, cy + 38), 1)

        # Hombreras góticas de hueso/hierro
        pygame.draw.ellipse(surface, (74, 72, 92), (cx + 2, cy + 10, 12, 7))
        pygame.draw.ellipse(surface, (74, 72, 92), (cx + 20, cy + 10, 12, 7))

        # Capucha catedralicia y corona de espinas dorada
        hood = [(cx + 17, cy - 3), (cx + 26, cy + 6), (cx + 24, cy + 13), (cx + 10, cy + 13), (cx + 8, cy + 6)]
        pygame.draw.polygon(surface, (14, 7, 22), hood)
        pygame.draw.polygon(surface, (215, 70, 165), hood, 1)
        pygame.draw.polygon(surface, (225, 195, 95), [(cx + 11, cy + 3), (cx + 13, cy - 4), (cx + 17, cy + 1), (cx + 21, cy - 4), (cx + 23, cy + 3)])
        # Ojos ardientes ámbar-violeta
        pygame.draw.rect(surface, (255, 230, 80), (cx + 13, cy + 7, 3, 3))
        pygame.draw.rect(surface, (255, 230, 80), (cx + 19, cy + 7, 3, 3))

        # Guadaña-Pala ritual con filo brillante apuntando hacia afuera (sin tapar la corona)
        pygame.draw.line(surface, (118, 86, 62), (cx + 3, cy + 38), (cx + 3, cy + 1), 2)
        pygame.draw.polygon(surface, (215, 225, 245), [(cx + 3, cy + 1), (cx - 9, cy + 4), (cx - 1, cy + 10)])
        pygame.draw.polygon(surface, (215, 65, 145), [(cx + 3, cy + 1), (cx - 9, cy + 4), (cx - 1, cy + 10)], 1)

        # Incensario / Farol de Almas encadenado a la derecha
        pygame.draw.line(surface, (110, 105, 130), (cx + 29, cy + 14), (cx + 33, cy + 21), 1)
        pygame.draw.rect(surface, (36, 30, 50), (cx + 30, cy + 20, 7, 9), border_radius=1)
        pygame.draw.circle(surface, (135, 245, 255), (cx + 33, cy + 24), 3)

    def _draw_arconte_overworld(self, surface, cx, cy):
        """Dibuja al Jefe Supremo Vaelkor (Soberano de las Sombras de la Bruja y Cristal Negro)."""
        t = pygame.time.get_ticks() * 0.005
        # Aura de Fuego Oscuro y Miasma con borde negro
        aura = pygame.Surface((50, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (0, 0, 0, 210), (0, 1, 50, 18))
        pygame.draw.ellipse(aura, (220, 30, 115, 165), (2, 3, 46, 14))
        pygame.draw.ellipse(aura, (25, 4, 42, 225), (6, 5, 38, 10))
        surface.blit(aura, (cx - 8, cy + 27))

        # 4 Manos de Sombra de la Bruja desplegadas tras su espalda
        w1 = int(math.sin(t * 1.6) * 4)
        self._draw_mini_unseen_hand(surface, cx + 7, cy + 11, cx - 10, cy + 1 + w1, aura=(235, 40, 125))
        self._draw_mini_unseen_hand(surface, cx + 27, cy + 11, cx + 44, cy + 1 - w1, aura=(235, 40, 125))
        self._draw_mini_unseen_hand(surface, cx + 8, cy + 21, cx - 7, cy + 19 - w1, aura=(185, 45, 245))
        self._draw_mini_unseen_hand(surface, cx + 26, cy + 21, cx + 41, cy + 19 + w1, aura=(185, 45, 245))

        # Esquirlas de cristal negro flotando
        for ox, oy in [(-4, 6), (31, 6)]:
            shard = [(cx + ox + 4, cy + oy - 5), (cx + ox + 8, cy + oy + 2), (cx + ox + 4, cy + oy + 8), (cx + ox, cy + oy + 2)]
            pygame.draw.polygon(surface, (235, 40, 105), shard)
            pygame.draw.polygon(surface, (0, 0, 0), shard, 2)

        # Manto imperial de obsidiana de la Bruja
        cloak_pts = [(cx + 7, cy + 9), (cx + 27, cy + 9), (cx + 34, cy + 40), (cx + 17, cy + 43), (cx, cy + 40)]
        pygame.draw.polygon(surface, (14, 5, 24), cloak_pts)
        pygame.draw.polygon(surface, (240, 42, 110), cloak_pts, 2)
        pygame.draw.polygon(surface, (0, 0, 0), cloak_pts, 1)

        # Halo de Eclipse tras la corona y cabeza sombría
        pygame.draw.circle(surface, (235, 45, 115), (cx + 17, cy + 5), 11, 1)
        pygame.draw.circle(surface, (10, 4, 16), (cx + 17, cy + 7), 8)
        crown = [(cx + 8, cy + 3), (cx + 10, cy - 6), (cx + 14, cy), (cx + 17, cy - 9), (cx + 20, cy), (cx + 24, cy - 6), (cx + 26, cy + 3)]
        pygame.draw.polygon(surface, (240, 35, 95), crown)
        pygame.draw.polygon(surface, (0, 0, 0), crown, 1)

        for ex, ey in [(cx + 12, cy + 5), (cx + 20, cy + 5), (cx + 13, cy + 8), (cx + 19, cy + 8)]:
            pygame.draw.rect(surface, (255, 70, 130), (ex, ey, 2, 2))

        # Mandoble de Fuego Oscuro y Cristal
        blade = [(cx + 32, cy - 6), (cx + 37, cy + 8), (cx + 32, cy + 35), (cx + 28, cy + 8)]
        pygame.draw.polygon(surface, (28, 5, 44), blade)
        pygame.draw.polygon(surface, (245, 45, 110), blade, 1)
        pygame.draw.polygon(surface, (0, 0, 0), blade, 2)

    def _draw_bufon_caos_overworld(self, surface, cx, cy):
        """Dibuja a Jevix, Bufón del Caos en el mapa del Dark World."""
        pygame.draw.rect(surface, (55, 25, 95), (cx + 4, cy + 10, 14, 14), border_radius=3)
        pygame.draw.rect(surface, (255, 225, 75), (cx + 4, cy + 10, 14, 14), 1, border_radius=3)
        pygame.draw.circle(surface, (215, 195, 245), (cx + 11, cy + 8), 6)
        pygame.draw.rect(surface, (255, 235, 70), (cx + 8, cy + 6, 2, 2))
        pygame.draw.rect(surface, (255, 235, 70), (cx + 12, cy + 6, 2, 2))
        pygame.draw.polygon(surface, (140, 40, 220), [(cx + 5, cy + 4), (cx + 1, cy - 3), (cx + 11, cy + 3)])
        pygame.draw.polygon(surface, (255, 70, 190), [(cx + 17, cy + 4), (cx + 21, cy - 3), (cx + 11, cy + 3)])
        pygame.draw.circle(surface, (255, 235, 80), (cx + 1, cy - 3), 2)
        pygame.draw.circle(surface, (255, 235, 80), (cx + 21, cy - 3), 2)

    def _draw_centinela_neon_overworld(self, surface, cx, cy):
        """Dibuja al Viro-Centinela Neón en el mapa del Dark World."""
        pygame.draw.polygon(surface, (60, 245, 255), [(cx + 4, cy + 8), (cx - 2, cy + 3), (cx + 2, cy + 18)], 1)
        pygame.draw.polygon(surface, (255, 75, 215), [(cx + 18, cy + 8), (cx + 24, cy + 3), (cx + 20, cy + 18)], 1)
        pygame.draw.rect(surface, (22, 18, 44), (cx + 5, cy + 5, 12, 18), border_radius=3)
        pygame.draw.rect(surface, (75, 245, 255), (cx + 5, cy + 5, 12, 18), 1, border_radius=3)
        pygame.draw.rect(surface, (255, 80, 215), (cx + 7, cy + 8, 8, 4), border_radius=1)

    def _draw_nyxar_overworld(self, surface, cx, cy):
        """Dibuja a Nyxar, Jefe del Trono Oscuro, flotando con alas neón y corona quebrada."""
        t = pygame.time.get_ticks() * 0.005
        # Sello neón de la Fuente Oscura bajo sus pies
        aura = pygame.Surface((40, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (75, 245, 255, 95), (2, 2, 36, 10))
        pygame.draw.ellipse(aura, (255, 75, 215, 200), (4, 3, 32, 8), 1)
        surface.blit(aura, (cx - 3, cy + 32))
        # Alas holográficas cian y magenta
        flap = int(math.sin(t * 2.6) * 3)
        pygame.draw.polygon(surface, (26, 12, 52), [(cx + 8, cy + 14), (cx - 8, cy + 4 + flap), (cx - 4, cy + 28 - flap), (cx + 9, cy + 24)])
        pygame.draw.polygon(surface, (75, 245, 255), [(cx + 8, cy + 14), (cx - 8, cy + 4 + flap), (cx - 4, cy + 28 - flap), (cx + 9, cy + 24)], 1)
        pygame.draw.polygon(surface, (26, 12, 52), [(cx + 26, cy + 14), (cx + 42, cy + 4 + flap), (cx + 38, cy + 28 - flap), (cx + 25, cy + 24)])
        pygame.draw.polygon(surface, (255, 75, 215), [(cx + 26, cy + 14), (cx + 42, cy + 4 + flap), (cx + 38, cy + 28 - flap), (cx + 25, cy + 24)], 1)
        # Manto real del Dark World y núcleo Delta dorado
        robe = [(cx + 9, cy + 10), (cx + 25, cy + 10), (cx + 29, cy + 36), (cx + 17, cy + 33), (cx + 5, cy + 36)]
        pygame.draw.polygon(surface, (16, 10, 34), robe)
        pygame.draw.polygon(surface, (85, 245, 255), robe, 1)
        pygame.draw.polygon(surface, (255, 232, 85), [(cx + 17, cy + 16), (cx + 21, cy + 22), (cx + 17, cy + 27), (cx + 13, cy + 22)])
        # Cabeza oscura, visor asimétrico y corona flotante
        pygame.draw.circle(surface, (10, 6, 22), (cx + 17, cy + 6), 7)
        pygame.draw.circle(surface, (255, 75, 215), (cx + 17, cy + 6), 7, 1)
        pygame.draw.rect(surface, (80, 245, 255), (cx + 13, cy + 5, 3, 2))
        pygame.draw.rect(surface, (255, 235, 80), (cx + 18, cy + 5, 3, 2))
        crown = [(cx + 10, cy - 1), (cx + 12, cy - 8), (cx + 17, cy - 4), (cx + 22, cy - 8), (cx + 24, cy - 1)]
        pygame.draw.polygon(surface, (255, 230, 85), crown)
        pygame.draw.polygon(surface, (0, 0, 0), crown, 1)

    def _draw_tutorial_dummy_overworld(self, surface, cx, cy):
        """Dibuja a los 3 Instructores del Tutorial en sus pedestales de entrenamiento."""
        col = self.template.get("color", (120, 225, 255))
        # Pedestal y poste de madera/cristal
        pygame.draw.ellipse(surface, (35, 30, 52), (cx + 2, cy + 20, 18, 7))
        pygame.draw.ellipse(surface, col, (cx + 2, cy + 20, 18, 7), 1)
        pygame.draw.rect(surface, (110, 80, 50), (cx + 9, cy + 12, 4, 12))
        # Torso acorazado de entrenamiento
        pygame.draw.rect(surface, (42, 34, 64), (cx + 4, cy + 6, 14, 12), border_radius=3)
        pygame.draw.rect(surface, col, (cx + 4, cy + 6, 14, 12), 1, border_radius=3)
        # Cabeza con emblema luminoso
        pygame.draw.circle(surface, (235, 225, 200), (cx + 11, cy + 3), 5)
        pygame.draw.circle(surface, col, (cx + 11, cy + 3), 5, 1)
        pygame.draw.rect(surface, col, (cx + 8, cy + 2, 2, 2))
        pygame.draw.rect(surface, col, (cx + 12, cy + 2, 2, 2))



# 4. RENDERIZADOR DE SPRITES DE BATALLA RETRO PROCEDURAL
class DeltaruneEnemyRenderer:
    """Genera y anima los sprites de combate de los enemigos en pantalla."""
    @staticmethod
    def draw_enemy(surface, template_id, x, y, anim_time, hit_flash=0.0, mercy=0):
        bob = int(math.sin(anim_time * 3.5) * 3)
        shake_x = int(math.sin(hit_flash * 40.0) * 4) if hit_flash > 0 else 0
        ex = x + shake_x
        ey = y + bob

        if template_id == "sombra":
            DeltaruneEnemyRenderer._draw_sombra(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "rudinn":
            DeltaruneEnemyRenderer._draw_rudinn(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "fantasmino":
            DeltaruneEnemyRenderer._draw_fantasmino(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "sectario":
            DeltaruneEnemyRenderer._draw_sectario(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "sepulturero":
            DeltaruneEnemyRenderer._draw_sepulturero(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "arconte":
            DeltaruneEnemyRenderer._draw_arconte(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "bufon_caos":
            DeltaruneEnemyRenderer._draw_bufon_caos(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "centinela_neon":
            DeltaruneEnemyRenderer._draw_centinela_neon(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id == "nyxar":
            DeltaruneEnemyRenderer._draw_nyxar(surface, ex, ey, anim_time, hit_flash, mercy)
        elif template_id in ("maniqui_esquiva", "maniqui_parry", "maniqui_dash"):
            DeltaruneEnemyRenderer._draw_tutorial_dummy(surface, template_id, ex, ey, anim_time, hit_flash, mercy)

    @staticmethod
    def _draw_unseen_hand(surface, sx, sy, mx, my, ex, ey, aura_col=(185, 50, 245), core_col=(10, 4, 18), thick=5):
        """Dibuja una Mano Invisible articulada estilo Re:Zero (Autoridad de la Pereza / Bruja de la Envidia)."""
        pts = [(int(sx), int(sy)), (int(mx), int(my)), (int(ex), int(ey))]
        # Halo espectral de miasma violeta-oscuro
        pygame.draw.lines(surface, aura_col, False, pts, thick + 3)
        pygame.draw.lines(surface, (0, 0, 0), False, pts, thick + 1)
        pygame.draw.lines(surface, core_col, False, pts, max(2, thick - 1))
        # Palma de sombra articulada
        hx, hy = int(ex), int(ey)
        ang = math.atan2(ey - my, ex - mx)
        pygame.draw.circle(surface, aura_col, (hx, hy), 6)
        pygame.draw.circle(surface, core_col, (hx, hy), 4)
        # 4 dedos largos en garra
        for f_off in (-0.65, -0.22, 0.22, 0.65):
            fa = ang + f_off
            fx1 = hx + math.cos(fa) * 5
            fy1 = hy + math.sin(fa) * 5
            fx2 = hx + math.cos(fa + f_off * 0.25) * 10
            fy2 = hy + math.sin(fa + f_off * 0.25) * 10
            pygame.draw.line(surface, aura_col, (hx, hy), (int(fx2), int(fy2)), 3)
            pygame.draw.line(surface, core_col, (hx, hy), (int(fx1), int(fy1)), 1)
            pygame.draw.line(surface, (240, 175, 255), (int(fx1), int(fy1)), (int(fx2), int(fy2)), 1)

    @staticmethod
    def _draw_witch_gospel(surface, gx, gy, t, trim_col=(195, 65, 245)):
        """Dibuja el Evangelio Negro abierto del Culto de la Bruja flotando con escritura arcana."""
        bx, by = int(gx), int(gy)
        # Halo de miasma tras el Evangelio
        halo = pygame.Surface((32, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(halo, (*trim_col, 55), (2, 4, 28, 20))
        surface.blit(halo, (bx - 16, by - 12))
        # Tapas de cuero negro con borde dorado/violeta
        pygame.draw.polygon(surface, (18, 8, 28), [(bx - 11, by - 1), (bx, by + 3), (bx + 11, by - 1), (bx + 10, by + 8), (bx, by + 11), (bx - 10, by + 8)])
        pygame.draw.polygon(surface, (235, 198, 95), [(bx - 11, by - 1), (bx, by + 3), (bx + 11, by - 1), (bx + 10, by + 8), (bx, by + 11), (bx - 10, by + 8)], 1)
        # Páginas abiertas con runas ilegibles brillantes
        pygame.draw.polygon(surface, (238, 228, 210), [(bx - 9, by - 3), (bx, by + 1), (bx + 9, by - 3), (bx + 8, by + 5), (bx, by + 8), (bx - 8, by + 5)])
        pygame.draw.line(surface, (95, 40, 120), (bx, by + 1), (bx, by + 8), 1)
        pygame.draw.line(surface, trim_col, (bx - 7, by), (bx - 2, by + 2), 1)
        pygame.draw.line(surface, trim_col, (bx + 2, by + 2), (bx + 7, by), 1)
        pygame.draw.line(surface, (130, 35, 90), (bx - 6, by + 3), (bx - 2, by + 4), 1)
        pygame.draw.line(surface, (130, 35, 90), (bx + 2, by + 4), (bx + 6, by + 3), 1)
        # Sello flotante sobre el Evangelio
        orb_y = by - 9 + int(math.sin(t * 5.0) * 2)
        pygame.draw.circle(surface, trim_col, (bx, orb_y), 5, 1)
        pygame.draw.circle(surface, (255, 225, 115), (bx, orb_y), 2)

    @staticmethod
    def _draw_miasma_aura(surface, x, y, t, count=5, rx=24, col=(165, 45, 225)):
        """Dibuja volutas oscuras de Miasma de la Bruja flotando alrededor del enemigo."""
        for i in range(count):
            ang = t * 1.9 + i * (math.tau / count)
            mx = int(x + math.cos(ang) * rx)
            my = int(y + 10 - ((t * 18 + i * 11) % 36))
            r = 3 + (i % 2)
            ms = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ms, (12, 4, 22, 150), (r + 2, r + 2), r + 1)
            pygame.draw.circle(ms, (*col, 130), (r + 2, r + 2), r, 1)
            surface.blit(ms, (mx - r - 2, my - r - 2))

    @staticmethod
    def _draw_sombra(surface, x, y, t, flash, mercy):
        """Dibuja al Acechador de la Gula (Secuaz asesino del Culto de la Bruja con vendas, dagas y miasma)."""
        is_spared = (mercy >= 100)
        c_robe = (255, 255, 255) if flash > 0.05 else (20, 10, 30)
        c_inner = (255, 255, 255) if flash > 0.05 else (44, 18, 66)
        c_trim = (255, 235, 95) if is_spared else (175, 55, 240)

        # Sello brujeril y miasma bajo sus pies
        aura = pygame.Surface((56, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (120, 28, 185, 95), (2, 2, 52, 12))
        pygame.draw.ellipse(aura, (*c_trim, 190), (4, 3, 48, 10), 1)
        surface.blit(aura, (x - 28, y + 36))
        DeltaruneEnemyRenderer._draw_miasma_aura(surface, x, y + 6, t, count=5, rx=23, col=c_trim)

        # Dos garras sombrías de miasma brotando tras los hombros
        sw = math.sin(t * 4.2) * 5
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x - 12, y - 4, x - 26, y - 14 + sw, x - 34, y - 24 - sw, aura_col=c_trim, thick=3)
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x + 12, y - 4, x + 26, y - 14 - sw, x + 34, y - 24 + sw, aura_col=c_trim, thick=3)

        # Manto negro desgarrado en jirones ondulantes
        wave = int(math.sin(t * 4.6) * 3)
        cloak_pts = [
            (x - 15, y - 6), (x + 15, y - 6),
            (x + 23, y + 36 + wave), (x + 11, y + 43), (x + 4, y + 37 - wave),
            (x - 4, y + 44), (x - 13, y + 37 + wave), (x - 23, y + 36 - wave),
        ]
        pygame.draw.polygon(surface, c_robe, cloak_pts)
        pygame.draw.polygon(surface, c_trim, cloak_pts, 2)

        # Pechera cruzada con correas y estola púrpura
        pygame.draw.polygon(surface, c_inner, [(x - 9, y - 2), (x + 9, y - 2), (x + 12, y + 32), (x - 12, y + 32)])
        pygame.draw.line(surface, (225, 195, 95), (x - 8, y + 2), (x + 8, y + 18), 2)
        pygame.draw.line(surface, (225, 195, 95), (x + 8, y + 2), (x - 8, y + 18), 2)

        # Brazos vendados sosteniendo dagas rituales curvas afiladas con empuñadura dorada
        d_bob = int(math.sin(t * 5.0) * 3)
        for side in (-1, 1):
            ax = x + side * 18
            ay = y + 12 + (d_bob if side < 0 else -d_bob)
            pygame.draw.line(surface, c_robe, (x + side * 11, y), (ax, ay), 6)
            pygame.draw.line(surface, (220, 214, 230), (x + side * 13, y + 4), (ax, ay), 3)
            # Empuñadura y guarda dorada
            pygame.draw.circle(surface, (230, 195, 92), (ax, ay), 2)
            # Hoja curva ritual larga apuntando hacia afuera/abajo
            blade = [
                (ax + side * 1, ay - 2),
                (ax + side * 16, ay - 10),
                (ax + side * 19, ay - 4),
                (ax + side * 11, ay + 2),
                (ax + side * 1, ay + 2),
            ]
            pygame.draw.polygon(surface, (28, 14, 44), blade)
            pygame.draw.polygon(surface, c_trim, blade, 1)
            pygame.draw.line(surface, (245, 218, 255), (ax + side * 3, ay - 2), (ax + side * 16, ay - 8), 1)

        # Capucha puntiaguda profunda del Culto y rostro vendado
        hood = [(x, y - 34), (x + 17, y - 16), (x + 15, y - 1), (x - 15, y - 1), (x - 17, y - 16)]
        pygame.draw.polygon(surface, c_robe, hood)
        pygame.draw.polygon(surface, c_trim, hood, 2)
        pygame.draw.circle(surface, (8, 4, 14), (x, y - 12), 11)

        # Bufanda/vendas oscurecidas cubriendo el rostro inferior con extremo colgante
        pygame.draw.polygon(surface, (198, 190, 212), [(x - 10, y - 10), (x + 10, y - 10), (x + 9, y - 2), (x - 9, y - 2)])
        pygame.draw.line(surface, (120, 108, 140), (x - 9, y - 7), (x + 9, y - 5), 1)
        pygame.draw.line(surface, (120, 108, 140), (x - 9, y - 4), (x + 9, y - 6), 1)
        # Ojos rasgados y chispeantes en la penumbra
        eye_col = (255, 240, 110) if is_spared else (235, 115, 255)
        pygame.draw.polygon(surface, eye_col, [(x - 8, y - 16), (x - 2, y - 13), (x - 7, y - 12)])
        pygame.draw.polygon(surface, eye_col, [(x + 8, y - 16), (x + 2, y - 13), (x + 7, y - 12)])
        pygame.draw.circle(surface, (255, 255, 255), (x - 5, y - 14), 1)
        pygame.draw.circle(surface, (255, 255, 255), (x + 5, y - 14), 1)

    @staticmethod
    def _draw_rudinn(surface, x, y, t, flash, mercy):
        """Dibuja al Heraldo de la Codicia (Inspirado en Regulus Corneas: abrigo blanco/oro y lanzas detenidas)."""
        is_spared = (mercy >= 100)
        c_coat = (255, 255, 255) if flash > 0.05 else (238, 236, 248)
        c_dark = (255, 255, 255) if flash > 0.05 else (24, 16, 38)
        c_gold = (255, 235, 95) if is_spared else (232, 198, 92)
        c_aura = (130, 215, 255) if not is_spared else (255, 235, 110)

        # Sello geométrico dorado inmaculado bajo sus pies
        pygame.draw.ellipse(surface, (24, 18, 42), (x - 24, y + 38, 48, 12))
        pygame.draw.ellipse(surface, c_gold, (x - 22, y + 39, 44, 10), 1)

        # Halo temporal detenido detrás de la espalda con 4 lanzas de cristal blanco-dorado
        pygame.draw.circle(surface, c_aura, (x, y - 4), 26, 1)
        for i in range(4):
            ang = t * 1.4 + i * (math.pi / 2.0) + 0.4
            lx = int(x + math.cos(ang) * 29)
            ly = int(y - 4 + math.sin(ang) * 20)
            shard = [(lx, ly - 9), (lx + 4, ly), (lx, ly + 9), (lx - 4, ly)]
            pygame.draw.polygon(surface, (235, 248, 255), shard)
            pygame.draw.polygon(surface, c_gold, shard, 1)

        # Capa interior púrpura real del Culto
        pygame.draw.polygon(surface, (62, 22, 94), [(x - 16, y - 6), (x + 16, y - 6), (x + 24, y + 38), (x - 24, y + 38)])

        # Abrigo ceremonial largo blanco marfil con solapas altas y ribete dorado
        coat_l = [(x - 15, y - 8), (x - 3, y - 6), (x - 5, y + 40), (x - 20, y + 37)]
        coat_r = [(x + 15, y - 8), (x + 3, y - 6), (x + 5, y + 40), (x + 20, y + 37)]
        pygame.draw.rect(surface, c_dark, (x - 8, y - 6, 16, 42))
        pygame.draw.polygon(surface, c_coat, coat_l)
        pygame.draw.polygon(surface, c_coat, coat_r)
        pygame.draw.polygon(surface, (42, 34, 58), coat_l, 1)
        pygame.draw.polygon(surface, (42, 34, 58), coat_r, 1)
        # Bordados dorados y cuello alto aristocrático
        pygame.draw.line(surface, c_gold, (x - 4, y - 4), (x - 6, y + 38), 2)
        pygame.draw.line(surface, c_gold, (x + 4, y - 4), (x + 6, y + 38), 2)
        pygame.draw.polygon(surface, c_coat, [(x - 14, y - 7), (x - 18, y - 18), (x - 7, y - 10)])
        pygame.draw.polygon(surface, c_coat, [(x + 14, y - 7), (x + 18, y - 18), (x + 7, y - 10)])
        pygame.draw.line(surface, c_gold, (x - 18, y - 18), (x - 7, y - 10), 1)
        pygame.draw.line(surface, c_gold, (x + 18, y - 18), (x + 7, y - 10), 1)

        # Cabeza con cabello plateado impecable y máscara de porcelana blanca agrietada en oro
        pygame.draw.circle(surface, (238, 240, 250), (x, y - 20), 12)
        pygame.draw.circle(surface, (36, 30, 52), (x, y - 20), 12, 2)
        # Flequillo elegante plateado
        pygame.draw.polygon(surface, (212, 218, 236), [(x - 12, y - 22), (x - 5, y - 34), (x + 5, y - 34), (x + 12, y - 22), (x + 4, y - 25), (x - 2, y - 18), (x - 7, y - 25)])
        # Grieta dorada ceremonial y ojos gélidos
        pygame.draw.line(surface, c_gold, (x + 5, y - 27), (x + 2, y - 16), 1)
        pygame.draw.line(surface, c_gold, (x + 2, y - 16), (x + 6, y - 12), 1)
        pygame.draw.rect(surface, (22, 16, 36), (x - 8, y - 21, 5, 3))
        pygame.draw.rect(surface, (22, 16, 36), (x + 3, y - 21, 5, 3))
        pygame.draw.rect(surface, c_aura, (x - 6, y - 20, 2, 2))
        pygame.draw.rect(surface, c_aura, (x + 4, y - 20, 2, 2))

        # Estoque ceremonial con empuñadura dorada
        sword_ang = math.sin(t * 2.8) * 0.12 + (0.45 if is_spared else 0.0)
        sx, sy = x + 21, y + 14
        ex = sx + math.cos(sword_ang - 0.85) * 30
        ey = sy + math.sin(sword_ang - 0.85) * 30
        pygame.draw.line(surface, (235, 248, 255), (sx, sy), (ex, ey), 3)
        pygame.draw.line(surface, c_aura, (sx, sy), (ex, ey), 1)
        pygame.draw.circle(surface, c_gold, (int(sx), int(sy)), 5)
        pygame.draw.circle(surface, (255, 252, 225), (int(sx), int(sy)), 2)

    @staticmethod
    def _draw_fantasmino(surface, x, y, t, flash, mercy):
        """Dibuja al Lamento de la Ira (Inspirado en Sirius Romanée-Conti: vendas, ojo ardiente y cadenas en llamas)."""
        is_spared = (mercy >= 100)
        c_robe = (255, 255, 255) if flash > 0.05 else (34, 14, 46)
        c_band = (255, 255, 255) if flash > 0.05 else (238, 232, 240)
        c_flame = (255, 235, 95) if is_spared else (255, 85, 110)

        # Halo de brasas espectrales bajo sus pies
        aura = pygame.Surface((56, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (225, 65, 110, 85), (4, 2, 48, 12))
        surface.blit(aura, (x - 28, y + 36))

        # Cintas de vendas flotando con el viento detrás + chal oscuro rasgado
        for side in (-1, 1):
            w1 = int(math.sin(t * 4.5 + side) * 5)
            w2 = int(math.cos(t * 3.8 + side) * 5)
            pts_b = [(x + side * 9, y - 12), (x + side * 22, y - 8 + w1), (x + side * 34, y + 6 + w2)]
            pygame.draw.lines(surface, (150, 134, 162), False, pts_b, 5)
            pygame.draw.lines(surface, c_band, False, pts_b, 3)

        # Túnica fúnebre ondulante con pliegues y ribete carmesí-violeta
        wave = int(math.sin(t * 4.4) * 3)
        robe_pts = [
            (x - 15, y - 8), (x + 15, y - 8),
            (x + 22, y + 36 + wave), (x + 10, y + 43), (x, y + 36 - wave), (x - 10, y + 43), (x - 22, y + 36 - wave)
        ]
        pygame.draw.polygon(surface, c_robe, robe_pts)
        pygame.draw.polygon(surface, (58, 22, 74), [(x - 9, y - 4), (x + 9, y - 4), (x + 14, y + 34), (x - 14, y + 34)])
        pygame.draw.polygon(surface, c_flame, robe_pts, 2)

        # Vendas cruzadas abrazando el torso
        for vy in (y - 1, y + 7, y + 15):
            pygame.draw.line(surface, c_band, (x - 11, vy), (x + 11, vy + 4), 3)
            pygame.draw.line(surface, (155, 138, 166), (x - 11, vy + 2), (x + 11, vy + 6), 1)

        # Cadenas de hierro curvadas con dos incensarios en llamas balanceándose a ambos lados
        for side in (-1, 1):
            sw_x = int(math.sin(t * 4.8 + side) * 5)
            sw_y = int(math.cos(t * 4.8 + side) * 3)
            cx_f = x + side * 29 + sw_x
            cy_f = y + 17 + sw_y
            mid_x = x + side * 22 + sw_x // 2
            mid_y = y + 4 + sw_y // 2
            pygame.draw.lines(surface, (115, 110, 136), False, [(x + side * 13, y - 3), (mid_x, mid_y), (cx_f, cy_f - 6)], 2)
            # Incensario metálico
            pygame.draw.circle(surface, (42, 36, 56), (cx_f, cy_f), 6)
            pygame.draw.circle(surface, (232, 198, 95), (cx_f, cy_f), 6, 1)
            # Llama ardiente brotando del incensario
            fl_h = int(12 + math.sin(t * 9.0 + side) * 3)
            pygame.draw.polygon(surface, c_flame, [(cx_f - 5, cy_f - 3), (cx_f, cy_f - 3 - fl_h), (cx_f + 5, cy_f - 3)])
            pygame.draw.polygon(surface, (255, 240, 150), [(cx_f - 2, cy_f - 3), (cx_f, cy_f - 2 - fl_h // 2), (cx_f + 2, cy_f - 3)])

        # Capucha rasgada/velo oscuro detrás de la cabeza vendada + mechones plateados-violeta
        veil = [(x, y - 36), (x + 16, y - 22), (x + 14, y - 6), (x - 14, y - 6), (x - 16, y - 22)]
        pygame.draw.polygon(surface, c_robe, veil)
        pygame.draw.polygon(surface, c_flame, veil, 1)

        # Cabeza envuelta en vendas rituales con un solo ojo llameante al descubierto (homenaje a Sirius)
        pygame.draw.circle(surface, c_band, (x, y - 20), 12)
        pygame.draw.circle(surface, (65, 52, 78), (x, y - 20), 12, 2)
        for bx1, by1, bx2, by2 in [(-10, -24, 10, -20), (-11, -18, 11, -15), (-8, -13, 8, -11)]:
            pygame.draw.line(surface, (160, 145, 175), (x + bx1, y + by1), (x + bx2, y + by2), 1)
        # Abertura sombría del ojo derecho ardiendo en llamas
        pygame.draw.ellipse(surface, (18, 8, 22), (x + 1, y - 24, 9, 7))
        pygame.draw.circle(surface, c_flame, (x + 5, y - 21), 3)
        pygame.draw.circle(surface, (255, 248, 180), (x + 5, y - 21), 1)
        # Lágrima violeta-fuego deslizándose por las vendas
        tear_y = y - 16 + int((t * 14) % 8)
        pygame.draw.circle(surface, (215, 120, 255), (x + 5, tear_y), 2)

    @staticmethod
    def _draw_sectario(surface, x, y, t, flash, mercy):
        """Dibuja al Dedo de la Pereza (Cultista de la Bruja estilo Betelgeuse con Manos Invisibles y Evangelio)."""
        is_spared = (mercy >= 100)
        c_robe = (255, 255, 255) if flash > 0.05 else (20, 10, 28)
        c_trim = (255, 235, 90) if is_spared else (188, 55, 245)
        c_gold = (232, 198, 92)

        # Sello del Culto de la Bruja y miasma bajo sus pies
        aura = pygame.Surface((60, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (125, 25, 185, 105), (2, 2, 56, 12))
        pygame.draw.ellipse(aura, (*c_trim, 210), (4, 3, 52, 10), 1)
        surface.blit(aura, (x - 30, y + 36))
        DeltaruneEnemyRenderer._draw_miasma_aura(surface, x, y + 8, t, count=6, rx=26, col=c_trim)

        # 3 Manos Invisibles articuladas brotando detrás del cultista
        w1 = math.sin(t * 3.8) * 6
        w2 = math.cos(t * 4.4) * 6
        w3 = math.sin(t * 3.2 + 1.5) * 5
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x - 12, y - 2, x - 28, y - 14 + w1, x - 38, y - 26 - w2, aura_col=c_trim, thick=4)
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x + 12, y - 2, x + 28, y - 16 - w1, x + 38, y - 26 + w2, aura_col=c_trim, thick=4)
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x + 8, y + 10, x + 26, y + 14 + w3, x + 36, y + 4 - w3, aura_col=(150, 40, 225), thick=4)

        # Túnica negra clásica del Culto de la Bruja con costuras doradas/violeta
        sway = int(math.sin(t * 4.0) * 2)
        robe_pts = [
            (x - 15, y - 6), (x + 15, y - 6),
            (x + 23, y + 40 + sway), (x, y + 44), (x - 23, y + 40 - sway),
        ]
        pygame.draw.polygon(surface, c_robe, robe_pts)
        pygame.draw.polygon(surface, c_trim, robe_pts, 2)

        # Estola sacerdotal púrpura con el Ojo del Culto en oro
        pygame.draw.rect(surface, (46, 16, 72), (x - 6, y - 3, 12, 43))
        pygame.draw.line(surface, c_gold, (x - 6, y - 3), (x - 6, y + 40), 1)
        pygame.draw.line(surface, c_gold, (x + 6, y - 3), (x + 6, y + 40), 1)
        pygame.draw.ellipse(surface, c_gold, (x - 5, y + 9, 10, 6), 1)
        pygame.draw.circle(surface, c_trim, (x, y + 12), 2)

        # Mangas largas y daga ritual curva a la derecha
        hand_bob = int(math.sin(t * 4.8) * 3)
        pygame.draw.polygon(surface, c_robe, [(x - 13, y - 2), (x - 25, y + 10 + hand_bob), (x - 16, y + 19 + hand_bob)])
        pygame.draw.polygon(surface, c_trim, [(x - 13, y - 2), (x - 25, y + 10 + hand_bob), (x - 16, y + 19 + hand_bob)], 1)
        pygame.draw.polygon(surface, c_robe, [(x + 13, y - 2), (x + 25, y + 10 - hand_bob), (x + 16, y + 19 - hand_bob)])
        pygame.draw.polygon(surface, c_trim, [(x + 13, y - 2), (x + 25, y + 10 - hand_bob), (x + 16, y + 19 - hand_bob)], 1)
        # Daga curva del Culto en la mano derecha
        dx, dy = x + 22, y + 14 - hand_bob
        pygame.draw.polygon(surface, (200, 215, 235), [(dx, dy), (dx + 12, dy - 7), (dx + 6, dy + 4)])
        pygame.draw.polygon(surface, c_trim, [(dx, dy), (dx + 12, dy - 7), (dx + 6, dy + 4)], 1)

        # Capucha puntiaguda profunda ligeramente ladeada (tic de Pereza)
        tilt = int(math.sin(t * 5.2) * 2) if not is_spared else 0
        hood_pts = [
            (x + tilt, y - 36), (x + 17 + tilt, y - 16), (x + 14, y - 2), (x - 14, y - 2), (x - 17 + tilt, y - 16)
        ]
        pygame.draw.polygon(surface, c_robe, hood_pts)
        pygame.draw.polygon(surface, c_trim, hood_pts, 2)
        pygame.draw.circle(surface, (6, 2, 12), (x + tilt // 2, y - 13), 10)

        # Ojos desorbitados asimétricos (guiño a Betelgeuse) y sonrisa fanática bajo la capucha
        eye_c = (255, 240, 110) if is_spared else (120, 255, 130)
        pygame.draw.circle(surface, eye_c, (x - 4 + tilt // 2, y - 14), 3)
        pygame.draw.circle(surface, eye_c, (x + 4 + tilt // 2, y - 15), 4)
        pygame.draw.circle(surface, (10, 6, 16), (x - 4 + tilt // 2, y - 14), 1)
        pygame.draw.circle(surface, (10, 6, 16), (x + 4 + tilt // 2, y - 15), 1)
        pygame.draw.arc(surface, (235, 225, 240), (x - 6 + tilt // 2, y - 12, 12, 6), math.pi, 2 * math.pi, 1)

        # Evangelio Negro abierto flotando a la izquierda
        DeltaruneEnemyRenderer._draw_witch_gospel(surface, x - 28, y - 4 + hand_bob, t, trim_col=c_trim)

    @staticmethod
    def _draw_sepulturero(surface, x, y, t, flash, mercy):
        """Dibuja al Jefe Morvath el Sepulturero como Arzobispo del Osario (Re:Zero Witch Cult Boss)."""
        is_spared = (mercy >= 100)
        c_cloak = (255, 255, 255) if flash > 0.05 else (20, 10, 30)
        c_trim = (255, 235, 95) if is_spared else (210, 48, 125)
        c_miasma = (255, 235, 95) if is_spared else (180, 48, 240)
        c_armor = (255, 255, 255) if flash > 0.05 else (90, 92, 114)

        # Sello ritual y miasma ascendente bajo el Jefe
        aura = pygame.Surface((72, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (165, 32, 175, 115), (0, 1, 72, 18))
        pygame.draw.ellipse(aura, (*c_trim, 210), (3, 3, 66, 14), 1)
        surface.blit(aura, (x - 36, y + 36))
        DeltaruneEnemyRenderer._draw_miasma_aura(surface, x, y + 8, t, count=7, rx=32, col=c_miasma)

        # 4 Manos Invisibles masivas brotando tras el manto de Morvath
        w1 = math.sin(t * 3.4) * 7
        w2 = math.cos(t * 4.0) * 7
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x - 16, y - 8, x - 34, y - 22 + w1, x - 44, y - 34 - w2, aura_col=c_miasma, thick=5)
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x + 16, y - 8, x + 34, y - 22 - w1, x + 44, y - 34 + w2, aura_col=c_miasma, thick=5)
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x - 16, y + 10, x - 36, y + 16 - w2, x - 46, y + 4 + w1, aura_col=c_trim, thick=4)
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x + 16, y + 10, x + 36, y + 16 + w2, x + 46, y + 4 - w1, aura_col=c_trim, thick=4)

        # Manto arzobispal negro en capas rasgadas
        wave = int(math.sin(t * 4.2) * 3)
        cloak_pts = [
            (x - 21, y - 10), (x + 21, y - 10),
            (x + 30, y + 39 + wave), (x + 11, y + 45), (x, y + 39 - wave),
            (x - 12, y + 45), (x - 30, y + 39 - wave),
        ]
        pygame.draw.polygon(surface, c_cloak, cloak_pts)
        pygame.draw.polygon(surface, c_trim, cloak_pts, 2)

        # Pechera de costillas de hierro forjado y estola púrpura-oro
        pygame.draw.rect(surface, (36, 14, 56), (x - 13, y - 6, 26, 36), border_radius=4)
        for ry in range(y - 2, y + 22, 6):
            pygame.draw.line(surface, c_armor, (x - 10, ry), (x + 10, ry), 2)
        pygame.draw.line(surface, (235, 200, 95), (x, y - 4), (x, y + 28), 2)

        # Hombreras góticas con púas de hierro
        pygame.draw.ellipse(surface, c_armor, (x - 28, y - 13, 17, 11))
        pygame.draw.ellipse(surface, c_armor, (x + 11, y - 13, 17, 11))
        pygame.draw.polygon(surface, c_trim, [(x - 23, y - 13), (x - 27, y - 22), (x - 17, y - 13)])
        pygame.draw.polygon(surface, c_trim, [(x + 23, y - 13), (x + 27, y - 22), (x + 17, y - 13)])

        # Capucha catedralicia puntiaguda y Corona de Espinas dorada
        hood = [(x, y - 39), (x + 18, y - 20), (x + 15, y - 6), (x - 15, y - 6), (x - 18, y - 20)]
        pygame.draw.polygon(surface, (14, 6, 22), hood)
        pygame.draw.polygon(surface, c_trim, hood, 2)
        pygame.draw.circle(surface, (6, 2, 12), (x, y - 18), 11)
        crown_pts = [
            (x - 12, y - 27), (x - 10, y - 37), (x - 4, y - 30),
            (x, y - 41), (x + 4, y - 30), (x + 10, y - 37), (x + 12, y - 27),
        ]
        pygame.draw.polygon(surface, (228, 198, 95), crown_pts)
        pygame.draw.polygon(surface, (42, 24, 18), crown_pts, 1)

        # Ojos rasgados incandescentes bajo la capucha
        eye_col = (120, 245, 255) if is_spared else (255, 225, 75)
        pygame.draw.polygon(surface, eye_col, [(x - 9, y - 20), (x - 2, y - 17), (x - 6, y - 14)])
        pygame.draw.polygon(surface, eye_col, [(x + 9, y - 20), (x + 2, y - 17), (x + 6, y - 14)])
        pygame.draw.circle(surface, (255, 255, 255), (x - 5, y - 17), 1)
        pygame.draw.circle(surface, (255, 255, 255), (x + 5, y - 17), 1)

        # Guadaña-Pala Ancestral con hoja en medialuna apuntando hacia afuera (sin tapar la corona)
        scythe_bob = int(math.sin(t * 3.0) * 3)
        sx = x + 28
        sy = y + scythe_bob
        pygame.draw.line(surface, (132, 94, 62), (sx, sy - 34), (sx - 3, sy + 39), 3)
        pygame.draw.circle(surface, (230, 198, 95), (sx, sy - 33), 3)
        blade_pts = [
            (sx, sy - 32),
            (sx + 18, sy - 36),
            (sx + 30, sy - 22),
            (sx + 21, sy - 10),
            (sx + 16, sy - 22),
            (sx + 1, sy - 24),
        ]
        pygame.draw.polygon(surface, (205, 220, 245), blade_pts)
        pygame.draw.polygon(surface, c_trim, blade_pts, 2)
        pygame.draw.lines(surface, (255, 235, 250), False, [(sx + 2, sy - 31), (sx + 17, sy - 34), (sx + 27, sy - 22)], 1)

        # Incensario / Farol de Almas encadenado a la izquierda
        lan_x = x - 29 + int(math.sin(t * 3.6) * 3)
        lan_y = y + 5 + int(math.cos(t * 3.6) * 2)
        pygame.draw.line(surface, c_armor, (x - 18, y - 4), (lan_x, lan_y - 8), 2)
        pygame.draw.rect(surface, (36, 28, 52), (lan_x - 6, lan_y - 6, 12, 15), border_radius=2)
        pygame.draw.rect(surface, (225, 195, 90), (lan_x - 6, lan_y - 6, 12, 15), 1, border_radius=2)
        pygame.draw.circle(surface, (120, 240, 255), (lan_x, lan_y + 1), 4)
        pygame.draw.circle(surface, (255, 255, 255), (lan_x, lan_y + 1), 2)

        # Evangelio abierto flotando junto al pecho
        DeltaruneEnemyRenderer._draw_witch_gospel(surface, x, y + 26, t, trim_col=c_miasma)

    @staticmethod
    def _draw_arconte(surface, x, y, t, flash, mercy):
        """Dibuja al Jefe Supremo Vaelkor, Soberano del Cristal Negro y las Sombras de la Bruja."""
        is_spared = (mercy >= 100)
        c_cloak = (255, 255, 255) if flash > 0.05 else (14, 5, 24)
        c_fire = (255, 235, 95) if is_spared else (238, 38, 98)
        c_miasma = (255, 235, 95) if is_spared else (185, 42, 245)

        # Sombra abismal con doble borde negro y carmesí
        pygame.draw.ellipse(surface, (0, 0, 0), (x - 38, y + 35, 76, 18))
        pygame.draw.ellipse(surface, c_fire, (x - 36, y + 37, 72, 14), 2)
        pygame.draw.ellipse(surface, (38, 6, 56), (x - 28, y + 39, 56, 10))
        DeltaruneEnemyRenderer._draw_miasma_aura(surface, x, y + 6, t, count=8, rx=38, col=c_miasma)

        # 6 Manos de Sombra de la Bruja desplegadas como alas abismales
        for side in (-1, 1):
            for idx, (oy, reach, phase) in enumerate([(-14, 46, 0.0), (0, 50, 1.2), (14, 42, 2.4)]):
                sw = math.sin(t * 3.8 + phase) * 6
                DeltaruneEnemyRenderer._draw_unseen_hand(
                    surface,
                    x + side * 16, y + oy,
                    x + side * (reach * 0.62), y + oy - 8 + sw,
                    x + side * reach, y + oy - 16 - sw,
                    aura_col=c_fire if idx == 0 else c_miasma,
                    thick=5 if idx == 1 else 4,
                )

        # 6 Esquirlas de Cristal Quebrado orbitando detrás de Vaelkor
        for i in range(6):
            ang = t * 1.8 + i * (math.pi / 3.0)
            sx = int(x + math.cos(ang) * 34)
            sy = int(y - 4 + math.sin(ang) * 19)
            shard = [(sx, sy - 8), (sx + 5, sy), (sx, sy + 8), (sx - 5, sy)]
            pygame.draw.polygon(surface, c_fire, shard)
            pygame.draw.polygon(surface, (0, 0, 0), shard, 2)
            pygame.draw.line(surface, (255, 225, 245), (sx, sy - 6), (sx, sy + 6), 1)

        # Halo de Eclipse lunar detrás de su cabeza
        pygame.draw.circle(surface, (0, 0, 0), (x, y - 22), 23, 4)
        pygame.draw.circle(surface, c_fire, (x, y - 22), 22, 2)
        pygame.draw.circle(surface, c_miasma, (x, y - 22), 18, 1)

        # Lenguas de Fuego Oscuro emergiendo de sus hombros
        for fx_off in (-22, -12, 12, 22):
            fl_h = int(14 + 6 * math.sin(t * 10.0 + fx_off))
            f_pts = [(x + fx_off - 6, y - 6), (x + fx_off, y - 12 - fl_h), (x + fx_off + 6, y - 6)]
            pygame.draw.polygon(surface, (35, 5, 52), f_pts)
            pygame.draw.polygon(surface, (0, 0, 0), f_pts, 2)
            pygame.draw.line(surface, c_fire, (x + fx_off, y - 8), (x + fx_off, y - 10 - fl_h // 2), 2)

        # Manto del Rey del Cristal Negro
        wave = int(math.sin(t * 4.8) * 3)
        cloak_pts = [
            (x - 22, y - 12), (x + 22, y - 12),
            (x + 31, y + 41 + wave), (x + 12, y + 46),
            (x, y + 39 - wave), (x - 12, y + 46), (x - 31, y + 41 - wave),
        ]
        pygame.draw.polygon(surface, c_cloak, cloak_pts)
        pygame.draw.polygon(surface, c_fire, cloak_pts, 2)
        pygame.draw.polygon(surface, (0, 0, 0), cloak_pts, 1)

        # Núcleo de cristal agrietado encadenado en el pecho
        core_pts = [(x, y - 6), (x + 11, y + 8), (x, y + 23), (x - 11, y + 8)]
        pygame.draw.polygon(surface, c_fire, core_pts)
        pygame.draw.polygon(surface, (0, 0, 0), core_pts, 2)
        pygame.draw.line(surface, (255, 240, 255), (x - 5, y + 4), (x + 5, y + 12), 2)
        pygame.draw.line(surface, (0, 0, 0), (x + 4, y + 3), (x - 4, y + 14), 1)

        # Cabeza abismal velada y Corona de Cristal Negro Quebrado
        pygame.draw.circle(surface, (8, 3, 16), (x, y - 20), 14)
        pygame.draw.circle(surface, (0, 0, 0), (x, y - 20), 14, 2)
        crown_pts = [
            (x - 14, y - 28), (x - 12, y - 42), (x - 5, y - 32),
            (x, y - 47), (x + 5, y - 32), (x + 12, y - 42), (x + 14, y - 28),
        ]
        pygame.draw.polygon(surface, c_fire, crown_pts)
        pygame.draw.polygon(surface, (0, 0, 0), crown_pts, 2)

        # 4 Ojos incandescentes rasgados
        eye_col = (255, 240, 95) if is_spared else (255, 65, 130)
        for ex, ey in [(x - 8, y - 22), (x + 4, y - 22), (x - 6, y - 16), (x + 2, y - 16)]:
            pygame.draw.rect(surface, eye_col, (ex, ey, 4, 3))
            pygame.draw.rect(surface, (255, 235, 245), (ex + 1, ey + 1, 2, 1))

        # Gran Mandoble de Fuego Oscuro y Cristal Quebrado (con guarda gótica inclinada hacia afuera)
        sw_y = y + int(math.sin(t * 3.8) * 4)
        gx_s, gy_s = x + 31, sw_y + 18
        # Empuñadura y guarda en cruz
        pygame.draw.line(surface, (232, 198, 95), (gx_s, gy_s + 14), (gx_s + 2, gy_s - 2), 3)
        pygame.draw.line(surface, c_fire, (gx_s - 8, gy_s - 1), (gx_s + 11, gy_s - 4), 4)
        pygame.draw.circle(surface, (255, 235, 130), (gx_s, gy_s + 15), 3)
        # Hoja flamígera oscura inclinada ligeramente a la derecha
        sword_pts = [
            (gx_s + 6, sw_y - 42),
            (gx_s + 11, sw_y - 12),
            (gx_s + 6, gy_s - 3),
            (gx_s - 2, gy_s - 2),
            (gx_s - 3, sw_y - 14),
        ]
        pygame.draw.polygon(surface, (24, 5, 42), sword_pts)
        pygame.draw.polygon(surface, c_fire, sword_pts, 2)
        pygame.draw.line(surface, (255, 230, 248), (gx_s + 5, sw_y - 35), (gx_s + 2, gy_s - 6), 2)

    @staticmethod
    def _draw_bufon_caos(surface, x, y, t, flash, mercy):
        """Dibuja a Jevix, Bufón del Caos en combate estilo Deltarune Dark World."""
        is_spared = (mercy >= 100)
        c_suit1 = (255, 255, 255) if flash > 0.05 else (95, 35, 165)
        c_suit2 = (255, 255, 255) if flash > 0.05 else (235, 55, 165)
        c_gold = (255, 235, 80)

        # Rebote elástico de bufón
        hop = int(abs(math.sin(t * 6.5)) * -6)
        by = y + hop

        pygame.draw.ellipse(surface, (25, 10, 40), (x - 22, y + 38, 44, 10))
        pygame.draw.ellipse(surface, c_gold, (x - 20, y + 39, 40, 8), 1)

        # Traje de arlequín dividido y cuello de picos amarillos
        pygame.draw.rect(surface, c_suit1, (x - 14, by - 2, 14, 34), border_top_left_radius=4, border_bottom_left_radius=4)
        pygame.draw.rect(surface, c_suit2, (x, by - 2, 14, 34), border_top_right_radius=4, border_bottom_right_radius=4)
        pygame.draw.rect(surface, (0, 0, 0), (x - 14, by - 2, 28, 34), 2, border_radius=4)

        for cx_off in (-10, 0, 10):
            collar = [(x + cx_off - 5, by - 3), (x + cx_off, by + 6), (x + cx_off + 5, by - 3)]
            pygame.draw.polygon(surface, c_gold, collar)
            pygame.draw.polygon(surface, (0, 0, 0), collar, 1)

        # Cabeza redonda lavanda y sonrisa de oreja a oreja
        pygame.draw.circle(surface, (215, 200, 245), (x, by - 14), 13)
        pygame.draw.circle(surface, (0, 0, 0), (x, by - 14), 13, 2)
        pygame.draw.ellipse(surface, (15, 10, 25), (x - 8, by - 19, 6, 6))
        pygame.draw.ellipse(surface, (15, 10, 25), (x + 2, by - 19, 6, 6))
        pygame.draw.circle(surface, c_gold, (x - 5, by - 16), 2)
        pygame.draw.circle(surface, c_gold, (x + 5, by - 16), 2)
        pygame.draw.arc(surface, (255, 235, 80) if is_spared else (40, 15, 65), (x - 8, by - 14, 16, 10), math.pi, 2 * math.pi, 2)

        # Gorro de bufón de dos puntas con cascabeles dorados
        wiggle = int(math.sin(t * 8.0) * 3)
        left_hat = [(x - 11, by - 22), (x - 26, by - 34 + wiggle), (x, by - 25)]
        right_hat = [(x + 11, by - 22), (x + 26, by - 34 - wiggle), (x, by - 25)]
        pygame.draw.polygon(surface, c_suit1, left_hat)
        pygame.draw.polygon(surface, (0, 0, 0), left_hat, 2)
        pygame.draw.polygon(surface, c_suit2, right_hat)
        pygame.draw.polygon(surface, (0, 0, 0), right_hat, 2)
        pygame.draw.circle(surface, c_gold, (x - 26, by - 34 + wiggle), 4)
        pygame.draw.circle(surface, c_gold, (x + 26, by - 34 - wiggle), 4)

        # Naipes mágicos orbitando alrededor
        for i in range(4):
            ang = t * 3.8 + i * (math.pi / 2.0)
            kx = int(x + math.cos(ang) * 28)
            ky = int(by + 6 + math.sin(ang) * 14)
            col_c = (255, 75, 195) if i % 2 == 0 else (80, 240, 255)
            pts = [(kx, ky - 6), (kx + 5, ky), (kx, ky + 6), (kx - 5, ky)]
            pygame.draw.polygon(surface, col_c, pts)
            pygame.draw.polygon(surface, (0, 0, 0), pts, 1)

    @staticmethod
    def _draw_centinela_neon(surface, x, y, t, flash, mercy):
        """Dibuja al Viro-Centinela Neón en combate estilo Cyber Dark World."""
        is_spared = (mercy >= 100)
        c_body = (255, 255, 255) if flash > 0.05 else (20, 18, 44)
        c_neon = (255, 240, 85) if is_spared else (70, 245, 255)
        c_mag = (255, 75, 215)

        pygame.draw.ellipse(surface, (15, 35, 55), (x - 24, y + 38, 48, 10))
        pygame.draw.ellipse(surface, c_neon, (x - 22, y + 39, 44, 8), 1)

        # Alas holográficas flotantes a los lados
        wing_off = int(math.sin(t * 6.0) * 4)
        for side in (-1, 1):
            w_pts = [
                (x + side * 14, y - 8),
                (x + side * 34, y - 22 + wing_off),
                (x + side * 28, y + 6),
                (x + side * 34, y + 22 - wing_off),
                (x + side * 14, y + 14),
            ]
            pygame.draw.polygon(surface, (30, 15, 55), w_pts)
            pygame.draw.polygon(surface, c_neon if side < 0 else c_mag, w_pts, 2)

        # Torso blindado cibernético
        armor_pts = [(x, y - 28), (x + 18, y - 8), (x + 12, y + 34), (x - 12, y + 34), (x - 18, y - 8)]
        pygame.draw.polygon(surface, c_body, armor_pts)
        pygame.draw.polygon(surface, c_neon, armor_pts, 2)

        # Visor LED cyberpunk en el rostro
        pygame.draw.rect(surface, (0, 0, 0), (x - 13, y - 16, 26, 9), border_radius=2)
        pygame.draw.rect(surface, c_mag if int(t * 10) % 2 == 0 else c_neon, (x - 11, y - 14, 22, 5), border_radius=1)

        # Lanza de plasma neón en la mano derecha
        lx = x + 24
        ly = y + int(math.sin(t * 4.5) * 3)
        pygame.draw.line(surface, (0, 0, 0), (lx, ly - 32), (lx, ly + 34), 5)
        pygame.draw.line(surface, c_neon, (lx, ly - 32), (lx, ly + 34), 2)
        pygame.draw.polygon(surface, c_mag, [(lx, ly - 40), (lx + 6, ly - 26), (lx - 6, ly - 26)])

    @staticmethod
    def _draw_nyxar(surface, x, y, t, flash, mercy):
        """Dibuja a Nyxar, Soberano de la Fuente Oscura (Jefe del Dark World) con alas neón, corona flotante y manos cibernéticas."""
        is_spared = (mercy >= 100)
        c_body = (255, 255, 255) if flash > 0.05 else (16, 10, 34)
        c_cyan = (255, 240, 95) if is_spared else (75, 245, 255)
        c_mag = (255, 215, 95) if is_spared else (255, 70, 215)
        c_gold = (255, 232, 85)

        # Halo de Fuente Oscura giratorio en el suelo
        floor_aura = pygame.Surface((74, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(floor_aura, (75, 245, 255, 80), (2, 3, 70, 14))
        pygame.draw.ellipse(floor_aura, (255, 70, 215, 195), (6, 4, 62, 12), 2)
        surface.blit(floor_aura, (x - 37, y + 36))

        # Anillo orbital con 4 fragmentos de neón girando detrás de Nyxar
        for i in range(4):
            ang = t * 2.4 + i * (math.pi / 2.0)
            ox = int(x + math.cos(ang) * 34)
            oy = int(y - 6 + math.sin(ang) * 16)
            col_o = c_cyan if i % 2 == 0 else c_mag
            pts = [(ox, oy - 7), (ox + 5, oy), (ox, oy + 7), (ox - 5, oy)]
            pygame.draw.polygon(surface, col_o, pts)
            pygame.draw.polygon(surface, (0, 0, 0), pts, 1)

        # Dos Manos Invisibles cibernéticas cargadas de energía neón
        sw = math.sin(t * 4.5) * 6
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x - 16, y + 2, x - 32, y - 6 + sw, x - 42, y - 18 - sw, aura_col=c_cyan, thick=4)
        DeltaruneEnemyRenderer._draw_unseen_hand(surface, x + 16, y + 2, x + 32, y - 6 - sw, x + 42, y - 18 + sw, aura_col=c_mag, thick=4)

        # Grandes alas holográficas dobles (estilo NEO / Dark Fountain)
        flap = int(math.sin(t * 5.2) * 5)
        for side, wcol in ((-1, c_cyan), (1, c_mag)):
            wing_outer = [
                (x + side * 14, y - 10),
                (x + side * 44, y - 30 + flap),
                (x + side * 36, y - 4),
                (x + side * 42, y + 22 - flap),
                (x + side * 16, y + 16),
            ]
            pygame.draw.polygon(surface, (24, 12, 48), wing_outer)
            pygame.draw.polygon(surface, wcol, wing_outer, 2)
            pygame.draw.line(surface, c_gold, (x + side * 16, y - 4), (x + side * 38, y - 18 + flap), 1)
            pygame.draw.line(surface, c_gold, (x + side * 16, y + 6), (x + side * 36, y + 14 - flap), 1)

        # Manto real geométrico y armadura pectoral con emblema Delta
        wave = int(math.sin(t * 4.4) * 3)
        cloak = [
            (x - 20, y - 12), (x + 20, y - 12),
            (x + 28, y + 40 + wave), (x + 10, y + 44),
            (x, y + 36 - wave), (x - 10, y + 44), (x - 28, y + 40 - wave),
        ]
        pygame.draw.polygon(surface, c_body, cloak)
        pygame.draw.polygon(surface, c_cyan, cloak, 2)
        # Núcleo brillante de la Fuente Oscura en el pecho
        core = [(x, y - 6), (x + 10, y + 8), (x, y + 22), (x - 10, y + 8)]
        pygame.draw.polygon(surface, c_mag, core)
        pygame.draw.polygon(surface, c_gold, core, 2)
        pygame.draw.circle(surface, (255, 255, 255), (x, y + 8), 3)

        # Cabeza blindada, ojos asimétricos neón y corona quebrada flotante
        pygame.draw.circle(surface, (10, 6, 22), (x, y - 20), 13)
        pygame.draw.circle(surface, c_cyan, (x, y - 20), 13, 2)
        # Ojos asimétricos brillantes (cian y dorado/magenta)
        pygame.draw.rect(surface, c_cyan, (x - 8, y - 22, 6, 4), border_radius=1)
        pygame.draw.rect(surface, c_gold if int(t * 8) % 2 == 0 else c_mag, (x + 2, y - 22, 6, 4), border_radius=1)
        pygame.draw.line(surface, (255, 255, 255), (x - 6, y - 21), (x - 4, y - 21), 1)
        pygame.draw.line(surface, (255, 255, 255), (x + 4, y - 21), (x + 6, y - 21), 1)

        # Corona flotante dorada-neón
        cy_cr = y - 34 + int(math.sin(t * 4.0) * 2)
        crown = [
            (x - 14, cy_cr + 4), (x - 12, cy_cr - 10), (x - 5, cy_cr - 2),
            (x, cy_cr - 15), (x + 5, cy_cr - 2), (x + 12, cy_cr - 10), (x + 14, cy_cr + 4),
        ]
        pygame.draw.polygon(surface, c_gold, crown)
        pygame.draw.polygon(surface, (0, 0, 0), crown, 2)
        pygame.draw.circle(surface, c_cyan, (x, cy_cr - 5), 2)

        # Lanza de la Fuente Oscura levitando a la derecha
        lx = x + 31
        ly = y + int(math.sin(t * 3.6) * 4)
        pygame.draw.line(surface, (0, 0, 0), (lx, ly - 38), (lx, ly + 34), 5)
        pygame.draw.line(surface, c_cyan, (lx, ly - 38), (lx, ly + 34), 2)
        pygame.draw.polygon(surface, c_mag, [(lx, ly - 48), (lx + 7, ly - 30), (lx, ly - 24), (lx - 7, ly - 30)])
        pygame.draw.polygon(surface, c_gold, [(lx, ly - 48), (lx + 7, ly - 30), (lx, ly - 24), (lx - 7, ly - 30)], 1)

    @staticmethod
    def _draw_tutorial_dummy(surface, template_id, x, y, t, flash, mercy):
        """Dibuja al Instructor del Tutorial en combate con su icono de Esquiva, Escudo Parry [Z] o Dash [X]."""
        is_spared = (mercy >= 100)
        col = (255, 240, 85) if is_spared else (
            (95, 225, 255) if template_id == "maniqui_esquiva" else (
                (65, 250, 130) if template_id == "maniqui_parry" else (255, 195, 70)
            )
        )
        c_body = (255, 255, 255) if flash > 0.05 else (48, 38, 72)

        # Base / pedestal rúnico
        pygame.draw.ellipse(surface, (20, 14, 34), (x - 24, y + 36, 48, 12))
        pygame.draw.ellipse(surface, col, (x - 22, y + 37, 44, 10), 2)
        pygame.draw.rect(surface, (115, 82, 48), (x - 4, y + 18, 8, 22))

        # Torso de maniquí maestro con emblema
        pygame.draw.rect(surface, c_body, (x - 16, y - 10, 32, 30), border_radius=5)
        pygame.draw.rect(surface, col, (x - 16, y - 10, 32, 30), 2, border_radius=5)

        # Brazos de madera articulados
        sway = int(math.sin(t * 4.0) * 3)
        pygame.draw.line(surface, (140, 105, 65), (x - 16, y), (x - 28, y - 6 + sway), 4)
        pygame.draw.line(surface, (140, 105, 65), (x + 16, y), (x + 28, y - 6 - sway), 4)

        # Emblema en el pecho según la lección (Corazón / Escudo Verde / Rayo Dash)
        if template_id == "maniqui_esquiva":
            pygame.draw.circle(surface, col, (x, y + 5), 7, 2)
        elif template_id == "maniqui_parry":
            sh_pts = [(x, y - 4), (x + 8, y), (x + 6, y + 10), (x, y + 15), (x - 6, y + 10), (x - 8, y)]
            pygame.draw.polygon(surface, (35, 190, 95), sh_pts)
            pygame.draw.polygon(surface, col, sh_pts, 2)
        else:
            bolt = [(x + 3, y - 4), (x - 5, y + 5), (x + 1, y + 5), (x - 3, y + 14), (x + 6, y + 4), (x, y + 4)]
            pygame.draw.polygon(surface, col, bolt)

        # Cabeza y sombrero de instructor
        pygame.draw.circle(surface, (235, 222, 195), (x, y - 22), 11)
        pygame.draw.circle(surface, (0, 0, 0), (x, y - 22), 11, 2)
        pygame.draw.circle(surface, (30, 25, 45), (x - 4, y - 23), 2)
        pygame.draw.circle(surface, (30, 25, 45), (x + 4, y - 23), 2)
        pygame.draw.arc(surface, (30, 25, 45), (x - 5, y - 21, 10, 6), math.pi, 2 * math.pi, 2)
        pygame.draw.polygon(surface, c_body, [(x - 13, y - 30), (x, y - 42), (x + 13, y - 30)])
        pygame.draw.polygon(surface, col, [(x - 13, y - 30), (x, y - 42), (x + 13, y - 30)], 2)



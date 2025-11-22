# app/initial_data.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db import models
from app.db.models import ChatType, SessionStatus


def create_demo_data(db: Session) -> None:
    """
    Crea datos de ejemplo realistas para demo.
    Es idempotente: si ya existe el usuario demo, no vuelve a crear todo.
    """

    # 1) Usuario demo
    user = (
        db.query(models.User)
        .filter(models.User.name == "Demo Athlete")
        .first()
    )

    if user:
        # Ya hay demo, no volvemos a poblar para evitar duplicados
        return

    user = models.User(
        name="Julian Pinto",
        goal="Build Muscle",
        experience_level="beginner",
        weight_kg=75.0,
        height_cm=180.0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2) Catálogo de ejercicios
    exercises_data = [
        # pecho
        ("Bench Press", "chest", "barbell", "intermediate"),
        ("Incline Dumbbell Press", "chest", "dumbbell", "intermediate"),
        ("Chest Fly Machine", "chest", "machine", "beginner"),
        # espalda
        ("Lat Pulldown", "back", "machine", "beginner"),
        ("Barbell Row", "back", "barbell", "intermediate"),
        ("Seated Cable Row", "back", "cable", "beginner"),
        # piernas
        ("Back Squat", "legs", "barbell", "intermediate"),
        ("Leg Press", "legs", "machine", "beginner"),
        ("Romanian Deadlift", "legs", "barbell", "intermediate"),
        # hombros
        ("Overhead Press", "shoulders", "barbell", "intermediate"),
        ("Lateral Raise", "shoulders", "dumbbell", "beginner"),
        # brazos
        ("Barbell Curl", "arms", "barbell", "beginner"),
        ("Triceps Pushdown", "arms", "cable", "beginner"),
        ("Dumbbell Hammer Curl", "arms", "dumbbell", "beginner"),
    ]

    exercise_map = {}  # name -> Exercise
    for name, group, equip, level in exercises_data:
        ex = models.Exercise(
            name=name,
            muscle_group=group,
            equipment=equip,
            level=level,
        )
        db.add(ex)
        db.flush()  # para que tenga id
        exercise_map[name] = ex

    db.commit()

    # 3) Crear sesiones de las últimas ~2 semanas
    now = datetime.utcnow()

    # Lista de "planes" de sesión con contexto realista
    session_templates = [
        {
            "days_ago": 12,
            "status": SessionStatus.COMPLETED,
            "notes": "Empezando bloque nuevo de entrenamiento, me sentía bien.",
            "fatigue": 3,
            "sleep": 7.5,
            "exercises": [
                # name, series, reps, peso
                ("Bench Press", 3, 8, [60, 60, 60]),
                ("Lat Pulldown", 3, 10, [55, 55, 52.5]),
                ("Overhead Press", 3, 8, [35, 35, 32.5]),
            ],
        },
        {
            "days_ago": 9,
            "status": SessionStatus.COMPLETED,
            "notes": "Piernas fuertes, pero algo cansado del trabajo.",
            "fatigue": 6,
            "sleep": 6.0,
            "exercises": [
                ("Back Squat", 4, 6, [80, 80, 82.5, 82.5]),
                ("Leg Press", 3, 10, [140, 140, 140]),
                ("Romanian Deadlift", 3, 8, [70, 70, 70]),
            ],
        },
        {
            "days_ago": 7,
            "status": SessionStatus.COMPLETED,
            "notes": "Upper body, sensación de buena energía.",
            "fatigue": 4,
            "sleep": 8.0,
            "exercises": [
                ("Incline Dumbbell Press", 3, 10, [24, 24, 24]),
                ("Seated Cable Row", 3, 10, [60, 60, 60]),
                ("Lateral Raise", 3, 15, [7, 7, 7]),
                ("Triceps Pushdown", 3, 12, [32, 32, 32]),
            ],
        },
        {
            "days_ago": 4,
            "status": SessionStatus.COMPLETED,
            "notes": "Entreno de fuerza, buscando progresar en básicos.",
            "fatigue": 5,
            "sleep": 7.0,
            "exercises": [
                ("Bench Press", 4, 5, [70, 70, 72.5, 72.5]),
                ("Barbell Row", 4, 6, [70, 70, 70, 72.5]),
                ("Barbell Curl", 3, 10, [28, 28, 28]),
            ],
        },
        {
            "days_ago": 2,
            "status": SessionStatus.PLANNED,
            "notes": "Sesión planificada de piernas, aún no ejecutada.",
            "fatigue": 5,
            "sleep": 6.5,
            "exercises": [
                ("Back Squat", 4, 6, [85, 85, 85, 85]),
                ("Leg Press", 3, 10, [150, 150, 150]),
                ("Romanian Deadlift", 3, 8, [75, 75, 75]),
            ],
        },
        {
            "days_ago": 0,
            "status": SessionStatus.PLANNED,
            "notes": "Sesión de empuje para hoy.",
            "fatigue": 4,
            "sleep": 7.0,
            "exercises": [
                ("Bench Press", 4, 6, [75, 75, 75, 75]),
                ("Incline Dumbbell Press", 3, 10, [26, 26, 26]),
                ("Overhead Press", 3, 8, [40, 40, 40]),
            ],
        },
    ]

    sessions = []

    for template in session_templates:
        started_at = now - timedelta(days=template["days_ago"])
        finished_at = (
            started_at + timedelta(hours=1)
            if template["status"] == SessionStatus.COMPLETED
            else None
        )

        session = models.WorkoutSession(
            user_id=user.id,
            started_at=started_at,
            finished_at=finished_at,
            status=template["status"],
            fatigue_before=template["fatigue"],
            sleep_hours_last_night=template["sleep"],
            notes=template["notes"],
        )
        db.add(session)
        db.flush()
        sessions.append(session)

        exercise_order = 1
        for ex_name, sets, target_reps, weights in template["exercises"]:
            ex_obj = exercise_map.get(ex_name)
            if not ex_obj:
                continue

            for i in range(sets):
                target_weight = weights[i] if i < len(weights) else weights[-1]

                # Para sesiones completadas, dar resultados reales realistas
                if template["status"] == SessionStatus.COMPLETED:
                    # pequeñas variaciones en reps/peso y RPE
                    actual_reps = target_reps - (1 if i == sets - 1 and template["fatigue"] >= 5 else 0)
                    if actual_reps < 1:
                        actual_reps = 1

                    actual_weight = target_weight
                    rpe = 7.5 if i < sets - 1 else 8.5
                    comment = None
                    if rpe >= 8.5:
                        comment = "Última serie pesada, casi fallo."
                else:
                    actual_reps = None
                    actual_weight = None
                    rpe = None
                    comment = None

                wset = models.WorkoutSet(
                    session_id=session.id,
                    exercise_id=ex_obj.id,
                    exercise_order=exercise_order,
                    set_number=i + 1,
                    target_reps=target_reps,
                    target_weight=target_weight,
                    actual_reps=actual_reps,
                    actual_weight=actual_weight,
                    rpe=rpe,
                    comment=comment,
                    auto_adjusted=False,
                )
                db.add(wset)

            exercise_order += 1

    db.commit()

    # 4) Mensajes de chat (general y de sesión)
    # General: un par de consultas sobre rutina y alimentación
    general_msgs = [
        (
            ChatType.GENERAL,
            "user",
            "Arnold, quiero enfocarme en ganar músculo sin subir tanta grasa. ¿Qué me recomiendas?",
        ),
        (
            ChatType.GENERAL,
            "arnold",
            "Perfecto, vamos a priorizar un ligero superávit calórico y progresión de cargas. Apunta a 1.6–2 g de proteína por kg de peso y controla tus calorías semanales.",
        ),
        (
            ChatType.GENERAL,
            "user",
            "Dormí solo 5 horas, ¿bajo la intensidad del entreno de hoy?",
        ),
        (
            ChatType.GENERAL,
            "arnold",
            "Sí, hoy mantén el volumen un poco más bajo y evita series al fallo. La prioridad es la consistencia, no reventarte en cada sesión.",
        ),
    ]

    for chat_type, role, text in general_msgs:
        msg = models.ChatMessage(
            user_id=user.id,
            session_id=None,
            chat_type=chat_type,
            role=role,
            text=text,
        )
        db.add(msg)

    # Chat de sesión para la sesión de hace 4 días (índice 3)
    if len(sessions) >= 4:
        session_force = sessions[3]
        session_msgs = [
            (
                ChatType.SESSION,
                "user",
                session_force.id,
                "La tercera serie de bench se sintió mucho más pesada, apenas hice 4 reps.",
            ),
            (
                ChatType.SESSION,
                "arnold",
                session_force.id,
                "Bien, para la próxima vez mantengamos este peso pero evita ir tan cerca del fallo en todas las series. Hoy cuenta como una buena sesión de fuerza.",
            ),
        ]
        for chat_type, role, sess_id, text in session_msgs:
            msg = models.ChatMessage(
                user_id=user.id,
                session_id=sess_id,
                chat_type=chat_type,
                role=role,
                text=text,
            )
            db.add(msg)

    db.commit()

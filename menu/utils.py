from .models import HorarioAtencion

def validar_horario_reserva(restaurante, fecha, hora):
    dia_semana = fecha.weekday()  # 0 lunes - 6 domingo

    horario = HorarioAtencion.objects.filter(
        restaurante=restaurante,
        dia=dia_semana,   # 👈 ESTE ES TU CAMPO REAL
        activo=True
    ).first()

    if not horario:
        return False

    if hora < horario.hora_apertura or hora > horario.hora_cierre:
        return False

    return True
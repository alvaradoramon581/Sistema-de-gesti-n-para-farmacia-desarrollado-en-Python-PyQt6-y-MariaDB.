"""Contraseñas nuevas con bcrypt; compatibilidad con las cuentas existentes."""
import hmac
import bcrypt


def es_hash(valor):
    return valor.startswith(('$2a$', '$2b$', '$2y$'))


def cifrar_contrasena(valor):
    if len(valor) < 8 or len(valor.encode('utf-8')) > 72:
        raise ValueError('La contraseña debe tener al menos 8 caracteres y como máximo 72 bytes.')
    return bcrypt.hashpw(valor.encode('utf-8'), bcrypt.gensalt()).decode('ascii')


def verificar_contrasena(valor, almacenada):
    if es_hash(almacenada):
        try:
            return bcrypt.checkpw(valor.encode('utf-8'), almacenada.encode('ascii'))
        except (ValueError, UnicodeError):
            return False
    return hmac.compare_digest(valor.encode('utf-8'), almacenada.encode('utf-8'))

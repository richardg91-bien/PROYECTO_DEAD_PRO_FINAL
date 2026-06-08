"""Excepciones personalizadas de la aplicación"""


class AppException(Exception):
    """Excepción base de la aplicación"""
    
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AppException):
    """Error de validación"""
    
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(AppException):
    """Recurso no encontrado"""
    
    def __init__(self, message="Recurso no encontrado"):
        super().__init__(message, 404)


class IAServiceError(AppException):
    """Error en servicio de IA"""
    
    def __init__(self, message="Error al consultar IA"):
        super().__init__(message, 503)


class FileUploadError(AppException):
    """Error en carga de archivo"""
    
    def __init__(self, message="Error en carga de archivo"):
        super().__init__(message, 400)

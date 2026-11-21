# Contribuir al proyecto

## Manejo de excepciones

Las excepciones de dominio se encuentran en `app/core/exceptions.py`.

Antes de crear una nueva excepción, verifica si una existente describe correctamente
el caso. Solo se debe crear una nueva clase cuando represente un comportamiento o
una respuesta HTTP diferente.

Excepciones principales:

- `NotFoundError`: el recurso solicitado no existe.
- `BusinessRuleError`: se violó una regla del negocio.

No se deben crear excepciones específicas por entidad, como `UserNotFoundError` o
`ProductNotFoundError`, si ambas tienen el mismo significado y tratamiento HTTP.

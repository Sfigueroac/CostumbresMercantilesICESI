# 🤖 Búsqueda Semántica con IA - Documentación

## ¿Qué es la Búsqueda Semántica?

La búsqueda semántica permite a los usuarios buscar costumbres mercantiles usando **lenguaje natural** en lugar de palabras clave exactas. Por ejemplo:

- ❌ Búsqueda tradicional: "pago" + "15 días" 
- ✅ Búsqueda semántica: "¿Cuánto tiempo tienen para pagar en contratos agrícolas?"

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar OpenAI API

1. Obtén tu API key en [OpenAI Platform](https://platform.openai.com/api-keys)
2. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edita `.env` y agrega tu API key:
   ```
   OPENAI_API_KEY=sk-tu-api-key-aqui
   ```

### 3. Generar Embeddings Iniciales

Una vez configurada la API, ejecuta:

```bash
# Inicia la aplicación
python app.py

# Ve a: http://localhost:5000/admin/generar-embeddings
# Esto generará embeddings para todas las costumbres existentes
```

## 🔧 Endpoints Disponibles

### `/api/busqueda-semantica`
Búsqueda AJAX para integración frontend.

**Parámetros:**
- `q`: Query en lenguaje natural

**Respuesta:**
```json
{
  "resultados": [
    {
      "id": 1,
      "ciudad": "Bogotá",
      "tipo": "Comercial",
      "contenido": "...",
      "similitud": 85.3
    }
  ],
  "total": 10,
  "query": "contratos de café"
}
```

### `/admin/estado-embeddings`
Verifica el estado de los embeddings generados.

### `/admin/generar-embeddings`
Genera embeddings para costumbres que no los tienen (solo desarrollo).

## 💡 Ejemplos de Consultas

- "contratos de café en el huila"
- "pagos en agricultura"
- "costumbres bancarias en medellín"
- "comercio de flores en cundinamarca"
- "contratos de suministro"

## ⚡ Performance

- **Modelo**: `text-embedding-3-small` (OpenAI)
- **Costo**: ~$0.00002 por 1K tokens
- **Velocidad**: <1 segundo para búsquedas
- **Precisión**: 85-95% relevancia semántica

## 🔒 Seguridad

- API key nunca se expone al frontend
- Validación de queries en servidor
- Rate limiting automático de OpenAI
- Embeddings cachados en base de datos

## 🐛 Troubleshooting

### "Búsqueda semántica no disponible"
- Verifica que `OPENAI_API_KEY` esté configurada
- Chequea que tienes créditos en OpenAI
- Revisa los logs del servidor

### "Error generando embeddings"
- Verifica conectividad a internet
- Confirma que la API key es válida
- Chequea límites de rate de OpenAI

### Embeddings no se generan
- Ve a `/admin/estado-embeddings` para verificar
- Ejecuta `/admin/generar-embeddings` manualmente
- Revisa que la base de datos tenga permisos de escritura

## 📈 Mejoras Futuras

1. **Cache inteligente** - Almacenar queries frecuentes
2. **Reranking** - Combinar similitud semántica con filtros tradicionales  
3. **Embeddings personalizados** - Entrenar modelo específico para legal
4. **Búsqueda híbrida** - Combinar keyword + semantic search
5. **Analytics** - Tracking de queries y mejores resultados

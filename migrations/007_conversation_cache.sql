-- 007_conversation_cache.sql
-- Sistema de Cache y Historial de Conversaciones para IA
-- Permite que ChatGPT tenga contexto de conversaciones previas
-- Reduce tokens consumidos con caching de respuestas comunes

-- =============================================================================
-- TABLA: conversation_cache
-- =============================================================================
-- Almacena el historial de conversaciones por cliente
-- SIMPLIFICADA: Usa phone_number directamente, sin FK a clients
CREATE TABLE IF NOT EXISTS conversation_cache (
    id BIGSERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    
    -- Contenido de la conversación
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    
    -- Metadatos
    conversation_topic VARCHAR(100),  -- ej: "plan_purchase", "technical_support", "billing"
    is_resolved BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '30 days',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_tokens CHECK (tokens_used >= 0)
);

-- Comentario de tabla
COMMENT ON TABLE conversation_cache IS 'Almacena historial de conversaciones para proporcionar contexto a la IA y reducir consumo de tokens';

-- Comentarios de columnas
COMMENT ON COLUMN conversation_cache.tokens_used IS 'Total de tokens consumidos en esta interacción';
COMMENT ON COLUMN conversation_cache.conversation_topic IS 'Categoría automática de la conversación (usado para contexto)';
COMMENT ON COLUMN conversation_cache.expires_at IS 'Fecha de expiración del cache (30 días por defecto)';
COMMENT ON COLUMN conversation_cache.is_resolved IS 'Indica si la conversación fue resuelta (para estadísticas)';

-- =============================================================================
-- TABLA: conversation_context
-- =============================================================================
-- Almacena información contextual de conversaciones activas
-- SIMPLIFICADA: Solo phone_number, sin FK
CREATE TABLE IF NOT EXISTS conversation_context (
    id BIGSERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL UNIQUE,
    
    -- Contexto actual
    current_topic VARCHAR(100) NOT NULL DEFAULT 'idle',
    context_data JSONB DEFAULT '{}',  -- Datos específicos del contexto
    
    -- ej: {"ultimo_usuario": "pepa", "plan_solicitado": "3Dias"}
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '24 hours',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE conversation_context IS 'Contexto activo de conversaciones en progreso para dar respuestas personalizadas';
COMMENT ON COLUMN conversation_context.context_data IS 'JSON con datos del flujo actual (plan, monto, etc)';

-- =============================================================================
-- TABLA: prompt_cache
-- =============================================================================
-- Cache de respuestas frecuentes para evitar llamadas innecesarias a OpenAI
-- Mejora velocidad y reduce costos dramáticamente
CREATE TABLE IF NOT EXISTS prompt_cache (
    id BIGSERIAL PRIMARY KEY,
    
    -- Hash del prompt para búsqueda rápida
    prompt_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256 del prompt
    original_prompt TEXT NOT NULL,
    
    -- Respuesta cacheada
    cached_response TEXT NOT NULL,
    
    -- Metadatos
    hit_count INTEGER DEFAULT 0,  -- Cuántas veces fue usado
    model VARCHAR(50) DEFAULT 'gpt-3.5-turbo',
    tokens_saved INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '7 days',
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE prompt_cache IS 'Cache de respuestas frecuentes a prompts similares para reducir costos de API';
COMMENT ON COLUMN prompt_cache.prompt_hash IS 'SHA256 hash del prompt para búsqueda rápida';
COMMENT ON COLUMN prompt_cache.hit_count IS 'Contador de cuántas veces se reutilizó esta respuesta';
COMMENT ON COLUMN prompt_cache.tokens_saved IS 'Tokens de OpenAI ahorrados al reutilizar esta respuesta';

-- =============================================================================
-- TABLA: ai_cost_tracking
-- =============================================================================
-- Monitoreo de costos de IA por phone_number
CREATE TABLE IF NOT EXISTS ai_cost_tracking (
    id BIGSERIAL PRIMARY KEY,
    phone_number TEXT,  -- Opcional, puede ser NULL para requests generales
    
    -- Detalles del costo
    request_type VARCHAR(100),  -- "chat_completion", "function_call", etc
    model_used VARCHAR(50) DEFAULT 'gpt-3.5-turbo',
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    
    -- Cálculo de costo (GPT-3.5-turbo: $0.0015/1K input, $0.002/1K output)
    input_cost DECIMAL(10, 6) DEFAULT 0,
    output_cost DECIMAL(10, 6) DEFAULT 0,
    total_cost DECIMAL(10, 6) DEFAULT 0,
    
    -- Flags
    was_cached BOOLEAN DEFAULT FALSE,  -- Si usó cache
    function_called TEXT,  -- Nombre de función si hubo function call
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_tokens CHECK (total_tokens >= 0),
    CONSTRAINT valid_cost CHECK (total_cost >= 0)
);

COMMENT ON TABLE ai_cost_tracking IS 'Registra todos los costos de IA para auditoría y optimización';
COMMENT ON COLUMN ai_cost_tracking.was_cached IS 'Indica si se usó cache para evitar la llamada a API';

-- =============================================================================
-- ÍNDICES PARA PERFORMANCE
-- =============================================================================

-- conversation_cache indexes
CREATE INDEX IF NOT EXISTS idx_conversation_cache_phone 
    ON conversation_cache(phone_number) 
    WHERE expires_at > CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_conversation_cache_created_at 
    ON conversation_cache(created_at DESC) 
    WHERE expires_at > CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_conversation_cache_topic 
    ON conversation_cache(conversation_topic) 
    WHERE expires_at > CURRENT_TIMESTAMP AND is_resolved = FALSE;

-- conversation_context indexes
CREATE INDEX IF NOT EXISTS idx_conversation_context_phone 
    ON conversation_context(phone_number) 
    WHERE expires_at > CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_conversation_context_topic 
    ON conversation_context(current_topic) 
    WHERE expires_at > CURRENT_TIMESTAMP;

-- prompt_cache indexes
CREATE INDEX IF NOT EXISTS idx_prompt_cache_hash 
    ON prompt_cache(prompt_hash) 
    WHERE expires_at > CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_prompt_cache_hit_count 
    ON prompt_cache(hit_count DESC) 
    WHERE expires_at > CURRENT_TIMESTAMP;

-- ai_cost_tracking indexes
CREATE INDEX IF NOT EXISTS idx_ai_cost_tracking_phone 
    ON ai_cost_tracking(phone_number, created_at DESC) 
    WHERE phone_number IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ai_cost_tracking_model 
    ON ai_cost_tracking(model_used, created_at DESC);

-- =============================================================================
-- FUNCIONES Y TRIGGERS
-- =============================================================================

-- Función para limpiar cache expirado automáticamente
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS TABLE(cleaned_conversations BIGINT, cleaned_context BIGINT, cleaned_prompts BIGINT) AS $$
DECLARE
    v_conversations BIGINT;
    v_context BIGINT;
    v_prompts BIGINT;
BEGIN
    -- Limpiar conversation_cache expirado
    DELETE FROM conversation_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS v_conversations = ROW_COUNT;
    
    -- Limpiar conversation_context expirado
    DELETE FROM conversation_context WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS v_context = ROW_COUNT;
    
    -- Limpiar prompt_cache expirado
    DELETE FROM prompt_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS v_prompts = ROW_COUNT;
    
    RETURN QUERY SELECT v_conversations, v_context, v_prompts;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar updated_at en conversation_cache
CREATE OR REPLACE FUNCTION update_conversation_cache_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SET search_path = pg_catalog, public;

CREATE TRIGGER trigger_conversation_cache_updated_at
    BEFORE UPDATE ON conversation_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_cache_timestamp();

-- Trigger para actualizar last_interaction en conversation_context
CREATE OR REPLACE FUNCTION update_conversation_context_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_interaction = CURRENT_TIMESTAMP;
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SET search_path = pg_catalog, public;

CREATE TRIGGER trigger_conversation_context_updated_at
    BEFORE UPDATE ON conversation_context
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_context_timestamp();

-- Trigger para actualizar last_used y updated_at en prompt_cache
CREATE OR REPLACE FUNCTION update_prompt_cache_usage()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_used = CURRENT_TIMESTAMP;
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prompt_cache_updated_at
    BEFORE UPDATE ON prompt_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_prompt_cache_usage();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Habilitar RLS en las nuevas tablas
ALTER TABLE conversation_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_cost_tracking ENABLE ROW LEVEL SECURITY;

-- Políticas para conversation_cache
CREATE POLICY conversation_cache_select_own
    ON conversation_cache FOR SELECT
    USING (
        client_id = (SELECT id FROM clients WHERE auth_user_id = auth.uid())
        OR
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'support'))
    );

CREATE POLICY conversation_cache_insert_own
    ON conversation_cache FOR INSERT
    WITH CHECK (
        client_id = (SELECT id FROM clients WHERE auth_user_id = auth.uid())
        OR
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

-- Políticas para conversation_context
CREATE POLICY conversation_context_select_own
    ON conversation_context FOR SELECT
    USING (
        client_id = (SELECT id FROM clients WHERE auth_user_id = auth.uid())
        OR
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'support'))
    );

CREATE POLICY conversation_context_insert_own
    ON conversation_context FOR INSERT
    WITH CHECK (
        client_id = (SELECT id FROM clients WHERE auth_user_id = auth.uid())
        OR
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY conversation_context_update_own
    ON conversation_context FOR UPDATE
    USING (
        client_id = (SELECT id FROM clients WHERE auth_user_id = auth.uid())
        OR
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

-- Políticas para ai_cost_tracking (solo admin puede ver todos)
CREATE POLICY ai_cost_tracking_select_own
    ON ai_cost_tracking FOR SELECT
    USING (
        client_id = (SELECT id FROM clients WHERE auth_user_id = auth.uid())
        OR
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY ai_cost_tracking_insert_admin
    ON ai_cost_tracking FOR INSERT
    WITH CHECK (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

-- Políticas para prompt_cache (solo admin puede insertar, todos pueden leer)
CREATE POLICY prompt_cache_select_all
    ON prompt_cache FOR SELECT
    USING (TRUE);

CREATE POLICY prompt_cache_insert_admin
    ON prompt_cache FOR INSERT
    WITH CHECK (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY prompt_cache_update_admin
    ON prompt_cache FOR UPDATE
    USING (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );

-- =============================================================================
-- VISTAS ÚTILES
-- =============================================================================

-- Vista para estadísticas de conversaciones recientes
CREATE OR REPLACE VIEW v_conversation_stats AS
SELECT
    c.client_id,
    c.phone_number,
    COUNT(DISTINCT DATE(c.created_at)) as days_active,
    COUNT(*) as total_messages,
    AVG(c.tokens_used) as avg_tokens_per_message,
    SUM(c.tokens_used) as total_tokens_consumed,
    COUNT(*) FILTER (WHERE c.is_resolved) as resolved_conversations,
    MAX(c.created_at) as last_interaction
FROM conversation_cache c
WHERE c.created_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY c.client_id, c.phone_number;

-- Vista para eficiencia de cache
CREATE OR REPLACE VIEW v_prompt_cache_stats AS
SELECT
    COUNT(*) as total_cached_prompts,
    SUM(hit_count) as total_reuses,
    SUM(tokens_saved) as total_tokens_saved,
    AVG(hit_count) as avg_hits_per_prompt,
    COUNT(*) FILTER (WHERE hit_count > 0) as actively_used_prompts,
    ROUND(100.0 * SUM(tokens_saved) / NULLIF(SUM(tokens_saved) + (SELECT COALESCE(SUM(total_tokens), 0) FROM ai_cost_tracking), 0), 2) as cache_efficiency_percent
FROM prompt_cache
WHERE expires_at > CURRENT_TIMESTAMP;

-- Vista para costos de IA por cliente
CREATE OR REPLACE VIEW v_ai_costs_by_client AS
SELECT
    c.id,
    c.name,
    c.phone_number,
    COUNT(*) as total_interactions,
    SUM(act.input_tokens) as total_input_tokens,
    SUM(act.output_tokens) as total_output_tokens,
    SUM(act.total_tokens) as total_tokens,
    SUM(act.total_cost) as total_cost,
    COUNT(*) FILTER (WHERE act.was_cached) as cached_interactions,
    ROUND(100.0 * COUNT(*) FILTER (WHERE act.was_cached) / COUNT(*), 2) as cache_hit_percentage,
    MAX(act.created_at) as last_interaction
FROM clients c
LEFT JOIN ai_cost_tracking act ON c.id = act.client_id
WHERE act.created_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY c.id, c.name, c.phone_number;

-- =============================================================================
-- GRANTS PARA PERMISOS
-- =============================================================================

-- Grant para usuarios de aplicación (no muestres tokens de IA)
GRANT SELECT, INSERT, UPDATE ON conversation_cache TO authenticated;
GRANT SELECT, INSERT, UPDATE ON conversation_context TO authenticated;
GRANT SELECT ON prompt_cache TO authenticated;

-- Grant para admin
GRANT ALL ON conversation_cache TO authenticated;
GRANT ALL ON conversation_context TO authenticated;
GRANT ALL ON prompt_cache TO authenticated;
GRANT ALL ON ai_cost_tracking TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_cache TO authenticated;

-- =============================================================================
-- EJEMPLOS DE USO (comentados)
-- =============================================================================

/*
-- 1. Insertar una conversación en el cache
INSERT INTO conversation_cache (client_id, phone_number, user_message, ai_response, tokens_used, conversation_topic)
VALUES (
    'uuid-del-cliente',
    '+51999888777',
    '¿Cuánto cuesta un día de internet?',
    'Cobramos S/1.00 por día de internet. ¿Cuántos días necesitas?',
    45,
    'plan_purchase'
);

-- 2. Obtener últimas 5 mensajes de un cliente
SELECT user_message, ai_response, created_at
FROM conversation_cache
WHERE client_id = 'uuid-del-cliente'
ORDER BY created_at DESC
LIMIT 5;

-- 3. Guardar contexto actual de compra
INSERT INTO conversation_context (client_id, phone_number, current_topic, context_data)
VALUES (
    'uuid-del-cliente',
    '+51999888777',
    'payment_waiting',
    '{"plan_type": "day", "duration": 1, "price": 1.00, "pending_payment": true}'::JSONB
);

-- 4. Verificar si hay cache para un prompt
SELECT cached_response, hit_count
FROM prompt_cache
WHERE prompt_hash = 'sha256-hash-del-prompt'
AND expires_at > CURRENT_TIMESTAMP;

-- 5. Limpiar cache expirado
SELECT cleanup_expired_cache();

-- 6. Ver estadísticas de caché
SELECT * FROM v_prompt_cache_stats;

-- 7. Ver costos de IA por cliente
SELECT * FROM v_ai_costs_by_client;
*/

-- =============================================================================
-- FIN DE LA MIGRACIÓN 007
-- =============================================================================
COMMENT ON SCHEMA public IS 'Schema con sistema de cache de conversaciones e IA optimizado para reducir costos';

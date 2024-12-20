-- Verificar que no existan mediciones para este ciclo
INSERT INTO cycle_measurements (
    cycle_id,
    phase_number,
    timestamp,
    flow,
    accum_flow,
    temperature,
    pressure,
    itv_value
)
WITH cycle_data AS (
    SELECT start_time, end_time 
    FROM cycle_patterns 
    WHERE id = 1
)
SELECT 
    1,
    CASE 
        WHEN fecha_hora BETWEEN '2024-12-20 13:22:42.155' AND '2024-12-20 13:22:46.267' THEN 1
        WHEN fecha_hora BETWEEN '2024-12-20 13:23:30.164' AND '2024-12-20 13:23:47.779' THEN 2
        WHEN fecha_hora BETWEEN '2024-12-20 13:24:44.460' AND '2024-12-20 13:25:08.240' THEN 3
        ELSE 0
    END,
    fecha_hora,
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_Flow' THEN valor END),
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_AccumFlow' THEN valor END),
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_Temperature' THEN valor END),
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_Pressure' THEN valor END),
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_ITV_Value' THEN valor END)
FROM tags 
WHERE fecha_hora BETWEEN (SELECT start_time FROM cycle_data) 
                    AND (SELECT end_time FROM cycle_data)
GROUP BY fecha_hora
ORDER BY fecha_hora ASC;


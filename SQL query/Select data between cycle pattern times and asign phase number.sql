WITH cycle_data AS (
    SELECT start_time, end_time 
    FROM cycle_patterns 
    WHERE id = 1
)
SELECT 
    1 as cycle_id,
    CASE 
        WHEN fecha_hora BETWEEN '2024-12-20 13:22:42.155' AND '2024-12-20 13:22:46.267' THEN 1
        WHEN fecha_hora BETWEEN '2024-12-20 13:23:30.164' AND '2024-12-20 13:23:47.779' THEN 2
        WHEN fecha_hora BETWEEN '2024-12-20 13:24:44.460' AND '2024-12-20 13:25:08.240' THEN 3
        ELSE 0
    END as phase_number,
    fecha_hora,
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_Flow' THEN valor END) as flow,
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_AccumFlow' THEN valor END) as accum_flow,
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_Temperature' THEN valor END) as temperature,
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_PF3A_Pressure' THEN valor END) as pressure,
    GROUP_CONCAT(CASE WHEN nombre = 'AMS00_ITV_Value' THEN valor END) as itv_value
FROM tags 
WHERE fecha_hora BETWEEN (SELECT start_time FROM cycle_data) 
                    AND (SELECT end_time FROM cycle_data)
GROUP BY fecha_hora
ORDER BY fecha_hora ASC;

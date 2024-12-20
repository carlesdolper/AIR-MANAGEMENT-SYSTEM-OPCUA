SELECT 
    fecha_hora,
    GROUP_CONCAT(CASE 
        WHEN nombre = 'AMS00_PF3A_Flow' THEN valor 
    END) as flow,
    GROUP_CONCAT(CASE 
        WHEN nombre = 'AMS00_PF3A_Pressure' THEN valor 
    END) as pressure,
    GROUP_CONCAT(CASE 
        WHEN nombre = 'AMS00_PF3A_Temperature' THEN valor 
    END) as temperature,
    GROUP_CONCAT(CASE 
        WHEN nombre = 'AMS00_ITV_Value' THEN valor 
    END) as itv_value,
    GROUP_CONCAT(CASE 
        WHEN nombre = 'AMS00_PF3A_AccumFlow' THEN valor 
    END) as accum_flow
FROM tags 
WHERE fecha_hora BETWEEN '2024-12-19 11:44:42.151' AND '2024-12-19 11:45:01.323'
GROUP BY fecha_hora
ORDER BY fecha_hora ASC;



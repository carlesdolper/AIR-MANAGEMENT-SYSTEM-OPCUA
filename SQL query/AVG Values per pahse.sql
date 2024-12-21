WITH cycle_data AS (
    SELECT 
        cycle_id,
        phase_number,
        AVG(flow) as avg_flow,
        AVG(temperature) as avg_temp,
        AVG(pressure) as avg_pressure,
        AVG(itv_value) as avg_itv,
        CASE 
            WHEN phase_number = 0 THEN SUM(phase_consumption)
            ELSE MAX(accum_flow) - MIN(accum_flow)
        END as phase_consumption,
        COUNT(*) as num_measurements
    FROM (
        SELECT 
            *,
            CASE 
                WHEN phase_number = 0 AND 
                     LAG(phase_number) OVER (ORDER BY timestamp) != 0 THEN
                    accum_flow - LAG(accum_flow) OVER (ORDER BY timestamp)
                ELSE 0
            END as phase_consumption
        FROM cycle_measurements
    ) subquery
    GROUP BY cycle_id, phase_number
    ORDER BY cycle_id, phase_number
)
SELECT 
    cycle_id as "Ciclo",
    phase_number as "Fase",
    ROUND(avg_flow, 2) as "Flujo Medio",
    ROUND(avg_temp, 2) as "Temperatura Media",
    ROUND(avg_pressure, 3) as "Presión Media",
    ROUND(avg_itv, 3) as "ITV Medio",
    phase_consumption as "Consumo Fase",
    num_measurements as "Número de Mediciones"
FROM cycle_data;

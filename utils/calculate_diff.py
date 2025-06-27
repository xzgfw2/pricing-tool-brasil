def calculate_diff(value, other_value):
    try:
        # Tentar converter os valores para float
        value = float(value)
        other_value = float(other_value)

        # Calcular a diferença percentual
        return ((other_value - value) / value) * 100
    except (ValueError, ZeroDivisionError) as e:
        # Tratar erros de conversão ou divisão por zero
        print(f"Erro ao calcular diferença: {e}")
        return None

def format_number_color(number):
    if number is None or number == "":
        # Retornar um estilo padrão quando não há valor
        return {"color": "black"}
    
    try:
        # Tentar converter o valor para float
        number = float(number)

        # Definir a cor com base no valor
        style = {"color": "red"} if number < 0 else {"color": "blue"}
        return style
    except ValueError as e:
        # Tratar erros de conversão
        print(f"Erro ao formatar número: {e}")
        return {"color": "black"}  # Cor padrão em caso de erro

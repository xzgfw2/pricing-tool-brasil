def modify_column_if_other_column_changed(cell_value_changed, row_data, column_to_change, value_to_input):
    if cell_value_changed:
        for change in cell_value_changed:  # Percorre todas as alterações
            row_index = change['rowIndex']  # Captura o índice da linha alterada
            row_data[row_index][column_to_change] = value_to_input  # Altera a coluna "manual"
    return row_data
